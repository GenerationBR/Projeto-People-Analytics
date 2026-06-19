"""Agente 3 — Analista de Dados (EDA & Funnel Agent)."""

import json
import logging
from pathlib import Path
from typing import Optional

from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)


class EDAAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o Analista de Dados. O projeto analisa desigualdade de gênero na ÁREA DE DADOS
(nicho tech no Brasil). A base principal é dado real verificado.

OBJETIVO PRINCIPAL: Analisar desigualdade de gênero no mercado de dados brasileiro
usando o State of Data Brazil 2021 (fato_dados_2021). Comparações globais são feitas
com fato_mercado_mundial (WomenHack + Brasscom + McKinsey) apenas onde possível.

ANÁLISES PRIORITÁRIAS (fato_dados_2021):
1. Distribuição de gênero por cargo (DS, DE, DA, BI Analyst, Analytics Engineer, etc.)
2. Gender Pay Gap por cargo e UF — onde a diferença é maior?
3. Broken rung: razão mulheres/homens que chegam a posições de gestão/liderança
4. Funil acadêmico (fato_educacao_tech — ref. INEP): ~18–21% de ingressantes femininas
   em Computação → cruzar com % no mercado de dados para medir o "salto"
5. D&I signal em vagas (fato_vagas_linkedin): % vagas afirmativas por área/UF

COMPARAÇÕES GLOBAIS (fato_mercado_mundial — apenas onde os dados permitem):
- Pay gap global vs. pay gap brasileiro na área de dados
- Referências: 29% C-Suite mulheres (WomenHack), broken rung McKinsey, 34,2% Brasscom

