"""Agente 1 — Engenheiro de Dados (ETL Agent)."""

import json
import logging
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent
from tools.etl_tools import ETLTools

logger = logging.getLogger(__name__)


class ETLAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o Engenheiro de Dados (ETL) do projeto. Trabalha com bases massivas de educação
(INEP) e de mercado (base_mercado_tech_brasil.csv — dataset simulado).

ATENÇÃO — Base de mercado:
A base `data/raw/base_mercado_tech_brasil.csv` é um dataset mockado pedagogicamente a
partir de três referências de mercado:
  1. Brasscom (salario_base): valores derivados do relatório Brasscom com multiplicador
     que gera ~27% de gap salarial entre gêneros — padrão intencional e detectável.
  2. State of Data Brazil (cargos): nomes de cargos e tempo médio de experiência por
     nível hierárquico (Júnior → Pleno → Sênior → Liderança → Diretoria → C-Level).
  3. McKinsey — Women in the Workplace (promoção/retenção): lógica de gargalo no meio
     da pirâmide corporativa; dificuldade estatística maior para mulheres em Diretoria/CTO.
Esta base possui coluna de gênero e é adequada para análise de pay gap e liderança.

Diretrizes técnicas:
- Para o INEP, NUNCA carregue o arquivo inteiro em memória. Use leitura por chunks ou
  Polars/DuckDB, selecione só as colunas necessárias e salve em Parquet.
- Filtre os dados educacionais EXCLUSIVAMENTE para Computação, TI e Engenharias, usando
  a tabela de mapeamento de cursos fornecida/aprovada.
- Trate outliers salariais com método estatístico explícito (IQR ou percentis). Registre
  quantas linhas foram afetadas e por quê. Jamais descarte dados sem documentar.
- Harmonize as bases em categorias comuns: Ano, Região, Gênero, Faixa Salarial, Cargo.
  Como não há CPF para cruzar educação x mercado, o cruzamento é AGREGADO, não individual.

Saída esperada: arquivos Parquet + um relatório de qualidade (linhas, nulos, outliers
removidos, distribuições). Reporte qualquer anomalia ao Orquestrador.
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
            "salary": "salary", "total_yearly_compensation": "salary",
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
        inep_files = list(raw_dir.glob("*INEP*.*")) + list(raw_dir.glob("*inep*.*")) + list(raw_dir.glob("*microdados*.*"))
        salary_files = (
            list(raw_dir.glob("*salary*.*")) +
            list(raw_dir.glob("*salaries*.*")) +
            list(raw_dir.glob("*stackoverflow*.*")) +
            list(raw_dir.glob("*base_mercado*.*"))
        )

        if not inep_files and not salary_files:
            open_questions.append(
                "Nenhum arquivo bruto encontrado em data/raw/. "
                "Baixar microdados INEP de https://www.gov.br/inep e bases salariais do Kaggle/StackOverflow."
            )
            self.log_action("AVISO: data/raw/ vazio. ETL aguarda dados.")
        else:
            for f in inep_files:
                result = self.process_inep(str(f))
                artifacts.append({"type": "parquet", "path": result["path"], "source": "INEP"})

            for f in salary_files:
                source = "StackOverflow" if "stackoverflow" in f.name.lower() else "Kaggle"
                result = self.process_salaries(str(f), source=source)
                if not result.get("skipped"):
                    artifacts.append({"type": "parquet", "path": result["path"], "source": source})

        # Gera relatório de qualidade
        report_md = self.generate_quality_report_md()
        report_path = self.save_output("qualidade_dados_etl.md", report_md)
        artifacts.append({"type": "report", "path": str(report_path)})

        # LLM gera instruções de download se não há dados
        if not inep_files:
            instrucoes = self.ask_llm(
                "Gere instruções detalhadas passo a passo para baixar os microdados do "
                "Censo da Educação Superior INEP (últimos 5 anos) e as bases do Kaggle "
                "'Data Science and STEM Salaries' e do StackOverflow Developer Survey. "
                "Inclua links diretos, formato esperado dos arquivos e onde salvá-los."
            )
            instrucoes_path = self.save_output("instrucoes_download_dados.md", instrucoes)
            artifacts.append({"type": "instructions", "path": str(instrucoes_path)})

        return self.build_message(
            to_agent="modeling",
            task_id="T-001",
            status="done" if (inep_files or salary_files) else "needs_human_approval",
            artifacts=artifacts,
            assumptions=assumptions,
            open_questions=open_questions,
            needs_human_approval=bool(open_questions),
        )
