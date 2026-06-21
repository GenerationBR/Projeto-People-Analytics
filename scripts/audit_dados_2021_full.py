"""
Extração completa dos valores reais do State of Data 2021
para comparação e atualização do Dashboard.jsx
"""
import csv, sys
from collections import defaultdict, Counter
sys.stdout.reconfigure(encoding='utf-8')

src = "data/treated/base_mercado_dados_2021_brasil.csv"
with open(src,"r",encoding="utf-8-sig") as f:
    raw = list(csv.reader(f))

headers = raw[0]
data    = raw[1:]   # 2645 linhas

COL_GENERO = 3   # P1_b  Genero
COL_CARGO  = 16  # P2_f  Cargo Atual
COL_NIVEL  = 17  # P2_g  Nivel
COL_FAIXA  = 18  # P2_h  Faixa salarial

def is_fem(row): return "eminino" in row[COL_GENERO]
def is_mas(row): return "asculino" in row[COL_GENERO]

# ── 1. % FEMININO GLOBAL ─────────────────────────────────────────
fem = sum(1 for r in data if len(r)>COL_GENERO and is_fem(r))
mas = sum(1 for r in data if len(r)>COL_GENERO and is_mas(r))
total = fem + mas
print("=" * 60)
print("1. % FEMININO GLOBAL")
print("=" * 60)
print(f"  Feminino: {fem}  |  Masculino: {mas}  |  Total c/ gênero: {total}")
print(f"  % Feminino: {round(fem/total*100,1)}%")
print(f"  Dashboard atual: 26.8%")
print(f"  Delta: {round(fem/total*100 - 26.8, 1):+.1f} p.p.")

# ── 2. CARGO ATUAL — todos os valores únicos ──────────────────────
print("\n" + "=" * 60)
print("2. CARGOS ATUAIS no CSV (todos com >5 registros)")
print("=" * 60)
cargo_g = defaultdict(lambda:{"fem":0,"mas":0})
for r in data:
    if len(r) <= max(COL_GENERO, COL_CARGO): continue
    c = r[COL_CARGO].strip()
    if not c: continue
    if is_fem(r): cargo_g[c]["fem"] += 1
    elif is_mas(r): cargo_g[c]["mas"] += 1

fem_total = sum(d["fem"] for d in cargo_g.values())
mas_total = sum(d["mas"] for d in cargo_g.values())

print(f"{'Cargo':<50} {'Total':>6} {'Fem':>5} {'Fem%':>7}")
for cargo, d in sorted(cargo_g.items(), key=lambda x: -(x[1]["fem"]+x[1]["mas"])):
    t = d["fem"]+d["mas"]
    if t < 5: continue
    pct = round(d["fem"]/t*100,1) if t else 0
    print(f"  {cargo[:48]:<48} {t:>6} {d['fem']:>5} {pct:>7.1f}%")

# ── 3. NÍVEL — valores únicos + % por gênero ──────────────────────
print("\n" + "=" * 60)
print("3. NÍVEL (nivelGeneroDados)")
print("=" * 60)
nivel_g = defaultdict(lambda:{"fem":0,"mas":0})
for r in data:
    if len(r) <= max(COL_GENERO, COL_NIVEL): continue
    n = r[COL_NIVEL].strip()
    if not n: continue
    if is_fem(r): nivel_g[n]["fem"] += 1
    elif is_mas(r): nivel_g[n]["mas"] += 1

total_fem_nivel = sum(d["fem"] for d in nivel_g.values())
total_mas_nivel = sum(d["mas"] for d in nivel_g.values())
print(f"Total com nível: fem={total_fem_nivel}  mas={total_mas_nivel}")
print(f"{'Nivel':<25} {'Fem':>5} {'Fem% dentro F':>15} {'Mas':>5} {'Mas% dentro M':>15}")
for nivel, d in sorted(nivel_g.items(), key=lambda x:-(x[1]["fem"]+x[1]["mas"])):
    pf = round(d["fem"]/total_fem_nivel*100,1) if total_fem_nivel else 0
    pm = round(d["mas"]/total_mas_nivel*100,1) if total_mas_nivel else 0
    print(f"  {nivel:<23} {d['fem']:>5} {pf:>14.1f}% {d['mas']:>5} {pm:>14.1f}%")

# ── 4. FAIXA SALARIAL — valores únicos + agrupamento ──────────────
print("\n" + "=" * 60)
print("4. FAIXA SALARIAL (faixaSalarialDados)")
print("=" * 60)
faixa_g = defaultdict(lambda:{"fem":0,"mas":0})
for r in data:
    if len(r) <= max(COL_GENERO, COL_FAIXA): continue
    f = r[COL_FAIXA].strip()
    if not f: continue
    if is_fem(r): faixa_g[f]["fem"] += 1
    elif is_mas(r): faixa_g[f]["mas"] += 1

