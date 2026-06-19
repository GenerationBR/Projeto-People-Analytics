"""
EDA — Funil da Mulher na Tech
People Analytics & DE&I: A Trajetória Feminina do Câmpus ao Mercado Tech

Fontes:
  - data/treated/fato_educacao_tech_agregado.csv  (INEP simulado, Sudeste 2019-2022)
  - data/treated/fato_mercado_tech_brasil.csv      (Brasscom + State of Data + McKinsey)
  - data/treated/fato_vagas_linkedin.csv           (LinkedIn simulado, ago/2025-mai/2026)
  - reports/metricas_funil.json

Executar:
  python outputs/eda_funil_feminino.py
"""

# ── Dependências ──────────────────────────────────────────────────────────────
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")   # sem GUI; remova se quiser janela interativa
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent

# ── Paleta ────────────────────────────────────────────────────────────────────
C_FEM  = "#9c2f5c"
C_MASC = "#c3a7af"
C_LINE = "#5c1638"
C_SOFT = "#f3c4d3"

OUT_DIR = ROOT / "outputs" / "eda_charts"
OUT_DIR.mkdir(exist_ok=True)


def save(fig: plt.Figure, name: str) -> None:
    path = OUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [OK] {path.relative_to(ROOT)}")


# =============================================================================
# 1. FUNIL EDUCACIONAL — participação feminina por etapa
# =============================================================================

print("\n=== 1. Funil educacional ===")

edu = pd.read_csv(ROOT / "data/treated/fato_educacao_tech_agregado.csv")
edu["ano"] = edu["ano"].astype(str)

fig, axes = plt.subplots(1, 3, figsize=(13, 4), sharey=False)
fig.suptitle("Participação Feminina em TIC — Sudeste 2019-2022", fontsize=13, color=C_LINE)

metricas = [
    ("pct_mat_fem",  "Matrículas"),
    ("pct_ing_fem",  "Ingressantes"),
    ("pct_conc_fem", "Concluintes"),
]
for ax, (col, label) in zip(axes, metricas):
    ax.bar(edu["ano"], edu[col], color=C_FEM, alpha=0.85, width=0.5)
    ax.set_title(label, fontsize=11, color=C_LINE)
    ax.set_ylim(0, 35)
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
    ax.axhline(y=edu[col].mean(), color=C_LINE, linestyle="--", linewidth=1, alpha=0.6)
    ax.set_xlabel("Ano")
    for bar, val in zip(ax.patches, edu[col]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.4,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=9, color=C_LINE)

plt.tight_layout()
save(fig, "01_funil_educacional")

# =============================================================================
# 2. EVASÃO — comparação feminino × masculino por ano
# =============================================================================

print("\n=== 2. Evasão por gênero ===")

fig, ax = plt.subplots(figsize=(8, 4))
x = range(len(edu))
width = 0.35
ax.bar([i - width / 2 for i in x], edu["tx_evasao_fem_pct"],  width, label="Feminino",  color=C_FEM,  alpha=0.85)
ax.bar([i + width / 2 for i in x], edu["tx_evasao_masc_pct"], width, label="Masculino", color=C_MASC, alpha=0.85)
ax.set_xticks(list(x))
ax.set_xticklabels(edu["ano"])
ax.set_title("Taxa de Evasão em TIC por Gênero — Sudeste 2019-2022", color=C_LINE)
ax.set_ylabel("Taxa de evasão (%)")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.legend()

for bar in ax.patches:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{bar.get_height():.1f}%", ha="center", va="bottom", fontsize=8.5)

plt.tight_layout()
save(fig, "02_evasao_por_genero")

# =============================================================================
# 3. GAP SALARIAL por cargo × nível
# =============================================================================

print("\n=== 3. Gap salarial por cargo ===")

merc = pd.read_csv(ROOT / "data/treated/fato_mercado_tech_brasil.csv")

pivot = merc.pivot_table(
    index="cargo", columns="genero",
    values="salario_medio_brl", aggfunc="mean"
).reindex(["Estagiário", "Júnior", "Pleno", "Sênior", "Especialista", "Gerente", "Diretor", "CTO/CIO"])

pivot["gap_pct"] = (pivot["Masculino"] - pivot["Feminino"]) / pivot["Masculino"] * 100

fig, ax = plt.subplots(figsize=(9, 5))
x = range(len(pivot))
width = 0.35
ax.bar([i - width / 2 for i in x], pivot["Feminino"],  width, label="Feminino",  color=C_FEM,  alpha=0.85)
ax.bar([i + width / 2 for i in x], pivot["Masculino"], width, label="Masculino", color=C_MASC, alpha=0.85)
ax.set_xticks(list(x))
ax.set_xticklabels(pivot.index, rotation=20, ha="right")
ax.set_title("Salário Médio por Cargo e Gênero — Base Mercado Tech Brasil", color=C_LINE)
ax.set_ylabel("Salário médio (R$)")
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v, _: f"R${v:,.0f}"))
ax.legend()

