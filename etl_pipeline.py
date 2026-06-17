"""
ETL Pipeline — People Analytics & DE&I
Lê os microdados reais do INEP (2019–2024) e a base de mercado tech brasil.
Produz Parquet e banco DuckDB prontos para análise.

Uso: python etl_pipeline.py
"""

import csv
import json
import logging
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("etl")

BASE   = Path(__file__).parent
RAW    = BASE / "data" / "raw"
OUT    = BASE / "data" / "treated"
DB     = BASE / "data" / "analytics.duckdb"
OUT.mkdir(parents=True, exist_ok=True)

# ─── Caminhos reais dos arquivos INEP ─────────────────────────────────────────

INEP_FILES = {
    2019: RAW / "microdados_censo_da_educacao_superior_2019" / "Microdados do Censo da Educação Superior 2019" / "dados" / "MICRODADOS_CADASTRO_CURSOS_2019.CSV",
    2020: RAW / "microdados_censo_da_educacao_superior_2020" / "Microdados do Censo da Educação Superior 2020" / "dados" / "MICRODADOS_CADASTRO_CURSOS_2020.CSV",
    2021: RAW / "microdados_censo_da_educacao_superior_2021" / "Microdados do Censo da Educação Superior 2021" / "dados" / "MICRODADOS_CADASTRO_CURSOS_2021.CSV",
    2022: RAW / "microdados_censo_da_educacao_superior_2022" / "microdados_educação_superior_2022" / "dados" / "MICRODADOS_CADASTRO_CURSOS_2022.CSV",
    2023: RAW / "microdados_censo_da_educacao_superior_2023" / "microdados_censo_da_educacao_superior_2023" / "dados" / "MICRODADOS_CADASTRO_CURSOS_2023.CSV",
    2024: RAW / "microdados_censo_da_educacao_superior_2024" / "microdados_censo_da_educacao_superior_2024" / "dados" / "MICRODADOS_CADASTRO_CURSOS_2024.CSV",
}

# Dataset simulado de mercado (Brasscom + State of Data Brazil + McKinsey)
MERCADO_FILE = RAW / "base_mercado_tech_brasil.csv"

# ─── Filtro de cursos Tech (via CINE) ─────────────────────────────────────────
# Valores confirmados inspecionando os arquivos reais do INEP

CINE_AREA_GERAL_TECH = {
    "Computação e Tecnologias da Informação e Comunicação (TIC)",
}

CINE_AREA_ESPECIFICA_ENGENHARIA_TECH = {
    "Engenharia e profissões correlatas",
}

# Colunas que vamos extrair de cada arquivo INEP
INEP_COLS = [
    "NU_ANO_CENSO", "NO_REGIAO", "CO_REGIAO",
    "NO_CURSO", "CO_CURSO",
    "NO_CINE_AREA_GERAL", "NO_CINE_AREA_ESPECIFICA",
    "TP_GRAU_ACADEMICO", "TP_MODALIDADE_ENSINO",
    "QT_MAT", "QT_MAT_FEM", "QT_MAT_MASC",
    "QT_ING", "QT_ING_FEM", "QT_ING_MASC",
    "QT_CONC", "QT_CONC_FEM", "QT_CONC_MASC",
]

# ─── Utilitários ──────────────────────────────────────────────────────────────

def to_int(val: str) -> int:
    try:
        return int(val.strip()) if val.strip() else 0
    except ValueError:
        return 0


def is_tech(row: dict) -> bool:
    area_geral = row.get("NO_CINE_AREA_GERAL", "").strip()
    area_esp   = row.get("NO_CINE_AREA_ESPECIFICA", "").strip()

    if area_geral in CINE_AREA_GERAL_TECH:
        return True
    if (area_geral == "Engenharia, produção e construção"
            and area_esp in CINE_AREA_ESPECIFICA_ENGENHARIA_TECH):
        return True
    return False


