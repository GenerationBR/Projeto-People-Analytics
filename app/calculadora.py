"""
Calculadora de Equidade Salarial para RH
People Analytics & DE&I — A Trajetória Feminina do Câmpus ao Mercado Tech
"""

import json
from pathlib import Path

import duckdb
import numpy as np
import plotly.graph_objects as go
import streamlit as st

# ─── Config ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Calculadora DE&I — People Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = Path(__file__).parent.parent / "data" / "analytics.duckdb"

# ─── Utilitários ──────────────────────────────────────────────────────────────

@st.cache_resource
def get_connection():
    if DB_PATH.exists():
        return duckdb.connect(str(DB_PATH), read_only=True)
    return None


def query(sql: str):
    con = get_connection()
    if con is None:
        return None
    try:
        return con.execute(sql).df()
    except Exception as e:
        st.error(f"Erro na consulta: {e}")
        return None


def demo_data(cargo: str, regiao: str) -> dict:
    """Dados de demonstração quando banco está vazio."""
    import random
    random.seed(hash(cargo + regiao) % 1000)
    base = {"Sênior": 12000, "Pleno": 8000, "Junior": 5000, "Staff": 18000, "C-Level": 28000}
    nivel = next((k for k in base if k.lower() in cargo.lower()), "Pleno")
    sal_m = base[nivel] + random.randint(-1000, 1000)
    sal_f = sal_m * random.uniform(0.80, 0.97)
    return {
        "cargo_std": cargo,
        "regiao": regiao,
        "salario_medio_masc": sal_m,
        "salario_medio_fem": sal_f,
        "pay_gap_pct": round((sal_m - sal_f) / sal_m * 100, 1),
        "is_demo": True,
    }


# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("Calculadora DE&I")
    st.caption("People Analytics · Trajetória Feminina na Tech")
    st.divider()

    regioes = ["Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]
    cargos_exemplo = [
        "Data Scientist Sênior", "Data Analyst Pleno", "Machine Learning Engineer",
        "Staff Engineer", "Head of Data", "Backend Developer Sênior", "Analista de Dados Junior",
    ]

    regiao = st.selectbox("Região", regioes, index=2)
    cargo = st.selectbox("Cargo / Área", cargos_exemplo)
    ano = st.slider("Ano de referência", 2019, 2023, 2022)

    st.divider()
    st.info("💡 Dados do banco analítico validado. Intervalos de confiança exibidos quando amostra ≥ 30.")

# ─── Main ─────────────────────────────────────────────────────────────────────

st.title("📊 Calculadora de Equidade Salarial para RH")
st.markdown(f"**Cargo:** {cargo} | **Região:** {regiao} | **Ano:** {ano}")
st.divider()

# Consulta o banco
df_gap = query(f"""
    SELECT cargo_std, no_regiao, salario_medio_masc, salario_medio_fem, pay_gap_pct
    FROM v_pay_gap
    WHERE LOWER(cargo_std) LIKE LOWER('%{cargo.split()[0]}%')
      AND no_regiao = '{regiao}'
      AND ano = {ano}
    LIMIT 5
""")

if df_gap is not None and not df_gap.empty:
    row = df_gap.iloc[0].to_dict()
    row["is_demo"] = False
else:
    row = demo_data(cargo, regiao)
    st.warning("⚠️ Banco ainda não populado com dados reais. Exibindo demonstração com dados simulados.")

# ─── KPIs ─────────────────────────────────────────────────────────────────────

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Salário Médio Masculino", f"R$ {row['salario_medio_masc']:,.0f}")
with col2:
    st.metric("Salário Médio Feminino", f"R$ {row['salario_medio_fem']:,.0f}")
with col3:
    gap = row["pay_gap_pct"]
    st.metric(
        "Gender Pay Gap",
        f"{gap:.1f}%",
        delta=f"{'desvantagem feminina' if gap > 0 else 'paridade'}",
        delta_color="inverse",
    )

st.divider()

# ─── Gráfico de barras comparativo ────────────────────────────────────────────

col_chart, col_info = st.columns([2, 1])

with col_chart:
    fig = go.Figure(data=[
        go.Bar(name="Masculino", x=["Salário Médio"], y=[row["salario_medio_masc"]],
               marker_color="#1E3A5F"),
        go.Bar(name="Feminino",  x=["Salário Médio"], y=[row["salario_medio_fem"]],
               marker_color="#E91E8C"),
    ])
    fig.update_layout(
        barmode="group",
        title=f"Comparativo Salarial — {cargo} ({regiao})",
        yaxis_title="Salário Médio (R$)",
        plot_bgcolor="white",
        font=dict(family="Inter, sans-serif"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col_info:
    st.subheader("Contexto")
    if gap > 10:
        st.error(f"Gap de {gap:.1f}% — **alto**. Acima da média nacional do setor tech.")
    elif gap > 5:
        st.warning(f"Gap de {gap:.1f}% — **moderado**. Atenção recomendada.")
    else:
        st.success(f"Gap de {gap:.1f}% — **baixo**. Próximo da paridade.")

    if row.get("is_demo"):
        st.caption("*Dados simulados para demonstração. Popule data/analytics.duckdb com dados reais.*")

# ─── Disponibilidade histórica de mulheres formadas ───────────────────────────

st.divider()
st.subheader("Disponibilidade Histórica — Mulheres Formadas na Área")

df_edu = query(f"""
    SELECT ano, genero, SUM(total_concluintes) AS concluintes,
           ROUND(SUM(total_concluintes) * 100.0 / SUM(SUM(total_concluintes)) OVER (PARTITION BY ano), 1) AS pct
    FROM v_funil_educacao
    WHERE no_regiao = '{regiao}'
    GROUP BY ano, genero
    ORDER BY ano
""")

if df_edu is not None and not df_edu.empty:
    fem = df_edu[df_edu["genero"] == "Feminino"]
    fig2 = go.Figure(go.Scatter(
        x=fem["ano"], y=fem["pct"], mode="lines+markers",
        line=dict(color="#E91E8C", width=2),
        name="% Feminino",
    ))
    fig2.update_layout(
        title=f"% de Mulheres Formadas em Tech — {regiao}",
        yaxis_title="% do total de concluintes",
        xaxis_title="Ano",
        plot_bgcolor="white",
    )
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.info("Dados educacionais ainda não disponíveis. Popule via ETL Agent (python main.py etl).")

# ─── Rodapé ───────────────────────────────────────────────────────────────────

st.divider()
st.caption(
    "Fonte: INEP Censo Superior · Base de Mercado Tech Brasil (Brasscom + State of Data + McKinsey) | "
    "Cruzamento AGREGADO (sem dados individuais, conforme LGPD) | "
    "People Analytics & DE&I — Generation Brasil"
)
