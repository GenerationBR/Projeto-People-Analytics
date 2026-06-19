"""Agente 6 — Documentação (Data Dictionary & README Agent)."""

import json
import logging
from datetime import datetime
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)


class DocsAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o agente de Documentação. O projeto analisa desigualdade de gênero na área de
DADOS no Brasil. Documente todas as fontes, tabelas e decisões metodológicas.

Produza:
1. DICIONÁRIO DE DADOS: cada tabela e coluna (nome, tipo, descrição, origem, regra).
   Destaque que fato_dados_2021 é dado real e as demais são contexto/comparação.
2. README.md: objetivo, fontes, pipeline, como rodar, premissas sensíveis datadas.

Fontes do projeto:
- fato_dados_2021: State of Data Brazil 2021 — Data Hackers / Bain & Company (DADO REAL)
- fato_mercado_mundial: WomenHack 2026 + Brasscom 2024/25 + McKinsey/LeanIn 2025 (comparação global)
- fato_educacao_tech: INEP Censo Superior (simulado — funil acadêmico)
- fato_vagas_linkedin: Vagas coletadas pela Generation (D&I signal — sem scraping ativo)

Premissas sensíveis que devem estar explícitas:
- Salário no State of Data 2021 é faixa declarada → usado midpoint para análise quantitativa
- Cruzamento educação × mercado é AGREGADO (sem CPF individual — conforme LGPD)
- Gênero binário (Feminino/Masculino) por limitação das fontes; registrar como limitação
- Broken rung medido via is_gestor (auto-declarado no survey)
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
sobre desigualdade de gênero na área de DADOS no Brasil.

TABELAS DO BANCO DuckDB (analytics.duckdb):

BASE PRINCIPAL (dado real):
- fato_dados_2021: genero, cargo, cargo_raw, salario_midpoint, uf, setor, is_gestor, experiencia_raw
  Origem: State of Data Brazil 2021 — Data Hackers / Bain & Company
  Nota: salario_midpoint = ponto médio da faixa salarial auto-declarada no survey

COMPARAÇÃO GLOBAL:
- fato_mercado_mundial: cargo, nivel, genero, regiao, n, salario_medio_brl, salario_mediano_brl
  Origem compilada: WomenHack 2026 + Brasscom Diversidade 2024/25 + McKinsey/LeanIn Women in the Workplace 2025

FUNIL ACADÊMICO (simulado ref. INEP):
- fato_educacao_tech: ano, regiao, co_regiao, area_geral, qt_mat_fem, qt_mat_masc, qt_ing_fem,
  qt_ing_masc, qt_conc_fem, qt_conc_masc, qt_mat_total, qt_ing_total, qt_conc_total,
  pct_mat_fem, pct_ing_fem, pct_conc_fem, tx_evasao_fem_pct, tx_evasao_masc_pct

D&I SIGNAL:
- fato_vagas_linkedin: id, empresa, titulo, nivel, area_tech, cidade, uf, remoto,
  tipo_di, eh_di, mes_ano, inserted_at, descricao
  Origem: Vagas coletadas pela Generation (sem scraping ativo — base já disponível)

VIEWS:
- v_pay_gap: pay gap por cargo × UF (fonte: fato_dados_2021)
- v_lideranca_dados: % mulheres em gestão por cargo (fonte: fato_dados_2021)
- v_pay_gap_global: pay gap global por cargo × região (fonte: fato_mercado_mundial)
- v_funil_nacional: funil educacional agregado (fonte: fato_educacao_tech)
- v_funil_por_regiao: funil por região (fonte: fato_educacao_tech)
- v_vagas_di: análise D&I de vagas (fonte: fato_vagas_linkedin)

PREMISSAS SENSÍVEIS:
- Salário midpoint: faixa declarada no survey → midpoint usado para análise quantitativa
- Cruzamento AGREGADO: sem CPF individual (LGPD)
- Gênero binário por limitação das fontes (registrar como limitação ética)
- Broken rung via is_gestor auto-declarado (viés de auto-percepção possível)
- Referências externas não foram auditadas individualmente

Premissas registradas no config:
{json.dumps(premises, ensure_ascii=False, indent=2)[:2000]}

Para cada tabela: nome, descrição, origem, regras de transformação.
Para cada coluna: nome, tipo, descrição, valores possíveis, regra de negócio.
Inclua seção "Premissas Sensíveis DE&I" com data e status de aprovação."""
        )

    def generate_readme(self) -> str:
        premises = self._load_config("premises.json")

        return self.ask_llm(
            f"""Gere um README.md completo para o projeto People Analytics & DE&I.

Título: "Desigualdade de Gênero na Área de Dados — People Analytics & DE&I"
Subtítulo: "Análise da trajetória feminina no mercado de dados brasileiro"

Contexto do projeto:
- Objetivo PRINCIPAL: Analisar desigualdade de gênero no mercado de dados no Brasil
  usando dado real verificado (State of Data Brazil 2021)
- Foco: profissionais de dados (DS, DE, DA, BI Analyst, Analytics Engineer, etc.)
- Comparações globais: WomenHack 2026, Brasscom 2024/25, McKinsey/LeanIn 2025
- Funil acadêmico: ref. INEP (simulado — ~18–21% mulheres em Computação)
- D&I em vagas: Generation LinkedIn (vagas já coletadas — sem scraping ativo)
- Entregas: banco analítico DuckDB, dicionário de dados, dashboard HTML, pitch executivo

Premissas críticas:
{json.dumps(premises.get("premissas", {}), ensure_ascii=False, indent=2)[:1500]}

O README deve conter:
1. Descrição do projeto e problema de negócio (foco em dados, não tech genérico)
2. Estrutura de pastas do repositório
3. Fontes de dados:
   - base_mercado_dados_2021_brasil.csv: State of Data Brazil 2021 (incluso no repo — dado real)
   - base_mercado_tech_mundial.csv: compilado global (incluso no repo)
   - base_campus_ti_brasil.csv: ref. INEP (incluso no repo — simulado)
   - generation_linkedin_vagas_tecnologia.csv: vagas Generation (incluso no repo)
4. Como instalar dependências (pip install -r requirements.txt)
5. Como executar o pipeline completo (python main.py) e o ETL isolado (python etl_pipeline.py)
6. Seção PREMISSAS (em destaque) com todas as decisões metodológicas, datas e status
7. Limitações éticas: LGPD, cruzamento agregado, gênero binário, dado de 2021
8. Estrutura dos agentes de IA

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
