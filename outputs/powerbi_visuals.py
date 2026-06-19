"""
Scripts Python para Visualizações no Power BI Desktop
======================================================
Como usar cada script:
  1. No Power BI Desktop, arraste o ícone "Py" (Visualização Python) para o canvas
  2. No painel Campos, arraste as colunas indicadas em cada script para "Valores"
  3. Cole o script no editor Python que aparece embaixo do canvas
  4. Clique em ► Executar

Paleta do projeto:
    C_FEM  = "#9c2f5c"   rosa escuro
    C_MASC = "#c3a7af"   rosê
    C_LINE = "#5c1638"   vinho
    C_SOFT = "#f3c4d3"   rosa claro

Obs: Power BI passa os campos selecionados como DataFrame chamado `dataset`.
"""

# ══════════════════════════════════════════════════════════════════════════════
# VISUAL 1 — Gap Salarial por Cargo (barras agrupadas + linha de gap %)
# Campos necessários: cargo · genero · salario_medio_brl · nivel_hierarquico
# Tabela: fato_mercado
# ══════════════════════════════════════════════════════════════════════════════
VISUAL_1 = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

C_FEM, C_MASC, C_LINE = "#9c2f5c", "#c3a7af", "#5c1638"

df = dataset.copy()
df['salario_medio_brl'] = df['salario_medio_brl'].astype(float)

pivot = df.pivot_table(index='cargo', columns='genero',
                       values='salario_medio_brl', aggfunc='mean')
ordem = ['Estagiário','Júnior','Pleno','Sênior','Especialista','Gerente','Diretor','CTO/CIO']
pivot = pivot.reindex([c for c in ordem if c in pivot.index])
pivot['gap_pct'] = (pivot['Masculino'] - pivot['Feminino']) / pivot['Masculino'] * 100

fig, ax = plt.subplots(figsize=(10, 5))
x = range(len(pivot))
w = 0.35
ax.bar([i - w/2 for i in x], pivot['Feminino'],  w, color=C_FEM,  label='Feminino',  alpha=0.88)
ax.bar([i + w/2 for i in x], pivot['Masculino'], w, color=C_MASC, label='Masculino', alpha=0.88)
ax.set_xticks(list(x))
ax.set_xticklabels(pivot.index, rotation=20, ha='right', fontsize=9)
ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda v,_: f'R${v:,.0f}'))
ax.set_title('Salário Médio por Cargo e Gênero', color=C_LINE, pad=10)
ax.legend(fontsize=9)

ax2 = ax.twinx()
ax2.plot(list(x), pivot['gap_pct'], color=C_LINE, marker='o',
         linewidth=1.8, markersize=5, label='Gap %')
ax2.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=1))
ax2.set_ylabel('Gap salarial (%)', color=C_LINE, fontsize=9)
ax2.tick_params(axis='y', colors=C_LINE)
ax2.set_ylim(0, 40)

plt.tight_layout()
plt.show()
"""

# ══════════════════════════════════════════════════════════════════════════════
# VISUAL 2 — IRF por Cargo (barras horizontais com cor condicional)
# Campos necessários: cargo · irf · nivel_hierarquico
# Tabela: dim_cargo
# ══════════════════════════════════════════════════════════════════════════════
VISUAL_2 = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd

df = dataset.copy()
df['irf'] = df['irf'].astype(float)
df = df.sort_values('nivel_hierarquico')

def cor(v):
    if v >= 1.10: return '#5c1638'
    if v >= 0.90: return '#9c2f5c'
    if v >= 0.70: return '#e8a0b9'
    return '#f3c4d3'

colors = [cor(v) for v in df['irf']]

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.barh(df['cargo'], df['irf'], color=colors, alpha=0.9)
ax.axvline(1.0, color='#8a6e78', linestyle='--', linewidth=1.5, label='Média (1.0)')
ax.set_title('IRF — Índice de Representatividade Feminina por Cargo',
             color='#5c1638', pad=10)
ax.set_xlabel('IRF')
ax.invert_yaxis()

for bar, val in zip(bars, df['irf']):
    ax.text(val + 0.01, bar.get_y() + bar.get_height()/2,
            f'{val:.2f}', va='center', fontsize=9)

legend = [
    mpatches.Patch(color='#5c1638', label='≥ 1.10  sobre-representada'),
    mpatches.Patch(color='#9c2f5c', label='0.90–1.10  proporcional'),
    mpatches.Patch(color='#e8a0b9', label='0.70–0.89  sub-representada'),
    mpatches.Patch(color='#f3c4d3', label='< 0.70  crítica'),
]
ax.legend(handles=legend, fontsize=8, loc='lower right')
plt.tight_layout()
plt.show()
"""

# ══════════════════════════════════════════════════════════════════════════════
# VISUAL 3 — Funil de Carreira (barras decrescentes com queda em pp)
# Campos necessários: etapa · ordem · pct_feminino
# Tabela: metricas_funil
# ══════════════════════════════════════════════════════════════════════════════
VISUAL_3 = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

C_FEM, C_LINE, C_MASC = "#9c2f5c", "#5c1638", "#c3a7af"

df = dataset.copy().sort_values('ordem')
df['pct_feminino'] = df['pct_feminino'].astype(float)

