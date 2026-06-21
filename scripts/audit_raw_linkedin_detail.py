import csv
import sys
from collections import Counter, defaultdict

sys.stdout.reconfigure(encoding='utf-8')

src = "data/raw/emp_find_jobs_robot.csv"

with open(src, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

DI_KEYWORDS = {
    "PCD": ["pcd", "pessoas com deficiência", "pessoa com deficiência", "deficiencia", "deficiência", "acessib"],
    "Mulheres": ["mulher", "mulheres", "feminino", "feminina", "women", "female", "gênero feminino", "genero feminino"],
    "Negros": ["negro", "negra", "negros", "negras", "preta", "preto", "pretas", "pretos", "pessoa negra", "pessoas negras",
               "raça", "raca", "afrodescend"],
}

# Verificar quais campos ativam "Negros"
print("=== VERIFICAÇÃO DETALHADA: Vagas classificadas como 'Negros' ===\n")

for row in rows:
    fields = {
        "job_title": row.get("job_title", ""),
        "description": row.get("description", ""),
        "responsibilities_text": row.get("responsibilities_text", ""),
        "requirements_text": row.get("requirements_text", ""),
    }

    all_text = " ".join(fields.values()).lower()
    negros_kws = DI_KEYWORDS["Negros"]
    matched_kws = [kw for kw in negros_kws if kw in all_text]

    if matched_kws:
        mes = row.get("inserted_at", "")[:7]
        print(f"[{mes}] {row.get('job_title', '')[:60]}")
        print(f"  Keywords matched: {matched_kws}")
        # Mostrar qual campo ativou
        for fname, ftext in fields.items():
            ftl = ftext.lower()
            hits = [kw for kw in negros_kws if kw in ftl]
            if hits:
                # Mostrar trecho
                for kw in hits:
                    idx = ftl.find(kw)
                    snippet = ftext[max(0,idx-40):idx+60].replace('\n',' ')
                    print(f"  Campo: {fname} | match '{kw}': ...{snippet}...")
        print()

print("\n=== VERIFICAÇÃO DETALHADA: Vagas classificadas como 'Mulheres' ===\n")
for row in rows:
    fields = {
        "job_title": row.get("job_title", ""),
        "description": row.get("description", ""),
        "responsibilities_text": row.get("responsibilities_text", ""),
        "requirements_text": row.get("requirements_text", ""),
    }
    all_text = " ".join(fields.values()).lower()
    kws = DI_KEYWORDS["Mulheres"]
    if any(kw in all_text for kw in kws):
        mes = row.get("inserted_at", "")[:7]
        print(f"[{mes}] {row.get('job_title', '')[:60]}")
        for fname, ftext in fields.items():
            ftl = ftext.lower()
            hits = [kw for kw in kws if kw in ftl]
            if hits:
                for kw in hits:
                    idx = ftl.find(kw)
                    snippet = ftext[max(0,idx-30):idx+60].replace('\n',' ')
                    print(f"  Campo: {fname} | match '{kw}': ...{snippet}...")
        print()
