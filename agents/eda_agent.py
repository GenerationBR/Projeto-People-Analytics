"""Agente 3 — Analista de Dados (EDA & Funnel Agent)."""

import json
import logging
from pathlib import Path
from typing import Optional

from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)


class EDAAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o Analista de Dados. Sua missão é revelar o FUNIL da mulher na tecnologia.

Para cada etapa, calcule a participação feminina e a variação ao longo dos anos:
1. Matrículas em cursos Tech
2. Conclusões (e taxa de evasão por gênero)
3. Empregabilidade no mercado tech
4. Posições de liderança (conforme definição aprovada: ex. Sênior, Staff, C-Level)
5. Gender Pay Gap por cargo/região

Entregue métricas claras e comparáveis (sempre % e variação YoY), gráficos exploratórios
e uma síntese em linguagem de negócio. Aponte onde está o maior "vazamento" do funil.
Não tire conclusões causais sem suporte — separe correlação de causalidade.
"""

    def __init__(self, db_path: str = "data/analytics.duckdb", output_dir: str = "outputs"):
        super().__init__("eda", output_dir=output_dir)
        self.db_path = db_path

    def _query(self, sql: str) -> Optional["pd.DataFrame"]:
        try:
            import duckdb
            con = duckdb.connect(self.db_path, read_only=True)
            return con.execute(sql).df()
        except Exception as e:
            logger.warning(f"Query falhou (banco pode estar vazio): {e}")
            return None

    # ─── Métricas do funil ────────────────────────────────────────────────────

    def pct_matriculas(self) -> dict:
        df = self._query("""
            SELECT ano, genero,
                   SUM(qt_matriculas) AS total,
                   ROUND(SUM(qt_matriculas) * 100.0 /
                         SUM(SUM(qt_matriculas)) OVER (PARTITION BY ano), 2) AS pct
            FROM fato_educacao fe
            JOIN dim_genero g ON g.id_genero = fe.id_genero
            GROUP BY ano, genero ORDER BY ano, genero
        """)
        return df.to_dict("records") if df is not None else []

    def taxa_evasao(self) -> dict:
        df = self._query("""
            SELECT ano, genero,
                   ROUND(AVG(tx_evasao) * 100, 2) AS tx_evasao_pct
            FROM fato_educacao fe
            JOIN dim_genero g ON g.id_genero = fe.id_genero
            WHERE tx_evasao IS NOT NULL
            GROUP BY ano, genero ORDER BY ano, genero
        """)
        return df.to_dict("records") if df is not None else []

    def pct_lideranca(self) -> dict:
        df = self._query("""
            SELECT ano, no_regiao, genero, pct_genero
            FROM v_lideranca ORDER BY ano, no_regiao, genero
        """)
        return df.to_dict("records") if df is not None else []

    def pay_gap_summary(self) -> dict:
        df = self._query("""
            SELECT ano, no_regiao, cargo_std, nivel, pay_gap_pct
            FROM v_pay_gap
            WHERE pay_gap_pct IS NOT NULL
            ORDER BY ABS(pay_gap_pct) DESC
            LIMIT 20
        """)
        return df.to_dict("records") if df is not None else []

    # ─── Notebook de análise ──────────────────────────────────────────────────

    def generate_eda_notebook(self, metricas: dict) -> str:
        return self.ask_llm(
            f"""Crie um notebook Python comentado (formato Markdown com blocos de código Python)
para análise exploratória do funil da mulher na tecnologia.

Métricas disponíveis (podem estar vazias se banco ainda não foi populado):
{json.dumps(metricas, ensure_ascii=False, indent=2)[:3000]}

O notebook deve conter:
1. Carregamento dos dados do DuckDB (`data/analytics.duckdb`)
2. Funil de matrículas → conclusões → empregabilidade → liderança → pay gap
3. Para cada etapa: % feminina, variação YoY, gráfico Plotly
4. Síntese em linguagem de negócio identificando onde está o maior "vazamento"
5. Nota explícita: correlação ≠ causalidade

Use Polars para leitura e Plotly para visualização. Inclua paleta de cores acessível."""
        )

    # ─── Síntese executiva ────────────────────────────────────────────────────

    def generate_executive_summary(self, metricas: dict) -> str:
        return self.ask_llm(
            f"""Com base nas métricas abaixo de People Analytics & DE&I, redija uma síntese executiva
(máx 400 palavras) em linguagem de negócio para RH e diretoria.

Métricas:
{json.dumps(metricas, ensure_ascii=False, indent=2)[:3000]}

Estrutura:
1. Contexto: panorama da entrada feminina na tech
2. O funil: onde ocorrem os maiores vazamentos
3. Pay gap: evidências e limitações
4. Ponto de atenção: onde intervir tem maior impacto

Se os dados estiverem vazios, gere a estrutura com placeholders [X%] prontos para preenchimento."""
        )

    # ─── run() ────────────────────────────────────────────────────────────────

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("EDA Agent iniciado")

        metricas = {
            "pct_matriculas": self.pct_matriculas(),
            "taxa_evasao": self.taxa_evasao(),
            "pct_lideranca": self.pct_lideranca(),
            "pay_gap_top20": self.pay_gap_summary(),
        }

        notebook = self.generate_eda_notebook(metricas)
        notebook_path = self.save_output("eda_funil_feminino.py", notebook)

        summary = self.generate_executive_summary(metricas)
        summary_path = self.save_output("sintese_executiva.md", summary)

        metricas_path = self.save_output(
            "metricas_funil.json",
            json.dumps(metricas, ensure_ascii=False, indent=2)
        )

        return self.build_message(
            to_agent="statistics",
            task_id="T-003",
            status="done",
            artifacts=[
                {"type": "script", "path": str(notebook_path)},
                {"type": "summary", "path": str(summary_path)},
                {"type": "json", "path": str(metricas_path)},
            ],
            assumptions=[
                "Pay gap calculado com grupos comparáveis (mesmo cargo, mesma região)",
                "Correlação e causalidade são separadas na análise",
                "Taxa de evasão = (ingressantes - concluintes) / ingressantes",
            ],
            open_questions=[
                "Definição de 'empregabilidade em tech' precisa de validação com RAIS",
                "Confirmar se Agente 4 deve controlar confounders por senioridade",
            ],
        )
