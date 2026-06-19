"""
Exporta tabelas prontas para importação direta no Power BI Desktop.

Execução:
    python outputs/export_para_powerbi.py

Saída: pasta  outputs/powerbi_data/
    fato_mercado.csv         — salário por cargo × gênero
    fato_educacao.csv        — funil educacional por ano
    fato_vagas.csv           — vagas LinkedIn com flag D&I
    dim_cargo.csv            — dimensão de cargos com flag liderança e IRF
    metricas_funil.csv       — funil carreira campus → C-level (para KPI cards)
"""

import csv
import json
from pathlib import Path

import pandas as pd

ROOT    = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "powerbi_data"
OUT_DIR.mkdir(exist_ok=True)

ORDEM_CARGO = ["Estagiário", "Júnior", "Pleno", "Sênior",
               "Especialista", "Gerente", "Diretor", "CTO/CIO"]
LIDERANCA   = {"Sênior", "Especialista", "Gerente", "Diretor", "CTO/CIO"}

# ─── 1. fato_mercado ─────────────────────────────────────────────────────────
merc = pd.read_csv(ROOT / "data/treated/fato_mercado_tech_brasil.csv")
merc["salario_medio_brl"]   = merc["salario_medio_brl"].astype(float).round(2)
merc["salario_mediano_brl"] = merc["salario_mediano_brl"].astype(float).round(2)
merc["n"]                   = merc["n"].astype(int)
merc["nivel_hierarquico"]   = merc["cargo"].apply(
    lambda c: ORDEM_CARGO.index(c) + 1 if c in ORDEM_CARGO else 99
)

# Gap salarial por cargo (wide → cálculo → melt back)
pivot = merc.pivot_table(index="cargo", columns="genero",
                         values="salario_medio_brl", aggfunc="mean")
pivot["gap_pct"] = ((pivot["Masculino"] - pivot["Feminino"])
                    / pivot["Masculino"] * 100).round(1)
merc = merc.merge(pivot[["gap_pct"]].reset_index(), on="cargo", how="left")

merc.to_csv(OUT_DIR / "fato_mercado.csv", index=False, encoding="utf-8-sig")
print(f"[OK] fato_mercado.csv  — {len(merc)} linhas")

# ─── 2. fato_educacao ────────────────────────────────────────────────────────
edu = pd.read_csv(ROOT / "data/treated/fato_educacao_tech_agregado.csv")
edu["ano"] = edu["ano"].astype(int)

# Calcula variação YoY de ingressantes femininas
edu = edu.sort_values("ano").copy()
edu["yoy_ing_fem_pp"] = edu["pct_ing_fem"].diff().round(1)

edu.to_csv(OUT_DIR / "fato_educacao.csv", index=False, encoding="utf-8-sig")
print(f"[OK] fato_educacao.csv — {len(edu)} linhas")

# ─── 3. fato_vagas ───────────────────────────────────────────────────────────
vagas = pd.read_csv(ROOT / "data/treated/fato_vagas_linkedin.csv")
vagas["eh_di"] = vagas["eh_di"].astype(int)
vagas["tipo_di"] = vagas["tipo_di"].fillna("Não D&I")

vagas.to_csv(OUT_DIR / "fato_vagas.csv", index=False, encoding="utf-8-sig")
print(f"[OK] fato_vagas.csv    — {len(vagas)} linhas")

# ─── 4. dim_cargo ────────────────────────────────────────────────────────────
total_fem   = merc[merc["genero"] == "Feminino"]["n"].sum()
total_geral = merc["n"].sum()
pct_fem_geral = total_fem / total_geral

cargo_stats = merc.groupby("cargo").agg(
    total=("n", "sum"),
    fem=("n", lambda s: merc.loc[s.index[merc.loc[s.index, "genero"] == "Feminino"], "n"].sum()
         if "Feminino" in merc.loc[s.index, "genero"].values else 0),
).reset_index()

