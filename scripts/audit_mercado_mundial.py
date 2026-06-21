"""
Auditoria: base_mercado_tech_mundial.csv vs Dashboard.jsx (IRF + Simulador)
"""
import csv, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

src = "data/treated/base_mercado_tech_mundial.csv"
with open(src,"r",encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

print(f"Total: {len(rows)} registros")

# ── % mulheres por setor (pctMulheresPorArea) ────────────────────
print("\n=== 1. pctMulheresPorArea ===")
DASH_AREA = {"Dados":26.8,"Desenvolvimento":19.5,"Gestão":31.0,"Infraestrutura":14.0,"UX/UI":44.5}
setor_g = defaultdict(lambda:{"total":0,"fem":0})
for r in rows:
    s = r["setor"]
    setor_g[s]["total"] += 1
    if r["genero"] == "Feminino":
        setor_g[s]["fem"] += 1

print(f"{'Setor':<16} {'CSV%':>8} {'Dash%':>8} {'Delta':>8}")
for setor in sorted(DASH_AREA):
    d = setor_g.get(setor, {"total":0,"fem":0})
    if d["total"] == 0:
        print(f"  {setor:<14}  NOT FOUND")
        continue
    pct_csv = round(d["fem"]/d["total"]*100, 1)
    pct_dash = DASH_AREA[setor]
    delta = round(pct_csv - pct_dash, 1)
    print(f"  {setor:<14} {pct_csv:>8.1f}% {pct_dash:>8.1f}% {delta:>+7.1f}")

# ── % mulheres por cargo (pctMulheresPorCargo) ───────────────────
print("\n=== 2. pctMulheresPorCargo ===")
DASH_CARGO = {"Estagiário":48.5,"Júnior":39.3,"Pleno":32.5,"Sênior":25.3,
              "Gerente":20.9,"Especialista":23.6,"Diretor":17.1,"CTO/CIO":15.0}
cargo_g = defaultdict(lambda:{"total":0,"fem":0})
for r in rows:
    c = r["cargo"]
    cargo_g[c]["total"] += 1
    if r["genero"] == "Feminino":
        cargo_g[c]["fem"] += 1

print(f"{'Cargo':<14} {'CSV%':>8} {'Dash%':>8} {'Delta':>8}")
for cargo in ["Estagiário","Júnior","Pleno","Sênior","Gerente","Especialista","Diretor","CTO/CIO"]:
    d = cargo_g.get(cargo, {"total":0,"fem":0})
    if d["total"] == 0:
        print(f"  {cargo:<12}  NOT FOUND — cargo ausente no CSV")
        continue
    pct_csv = round(d["fem"]/d["total"]*100, 1)
    pct_dash = DASH_CARGO[cargo]
    delta = round(pct_csv - pct_dash, 1)
    print(f"  {cargo:<12} {pct_csv:>8.1f}% {pct_dash:>8.1f}% {delta:>+7.1f}")

# ── Salário base por cargo (baseSalaryByCargo) ───────────────────
print("\n=== 3. baseSalaryByCargo (salário médio) ===")
DASH_SAL = {"Estagiário":1900,"Júnior":5200,"Pleno":9200,"Sênior":14500,
            "Gerente":19800,"Especialista":16200,"Diretor":28500,"CTO/CIO":38000}
cargo_sal = defaultdict(list)
for r in rows:
    try:
        cargo_sal[r["cargo"]].append(float(r["salario_base"]))
    except: pass

print(f"{'Cargo':<14} {'CSVmed':>9} {'Dash':>9} {'Delta':>9}")
for cargo in ["Estagiário","Júnior","Pleno","Sênior","Gerente","Especialista","Diretor","CTO/CIO"]:
    sals = cargo_sal.get(cargo, [])
    if not sals:
        print(f"  {cargo:<12}  NOT FOUND")
        continue
    med = round(sum(sals)/len(sals))
    dash_val = DASH_SAL[cargo]
    delta = med - dash_val
    print(f"  {cargo:<12} {med:>9,} {dash_val:>9,} {delta:>+9,}")

# ── brokenRung: promoção por gênero ──────────────────────────────
print("\n=== 4. brokenRung (promoção por gênero) ===")
# Dashboard: Homens=100, Mulheres=87
prom = {"Feminino":{"total":0,"prom":0},"Masculino":{"total":0,"prom":0}}
for r in rows:
    g = r["genero"]
    if g in prom:
        prom[g]["total"] += 1
        if r.get("promovido_ultimo_ano","") == "Sim":
            prom[g]["prom"] += 1

for g, d in prom.items():
    pct = round(d["prom"]/d["total"]*100, 1) if d["total"] else 0
    print(f"  {g}: {d['prom']}/{d['total']} promovidos = {pct}%")

# Calcular ratio relativo (homens=100)
h_pct = round(prom["Masculino"]["prom"]/prom["Masculino"]["total"]*100, 1) if prom["Masculino"]["total"] else 0
f_pct = round(prom["Feminino"]["prom"]/prom["Feminino"]["total"]*100, 1) if prom["Feminino"]["total"] else 0
ratio = round(f_pct/h_pct*100) if h_pct else 0
print(f"  Ratio CSV: Homens=100 / Mulheres={ratio}")
print(f"  Ratio Dashboard: Homens=100 / Mulheres=87")

# ── Gap salarial de gênero por cargo (gapPctByCargo) ─────────────
print("\n=== 5. gapPctByCargo (gap salarial real no CSV) ===")
DASH_GAP = {"Estagiário":0.03,"Júnior":0.08,"Pleno":0.14,"Sênior":0.21,
            "Gerente":0.27,"Especialista":0.19,"Diretor":0.33,"CTO/CIO":0.38}
cargo_sal_g = defaultdict(lambda:{"Feminino":[],"Masculino":[]})
for r in rows:
    try:
        cargo_sal_g[r["cargo"]][r["genero"]].append(float(r["salario_base"]))
    except: pass

print(f"{'Cargo':<14} {'Gap_CSV':>9} {'Gap_Dash':>9} {'Delta':>9}")
for cargo in ["Estagiário","Júnior","Pleno","Sênior","Gerente","Especialista","Diretor","CTO/CIO"]:
    d = cargo_sal_g.get(cargo)
    if not d or not d["Feminino"] or not d["Masculino"]:
        print(f"  {cargo:<12}  DADOS INSUFICIENTES")
        continue
    med_f = sum(d["Feminino"])/len(d["Feminino"])
    med_m = sum(d["Masculino"])/len(d["Masculino"])
    gap_csv = round((med_m - med_f)/med_m, 2) if med_m else 0
    gap_dash = DASH_GAP.get(cargo, 0)
    delta = round(gap_csv - gap_dash, 2)
    print(f"  {cargo:<12} {gap_csv:>9.2f} {gap_dash:>9.2f} {delta:>+9.2f}")
