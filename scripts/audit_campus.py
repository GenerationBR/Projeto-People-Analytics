"""
Auditoria: base_campus_ti_brasil.csv vs Dashboard.jsx (A Base)
"""
import csv, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

src = "data/treated/base_campus_ti_brasil.csv"
with open(src,"r",encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

# ── Distribuição por curso ────────────────────────────────────────
total = len(rows)
curso_count = defaultdict(int)
for r in rows:
    curso_count[r["curso"]] += 1

print("=== 1. distribuicaoCurso ===")
print(f"{'Curso':<45} {'CSV%':>7}  {'Dash%':>7}  {'Delta':>7}")
DASH_CURSO = {
    "Análise e Desenvolvimento de Sistemas": 44.2,
    "Ciência da Computação": 23.8,
    "Sistemas de Informação": 17.4,
    "Ciência de Dados": 8.2,
    "Engenharia de Software": 6.3,
}
# Mapear nomes
MAP = {
    "Análise e Desenv. de Sistemas": "Análise e Desenvolvimento de Sistemas",
    "Análise e Desenvolvimento de Sistemas": "Análise e Desenvolvimento de Sistemas",
    "Ciência da Computação": "Ciência da Computação",
    "Sistemas de Informação": "Sistemas de Informação",
    "Ciência de Dados": "Ciência de Dados",
    "Engenharia de Software": "Engenharia de Software",
}
for curso, n in sorted(curso_count.items(), key=lambda x: -x[1]):
    pct_csv = round(n/total*100, 1)
    nome_norm = MAP.get(curso, curso)
    pct_dash = DASH_CURSO.get(nome_norm, "?")
    delta = round(pct_csv - pct_dash, 1) if isinstance(pct_dash, float) else "?"
    print(f"  {curso:<43} {pct_csv:>7.1f}%  {pct_dash:>7}%  {delta:>+7}")

# ── Evasão por curso e gênero ────────────────────────────────────
print("\n=== 2. evasaoPorCurso (% não-conclusão) ===")
DASH_EVASAO = {
    "Sistemas de Informação": {"mulheres": 77.8, "homens": 69.6},
    "Ciência da Computação": {"mulheres": 85.7, "homens": 75.4},
    "Análise e Desenvolvimento de Sistemas": {"mulheres": 67.6, "homens": 70.8},
    "Engenharia de Software": {"mulheres": 50.0, "homens": 72.2},
    "Ciência de Dados": {"mulheres": 83.3, "homens": 97.4},
}
# Cohort 2019-2020 (prazo 2/4 anos) — "concluiu" = coluna
# ADS = 2 anos -> cohort 2019-2020 com concluiu em 2021-2022
# outros = 4 anos -> cohort 2019-2020 com concluiu em 2023-2024
# Mas o CSV tem só campo "concluiu" sem separar cohort vs prazo
# Usar toda a base para verificação geral
from collections import Counter
evasao = defaultdict(lambda: defaultdict(lambda: {"total":0,"concluiu":0}))
for r in rows:
    curso = MAP.get(r["curso"], r["curso"])
    gen = "mulheres" if r["genero"] == "Feminino" else "homens"
    evasao[curso][gen]["total"] += 1
    if r["concluiu"] == "1":
        evasao[curso][gen]["concluiu"] += 1

print(f"{'Curso':<45} {'Genero':>9} {'CSV%nao':>9} {'Dash%':>9} {'Delta':>8}")
for curso in DASH_EVASAO:
    for gen in ["mulheres","homens"]:
        d = evasao[curso][gen]
        t, c = d["total"], d["concluiu"]
        if t == 0:
            continue
        pct_nao_csv = round((1 - c/t)*100, 1)
        pct_nao_dash = DASH_EVASAO[curso][gen]
        delta = round(pct_nao_csv - pct_nao_dash, 1)
        print(f"  {curso:<43} {gen:>9} {pct_nao_csv:>9.1f}% {pct_nao_dash:>9.1f}% {delta:>+7.1f}")

# ── Ranking instituições ─────────────────────────────────────────
print("\n=== 3. rankingInstituicoes (% feminino) ===")
DASH_RANK = {"USP": 17.7, "Insper": 17.0, "FIAP": 16.7, "PUC-SP": 16.4, "UFMG": 14.4}
inst = defaultdict(lambda: {"total":0,"fem":0})
for r in rows:
    i = r["instituicao"]
    inst[i]["total"] += 1
    if r["genero"] == "Feminino":
        inst[i]["fem"] += 1

print(f"{'Instituicao':<12} {'CSV%':>8} {'Dash%':>8} {'Delta':>8}")
for nome in DASH_RANK:
    d = inst.get(nome, {"total":0,"fem":0})
    if d["total"] == 0:
        print(f"  {nome:<10}  NÃO ENCONTRADO")
        continue
    pct_csv = round(d["fem"]/d["total"]*100, 1)
    pct_dash = DASH_RANK[nome]
    delta = round(pct_csv - pct_dash, 1)
    print(f"  {nome:<10} {pct_csv:>8.1f}% {pct_dash:>8.1f}% {delta:>+7.1f}")

# ── % feminino por ano (inepIngressantes pctFem) ─────────────────
print("\n=== 4. inepIngressantes pctFem (% feminino anual no CSV) ===")
DASH_PCT = {"2019":13.9,"2020":15.8,"2021":18.2,"2022":17.9,"2023":18.1,"2024":18.4}
ano_gen = defaultdict(lambda: {"total":0,"fem":0})
for r in rows:
    a = r["ano_ingresso"]
    ano_gen[a]["total"] += 1
    if r["genero"] == "Feminino":
        ano_gen[a]["fem"] += 1

print(f"{'Ano':>5} {'CSV%':>8} {'Dash%':>8} {'Delta':>8}")
for ano in sorted(DASH_PCT):
    d = ano_gen.get(ano, {"total":0,"fem":0})
    if d["total"] == 0:
        print(f"  {ano}   N/A")
        continue
    pct_csv = round(d["fem"]/d["total"]*100, 1)
    pct_dash = DASH_PCT[ano]
    delta = round(pct_csv - pct_dash, 1)
    print(f"  {ano}  {pct_csv:>8.1f}% {pct_dash:>8.1f}% {delta:>+7.1f}")
