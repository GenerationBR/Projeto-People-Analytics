import csv
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

src = "data/raw/emp_find_jobs_robot.csv"

with open(src, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

print(f"Total registros: {len(rows)}")
print(f"Colunas: {list(rows[0].keys())[:10]}")

# Distribuição mensal
monthly_totals = defaultdict(int)
monthly_afirm = defaultdict(list)

DI_KEYWORDS = {
    "PCD": ["pcd", "pessoas com deficiência", "pessoa com deficiência", "deficiencia", "deficiência", "acessib"],
    "Mulheres": ["mulher", "mulheres", "feminino", "feminina", "women", "female", "gênero feminino", "genero feminino"],
    "Negros": ["negro", "negra", "negros", "negras", "preta", "preto", "pretas", "pretos", "pessoa negra", "pessoas negras",
               "raça", "raca", "afrodescend"],
}

def classify_di(row):
    text = " ".join([
        row.get("job_title", ""),
        row.get("description", ""),
        row.get("responsibilities_text", ""),
        row.get("requirements_text", ""),
    ]).lower()
    tipos = []
    for tipo, kws in DI_KEYWORDS.items():
        if any(kw in text for kw in kws):
            tipos.append(tipo)
    return tipos

total_afirm = 0
di_counter = Counter()
afirm_rows = []

for row in rows:
    mes = row.get("inserted_at", "")[:7]
    monthly_totals[mes] += 1

    tipos = classify_di(row)
    if tipos:
        total_afirm += 1
        for t in tipos:
            di_counter[t] += 1
        monthly_afirm[mes].append(tipos)
        afirm_rows.append(row)

print(f"\nTotal afirmativas: {total_afirm} / {len(rows)} ({total_afirm/len(rows)*100:.1f}%)")

print("\n--- Distribuição mensal ---")
for mes in sorted(monthly_totals):
    t = monthly_totals[mes]
    a = len(monthly_afirm.get(mes, []))
    pct = a/t*100 if t else 0
    print(f"  {mes}: {t:4d} total | {a} afirmativas ({pct:.1f}%)")

print("\n--- Tipos DI (podem sobrepor) ---")
for tipo, n in di_counter.most_common():
    print(f"  {tipo}: {n}")

print("\n--- Exemplos afirmativas ---")
for r in afirm_rows[:12]:
    tipos = classify_di(r)
    mes = r.get("inserted_at", "")[:7]
    title = r.get("job_title", "")[:55]
    print(f"  [{mes}] {title} → {tipos}")