total_fem_f = sum(d["fem"] for d in faixa_g.values())
total_mas_f = sum(d["mas"] for d in faixa_g.values())
print(f"Total com faixa: fem={total_fem_f}  mas={total_mas_f}")
print(f"\n{'Faixa original':<38} {'Fem':>5} {'Fem%':>7} {'Mas':>6} {'Mas%':>7}")
FAIXA_ORDER = [
    "Menos de R$ 1.000/mês",
    "de R$ 1.001/mês a R$ 2.000/mês",
    "de R$ 2.001/mês a R$ 3000/mês ",
    "de R$ 3.001/mês a R$ 4.000/mês",
    "de R$ 4.001/mês a R$ 6.000/mês",
    "de R$ 6.001/mês a R$ 8.000/mês",
    "de R$ 8.001/mês a R$ 12.000/mês",
    "de R$ 12.001/mês a R$ 16.000/mês",
    "de R$ 16.001/mês a R$ 20.000/mês",
    "de R$ 20.001/mês a R$ 25.000/mês",
    "de R$ 25.001/mês a R$ 30.000/mês",
    "de R$ 30.001/mês a R$ 40.000/mês",
    "Acima de R$ 40.001/mês",
]
for faixa in FAIXA_ORDER:
    # match parcial
    match = next((k for k in faixa_g if faixa[:20] in k), None)
    if not match: match = next((k for k in faixa_g if faixa[5:15] in k), None)
    if not match:
        print(f"  {faixa[:36]:<36}  NOT FOUND")
        continue
    d = faixa_g[match]
    pf = round(d["fem"]/total_fem_f*100,1) if total_fem_f else 0
    pm = round(d["mas"]/total_mas_f*100,1) if total_mas_f else 0
    print(f"  {match[:36]:<36} {d['fem']:>5} {pf:>6.1f}% {d['mas']:>6} {pm:>6.1f}%")

# Agrupar para formato Dashboard (6 faixas)
GRUPOS = {
    "Até R$4k":     ["Menos de R$ 1.000","de R$ 1.001/mês a R$ 2.000","de R$ 2.001/mês a R$ 3","de R$ 3.001/mês a R$ 4.000"],
    "R$4–8k":       ["de R$ 4.001/mês a R$ 6.000","de R$ 6.001/mês a R$ 8.000"],
    "R$8–12k":      ["de R$ 8.001/mês a R$ 12.000"],
    "R$12–16k":     ["de R$ 12.001/mês a R$ 16.000"],
    "R$16–20k":     ["de R$ 16.001/mês a R$ 20.000"],
    "Acima de R$20k":["de R$ 20.001","de R$ 25.001","de R$ 30.001","Acima de R$ 40.001"],
}
print(f"\n{'Faixa agrupada (Dashboard)':<22} {'Fem%':>7} {'Mas%':>7}  (Dashboard Fem% / Dashboard Mas%)")
DASH_FAI = {
    "Até R$4k":      (13.8, 8.6),
    "R$4–8k":        (31.5, 23.9),
    "R$8–12k":       (27.6, 27.1),
    "R$12–16k":      (14.2, 19.4),
    "R$16–20k":      (7.1, 11.8),
    "Acima de R$20k": (5.8, 9.2),
}
for grupo, prefixes in GRUPOS.items():
    fem_sum, mas_sum = 0, 0
    for faixa_key in faixa_g:
        if any(p in faixa_key for p in prefixes):
            fem_sum += faixa_g[faixa_key]["fem"]
            mas_sum += faixa_g[faixa_key]["mas"]
    pf = round(fem_sum/total_fem_f*100,1) if total_fem_f else 0
    pm = round(mas_sum/total_mas_f*100,1) if total_mas_f else 0
    df, dm = DASH_FAI[grupo]
    print(f"  {grupo:<20} {pf:>6.1f}% {pm:>6.1f}%   (Dash: {df}% / {dm}%)")

# ── 5. GESTÃO — % mulheres em cargos de gestão ────────────────────
# Col 15: P2_e Cargo como Gestor
COL_GESTOR = 15
print("\n" + "=" * 60)
print("5. GESTÃO (% feminino em cargos de gestão)")
print("=" * 60)
gestor_g = {"sim_f":0,"sim_m":0,"nao_f":0,"nao_m":0}
for r in data:
    if len(r) <= max(COL_GENERO, COL_GESTOR): continue
    g = r[COL_GESTOR].strip().lower()
    gen = r[COL_GENERO].strip()
    if not g: continue
    if "sim" in g or "gestor" in g:
        if is_fem(r): gestor_g["sim_f"] += 1
        elif is_mas(r): gestor_g["sim_m"] += 1
    else:
        if is_fem(r): gestor_g["nao_f"] += 1
        elif is_mas(r): gestor_g["nao_m"] += 1

print(f"  Valores únicos da coluna gestor (amostra): ", end="")
vals = Counter(r[COL_GESTOR].strip() for r in data if len(r)>COL_GESTOR and r[COL_GESTOR].strip())
print(dict(vals.most_common(5)))

total_gestores = gestor_g["sim_f"] + gestor_g["sim_m"]
if total_gestores > 0:
    pct_f_gestao = round(gestor_g["sim_f"]/total_gestores*100,1)
    print(f"  Total gestores: {total_gestores} | Feminino: {gestor_g['sim_f']} ({pct_f_gestao}%)")
    print(f"  Dashboard trajectoryStages 'Cargos de gestão em Dados': 14.6%")
else:
    print("  Coluna gestor não mapeada corretamente — ver valores acima")

# Mostrar valores brutos da coluna
print("\n  Todos os valores únicos de COL_GESTOR:")
for v, c in vals.most_common():
    print(f"    [{c:4d}x] '{v}'")
