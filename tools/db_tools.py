"""Ferramentas de banco de dados — DuckDB com modelo estrela."""

import logging
from pathlib import Path

import duckdb

logger = logging.getLogger(__name__)

DDL_SCHEMA = """
-- ─── Dimensões ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS dim_tempo (
    ano          INTEGER PRIMARY KEY,
    decada       INTEGER,
    periodo      VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_regiao (
    co_regiao    INTEGER PRIMARY KEY,
    no_regiao    VARCHAR NOT NULL,
    sigla_regiao VARCHAR(2)
);

CREATE TABLE IF NOT EXISTS dim_genero (
    id_genero  INTEGER PRIMARY KEY,
    genero     VARCHAR NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_curso_tech (
    co_curso    INTEGER PRIMARY KEY,
    no_curso    VARCHAR NOT NULL,
    categoria   VARCHAR NOT NULL,
    eixo_inep   VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_cargo (
    id_cargo     INTEGER PRIMARY KEY,
    cargo_bruto  VARCHAR,
    cargo_std    VARCHAR NOT NULL,
    nivel        VARCHAR,
    eh_lideranca BOOLEAN DEFAULT FALSE
);

-- ─── Fatos (criados/populados pelo etl_pipeline.py — IF NOT EXISTS para não conflitar) ──

-- Funil acadêmico (referência INEP — dataset simulado)
CREATE TABLE IF NOT EXISTS fato_educacao_tech (
    ano                INTEGER,
    regiao             VARCHAR,
    co_regiao          INTEGER,
    area_geral         VARCHAR,
    qt_mat_fem         INTEGER,
    qt_mat_masc        INTEGER,
    qt_ing_fem         INTEGER,
    qt_ing_masc        INTEGER,
    qt_conc_fem        INTEGER,
    qt_conc_masc       INTEGER,
    qt_mat_total       INTEGER,
    qt_ing_total       INTEGER,
    qt_conc_total      INTEGER,
    pct_mat_fem        DOUBLE,
    pct_ing_fem        DOUBLE,
    pct_conc_fem       DOUBLE,
    tx_evasao_fem_pct  DOUBLE,
    tx_evasao_masc_pct DOUBLE
);

-- BASE PRINCIPAL: State of Data Brazil 2021 (dado real verificado)
CREATE TABLE IF NOT EXISTS fato_dados_2021 (
    genero           VARCHAR,
    cargo            VARCHAR,
    cargo_raw        VARCHAR,
    salario_midpoint DOUBLE,
    uf               VARCHAR,
    setor            VARCHAR,
    is_gestor        INTEGER,
    experiencia_raw  VARCHAR
);

-- Comparação global: WomenHack 2026 + Brasscom 2024/25 + McKinsey/LeanIn 2025
CREATE TABLE IF NOT EXISTS fato_mercado_mundial (
    cargo               VARCHAR,
    nivel               VARCHAR,
    genero              VARCHAR,
    regiao              VARCHAR,
    n                   INTEGER,
    salario_medio_brl   DOUBLE,
    salario_mediano_brl DOUBLE
);

-- D&I signal: vagas Generation LinkedIn
CREATE TABLE IF NOT EXISTS fato_vagas_linkedin (
    id          VARCHAR,
    empresa     VARCHAR,
    titulo      VARCHAR,
    nivel       VARCHAR,
    area_tech   VARCHAR,
    cidade      VARCHAR,
    uf          VARCHAR,
    remoto      VARCHAR,
    tipo_di     VARCHAR,
    eh_di       INTEGER,
    mes_ano     VARCHAR,
    inserted_at VARCHAR,
    descricao   VARCHAR
);

-- ─── Views analíticas (espelham etl_pipeline.py — CREATE OR REPLACE é idempotente) ──

CREATE OR REPLACE VIEW v_funil_nacional AS
SELECT ano, area_geral,
       SUM(qt_mat_fem)   AS total_mat_fem,
       SUM(qt_mat_masc)  AS total_mat_masc,
       SUM(qt_ing_fem)   AS total_ing_fem,
       SUM(qt_ing_masc)  AS total_ing_masc,
       SUM(qt_conc_fem)  AS total_conc_fem,
       SUM(qt_conc_masc) AS total_conc_masc,
       SUM(qt_mat_total) AS total_mat,
       ROUND(SUM(qt_mat_fem) * 100.0 / NULLIF(SUM(qt_mat_total),0), 2) AS pct_mat_fem,
       ROUND(SUM(qt_ing_fem) * 100.0 / NULLIF(SUM(qt_ing_total),0), 2) AS pct_ing_fem,
       ROUND(SUM(qt_conc_fem) * 100.0 / NULLIF(SUM(qt_conc_total),0), 2) AS pct_conc_fem,
       ROUND(AVG(tx_evasao_fem_pct), 2)  AS media_evasao_fem,
       ROUND(AVG(tx_evasao_masc_pct), 2) AS media_evasao_masc
FROM fato_educacao_tech
GROUP BY ano, area_geral
ORDER BY ano, area_geral;

CREATE OR REPLACE VIEW v_pay_gap AS
SELECT
    cargo, uf,
    AVG(CASE WHEN genero = 'Masculino' THEN salario_midpoint END) AS salario_medio_masc,
    AVG(CASE WHEN genero = 'Feminino'  THEN salario_midpoint END) AS salario_medio_fem,
    COUNT(CASE WHEN genero = 'Masculino' THEN 1 END) AS n_masc,
    COUNT(CASE WHEN genero = 'Feminino'  THEN 1 END) AS n_fem,
    ROUND(
        (AVG(CASE WHEN genero = 'Masculino' THEN salario_midpoint END) -
         AVG(CASE WHEN genero = 'Feminino'  THEN salario_midpoint END)) * 100.0 /
        NULLIF(AVG(CASE WHEN genero = 'Masculino' THEN salario_midpoint END), 0),
    2) AS pay_gap_pct
FROM fato_dados_2021
GROUP BY cargo, uf
HAVING COUNT(*) >= 5;

CREATE OR REPLACE VIEW v_lideranca_dados AS
SELECT
    cargo,
    COUNT(*) AS total,
    COUNT(CASE WHEN genero = 'Feminino' THEN 1 END) AS n_fem,
    ROUND(COUNT(CASE WHEN genero = 'Feminino' THEN 1 END) * 100.0 / NULLIF(COUNT(*), 0), 2) AS pct_fem
FROM fato_dados_2021
WHERE is_gestor = 1
GROUP BY cargo
ORDER BY pct_fem;

CREATE OR REPLACE VIEW v_pay_gap_global AS
SELECT
    cargo, regiao,
    MAX(CASE WHEN genero = 'Masculino' THEN salario_medio_brl END) AS salario_medio_masc,
    MAX(CASE WHEN genero = 'Feminino'  THEN salario_medio_brl END) AS salario_medio_fem,
    ROUND(
        (MAX(CASE WHEN genero = 'Masculino' THEN salario_medio_brl END) -
         MAX(CASE WHEN genero = 'Feminino'  THEN salario_medio_brl END)) * 100.0 /
        NULLIF(MAX(CASE WHEN genero = 'Masculino' THEN salario_medio_brl END), 0),
    2) AS pay_gap_pct
FROM fato_mercado_mundial
GROUP BY cargo, regiao;
"""


