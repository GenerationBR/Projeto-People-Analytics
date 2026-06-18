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
    categoria   VARCHAR NOT NULL,  -- ex: "Computação", "Engenharia Tech"
    eixo_inep   VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_cargo (
    id_cargo    INTEGER PRIMARY KEY,
    cargo_bruto VARCHAR,
    cargo_std   VARCHAR NOT NULL,  -- cargo padronizado
    nivel       VARCHAR,           -- Junior, Pleno, Senior, Staff, C-Level
    eh_lideranca BOOLEAN DEFAULT FALSE
);

-- ─── Fatos ──────────────────────────────────────────────────────────────────

-- Escopo ACADÊMICO (INEP)
CREATE TABLE IF NOT EXISTS fato_educacao (
    id           BIGINT PRIMARY KEY,
    ano          INTEGER REFERENCES dim_tempo(ano),
    co_regiao    INTEGER REFERENCES dim_regiao(co_regiao),
    id_genero    INTEGER REFERENCES dim_genero(id_genero),
    co_curso     INTEGER REFERENCES dim_curso_tech(co_curso),
    qt_matriculas   INTEGER DEFAULT 0,
    qt_ingressantes INTEGER DEFAULT 0,
    qt_concluintes  INTEGER DEFAULT 0,
    qt_evasao       INTEGER DEFAULT 0,
    tx_evasao       DOUBLE PRECISION
);

-- Escopo PROFISSIONAL (base_mercado_tech_brasil.csv — Brasscom + State of Data + McKinsey)
CREATE TABLE IF NOT EXISTS fato_mercado (
    id             BIGINT PRIMARY KEY,
    ano            INTEGER REFERENCES dim_tempo(ano),
    co_regiao      INTEGER REFERENCES dim_regiao(co_regiao),
    id_genero      INTEGER REFERENCES dim_genero(id_genero),
    id_cargo       INTEGER REFERENCES dim_cargo(id_cargo),
    faixa_salarial VARCHAR,
    qt_empregados  INTEGER DEFAULT 0,
    salario_medio  DOUBLE PRECISION,
    salario_mediano DOUBLE PRECISION,
    fonte          VARCHAR  -- "base_mercado_tech_brasil" (Brasscom+StateOfData+McKinsey)
);

-- ─── Views de consumo BI ────────────────────────────────────────────────────

CREATE OR REPLACE VIEW v_funil_educacao AS
SELECT
    t.ano,
    r.no_regiao,
    g.genero,
    c.categoria,
    SUM(fe.qt_matriculas)   AS total_matriculas,
    SUM(fe.qt_concluintes)  AS total_concluintes,
    SUM(fe.qt_evasao)       AS total_evasao,
    ROUND(AVG(fe.tx_evasao) * 100, 2) AS tx_evasao_pct
FROM fato_educacao fe
JOIN dim_tempo t   ON t.ano       = fe.ano
JOIN dim_regiao r  ON r.co_regiao = fe.co_regiao
JOIN dim_genero g  ON g.id_genero = fe.id_genero
JOIN dim_curso_tech c ON c.co_curso = fe.co_curso
GROUP BY 1, 2, 3, 4;

CREATE OR REPLACE VIEW v_pay_gap AS
SELECT
    t.ano,
    r.no_regiao,
    ca.cargo_std,
    ca.nivel,
    MAX(CASE WHEN g.genero = 'Masculino' THEN fm.salario_medio END) AS salario_medio_masc,
    MAX(CASE WHEN g.genero = 'Feminino'  THEN fm.salario_medio END) AS salario_medio_fem,
    ROUND(
        (MAX(CASE WHEN g.genero = 'Masculino' THEN fm.salario_medio END) -
         MAX(CASE WHEN g.genero = 'Feminino'  THEN fm.salario_medio END))
        / NULLIF(MAX(CASE WHEN g.genero = 'Masculino' THEN fm.salario_medio END), 0) * 100,
        2
    ) AS pay_gap_pct
FROM fato_mercado fm
JOIN dim_tempo   t  ON t.ano       = fm.ano
JOIN dim_regiao  r  ON r.co_regiao = fm.co_regiao
JOIN dim_genero  g  ON g.id_genero = fm.id_genero
JOIN dim_cargo  ca  ON ca.id_cargo = fm.id_cargo
GROUP BY 1, 2, 3, 4;

CREATE OR REPLACE VIEW v_lideranca AS
SELECT
    t.ano,
    r.no_regiao,
    g.genero,
    SUM(fm.qt_empregados) AS qt_empregados,
    ROUND(
        SUM(fm.qt_empregados) * 100.0 /
        NULLIF(SUM(SUM(fm.qt_empregados)) OVER (PARTITION BY t.ano, r.no_regiao, ca.cargo_std), 0),
        2
    ) AS pct_genero
FROM fato_mercado fm
JOIN dim_tempo  t  ON t.ano       = fm.ano
JOIN dim_regiao r  ON r.co_regiao = fm.co_regiao
JOIN dim_genero g  ON g.id_genero = fm.id_genero
JOIN dim_cargo ca  ON ca.id_cargo = fm.id_cargo
WHERE ca.eh_lideranca = TRUE
GROUP BY 1, 2, 3, ca.cargo_std;
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