Diretrizes:
- Sempre use % e variação, nunca só números absolutos.
- Separe correlação de causalidade. Não force conclusões além dos dados.
- Tabela fato_dados_2021 tem: genero, cargo, salario_midpoint, uf, setor, is_gestor.
- Tabela fato_mercado_mundial tem: cargo, nivel, genero, regiao, salario_medio_brl.
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

    def dist_genero_por_cargo(self) -> dict:
        """Distribuição de gênero por cargo na área de dados (State of Data 2021)."""
        df = self._query("""
            SELECT cargo,
                   COUNT(*) AS total,
                   SUM(CASE WHEN genero = 'Feminino' THEN 1 ELSE 0 END) AS n_fem,
                   ROUND(SUM(CASE WHEN genero = 'Feminino' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_fem
            FROM fato_dados_2021
            GROUP BY cargo
            HAVING COUNT(*) >= 5
            ORDER BY pct_fem
        """)
        return df.to_dict("records") if df is not None else []

    def pay_gap_dados_2021(self) -> dict:
        """Pay gap por cargo na área de dados — dado real State of Data 2021."""
        df = self._query("""
            SELECT cargo, uf, salario_medio_masc, salario_medio_fem, n_masc, n_fem, pay_gap_pct
            FROM v_pay_gap
            WHERE pay_gap_pct IS NOT NULL
            ORDER BY ABS(pay_gap_pct) DESC
            LIMIT 20
        """)
        return df.to_dict("records") if df is not None else []

    def lideranca_dados(self) -> dict:
        """Broken rung: % mulheres em posições de gestão por cargo."""
        df = self._query("""
            SELECT cargo, total, n_fem, pct_fem, n_gestores, pct_gestoras
            FROM v_lideranca_dados
            ORDER BY pct_fem
        """)
        return df.to_dict("records") if df is not None else []

    def funil_academico(self) -> dict:
        """Funil INEP — % mulheres em cursos de Computação (ref. ~18–21%)."""
        df = self._query("""
            SELECT ano, pct_mat_fem, pct_ing_fem, pct_conc_fem,
                   media_evasao_fem, media_evasao_masc
            FROM v_funil_nacional
            ORDER BY ano
        """)
        return df.to_dict("records") if df is not None else []

    def pay_gap_global(self) -> dict:
        """Pay gap global para comparação (WomenHack + Brasscom + McKinsey)."""
        df = self._query("""
            SELECT cargo, regiao, salario_medio_masc, salario_medio_fem, pay_gap_pct
            FROM v_pay_gap_global
            WHERE pay_gap_pct IS NOT NULL
            ORDER BY ABS(pay_gap_pct) DESC
            LIMIT 15
        """)
        return df.to_dict("records") if df is not None else []

    def pct_matriculas(self) -> dict:
        """Mantido por compatibilidade — usa v_funil_nacional."""
        return self.funil_academico()

    def taxa_evasao(self) -> dict:
        df = self._query("""
            SELECT ano,
                   ROUND(AVG(media_evasao_fem), 2)  AS tx_evasao_fem_pct,
                   ROUND(AVG(media_evasao_masc), 2) AS tx_evasao_masc_pct
            FROM v_funil_nacional
            GROUP BY ano ORDER BY ano
        """)
        return df.to_dict("records") if df is not None else []

    def pay_gap_summary(self) -> dict:
        """Alias — usa pay_gap_dados_2021 como fonte principal."""
        return self.pay_gap_dados_2021()

    # ─── Notebook de análise ──────────────────────────────────────────────────

    def generate_eda_notebook(self, metricas: dict) -> str:
        return self.ask_llm(
            f"""Crie um notebook Python comentado (formato Markdown com blocos de código Python)
para análise exploratória da desigualdade de gênero na área de dados no Brasil.

BASE PRINCIPAL: State of Data Brazil 2021 (fato_dados_2021 — dado real).
COMPARAÇÃO GLOBAL: fato_mercado_mundial (WomenHack + Brasscom + McKinsey).
FUNIL ACADÊMICO: fato_educacao_tech (ref. INEP).

Métricas disponíveis (podem estar vazias se banco ainda não foi populado):
{json.dumps(metricas, ensure_ascii=False, indent=2)[:3000]}

O notebook deve conter:
1. Carregamento do DuckDB (`data/analytics.duckdb`) — tabelas: fato_dados_2021, v_pay_gap,
   v_lideranca_dados, v_funil_nacional, v_pay_gap_global
2. Distribuição de gênero por cargo na área de dados (% feminino por cargo)
3. Gender Pay Gap por cargo e UF — gráfico de barras divergentes
4. Broken rung: % mulheres em gestão vs. total (funnel chart)
5. Funil acadêmico INEP: % feminino em Computação por ano
6. Comparação global: pay gap Brasil (dados) vs. referências internacionais
7. D&I em vagas de dados (v_vagas_di): % afirmativas por área
8. Síntese: onde está o maior gap e qual intervenção teria maior impacto
9. Nota: correlação ≠ causalidade; dado de 2021 pode não refletir o presente

Use Polars para leitura e Plotly para visualização. Paleta acessível (contraste ≥ 4.5:1)."""
        )

    def generate_executive_summary(self, metricas: dict) -> str:
        return self.ask_llm(
            f"""Com base nas métricas abaixo, redija uma síntese executiva (máx 400 palavras)
sobre desigualdade de gênero na área de dados no Brasil. Público: gestores e RH.

Contexto do projeto:
- Base principal: State of Data Brazil 2021 (dado real verificado)
- Foco: profissionais de dados (DS, DE, DA, BI Analyst, Analytics Engineer)
- Comparação global disponível: WomenHack 2026 (29% C-Suite mulheres), Brasscom 2024/25
  (34,2% TIC Brasil, gap ~27%), McKinsey/LeanIn 2025 (broken rung: 87 vs 100)

Métricas:
{json.dumps(metricas, ensure_ascii=False, indent=2)[:3000]}

Estrutura:
1. Contexto: por que analisar especificamente a área de dados?
2. O cenário nacional: participação feminina por cargo (dado real 2021)
3. Pay gap: onde é maior e menor na área de dados
4. Broken rung: barreira de acesso à gestão
5. Comparação global: Brasil vs. referências internacionais
6. Ponto de maior impacto: onde intervir primeiro

Se dados estiverem vazios, use placeholders [X%] prontos para preenchimento."""
        )

    # ─── run() ────────────────────────────────────────────────────────────────

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("EDA Agent iniciado")

        metricas = {
            "dist_genero_por_cargo":   self.dist_genero_por_cargo(),
            "pay_gap_dados_2021":      self.pay_gap_dados_2021(),
            "lideranca_dados":         self.lideranca_dados(),
            "funil_academico_inep":    self.funil_academico(),
            "pay_gap_global":          self.pay_gap_global(),
            "taxa_evasao":             self.taxa_evasao(),
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