class DBTools:
    def __init__(self, db_path: str = "data/analytics.duckdb"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        return duckdb.connect(str(self.db_path))

    def create_schema(self) -> None:
        """Cria todo o schema estrela."""
        with self.get_connection() as con:
            for stmt in DDL_SCHEMA.split(";"):
                stmt = stmt.strip()
                if stmt:
                    con.execute(stmt)
        logger.info(f"Schema criado em {self.db_path}")

    def populate_dim_genero(self) -> None:
        with self.get_connection() as con:
            con.execute("""
                INSERT INTO dim_genero VALUES
                (1, 'Masculino'),
                (2, 'Feminino'),
                (3, 'Outro/Não informado')
                ON CONFLICT DO NOTHING
            """)

    def populate_dim_tempo(self, anos: list[int]) -> None:
        with self.get_connection() as con:
            for ano in anos:
                con.execute(
                    "INSERT INTO dim_tempo VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
                    [ano, (ano // 10) * 10, f"{ano}"]
                )

    def populate_dim_regiao(self) -> None:
        regioes = [
            (1, "Norte", "N"),
            (2, "Nordeste", "NE"),
            (3, "Sudeste", "SE"),
            (4, "Sul", "S"),
            (5, "Centro-Oeste", "CO"),
        ]
        with self.get_connection() as con:
            for r in regioes:
                con.execute("INSERT INTO dim_regiao VALUES (?, ?, ?) ON CONFLICT DO NOTHING", list(r))

    def query(self, sql: str) -> "duckdb.DuckDBPyRelation":
        con = self.get_connection()
        return con.execute(sql).df()