ax2 = ax.twinx()
ax2.plot([i for i in x], pivot["gap_pct"], color=C_LINE, marker="o", linewidth=1.8,
         markersize=5, label="Gap %", zorder=5)
ax2.set_ylabel("Gap salarial (%)", color=C_LINE)
ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
ax2.tick_params(axis="y", colors=C_LINE)
ax2.set_ylim(0, 40)

lines, labels   = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines + lines2, labels + labels2, loc="upper left")

plt.tight_layout()
save(fig, "03_gap_salarial_por_cargo")

# =============================================================================
# 4. GAP SALARIAL por área
# =============================================================================

print("\n=== 4. Gap salarial por área ===")

area_pivot = merc.pivot_table(
    index="regiao", columns="genero",
    values="salario_medio_brl", aggfunc="mean"
)
area_pivot["gap_pct"] = (area_pivot["Masculino"] - area_pivot["Feminino"]) / area_pivot["Masculino"] * 100
area_pivot = area_pivot.sort_values("gap_pct", ascending=True)

fig, ax = plt.subplots(figsize=(8, 4))
bars = ax.barh(area_pivot.index, area_pivot["gap_pct"], color=C_FEM, alpha=0.85)
ax.set_title("Gap Salarial por Área de Atuação", color=C_LINE)
ax.set_xlabel("Gap salarial (%)")
ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.axvline(area_pivot["gap_pct"].mean(), color=C_LINE, linestyle="--", linewidth=1.2, label="Média geral")
ax.legend(fontsize=9)

for bar, val in zip(bars, area_pivot["gap_pct"]):
    ax.text(val + 0.3, bar.get_y() + bar.get_height() / 2,
            f"{val:.1f}%", va="center", fontsize=9)

plt.tight_layout()
save(fig, "04_gap_por_area")

# =============================================================================
# 5. IRF — Índice de Representatividade Feminina por cargo
# =============================================================================

print("\n=== 5. IRF por cargo ===")

total_fem  = merc[merc["genero"] == "Feminino"]["n"].astype(float).sum()
total_geral = merc["n"].astype(float).sum()
pct_fem_geral = total_fem / total_geral

cargo_n = merc.groupby(["cargo", "genero"])["n"].sum().unstack(fill_value=0)
cargo_n["total"] = cargo_n.sum(axis=1)
cargo_n["pct_fem"] = cargo_n["Feminino"] / cargo_n["total"]
cargo_n["irf"] = cargo_n["pct_fem"] / pct_fem_geral
cargo_n = cargo_n.reindex(["Estagiário", "Júnior", "Pleno", "Sênior", "Especialista", "Gerente", "Diretor", "CTO/CIO"])

def irf_color(v):
    if v >= 1.10: return "#5c1638"
    if v >= 0.90: return "#9c2f5c"
    if v >= 0.70: return "#e8a0b9"
    return "#f3c4d3"

colors = [irf_color(v) for v in cargo_n["irf"]]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(cargo_n.index, cargo_n["irf"], color=colors, alpha=0.9)
ax.axvline(1.0, color="#8a6e78", linestyle="--", linewidth=1.5)
ax.set_title("IRF por Cargo — Índice de Representatividade Feminina", color=C_LINE)
ax.set_xlabel("IRF  (1.0 = representação proporcional)")
ax.invert_yaxis()

for bar, val in zip(bars, cargo_n["irf"]):
    ax.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
            f"{val:.2f}", va="center", fontsize=9)

from matplotlib.patches import Patch
legend_elements = [
    Patch(color="#5c1638", label="≥ 1.10 — sobre-representada"),
    Patch(color="#9c2f5c", label="0.90-1.10 — proporcional"),
    Patch(color="#e8a0b9", label="0.70-0.89 — sub-representada"),
    Patch(color="#f3c4d3", label="< 0.70 — crítica"),
]
ax.legend(handles=legend_elements, fontsize=8.5, loc="lower right")
plt.tight_layout()
save(fig, "05_irf_por_cargo")

# =============================================================================
# 6. VAGAS D&I — distribuição mensal e por tipo
# =============================================================================

print("\n=== 6. Vagas D&I LinkedIn ===")

vagas = pd.read_csv(ROOT / "data/treated/fato_vagas_linkedin.csv")
vagas_mes = vagas.groupby(["mes_ano", "eh_di"]).size().unstack(fill_value=0)
vagas_mes.columns = ["Demais vagas", "Vagas D&I"]

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
fig.suptitle("Iniciativas D&I em Vagas de TI — ago/2025–mai/2026", color=C_LINE, fontsize=12)