fig, ax = plt.subplots(figsize=(9, 4.5))
colors = [C_FEM if i == 0 else C_MASC if i == len(df)-1 else '#c3a7af'
          for i in range(len(df))]
bars = ax.bar(df['etapa'], df['pct_feminino'], color=colors, alpha=0.85, width=0.55)

ax.set_title('Funil Feminino — Do Campus ao C-Level', color=C_LINE, fontsize=13, pad=12)
ax.set_ylabel('% de mulheres na etapa')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.set_ylim(0, max(df['pct_feminino']) * 1.25)
ax.set_xticklabels(df['etapa'], rotation=15, ha='right', fontsize=9)

for bar, val in zip(bars, df['pct_feminino']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=10,
            fontweight='bold', color=C_LINE)

pcts = df['pct_feminino'].tolist()
for i in range(len(pcts)-1):
    diff = round(pcts[i+1] - pcts[i], 1)
    if diff < 0:
        ax.annotate(f'{diff:+.1f} pp', xy=(i + 0.5, (pcts[i]+pcts[i+1])/2),
                    ha='center', va='center', fontsize=8.5,
                    color='#8a6e78', style='italic')

plt.tight_layout()
plt.show()
"""

# ══════════════════════════════════════════════════════════════════════════════
# VISUAL 4 — Evasão por Gênero (barras agrupadas por ano)
# Campos necessários: ano · tx_evasao_fem_pct · tx_evasao_masc_pct
# Tabela: fato_educacao
# ══════════════════════════════════════════════════════════════════════════════
VISUAL_4 = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

C_FEM, C_MASC, C_LINE = "#9c2f5c", "#c3a7af", "#5c1638"

df = dataset.copy().sort_values('ano')
x = range(len(df))
w = 0.35

fig, ax = plt.subplots(figsize=(8, 4))
ax.bar([i-w/2 for i in x], df['tx_evasao_fem_pct'],  w, color=C_FEM,  label='Feminino',  alpha=0.88)
ax.bar([i+w/2 for i in x], df['tx_evasao_masc_pct'], w, color=C_MASC, label='Masculino', alpha=0.88)
ax.set_xticks(list(x))
ax.set_xticklabels(df['ano'].astype(str))
ax.set_title('Taxa de Evasão em TIC por Gênero', color=C_LINE, pad=10)
ax.set_ylabel('Taxa de evasão (%)')
ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
ax.legend()

for bar in ax.patches:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            f'{bar.get_height():.1f}%', ha='center', va='bottom', fontsize=8.5)

plt.tight_layout()
plt.show()
"""

# ══════════════════════════════════════════════════════════════════════════════
# VISUAL 5 — Vagas D&I por mês (barras empilhadas)
# Campos necessários: mes_ano · eh_di
# Tabela: fato_vagas
# ══════════════════════════════════════════════════════════════════════════════
VISUAL_5 = """
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

C_FEM, C_SOFT, C_LINE = "#9c2f5c", "#f3c4d3", "#5c1638"

df = dataset.copy()
df['eh_di'] = df['eh_di'].astype(int)
mes = df.groupby('mes_ano')['eh_di'].agg(
    di=lambda s: (s==1).sum(),
    outras=lambda s: (s==0).sum()
).reset_index()

ordem_mes = sorted(mes['mes_ano'].unique(),
                   key=lambda m: (int(m.split('/')[1]), int(m.split('/')[0])))
mes = mes.set_index('mes_ano').reindex(ordem_mes).reset_index()

fig, ax = plt.subplots(figsize=(10, 4))
ax.bar(mes['mes_ano'], mes['outras'], color=C_SOFT, label='Demais vagas', alpha=0.9)
ax.bar(mes['mes_ano'], mes['di'],     bottom=mes['outras'],
       color=C_FEM, label='Vagas D&I', alpha=0.9)
ax.set_title('Vagas por Mês — Iniciativas D&I em Destaque', color=C_LINE, pad=10)
ax.set_xticklabels(mes['mes_ano'], rotation=35, ha='right', fontsize=8.5)
ax.legend(fontsize=9)
plt.tight_layout()
plt.show()
"""

# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Este arquivo contém os scripts de visualização Python para o Power BI.")
    print()
    print("Scripts disponíveis (copie a string e cole no editor Python do Power BI):")
    scripts = {
        "VISUAL_1": ("Gap Salarial por Cargo",    "fato_mercado:  cargo, genero, salario_medio_brl, nivel_hierarquico"),
        "VISUAL_2": ("IRF por Cargo",              "dim_cargo:     cargo, irf, nivel_hierarquico"),
        "VISUAL_3": ("Funil de Carreira",          "metricas_funil: etapa, ordem, pct_feminino"),
        "VISUAL_4": ("Evasão por Gênero",          "fato_educacao:  ano, tx_evasao_fem_pct, tx_evasao_masc_pct"),
        "VISUAL_5": ("Vagas D&I por Mês",          "fato_vagas:    mes_ano, eh_di"),
    }
    for var, (titulo, campos) in scripts.items():
        print(f"  {var}  ->  {titulo}")
        print(f"           Campos: {campos}")
        print()
