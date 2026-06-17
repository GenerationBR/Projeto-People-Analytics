"""Agente 2 — Arquiteto de Dados (Data Modeling Agent)."""

import logging
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent
from tools.db_tools import DBTools

logger = logging.getLogger(__name__)


class ModelingAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o Arquiteto de Dados. Modele um banco analítico (esquema estrela) a partir das
tabelas tratadas.

Regras inegociáveis:
- Separe explicitamente o escopo ACADÊMICO (fato_educacao) do PROFISSIONAL (fato_mercado).
  Eles compartilham apenas dimensões agregadas (tempo, região, gênero) — nunca chave de
  pessoa, pois não há CPF para cruzar.
- Otimize para leitura do dashboard: pré-agregue métricas quando fizer sentido, crie
  índices/particionamento por ano e região.
- Entregue o DDL completo, as views de consumo do BI e um diagrama do modelo.
Documente cada tabela e coluna para o agente de Documentação.
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
            """Descreva em Markdown o seguinte modelo estrela para um banco de People Analytics:

Fatos:
- fato_educacao (grão: Ano × Região × Gênero × Curso) → métricas: matrículas, ingressantes, concluintes, evasão
- fato_mercado (grão: Ano × Região × Gênero × Cargo × Faixa Salarial) → métricas: nº empregados, salário médio/mediano

Dimensões:
- dim_tempo (ano, décade, período)
- dim_regiao (código, nome, sigla)
- dim_genero (id, gênero)
- dim_curso_tech (código, nome, categoria, eixo INEP)
- dim_cargo (id, cargo bruto, cargo padronizado, nível, é_liderança)

Views:
- v_funil_educacao — matrículas, concluintes, evasão por ano/região/gênero
- v_pay_gap — salário médio por gênero com cálculo de gap em %
- v_lideranca — proporção de mulheres em cargos de liderança

Inclua: decisão de design (por que fatos separados), como conectar ao Power BI."""
        )

    def generate_cargo_mapping_proposal(self) -> str:
        """Pede ao LLM uma proposta de mapeamento de cargos."""
        return self.ask_llm(
            """Crie uma tabela de mapeamento de cargos do mercado tech para inserir em dim_cargo.
Formatos de entrada (cargos brutos): Data Scientist, Sr. Data Scientist, Data Analyst,
Junior Data Analyst, Machine Learning Engineer, Staff Engineer, Principal Engineer,
Head of Data, VP of Engineering, Chief Data Officer, Backend Developer, Full Stack Dev.

Para cada um, forneça:
- cargo_std (padronizado, em português)
- nivel: Junior, Pleno, Sênior, Staff, C-Level
- eh_lideranca: TRUE/FALSE (conforme definição aprovada: Sênior em diante = liderança)

Formato: tabela Markdown + instruções SQL de INSERT."""
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