def _normalizar_genero(valor: str) -> str:
    v = valor.strip().upper()
    if v in ("F", "FEM", "FEMININO", "MULHER"):
        return "Feminino"
    if v in ("M", "MASC", "MASCULINO", "HOMEM"):
        return "Masculino"
    return valor.strip()


# ─── ETL INEP ─────────────────────────────────────────────────────────────────

def etl_inep() -> list[dict]:
    """
    Lê todos os anos INEP, filtra cursos Tech e retorna lista de dicts
    com métricas agregadas por Ano × Região × Curso × Gênero.
    """
    all_rows = []
    quality_log = []

    for ano, path in INEP_FILES.items():
        if not path.exists():
            logger.warning(f"Arquivo não encontrado: {path}")
            continue

        logger.info(f"Processando INEP {ano} ({path.stat().st_size / 1e6:.1f} MB)...")

        total = 0
        kept  = 0

        with open(path, encoding="latin1") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                total += 1
                if not is_tech(row):
                    continue
                kept += 1

                record = {
                    "ano":            to_int(row.get("NU_ANO_CENSO", "")),
                    "regiao":         row.get("NO_REGIAO", "").strip(),
                    "co_regiao":      to_int(row.get("CO_REGIAO", "")),
                    "no_curso":       row.get("NO_CURSO", "").strip(),
                    "co_curso":       to_int(row.get("CO_CURSO", "")),
                    "area_geral":     row.get("NO_CINE_AREA_GERAL", "").strip(),
                    "area_especifica":row.get("NO_CINE_AREA_ESPECIFICA", "").strip(),
                    "grau_academico": to_int(row.get("TP_GRAU_ACADEMICO", "")),
                    "modalidade":     to_int(row.get("TP_MODALIDADE_ENSINO", "")),
                    # Matrículas
                    "qt_mat":         to_int(row.get("QT_MAT", "")),
                    "qt_mat_fem":     to_int(row.get("QT_MAT_FEM", "")),
                    "qt_mat_masc":    to_int(row.get("QT_MAT_MASC", "")),
                    # Ingressantes
                    "qt_ing":         to_int(row.get("QT_ING", "")),
                    "qt_ing_fem":     to_int(row.get("QT_ING_FEM", "")),
                    "qt_ing_masc":    to_int(row.get("QT_ING_MASC", "")),
                    # Concluintes
                    "qt_conc":        to_int(row.get("QT_CONC", "")),
                    "qt_conc_fem":    to_int(row.get("QT_CONC_FEM", "")),
                    "qt_conc_masc":   to_int(row.get("QT_CONC_MASC", "")),
                }
                all_rows.append(record)

        pct_kept = kept / total * 100 if total else 0
        quality_log.append({
            "ano": ano,
            "total_cursos": total,
            "cursos_tech": kept,
            "pct_tech": round(pct_kept, 2),
        })
        logger.info(f"  INEP {ano}: {kept:,} cursos Tech de {total:,} total ({pct_kept:.1f}%)")

    # Salva log de qualidade
    with open(OUT / "qualidade_inep.json", "w", encoding="utf-8") as f:
        json.dump(quality_log, f, ensure_ascii=False, indent=2)

    return all_rows


# ─── ETL Base de Mercado Tech Brasil ──────────────────────────────────────────
# Fonte: dataset simulado com referências Brasscom (salario_base),
#        State of Data Brazil (cargos/níveis) e McKinsey (promoção/retenção).
# Possui coluna de gênero: pay gap é calculável diretamente.

