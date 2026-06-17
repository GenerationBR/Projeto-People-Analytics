"""Agente 6 — Documentação (Data Dictionary & README Agent)."""

import json
import logging
from datetime import datetime
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)


class DocsAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o agente de Documentação. Produza:
1. DICIONÁRIO DE DADOS: cada tabela e coluna (nome, tipo, descrição, origem, regra de
   transformação). Inclua a tabela de mapeamento "curso → categoria Tech" e
   "cargo bruto → cargo padronizado".
2. README.md: objetivo, fontes, pipeline ETL, como rodar, e — com destaque — TODAS as
   premissas (ex.: definição de "liderança", critério de outliers, recorte de eixos).
Escreva de forma que qualquer pessoa reproduza o projeto. Premissas sensíveis de DE&I
devem estar explícitas e datadas.
"""

    def __init__(self, config_dir: str = "config", output_dir: str = "outputs"):
        super().__init__("docs", output_dir=output_dir)
        self.config_dir = Path(config_dir)

    def _load_config(self, filename: str) -> dict:
        path = self.config_dir / filename
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate_data_dictionary(self) -> str:
        premises = self._load_config("premises.json")
        course_map = self._load_config("course_mapping.json")

        return self.ask_llm(
            f"""Gere um Dicionário de Dados completo em Markdown para o projeto People Analytics
sobre trajetória feminina na tecnologia.

Tabelas do banco DuckDB (analytics.duckdb):

FATOS:
- fato_educacao: id, ano, co_regiao, id_genero, co_curso, qt_matriculas, qt_ingressantes, qt_concluintes, qt_evasao, tx_evasao
- fato_mercado: id, ano, co_regiao, id_genero, id_cargo, faixa_salarial, qt_empregados, salario_medio, salario_mediano, fonte

DIMENSÕES:
- dim_tempo: ano, decada, periodo
- dim_regiao: co_regiao, no_regiao, sigla_regiao
- dim_genero: id_genero, genero
- dim_curso_tech: co_curso, no_curso, categoria, eixo_inep
- dim_cargo: id_cargo, cargo_bruto, cargo_std, nivel, eh_lideranca

VIEWS:
- v_funil_educacao, v_pay_gap, v_lideranca

ARQUIVOS PARQUET em data/treated/:
- fato_educacao_raw.parquet (origem: INEP microdados)
- fato_mercado_kaggle_raw.parquet (origem: Kaggle STEM Salaries)
- fato_mercado_stackoverflow_raw.parquet (origem: StackOverflow Survey)

Premissas registradas:
{json.dumps(premises, ensure_ascii=False, indent=2)[:2000]}

Mapeamento de cursos Tech:
{json.dumps(course_map, ensure_ascii=False, indent=2)[:1000]}

Para cada tabela: nome, descrição, origem dos dados, regras de transformação aplicadas.
Para cada coluna: nome, tipo, descrição, valores possíveis, regra de negócio.
Inclua seção de "Premissas Sensíveis DE&I" com data e status de aprovação."""
        )

    def generate_readme(self) -> str:
        premises = self._load_config("premises.json")

        return self.ask_llm(
            f"""Gere um README.md completo para o projeto People Analytics & DE&I.

Título: "A Trajetória Feminina do Câmpus ao Mercado Tech — People Analytics & DE&I"

Contexto do projeto:
- Objetivo: mapear o funil da mulher na tecnologia no Brasil (e dados globais)
- Fontes: INEP Censo Superior (≥5 anos), RAIS/CAGED, Kaggle STEM Salaries, StackOverflow Survey
- Entregas: banco analítico, dicionário de dados, dashboard Power BI, pitch executivo

Premissas críticas registradas:
{json.dumps(premises.get("premissas", {}), ensure_ascii=False, indent=2)[:1500]}

O README deve conter:
1. Descrição do projeto e problema de negócio
2. Estrutura de pastas do repositório (tree detalhada)
3. Fontes de dados e como baixá-las (links e instruções)
4. Como instalar dependências (pip install -r requirements.txt)
5. Como executar o pipeline completo (python main.py)
6. Como rodar o Data App (streamlit run app/calculadora.py)
7. Seção PREMISSAS (em destaque) com todas as decisões metodológicas, datas e status
8. Limitações e avisos éticos (LGPD, cruzamento apenas agregado)
9. Estrutura dos agentes de IA e como estender o sistema

Tom: técnico mas acessível. Data: {datetime.now().strftime('%Y-%m-%d')}."""
        )

    def generate_premises_log(self) -> str:
        premises = self._load_config("premises.json")
        lines = [
            f"# Log de Premissas — People Analytics & DE&I",
            f"*Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M')}*",
            "",
            "| Premissa | Decisão | Status | Data |",
            "|---|---|---|---|",
        ]
        for key, val in premises.get("premissas", {}).items():
            status = val.get("status", "INDEFINIDO")
            descricao = str(val.get("definicao") or val.get("descricao") or val.get("tipo") or val.get("anos", ""))[:80]
            lines.append(f"| {key} | {descricao} | {status} | {premises.get('data_criacao', '—')} |")

        return "\n".join(lines)

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("Docs Agent iniciado")

        dict_content = self.generate_data_dictionary()
        dict_path = self.save_output("dicionario/dicionario_de_dados.md", dict_content)

        readme_content = self.generate_readme()
        readme_path = Path("README.md")
        readme_path.write_text(readme_content, encoding="utf-8")
        self.log_action(f"README.md gerado em: {readme_path.absolute()}")

        premises_log = self.generate_premises_log()
        premises_path = self.save_output("log_premissas.md", premises_log)

        return self.build_message(
            to_agent="pitch",
            task_id="T-006",
            status="done",
            artifacts=[
                {"type": "markdown", "path": str(dict_path)},
                {"type": "readme", "path": str(readme_path)},
                {"type": "premises_log", "path": str(premises_path)},
            ],
            assumptions=[
                "Dicionário gerado a partir do schema DuckDB e configs em config/",
                "README inclui todas as premissas com status de aprovação",
                "Premissas sensíveis DE&I estão datadas e rastreáveis",
            ],
        )
