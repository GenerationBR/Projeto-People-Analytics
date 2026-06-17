"""Ferramentas de ETL para processamento de bases pesadas (INEP, RAIS, Kaggle)."""

import json
import logging
from pathlib import Path
from typing import Optional

import duckdb
import polars as pl
import numpy as np

logger = logging.getLogger(__name__)


class ETLTools:
    def __init__(self, config_dir: str = "config", data_dir: str = "data"):
        self.config_dir = Path(config_dir)
        self.raw_dir = Path(data_dir) / "raw"
        self.treated_dir = Path(data_dir) / "treated"
        self.treated_dir.mkdir(parents=True, exist_ok=True)

        with open(self.config_dir / "course_mapping.json", encoding="utf-8") as f:
            self.course_mapping = json.load(f)

        with open(self.config_dir / "premises.json", encoding="utf-8") as f:
            self.premises = json.load(f)

    # ─── INEP ─────────────────────────────────────────────────────────────────

    def load_inep_chunked(self, filepath: str, chunk_size: int = 500_000) -> pl.DataFrame:
        """Lê microdados INEP em chunks para evitar estourar memória."""
        path = Path(filepath)
        logger.info(f"Lendo INEP em chunks: {path.name}")

        cols_needed = [
            "NU_ANO_CENSO",
            "CO_REGIAO",
            "NO_REGIAO",
            "CO_UF",
            "TP_SEXO",
            "CO_CURSO",
            "NO_CURSO",
            "CO_CINE_ROTULO",
            "NO_CINE_ROTULO",
            "IN_INGRESSO",
            "IN_CONCLUINTE",
            "IN_MATRICULA",
        ]

        sep = ";" if path.suffix.lower() == ".csv" else ","
        frames = []

        reader = pl.read_csv_batched(
            path,
            separator=sep,
            columns=cols_needed,
            infer_schema_length=0,
            batch_size=chunk_size,
            encoding="latin1",
            ignore_errors=True,
        )

        while True:
            batch = reader.next_batches(1)
            if not batch:
                break
            frames.append(batch[0])

        df = pl.concat(frames)
        logger.info(f"INEP carregado: {df.shape[0]:,} linhas")
        return df

    def filter_tech_courses(self, df: pl.DataFrame) -> pl.DataFrame:
        """Filtra somente cursos de Computação, TI e Engenharias Tech."""
        all_tech_names = [
            name
            for group in self.course_mapping["cursos_incluidos"].values()
            for name in group
        ]
        excluded = self.course_mapping["cursos_excluidos_explicitamente"]

        filtered = df.filter(
            pl.col("NO_CURSO").str.contains_any(all_tech_names, ascii_case_insensitive=True)
            & ~pl.col("NO_CURSO").str.contains_any(excluded, ascii_case_insensitive=True)
        )

        removed = df.shape[0] - filtered.shape[0]
        logger.info(f"Filtro Tech: {filtered.shape[0]:,} mantidos, {removed:,} removidos")
        return filtered

    def harmonize_gender(self, df: pl.DataFrame, col: str = "TP_SEXO") -> pl.DataFrame:
        """Padroniza coluna de gênero para 'Feminino'/'Masculino'."""
        fem_vals = self.premises["premissas"]["genero"]["valores_feminino"]
        masc_vals = self.premises["premissas"]["genero"]["valores_masculino"]

        return df.with_columns(
            pl.when(pl.col(col).cast(str).is_in(fem_vals))
            .then(pl.lit("Feminino"))
            .when(pl.col(col).cast(str).is_in(masc_vals))
            .then(pl.lit("Masculino"))
            .otherwise(pl.lit("Outro/Não informado"))
            .alias("genero")
        )

    # ─── Outliers salariais ────────────────────────────────────────────────────

    def treat_salary_outliers(
        self,
        df: pl.DataFrame,
        salary_col: str = "salary",
        method: str = "winsorization_p99",
    ) -> tuple[pl.DataFrame, dict]:
        """
        Remove/winsoriza outliers salariais.
        Retorna o DataFrame tratado + log detalhado do que foi alterado.
        """
        original_count = df.shape[0]
        report = {"metodo": method, "coluna": salary_col}

        salary = df[salary_col].cast(pl.Float64, strict=False).drop_nulls()
        p1 = salary.quantile(0.01)
        p99 = salary.quantile(0.99)
        report["p01"] = float(p1)
        report["p99"] = float(p99)

        if method == "winsorization_p99":
            affected = df.filter(
                (pl.col(salary_col).cast(pl.Float64) > p99)
                | (pl.col(salary_col).cast(pl.Float64) < p1)
            ).shape[0]
            df = df.with_columns(
                pl.col(salary_col)
                .cast(pl.Float64)
                .clip(p1, p99)
                .alias(salary_col)
            )
            report["linhas_afetadas"] = affected
            report["acao"] = f"Valores clampados para [{p1:.2f}, {p99:.2f}]"
        elif method == "iqr_removal":
            q1 = salary.quantile(0.25)
            q3 = salary.quantile(0.75)
            iqr = q3 - q1
            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr
            before = df.shape[0]
            df = df.filter(
                pl.col(salary_col).cast(pl.Float64).is_between(lower, upper)
            )
            report["linhas_removidas"] = before - df.shape[0]
            report["acao"] = f"Linhas fora de [{lower:.2f}, {upper:.2f}] removidas"

        report["total_original"] = original_count
        report["total_final"] = df.shape[0]
        logger.info(f"Outliers tratados: {report}")
        return df, report

    # ─── Persistência ──────────────────────────────────────────────────────────

    def save_parquet(self, df: pl.DataFrame, name: str) -> Path:
        """Salva DataFrame como Parquet comprimido."""
        path = self.treated_dir / f"{name}.parquet"
        df.write_parquet(path, compression="snappy")
        logger.info(f"Salvo: {path} ({path.stat().st_size / 1024:.1f} KB)")
        return path

    def load_parquet(self, name: str) -> pl.DataFrame:
        path = self.treated_dir / f"{name}.parquet"
        return pl.read_parquet(path)

    # ─── Relatório de qualidade ────────────────────────────────────────────────

    def quality_report(self, df: pl.DataFrame, name: str) -> dict:
        """Gera relatório de qualidade de dados."""
        report = {
            "tabela": name,
            "linhas": df.shape[0],
            "colunas": df.shape[1],
            "nulos_por_coluna": {
                col: int(df[col].null_count())
                for col in df.columns
                if df[col].null_count() > 0
            },
            "tipos": {col: str(df[col].dtype) for col in df.columns},
        }
        return report
