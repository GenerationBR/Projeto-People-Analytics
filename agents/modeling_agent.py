"""Agente 2 — Arquiteto de Dados (Data Modeling Agent)."""

import logging
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent
from tools.db_tools import DBTools

logger = logging.getLogger(__name__)


class ModelingAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o Arquiteto de Dados. O banco analítico (analytics.duckdb) é criado pelo etl_pipeline.py.
Sua função é validar o schema, documentar o modelo e gerar mapeamentos auxiliares.

Tabela central: fato_dados_2021 (State of Data Brazil 2021 — dado real verificado).
Tabelas de suporte: fato_mercado_mundial (global), fato_educacao_tech (INEP), fato_vagas_linkedin.

Regras inegociáveis:
- Nunca cruzar fato_educacao_tech com fato_dados_2021 por indivíduo — LGPD.
  Cruzamento apenas via dimensões agregadas (ano, região, gênero).
- fato_dados_2021 é a fonte de verdade para pay gap e broken rung.
  As demais tabelas são contexto e comparação.
- Documente cada tabela e coluna para o agente de Documentação.
"""

    def __init__(self, db_path: str = "data/analytics.duckdb", output_dir: str = "outputs"):
        super().__init__("modeling", output_dir=output_dir)
        self.db = DBTools(db_path=db_path)

    def create_database(self) -> str:
        """Cria o banco DuckDB com todo o schema estrela."""
        self.log_action("Criando schema estrela no DuckDB")
        self.db.create_schema()
        self.db.populate_dim_genero()
        self.db.populate_dim_tempo(list(range(2019, 2024)))
        self.db.populate_dim_regiao()
        return str(self.db.db_path)

    def generate_diagram_description(self) -> str:
        """Pede ao LLM uma descrição textual do modelo para o README."""
        return self.ask_llm(
            """Descreva em Markdown o seguinte modelo analítico (DuckDB) para um projeto de
People Analytics sobre desigualdade de gênero na área de DADOS no Brasil.

Tabelas de fato:
- fato_dados_2021 (BASE PRINCIPAL — State of Data Brazil 2021, dado real):
  genero, cargo, cargo_raw, salario_midpoint, uf, setor, is_gestor, experiencia_raw
- fato_mercado_mundial (comparação global — WomenHack 2026 + Brasscom 2024/25 + McKinsey/LeanIn 2025):
  cargo, nivel, genero, regiao, n, salario_medio_brl, salario_mediano_brl
- fato_educacao_tech (funil acadêmico — referência INEP, simulado):
  ano, regiao, co_regiao, area_geral, qt_mat_fem/masc, qt_ing_fem/masc, qt_conc_fem/masc,
  qt_mat/ing/conc_total, pct_mat/ing/conc_fem, tx_evasao_fem/masc_pct
- fato_vagas_linkedin (D&I signal — vagas Generation):
  empresa, titulo, nivel, area_tech, uf, remoto, tipo_di, eh_di, mes_ano

Dimensões auxiliares:
- dim_tempo (ano, decada, periodo)
- dim_regiao (co_regiao, no_regiao, sigla)
- dim_genero (id_genero, genero)
- dim_curso_tech (co_curso, no_curso, categoria, eixo_inep)
- dim_cargo (id_cargo, cargo_bruto, cargo_std, nivel, eh_lideranca)

Views analíticas:
- v_pay_gap — gap salarial por cargo × UF (fonte: fato_dados_2021, mín 5 obs)
- v_lideranca_dados — % mulheres em gestão por cargo (broken rung — fato_dados_2021)
- v_pay_gap_global — gap por cargo × região (fato_mercado_mundial, para comparação)
- v_funil_nacional — funil educacional agregado por ano (fato_educacao_tech)
- v_funil_por_regiao — funil por ano × região (fato_educacao_tech)

Inclua: decisão de design (por que fato_dados_2021 é a tabela central), limitações éticas
(LGPD — cruzamento apenas agregado, gênero binário por limitação das fontes),
como as views alimentam o dashboard HTML."""
        )

    def generate_cargo_mapping_proposal(self) -> str:
        """Pede ao LLM uma proposta de mapeamento de cargos da área de dados para dim_cargo."""
        return self.ask_llm(
            """Crie uma tabela de mapeamento de cargos da ÁREA DE DADOS para inserir em dim_cargo.
Foco: profissionais de dados no Brasil (conforme State of Data Brazil 2021).

Cargos brutos de entrada: Data Scientist, Sr. Data Scientist, Data Analyst, Junior Data Analyst,
Data Engineer, Analytics Engineer, BI Analyst, Machine Learning Engineer, Data Architect,
Head of Data, Data Manager, Chief Data Officer, Staff Data Scientist, Principal Data Scientist.

Para cada um, forneça:
- cargo_std (padronizado, em português — ex: "Cientista de Dados", "Engenheiro de Dados")
- nivel: Junior, Pleno, Sênior, Staff, C-Level
- eh_lideranca: TRUE/FALSE (Head, Manager, Director, VP, C-Level = TRUE)

Formato: tabela Markdown + instruções SQL de INSERT para dim_cargo."""
        )

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("Modeling Agent iniciado")
        artifacts = []

        db_path = self.create_database()
        artifacts.append({"type": "duckdb", "path": db_path})

        diagram_md = self.generate_diagram_description()
        diagram_path = self.save_output("modelo_dados.md", diagram_md)
        artifacts.append({"type": "diagram", "path": str(diagram_path)})

        cargo_map = self.generate_cargo_mapping_proposal()
        cargo_path = self.save_output("mapeamento_cargos_proposta.md", cargo_map)
        artifacts.append({"type": "mapping", "path": str(cargo_path)})

        return self.build_message(
            to_agent="eda",
            task_id="T-002",
            status="done",
            artifacts=artifacts,
            assumptions=[
                "fato_educacao e fato_mercado NUNCA cruzados por indivíduo",
                "Cruzamento apenas via dimensões agregadas: tempo, região, gênero",
                "DuckDB escolhido pela leveza — pode ser migrado para PostgreSQL se necessário",
            ],
            open_questions=[
                "Confirmar mapeamento de cargos proposto em mapeamento_cargos_proposta.md",
                "Validar se 'Engenharia de Produção' entra na dim_curso_tech",
            ],
            needs_human_approval=True,
        )
