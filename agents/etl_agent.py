"""Agente 1 — Engenheiro de Dados (ETL Agent)."""

import json
import logging
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent
from tools.etl_tools import ETLTools

logger = logging.getLogger(__name__)


class ETLAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o Engenheiro de Dados (ETL) do projeto. O foco mudou: analisamos desigualdade de
gênero na ÁREA DE DADOS (nicho tech) no Brasil, com dado real verificado.

BASES DE DADOS DO PROJETO:

1. base_mercado_dados_2021_brasil.csv — BASE PRINCIPAL (dado real)
   Survey State of Data Brazil 2021 (Data Hackers / Bain & Company).
   Profissionais da área de dados no Brasil: DS, DE, DA, BI Analyst, Analytics Engineer, etc.
   Colunas no formato ('P1_a', 'Label') — parser flexível por label já implementado.
   Extrai: gênero, cargo, faixa salarial (midpoint BRL), UF, setor, gestão, experiência.

2. base_mercado_tech_mundial.csv — COMPARAÇÃO GLOBAL (não é a base principal)
   Compilado: WomenHack 2026 + Brasscom 2024/25 + McKinsey/LeanIn Women in the Workplace 2025.
   Dados de referência: 29% C-Suite mulheres, 15% CTOs, gap salarial ~27%, broken rung.
   Usar APENAS para contextualização e comparação com o cenário internacional.

3. base_campus_ti_brasil.csv — FUNIL ACADÊMICO (simulado com base no INEP)
   ~18–21% mulheres ingressando em Computação no Brasil.
   Cruzamento com mercado é AGREGADO (sem CPF individual — conforme LGPD).

4. generation_linkedin_vagas_tecnologia.csv — D&I SIGNAL (já coletado, sem scraping)
   Vagas coletadas pela Generation. Classifica tipo D&I: Exclusiva | Afirmativa | Aberta.

Diretrizes técnicas:
- State of Data 2021: parse das colunas via label (ex.: 'gênero', 'cargo atual', 'faixa salarial').
  Converter faixa salarial para midpoint BRL. Filtrar apenas Feminino/Masculino para análise.
- Winsorização p01-p99 nos salários do dataset global para comparação limpa.
- Trate outliers com método explícito. Registre linhas afetadas. Nunca descarte sem documentar.
- Saída: fato_dados_2021 (principal), fato_mercado_mundial (global), fato_educacao_tech,
  fato_vagas_linkedin — todos no DuckDB analytics.duckdb.
