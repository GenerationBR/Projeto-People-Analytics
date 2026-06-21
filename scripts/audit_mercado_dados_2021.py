"""
Auditoria: base_mercado_dados_2021_brasil.csv vs Dashboard.jsx (O Mercado)
Multi-index CSV — row 0 = headers (tuple strings), row 1+ = data
"""
import csv, sys
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8')

src = "data/treated/base_mercado_dados_2021_brasil.csv"
with open(src,"r",encoding="utf-8-sig") as f:
    raw = list(csv.reader(f))

headers = raw[0]
data = raw[1:]  # 2645 linhas

print(f"Total registros: {len(data)}")

# Localizar colunas relevantes
def find_col(keyword, headers):
    keyword_lower = keyword.lower()
    for i, h in enumerate(headers):
        if keyword_lower in h.lower():
            return i, h
    return None, None

# Imprimir índices das colunas de interesse
cols_interest = ["Genero", "Cargo", "Nivel", "Faixa", "Funcao", "Salario", "Area"]
print("\n=== Colunas encontradas ===")
for kw in cols_interest:
    idx, h = find_col(kw, headers)
    if idx is not None:
        print(f"  [{idx:3d}] {h}")

# Col índices fixos (confirmados na sessão anterior)
COL_GENERO = 3   # P1_b Genero
COL_CARGO  = 16  # Cargo Atual
COL_NIVEL  = 17  # Nível
COL_FAIXA  = 18  # Faixa salarial

print(f"\nColuna GENERO [{COL_GENERO}]: {headers[COL_GENERO]}")
print(f"Coluna CARGO  [{COL_CARGO}]:  {headers[COL_CARGO]}")
print(f"Coluna NIVEL  [{COL_NIVEL}]:  {headers[COL_NIVEL]}")
print(f"Coluna FAIXA  [{COL_FAIXA}]:  {headers[COL_FAIXA]}")

# ── % feminino global ─────────────────────────────────────────────
print("\n=== 1. % feminino global ===")
generos = Counter(r[COL_GENERO] for r in data if len(r) > COL_GENERO)
print(f"  Valores: {dict(generos.most_common(5))}")
fem_total = sum(v for k,v in generos.items() if "feminino" in k.lower() or "mulher" in k.lower())
total_valid = sum(v for k,v in generos.items() if k.strip())
pct_fem_real = round(fem_total/total_valid*100, 1) if total_valid else 0
print(f"  Feminino: {fem_total} / {total_valid} = {pct_fem_real}%")
print(f"  Dashboard representacaoFuncaoDados assume % global: 26.8%")
print(f"  Dashboard representacaoComparativa 'Profissionais de Dados': 26.8%")
print(f"  DIVERGÊNCIA: CSV={pct_fem_real}% vs Dashboard=26.8%  |  Delta={round(pct_fem_real-26.8,1):+.1f} p.p.")

# ── valores únicos de genero ──────────────────────────────────────
print(f"\n  Valores únicos genero: {list(generos.keys())[:8]}")

# ── Cargo atual — valores únicos e % feminino ─────────────────────
print("\n=== 2. representacaoFuncaoDados (% feminino por cargo/função) ===")
DASH_FUNC = {
    "Business Analyst": 33.4, "Analista de Dados": 32.1, "Analista de BI": 29.7,
    "Data Product Manager": 27.2, "Cientista de Dados": 23.6,
    "Analytics Engineer": 18.9, "Engenheiro de Dados": 15.8,
    "DBA": 14.7, "Arquiteto de Dados": 11.5,
}
cargo_g = defaultdict(lambda:{"total":0,"fem":0})
for r in data:
    if len(r) <= max(COL_GENERO, COL_CARGO):
        continue
    cargo = r[COL_CARGO].strip()
    genero = r[COL_GENERO].strip()
    if not cargo:
        continue
    cargo_g[cargo]["total"] += 1
    if "feminino" in genero.lower() or "mulher" in genero.lower():
        cargo_g[cargo]["fem"] += 1

# Mostrar top cargos
print("Top cargos no CSV (>20 registros):")
for cargo, d in sorted(cargo_g.items(), key=lambda x:-x[1]["total"]):
    if d["total"] >= 10:
        pct = round(d["fem"]/d["total"]*100, 1)
        print(f"  {cargo:<35} {d['total']:>5} reg | {pct:>6.1f}% fem")