# Recalcula fem corretamente
rows = []
for cargo in ORDEM_CARGO:
    sub = merc[merc["cargo"] == cargo]
    total = int(sub["n"].sum())
    fem   = int(sub[sub["genero"] == "Feminino"]["n"].sum())
    pct_c = fem / total if total > 0 else 0
    irf   = round(pct_c / pct_fem_geral, 2) if pct_fem_geral > 0 else 0
    gap   = sub["gap_pct"].iloc[0] if not sub["gap_pct"].isna().all() else 0
    rows.append({
        "cargo":              cargo,
        "nivel_hierarquico":  ORDEM_CARGO.index(cargo) + 1,
        "eh_lideranca":       1 if cargo in LIDERANCA else 0,
        "total_profissionais": total,
        "n_feminino":         fem,
        "pct_feminino":       round(pct_c * 100, 1),
        "irf":                irf,
        "gap_pct":            round(float(gap), 1),
    })

dim_cargo = pd.DataFrame(rows)
dim_cargo.to_csv(OUT_DIR / "dim_cargo.csv", index=False, encoding="utf-8-sig")
print(f"[OK] dim_cargo.csv     — {len(dim_cargo)} linhas")

# ─── 5. metricas_funil (KPI cards) ───────────────────────────────────────────
with open(ROOT / "reports/metricas_funil.json", encoding="utf-8") as fp:
    funil_json = json.load(fp)

merc_lideranca = merc[merc["cargo"].isin(["Gerente", "Diretor", "CTO/CIO"])]
n_lid_fem = int(merc_lideranca[merc_lideranca["genero"] == "Feminino"]["n"].sum())
n_lid_tot = int(merc_lideranca["n"].sum())

merc_pleno_senior = merc[merc["cargo"].isin(["Pleno", "Sênior"])]
n_ps_fem = int(merc_pleno_senior[merc_pleno_senior["genero"] == "Feminino"]["n"].sum())
n_ps_tot = int(merc_pleno_senior["n"].sum())

sal_fem  = float(merc[merc["genero"] == "Feminino"]["salario_medio_brl"].mean())
sal_masc = float(merc[merc["genero"] == "Masculino"]["salario_medio_brl"].mean())
gap_global = round((sal_masc - sal_fem) / sal_masc * 100, 1)

funil_rows = [
    {"etapa": "Ingressantes TIC",   "ordem": 1,
     "pct_feminino": funil_json["funil_tic"]["2022"]["pct_ing_fem"],
     "fonte": "INEP simulado — Sudeste 2022"},
    {"etapa": "Concluintes TIC",    "ordem": 2,
     "pct_feminino": funil_json["funil_tic"]["2022"]["pct_conc_fem"],
     "fonte": "INEP simulado — Sudeste 2022"},
    {"etapa": "No mercado tech",    "ordem": 3,
     "pct_feminino": round(pct_fem_geral * 100, 1),
     "fonte": "Base Mercado Tech Brasil"},
    {"etapa": "Pleno / Senior",     "ordem": 4,
     "pct_feminino": round(n_ps_fem / n_ps_tot * 100, 1),
     "fonte": "Base Mercado Tech Brasil"},
    {"etapa": "Lideranca (Mgmt+)",  "ordem": 5,
     "pct_feminino": round(n_lid_fem / n_lid_tot * 100, 1),
     "fonte": "Base Mercado Tech Brasil"},
]

metricas_funil = pd.DataFrame(funil_rows)
metricas_funil.to_csv(OUT_DIR / "metricas_funil.csv", index=False, encoding="utf-8-sig")
print(f"[OK] metricas_funil.csv — {len(metricas_funil)} linhas")

# ─── Sumário ─────────────────────────────────────────────────────────────────
print(f"""
Arquivos prontos em: outputs/powerbi_data/
  fato_mercado.csv    — {len(merc)} linhas
  fato_educacao.csv   — {len(edu)} linhas
  fato_vagas.csv      — {len(vagas)} linhas
  dim_cargo.csv       — {len(dim_cargo)} linhas
  metricas_funil.csv  — {len(metricas_funil)} linhas

Gap salarial global : {gap_global}%
Salario medio fem   : R$ {sal_fem:,.0f}
Salario medio masc  : R$ {sal_masc:,.0f}
""")
