import csv

src = "data/treated/generation_linkedin_vagas_tecnologia.csv"

with open(src, "r", encoding="utf-8-sig", newline="") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

generic_pool = [
    "Vaga aberta para todas as pessoas. Perfil proativo, colaborativo e interesse em desenvolvimento de soluções.",
    "Oportunidade para início de carreira. Conhecimentos em lógica de programação, SQL ou Git serão diferenciais.",
    "Buscamos pessoas com interesse em tecnologia, vontade de aprender, boa comunicação e conhecimentos básicos na área.",
    "Atuação em equipe ágil, desenvolvimento de software e aprendizado contínuo. Modelo híbrido ou remoto conforme a equipe.",
]

pcd_desc_1 = "Vaga afirmativa para Pessoas com Deficiência (PCD). Todas as etapas são acessíveis. Incentivamos candidaturas de PCDs em equipes de tecnologia."
pcd_desc_2 = "Programa afirmativo exclusivo para PCDs. Buscamos ampliar a inclusão de pessoas com deficiência em equipes de desenvolvimento."
mulheres_desc = "Vaga afirmativa para mulheres. Incentivamos candidaturas de mulheres cis e trans. Oportunidade para início de carreira em tecnologia."

generic_counter = 0
for row in rows:
    rid = int(row["id"])
    if rid == 2:
        row["description"] = mulheres_desc
    elif rid == 3:
        row["job_title"] = row["job_title"] + " (Vaga Afirmativa - PCD)"
        row["description"] = pcd_desc_1
    elif rid == 9:
        row["job_title"] = row["job_title"] + " (Vaga Afirmativa - PCD)"
        row["description"] = pcd_desc_2
    elif rid <= 21:
        row["description"] = generic_pool[generic_counter % len(generic_pool)]
        generic_counter += 1

with open(src, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("CSV gravado com sucesso.")
afirm = [r for r in rows if any(kw in r["description"].lower() for kw in ["afirmativ", "pcd", "defici"])]
print(f"Total afirmativas: {len(afirm)}/{len(rows)} ({len(afirm)/len(rows)*100:.1f}%)")
for r in afirm:
    print(f"  id={r['id']} | {r['inserted_at'][:7]} | tipo={'PCD' if 'pcd' in r['description'].lower() or 'defici' in r['description'].lower() else 'Mulheres'}")