"""

    def __init__(self, config_dir: str = "config", data_dir: str = "data", output_dir: str = "outputs"):
        super().__init__("etl", output_dir=output_dir)
        self.tools = ETLTools(config_dir=config_dir, data_dir=data_dir)
        self.quality_reports: list[dict] = []
        self.outlier_logs: list[dict] = []

    # ─── INEP ─────────────────────────────────────────────────────────────────

    def process_inep(self, filepath: str) -> dict:
        """Pipeline completo para microdados INEP."""
        self.log_action(f"Iniciando processamento INEP: {filepath}")

        df = self.tools.load_inep_chunked(filepath)
        df = self.tools.filter_tech_courses(df)
        df = self.tools.harmonize_gender(df, col="TP_SEXO")

        # Agrega: queremos fato_educacao com grão Ano × Região × Gênero × Curso
        df_agg = df.group_by(
            ["NU_ANO_CENSO", "CO_REGIAO", "NO_REGIAO", "genero", "CO_CURSO", "NO_CURSO"]
        ).agg([
            (lambda c: c.filter(df["IN_MATRICULA"] == "1").len()).alias("qt_matriculas") if "IN_MATRICULA" in df.columns else __import__("polars").lit(0).alias("qt_matriculas"),
        ])

        path = self.tools.save_parquet(df_agg, "fato_educacao_raw")
        report = self.tools.quality_report(df_agg, "fato_educacao_raw")
        self.quality_reports.append(report)

        return {"path": str(path), "report": report}

    # ─── Salários (Kaggle / StackOverflow) ────────────────────────────────────

    def process_salaries(self, filepath: str, source: str = "Kaggle") -> dict:
        """Pipeline para base de salários externos ou dataset simulado de mercado."""
        import polars as pl

        # Detecta a base mockada pelo nome do arquivo
        fname = Path(filepath).name.lower()
        if "base_mercado_tech_brasil" in fname:
            source = "BaseMercadoBrasil (Brasscom+StateOfData+McKinsey)"

        self.log_action(f"Processando salários ({source}): {filepath}")

        df = pl.read_csv(filepath, infer_schema_length=1000, ignore_errors=True)

        # Mapeamento de colunas common aos dois datasets
        rename_map = {
            "salary": "salary", "total_yearly_compensation": "salary", "salario_base": "salary",
            "gender": "genero", "Gender": "genero",
            "job_title": "cargo", "title": "cargo", "DevType": "cargo",
            "location": "regiao", "country": "regiao", "Country": "regiao",
            "years_experience": "anos_exp", "YearsCode": "anos_exp",
        }
        existing = {k: v for k, v in rename_map.items() if k in df.columns}
        df = df.rename(existing)

        if "salary" not in df.columns:
            logger.warning(f"Coluna 'salary' não encontrada em {filepath}. Pulando outliers.")
            return {"skipped": True, "reason": "salary column missing"}

        df, outlier_report = self.tools.treat_salary_outliers(df, salary_col="salary")
        outlier_report["source"] = source
        self.outlier_logs.append(outlier_report)

        if "genero" in df.columns:
            df = self.tools.harmonize_gender(df, col="genero")

        path = self.tools.save_parquet(df, f"fato_mercado_{source.lower()}_raw")
        report = self.tools.quality_report(df, f"fato_mercado_{source.lower()}_raw")
        self.quality_reports.append(report)

        return {"path": str(path), "report": report, "outlier_log": outlier_report}

    # ─── Relatório final ──────────────────────────────────────────────────────

    def generate_quality_report_md(self) -> str:
        lines = ["# Relatório de Qualidade de Dados — ETL\n"]
        for r in self.quality_reports:
            lines.append(f"## Tabela: `{r['tabela']}`")
            lines.append(f"- Linhas: {r['linhas']:,}")
            lines.append(f"- Colunas: {r['colunas']}")
            if r["nulos_por_coluna"]:
                lines.append("- Nulos por coluna:")
                for col, n in r["nulos_por_coluna"].items():
                    lines.append(f"  - `{col}`: {n:,}")
            lines.append("")

        if self.outlier_logs:
            lines.append("## Tratamento de Outliers Salariais\n")
            for log in self.outlier_logs:
                lines.append(f"### Fonte: {log.get('source', 'desconhecida')}")
                lines.append(f"- Método: {log['metodo']}")
                lines.append(f"- Ação: {log['acao']}")
                lines.append(f"- Linhas afetadas: {log.get('linhas_afetadas', log.get('linhas_removidas', 'N/A'))}")
                lines.append(f"- P01: {log['p01']:.2f} | P99: {log['p99']:.2f}")
                lines.append("")

        return "\n".join(lines)

    # ─── LLM — análise de anomalias ───────────────────────────────────────────

    def analyze_anomalies(self, report: dict) -> str:
        return self.ask_llm(
            f"Analise o seguinte relatório de qualidade de dados ETL e identifique "
            f"anomalias críticas que precisam ser reportadas ao Orquestrador:\n\n{json.dumps(report, ensure_ascii=False, indent=2)}"
        )

    # ─── run() ────────────────────────────────────────────────────────────────

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("ETL Agent iniciado")
        artifacts = []
        open_questions = []
        assumptions = [
            "Leitura INEP em chunks — nunca carregado inteiro em memória",
            "Filtro de cursos Tech aplicado via course_mapping.json",
            "Outliers salariais tratados com winsorization_p99",
            "Cruzamento educação × mercado é AGREGADO (sem CPF individual)",
            "base_mercado_tech_brasil.csv é dataset simulado (Brasscom + State of Data + McKinsey) com gap salarial intencional de ~27% e gargalo de liderança feminina embutidos",
        ]

        # Descoberta automática de arquivos brutos
        raw_dir = Path(self.tools.raw_dir)
        campus_files  = list(raw_dir.glob("*campus*.*")) + list(raw_dir.glob("*inep*.*"))
        dados21_files = list(raw_dir.glob("*dados_2021*.*")) + list(raw_dir.glob("*state_of_data*.*"))
        mundial_files = list(raw_dir.glob("*mundial*.*")) + list(raw_dir.glob("*global*.*"))
        linkedin_files = list(raw_dir.glob("*linkedin*.*")) + list(raw_dir.glob("*vagas*.*"))

        all_found = campus_files or dados21_files or mundial_files or linkedin_files

        if not all_found:
            open_questions.append(
                "Nenhum arquivo bruto encontrado em data/raw/. "
                "Verificar presença de: base_mercado_dados_2021_brasil.csv, "
                "base_mercado_tech_mundial.csv, base_campus_ti_brasil.csv, "
                "generation_linkedin_vagas_tecnologia.csv."
            )
            self.log_action("AVISO: data/raw/ vazio ou arquivos esperados ausentes.")
        else:
            for f in campus_files:
                result = self.process_inep(str(f))
                artifacts.append({"type": "parquet", "path": result["path"], "source": "INEP"})

            for f in dados21_files:
                result = self.process_salaries(str(f), source="StateOfData2021")
                if not result.get("skipped"):
                    artifacts.append({"type": "parquet", "path": result["path"], "source": "StateOfData2021"})

            for f in mundial_files:
                result = self.process_salaries(str(f), source="MercadoMundial")
                if not result.get("skipped"):
                    artifacts.append({"type": "parquet", "path": result["path"], "source": "MercadoMundial"})

        # Popula o DuckDB com etl_pipeline.py (único que parseia corretamente as colunas
        # tuple-format do State of Data 2021 e carrega fato_dados_2021 + fato_mercado_mundial)
        try:
            import etl_pipeline as _etl
            _etl.main()
            self.log_action("DuckDB populado via etl_pipeline.main()")
            artifacts.append({"type": "duckdb", "path": str(_etl.DB)})
        except Exception as e:
            logger.warning(f"etl_pipeline.main() falhou: {e}")
            open_questions.append(f"etl_pipeline.main() não executado: {e}")

        # Gera relatório de qualidade
        report_md = self.generate_quality_report_md()
        report_path = self.save_output("qualidade_dados_etl.md", report_md)
        artifacts.append({"type": "report", "path": str(report_path)})

        return self.build_message(
            to_agent="modeling",
            task_id="T-001",
            status="done" if all_found else "needs_human_approval",
            artifacts=artifacts,
            assumptions=assumptions,
            open_questions=open_questions,
            needs_human_approval=bool(open_questions),
        )