def etl_mercado_brasil() -> list[dict]:
    """
    Lê base_mercado_tech_brasil.csv — dataset simulado pedagogicamente.
    Gap salarial de ~27% entre gêneros embutido (ref. Brasscom).
    Gargalo de liderança feminina em Diretoria/CTO embutido (ref. McKinsey).
    """
    rows = []

    if not MERCADO_FILE.exists():
        logger.warning(f"Base de mercado não encontrada: {MERCADO_FILE}")
        return rows

    logger.info(f"Processando base de mercado ({MERCADO_FILE.stat().st_size / 1e6:.1f} MB)...")

    salaries = []
    with open(MERCADO_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Tenta múltiplos nomes de coluna de salário
            sal = 0.0
            for col in ["salario_base", "salario", "salary", "salary_in_usd"]:
                try:
                    val = row.get(col, 0) or 0
                    sal = float(str(val).replace(",", "."))
                    if sal > 0:
                        break
                except (ValueError, TypeError):
                    continue

            if sal <= 0:
                continue

            salaries.append(sal)
            rows.append({
                "cargo":            row.get("cargo", row.get("job_title", "")).strip(),
                "nivel":            row.get("nivel_hierarquico", row.get("nivel", row.get("experience_level", ""))).strip(),
                "genero":           _normalizar_genero(row.get("genero", row.get("gender", ""))),
                "regiao":           row.get("regiao", row.get("region", "Brasil")).strip(),
                "anos_experiencia": to_int(row.get("anos_experiencia", row.get("years_experience", "0"))),
                "salario_base":     sal,
            })

    if not salaries:
        logger.warning("Base de mercado vazia ou sem coluna de salário reconhecida.")
        return rows

    # Winsorização p99
    salaries_sorted = sorted(salaries)
    n = len(salaries_sorted)
    p1_idx  = max(0, int(0.01 * n))
    p99_idx = min(n - 1, int(0.99 * n))
    p1  = salaries_sorted[p1_idx]
    p99 = salaries_sorted[p99_idx]

    winsorized = 0
    for r in rows:
        if r["salario_base"] > p99:
            r["salario_base"] = p99
            winsorized += 1
        elif r["salario_base"] < p1:
            r["salario_base"] = p1
            winsorized += 1

    n_fem  = sum(1 for r in rows if r["genero"] == "Feminino")
    n_masc = sum(1 for r in rows if r["genero"] == "Masculino")
    logger.info(f"  Base mercado: {len(rows):,} linhas | p01=R${p1:,.0f} | p99=R${p99:,.0f} | winsorized={winsorized}")
    logger.info(f"  Gêneros — Feminino: {n_fem:,} | Masculino: {n_masc:,}")

    with open(OUT / "qualidade_mercado.json", "w", encoding="utf-8") as f:
        json.dump({
            "dataset": "base_mercado_tech_brasil.csv",
            "tipo": "dataset_simulado",
            "total_linhas": len(rows),
            "p01_brl": p1,
            "p99_brl": p99,
            "linhas_winsorized": winsorized,
            "n_feminino": n_fem,
            "n_masculino": n_masc,
            "possui_coluna_genero": True,
            "gap_salarial_esperado_pct": 27,
            "fontes_metodologia": {
                "salario_base": "Brasscom — Relatório de Mercado TIC (~27% gap intencional entre gêneros)",
                "cargos_e_niveis": "State of Data Brazil",
                "logica_promocao": "McKinsey Women in the Workplace (gargalo Diretoria/CTO)"
            },
        }, f, ensure_ascii=False, indent=2)

    return rows


# ─── Agregações e cálculos ────────────────────────────────────────────────────

def aggregate_inep(rows: list[dict]) -> list[dict]:
    """Agrega por Ano × Região × ÁreaCINE (para o dashboard)."""
    from collections import defaultdict

    agg: dict[tuple, dict] = defaultdict(lambda: {
        "qt_mat_fem": 0, "qt_mat_masc": 0,
        "qt_ing_fem": 0, "qt_ing_masc": 0,
        "qt_conc_fem": 0, "qt_conc_masc": 0,
    })

    for r in rows:
        key = (r["ano"], r["regiao"], r["co_regiao"], r["area_geral"])
        for m in ["qt_mat_fem","qt_mat_masc","qt_ing_fem","qt_ing_masc","qt_conc_fem","qt_conc_masc"]:
            agg[key][m] += r[m]

    result = []
    for (ano, regiao, co_regiao, area_geral), vals in agg.items():
        tot_mat  = vals["qt_mat_fem"]  + vals["qt_mat_masc"]
        tot_ing  = vals["qt_ing_fem"]  + vals["qt_ing_masc"]
        tot_conc = vals["qt_conc_fem"] + vals["qt_conc_masc"]

        pct_mat_fem  = round(vals["qt_mat_fem"]  / tot_mat  * 100, 2) if tot_mat  > 0 else 0
        pct_ing_fem  = round(vals["qt_ing_fem"]  / tot_ing  * 100, 2) if tot_ing  > 0 else 0
        pct_conc_fem = round(vals["qt_conc_fem"] / tot_conc * 100, 2) if tot_conc > 0 else 0

        # Taxa de evasão = (ingressantes - concluintes) / ingressantes
        tx_evasao_fem  = round((vals["qt_ing_fem"]  - vals["qt_conc_fem"])  / vals["qt_ing_fem"]  * 100, 2) if vals["qt_ing_fem"]  > 0 else None
        tx_evasao_masc = round((vals["qt_ing_masc"] - vals["qt_conc_masc"]) / vals["qt_ing_masc"] * 100, 2) if vals["qt_ing_masc"] > 0 else None

        result.append({
            "ano": ano, "regiao": regiao, "co_regiao": co_regiao, "area_geral": area_geral,
            **vals,
            "qt_mat_total": tot_mat, "qt_ing_total": tot_ing, "qt_conc_total": tot_conc,
            "pct_mat_fem": pct_mat_fem, "pct_ing_fem": pct_ing_fem, "pct_conc_fem": pct_conc_fem,
            "tx_evasao_fem_pct": tx_evasao_fem, "tx_evasao_masc_pct": tx_evasao_masc,
        })

    return sorted(result, key=lambda r: (r["ano"], r["regiao"]))


def aggregate_mercado(rows: list[dict]) -> list[dict]:
    """Agrega salários por cargo × nível × gênero × região para análise de pay gap."""
    from collections import defaultdict

    agg: dict[tuple, list] = defaultdict(list)
    for r in rows:
        key = (r["cargo"], r["nivel"], r["genero"], r["regiao"])
        agg[key].append(r["salario_base"])

    result = []
    for (cargo, nivel, genero, regiao), sals in agg.items():
        sals_sorted = sorted(sals)
        n = len(sals_sorted)
        media   = sum(sals_sorted) / n
        mediana = sals_sorted[n // 2]
        result.append({
            "cargo":               cargo,
            "nivel":               nivel,
            "genero":              genero,
            "regiao":              regiao,
            "n":                   n,
            "salario_medio_brl":   round(media, 2),
            "salario_mediano_brl": round(mediana, 2),
        })

    return sorted(result, key=lambda r: (-r["n"], r["cargo"]))


# ─── Persistência em DuckDB ───────────────────────────────────────────────────

def save_to_duckdb(inep_agg: list[dict], mercado_agg: list[dict]) -> None:
    import duckdb

    con = duckdb.connect(str(DB))

    # ─── Tabela INEP agregada
    con.execute("DROP TABLE IF EXISTS fato_educacao_tech")
    con.execute("""
        CREATE TABLE fato_educacao_tech (
            ano               INTEGER,
            regiao            VARCHAR,
            co_regiao         INTEGER,
            area_geral        VARCHAR,
            qt_mat_fem        INTEGER,
            qt_mat_masc       INTEGER,
            qt_ing_fem        INTEGER,
            qt_ing_masc       INTEGER,
            qt_conc_fem       INTEGER,
            qt_conc_masc      INTEGER,
            qt_mat_total      INTEGER,
            qt_ing_total      INTEGER,
            qt_conc_total     INTEGER,
            pct_mat_fem       DOUBLE,
            pct_ing_fem       DOUBLE,
            pct_conc_fem      DOUBLE,
            tx_evasao_fem_pct DOUBLE,
            tx_evasao_masc_pct DOUBLE
        )
    """)
    for r in inep_agg:
        con.execute("""
            INSERT INTO fato_educacao_tech VALUES (
                ?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?
            )
        """, [
            r["ano"], r["regiao"], r["co_regiao"], r["area_geral"],
            r["qt_mat_fem"], r["qt_mat_masc"],
            r["qt_ing_fem"], r["qt_ing_masc"],
            r["qt_conc_fem"], r["qt_conc_masc"],
            r["qt_mat_total"], r["qt_ing_total"], r["qt_conc_total"],
            r["pct_mat_fem"], r["pct_ing_fem"], r["pct_conc_fem"],
            r["tx_evasao_fem_pct"], r["tx_evasao_masc_pct"],
        ])

    # ─── Tabela de mercado (base_mercado_tech_brasil.csv — Brasscom + State of Data + McKinsey)
    con.execute("DROP TABLE IF EXISTS fato_mercado_tech_brasil")
    con.execute("""
        CREATE TABLE fato_mercado_tech_brasil (
            cargo              VARCHAR,
            nivel              VARCHAR,
            genero             VARCHAR,
            regiao             VARCHAR,
            n                  INTEGER,
            salario_medio_brl  DOUBLE,
            salario_mediano_brl DOUBLE
        )
    """)
    for r in mercado_agg:
        con.execute(
            "INSERT INTO fato_mercado_tech_brasil VALUES (?,?,?,?,?,?,?)",
            [r["cargo"], r["nivel"], r["genero"], r["regiao"],
             r["n"], r["salario_medio_brl"], r["salario_mediano_brl"]]
        )

    # ─── Views analíticas
    con.execute("""
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
        ORDER BY ano, area_geral
    """)

    con.execute("""
        CREATE OR REPLACE VIEW v_funil_por_regiao AS
        SELECT ano, regiao, area_geral,
               SUM(qt_mat_fem) AS total_mat_fem,
               SUM(qt_mat_total) AS total_mat,
               ROUND(SUM(qt_mat_fem) * 100.0 / NULLIF(SUM(qt_mat_total),0), 2) AS pct_mat_fem,
               ROUND(SUM(qt_conc_fem) * 100.0 / NULLIF(SUM(qt_conc_total),0), 2) AS pct_conc_fem,
               ROUND(AVG(tx_evasao_fem_pct), 2) AS media_evasao_fem
        FROM fato_educacao_tech
        GROUP BY ano, regiao, area_geral
        ORDER BY ano, regiao
    """)

    con.execute("""
        CREATE OR REPLACE VIEW v_pay_gap AS
        SELECT
            cargo, nivel, regiao,
            MAX(CASE WHEN genero = 'Masculino' THEN salario_medio_brl END) AS salario_medio_masc,
            MAX(CASE WHEN genero = 'Feminino'  THEN salario_medio_brl END) AS salario_medio_fem,
            ROUND(
                (MAX(CASE WHEN genero = 'Masculino' THEN salario_medio_brl END) -
                 MAX(CASE WHEN genero = 'Feminino'  THEN salario_medio_brl END)) * 100.0 /
                NULLIF(MAX(CASE WHEN genero = 'Masculino' THEN salario_medio_brl END), 0),
            2) AS pay_gap_pct
        FROM fato_mercado_tech_brasil
        GROUP BY cargo, nivel, regiao
        ORDER BY pay_gap_pct DESC
    """)

    n_edu    = con.execute("SELECT COUNT(*) FROM fato_educacao_tech").fetchone()[0]
    n_merc   = con.execute("SELECT COUNT(*) FROM fato_mercado_tech_brasil").fetchone()[0]
    con.close()

    logger.info(f"DuckDB salvo em {DB}")
    logger.info(f"  fato_educacao_tech: {n_edu:,} linhas")
    logger.info(f"  fato_mercado_tech_brasil: {n_merc:,} linhas")


# ─── Salva CSV consolidado ────────────────────────────────────────────────────

def save_csv(rows: list[dict], name: str) -> Path:
    if not rows:
        return OUT / f"{name}.csv"
    path = OUT / f"{name}.csv"
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    logger.info(f"CSV salvo: {path} ({len(rows):,} linhas)")
    return path


# ─── Relatório de métricas-chave ─────────────────────────────────────────────

def print_key_metrics(inep_agg: list[dict], mercado_agg: list[dict]) -> None:
    print("\n" + "="*60)
    print("  MÉTRICAS-CHAVE — FUNIL DA MULHER NA TECH")
    print("="*60)

    # Agrupa por ano (nacional, TIC)
    tic = [r for r in inep_agg if "Computa" in r["area_geral"]]
    anos = sorted(set(r["ano"] for r in tic))

    for ano in anos:
        ano_rows = [r for r in tic if r["ano"] == ano]
        mat_fem  = sum(r["qt_mat_fem"]  for r in ano_rows)
        mat_tot  = sum(r["qt_mat_total"] for r in ano_rows)
        ing_fem  = sum(r["qt_ing_fem"]  for r in ano_rows)
        ing_tot  = sum(r["qt_ing_total"] for r in ano_rows)
        conc_fem = sum(r["qt_conc_fem"] for r in ano_rows)
        conc_tot = sum(r["qt_conc_total"] for r in ano_rows)

        pct_mat  = mat_fem  / mat_tot  * 100 if mat_tot  > 0 else 0
        pct_ing  = ing_fem  / ing_tot  * 100 if ing_tot  > 0 else 0
        pct_conc = conc_fem / conc_tot * 100 if conc_tot > 0 else 0

        print(f"\n  {ano} | TIC (Computação e TIC):")
        print(f"    Matrículas:   {mat_tot:>8,} total | {mat_fem:>7,} fem ({pct_mat:.1f}%)")
        print(f"    Ingressantes: {ing_tot:>8,} total | {ing_fem:>7,} fem ({pct_ing:.1f}%)")
        print(f"    Concluintes:  {conc_tot:>8,} total | {conc_fem:>7,} fem ({pct_conc:.1f}%)")

    # Pay gap na base de mercado
    if mercado_agg:
        fem_sals  = [r["salario_medio_brl"] for r in mercado_agg if r["genero"] == "Feminino"]
        masc_sals = [r["salario_medio_brl"] for r in mercado_agg if r["genero"] == "Masculino"]
        if fem_sals and masc_sals:
            media_fem  = sum(fem_sals)  / len(fem_sals)
            media_masc = sum(masc_sals) / len(masc_sals)
            gap_pct    = (media_masc - media_fem) / media_masc * 100 if media_masc > 0 else 0
            print(f"\n  PAY GAP (base de mercado tech brasil):")
            print(f"    Salário médio Masculino: R${media_masc:,.0f}")
            print(f"    Salário médio Feminino:  R${media_fem:,.0f}")
            print(f"    Gap salarial: {gap_pct:.1f}%  (esperado ~27% — ref. Brasscom)")

    print("="*60 + "\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Iniciando ETL Pipeline — People Analytics & DE&I")

    # 1. Lê e filtra dados brutos
    inep_rows    = etl_inep()
    mercado_rows = etl_mercado_brasil()

    # 2. Agrega
    logger.info("Agregando dados INEP...")
    inep_agg    = aggregate_inep(inep_rows)
    mercado_agg = aggregate_mercado(mercado_rows)

    # 3. Persiste
    logger.info("Salvando CSVs...")
    save_csv(inep_agg,    "fato_educacao_tech_agregado")
    save_csv(mercado_agg, "fato_mercado_tech_brasil")

    logger.info("Salvando no DuckDB...")
    save_to_duckdb(inep_agg, mercado_agg)

    # 4. Mostra métricas
    print_key_metrics(inep_agg, mercado_agg)

    logger.info("ETL concluído. Próximo passo: python analise.py")