# Gráfico empilhado mensal
vagas_mes[["Demais vagas", "Vagas D&I"]].plot(
    kind="bar", stacked=True, ax=axes[0],
    color=[C_SOFT, C_FEM], alpha=0.9
)
axes[0].set_title("Vagas por mês")
axes[0].set_xlabel("")
axes[0].set_xticklabels(vagas_mes.index, rotation=35, ha="right", fontsize=8)
axes[0].legend(fontsize=9)

# Pizza por tipo D&I
di_vagas = vagas[vagas["eh_di"] == 1]
tipo_counts = di_vagas["tipo_di"].value_counts()
axes[1].pie(
    tipo_counts.values,
    labels=tipo_counts.index,
    autopct="%1.0f%%",
    colors=[C_LINE, C_FEM, C_SOFT],
    startangle=140,
    textprops={"fontsize": 9},
)
axes[1].set_title(f"Tipos de iniciativa D&I\n(total: {len(di_vagas)} vagas)")

plt.tight_layout()
save(fig, "06_vagas_di")

# =============================================================================
# 7. FUNIL COMPLETO — resumo agregado (educação → mercado → liderança)
# =============================================================================

print("\n=== 7. Funil completo ===")

with open(ROOT / "reports/metricas_funil.json", encoding="utf-8") as fp:
    funil = json.load(fp)

etapas = ["Ingressantes TIC", "Formadas TIC", "No mercado tech", "Pleno/Sênior", "Liderança"]
pcts   = [
    funil["funil_tic"]["2022"]["pct_ing_fem"],
    funil["funil_tic"]["2022"]["pct_conc_fem"],
    28.5,   # Brasscom nacional
    merc[merc["genero"] == "Feminino"].loc[
        merc["cargo"].isin(["Pleno", "Sênior"]), "n"
    ].astype(float).sum() /
    merc[merc["cargo"].isin(["Pleno", "Sênior"])]["n"].astype(float).sum() * 100,
    merc[merc["genero"] == "Feminino"].loc[
        merc["cargo"].isin(["Gerente", "Diretor", "CTO/CIO"]), "n"
    ].astype(float).sum() /
    merc[merc["cargo"].isin(["Gerente", "Diretor", "CTO/CIO"])]["n"].astype(float).sum() * 100,
]
pcts = [round(v, 1) for v in pcts]

fig, ax = plt.subplots(figsize=(9, 4))
bar_colors = [C_FEM if i == 0 else C_MASC if i == len(pcts) - 1 else "#c3a7af" for i in range(len(pcts))]
bars = ax.bar(etapas, pcts, color=bar_colors, alpha=0.85, width=0.55)
ax.set_title("Funil Feminino — Do Campus ao C-Level", color=C_LINE, fontsize=13)
ax.set_ylabel("% de mulheres na etapa")
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_ylim(0, 45)

for bar, val in zip(bars, pcts):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{val}%", ha="center", va="bottom", fontsize=10, fontweight="bold", color=C_LINE)

# Setas de queda
for i in range(len(pcts) - 1):
    diff = pcts[i + 1] - pcts[i]
    if diff < 0:
        mid_x = i + 0.5
        ax.annotate(
            f"{diff:+.1f} pp",
            xy=(mid_x, (pcts[i] + pcts[i + 1]) / 2),
            ha="center", va="center", fontsize=8.5,
            color="#8a6e78", style="italic",
        )

plt.tight_layout()
save(fig, "07_funil_completo")

# =============================================================================
# SUMÁRIO ESTATÍSTICO
# =============================================================================

print("\n=== Sumário estatístico ===")

gap_global = (
    merc[merc["genero"] == "Masculino"]["salario_medio_brl"].astype(float).mean() -
    merc[merc["genero"] == "Feminino"]["salario_medio_brl"].astype(float).mean()
) / merc[merc["genero"] == "Masculino"]["salario_medio_brl"].astype(float).mean() * 100

print(f"\n  Gap salarial global            : {gap_global:.1f}%")
print(f"  % mulheres no mercado (pipeline): {pct_fem_geral * 100:.1f}%")
print(f"  % concluintes fem TIC 2022      : {funil['funil_tic']['2022']['pct_conc_fem']:.1f}%")
print(f"  Vagas D&I (LinkedIn)            : {len(di_vagas)} de {len(vagas)} ({len(di_vagas)/len(vagas)*100:.1f}%)")
print(f"\n  Gráficos salvos em: outputs/eda_charts/")
print("  Análise concluída.\n")