print(f"\nComparação com Dashboard (match por substring):")
print(f"{'Função Dashboard':<30} {'CSV%':>8} {'Dash%':>8} {'Delta':>8} {'CSV n':>7}")
for func_dash, pct_dash in DASH_FUNC.items():
    func_lower = func_dash.lower()
    # buscar cargo no CSV com maior similaridade
    best_match = None
    best_n = 0
    for cargo, d in cargo_g.items():
        cargo_lower = cargo.lower()
        if any(w in cargo_lower for w in func_lower.split()):
            if d["total"] > best_n:
                best_match = cargo
                best_n = d["total"]
    if best_match:
        d = cargo_g[best_match]
        pct_csv = round(d["fem"]/d["total"]*100, 1)
        delta = round(pct_csv - pct_dash, 1)
        print(f"  {func_dash:<28} {pct_csv:>8.1f}% {pct_dash:>8.1f}% {delta:>+7.1f}  (n={d['total']}, match='{best_match[:20]}')")
    else:
        print(f"  {func_dash:<28}   NO MATCH   {pct_dash:>8.1f}%")

# ── Nível — distribuição por gênero (nivelGeneroDados) ───────────
print("\n=== 3. nivelGeneroDados (distribuição por nível e gênero) ===")
DASH_NIVEL = {
    "Estágio": {"mulheres":9.4,"homens":6.1},
    "Júnior":  {"mulheres":27.8,"homens":21.6},
    "Pleno":   {"mulheres":37.9,"homens":34.8},
    "Sênior":  {"mulheres":24.9,"homens":37.5},
}
nivel_g = defaultdict(lambda:{"fem":0,"mas":0})
total_fem_nivel = 0
total_mas_nivel = 0
for r in data:
    if len(r) <= max(COL_GENERO, COL_NIVEL):
        continue
    nivel = r[COL_NIVEL].strip()
    genero = r[COL_GENERO].strip()
    if not nivel:
        continue
    is_fem = "feminino" in genero.lower() or "mulher" in genero.lower()
    is_mas = "masculino" in genero.lower() or "homem" in genero.lower()
    if is_fem:
        nivel_g[nivel]["fem"] += 1
        total_fem_nivel += 1
    elif is_mas:
        nivel_g[nivel]["mas"] += 1
        total_mas_nivel += 1

print(f"Níveis encontrados no CSV:")
for nivel, d in sorted(nivel_g.items(), key=lambda x: -(x[1]["fem"]+x[1]["mas"])):
    total = d["fem"] + d["mas"]
    if total > 0:
        pct_f = round(d["fem"]/total_fem_nivel*100, 1) if total_fem_nivel else 0
        pct_m = round(d["mas"]/total_mas_nivel*100, 1) if total_mas_nivel else 0
        print(f"  {nivel:<20} fem={d['fem']} ({pct_f}%)  mas={d['mas']} ({pct_m}%)")

print(f"\nComparação Dashboard nivelGeneroDados (% por gênero dentro do gênero):")
for nivel_dash, vals in DASH_NIVEL.items():
    for nivel_csv, d in nivel_g.items():
        if nivel_dash.lower() in nivel_csv.lower() or nivel_csv.lower() in nivel_dash.lower():
            pct_f_csv = round(d["fem"]/total_fem_nivel*100,1) if total_fem_nivel else 0
            pct_m_csv = round(d["mas"]/total_mas_nivel*100,1) if total_mas_nivel else 0
            print(f"  {nivel_dash}: fem CSV={pct_f_csv}% Dash={vals['mulheres']}%  |  mas CSV={pct_m_csv}% Dash={vals['homens']}%")
            break

# ── Faixa salarial (faixaSalarialDados) ──────────────────────────
print("\n=== 4. faixaSalarialDados (distribuição salarial por gênero) ===")
faixa_g = defaultdict(lambda:{"fem":0,"mas":0})
total_fem_faixa = 0
total_mas_faixa = 0
for r in data:
    if len(r) <= max(COL_GENERO, COL_FAIXA):
        continue
    faixa = r[COL_FAIXA].strip()
    genero = r[COL_GENERO].strip()
    if not faixa:
        continue
    is_fem = "feminino" in genero.lower() or "mulher" in genero.lower()
    is_mas = "masculino" in genero.lower() or "homem" in genero.lower()
    if is_fem:
        faixa_g[faixa]["fem"] += 1
        total_fem_faixa += 1
    elif is_mas:
        faixa_g[faixa]["mas"] += 1
        total_mas_faixa += 1

print(f"Faixas no CSV:")
for faixa, d in sorted(faixa_g.items(), key=lambda x: -(x[1]["fem"]+x[1]["mas"])):
    pct_f = round(d["fem"]/total_fem_faixa*100,1) if total_fem_faixa else 0
    pct_m = round(d["mas"]/total_mas_faixa*100,1) if total_mas_faixa else 0
    print(f"  {faixa:<30} fem={d['fem']} ({pct_f}%)  mas={d['mas']} ({pct_m}%)")
