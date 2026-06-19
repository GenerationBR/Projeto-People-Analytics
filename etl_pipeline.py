"""
ETL Pipeline — People Analytics & DE&I
Foco: Desigualdade de gênero na área de DADOS (nicho tech no Brasil).

Fontes dos dados raw:
  - base_mercado_dados_2021_brasil.csv → State of Data Brazil 2021 (Data Hackers / Bain & Co.)
                                          Dado REAL verificado — BASE PRINCIPAL DA ANÁLISE.
                                          Mercado nacional de dados: salários, cargos, experiência.
  - base_mercado_tech_mundial.csv      → Compilado: WomenHack (2026) + Brasscom (2024/25)
                                          + McKinsey/LeanIn Women in the Workplace (2025).
                                          Usado apenas para comparações globais (pay gap, liderança).
  - base_campus_ti_brasil.csv         → INEP — Censo da Educação Superior (dataset simulado).
                                          Funil acadêmico: ~18–21% mulheres em Computação.
  - generation_linkedin_vagas_tecnologia.csv → Vagas coletadas pela Generation (D&I signal).

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

# ─── Caminhos dos arquivos raw ────────────────────────────────────────────────

CAMPUS_FILE    = RAW / "base_campus_ti_brasil.csv"                 # INEP (simulado)
MERCADO_FILE   = RAW / "base_mercado_tech_mundial.csv"             # Global: WomenHack + Brasscom + McKinsey
DADOS_2021_FILE = RAW / "base_mercado_dados_2021_brasil.csv"       # State of Data Brazil 2021 (REAL)
LINKEDIN_FILE  = RAW / "generation_linkedin_vagas_tecnologia.csv"  # Vagas Generation

# ─── Mapeamento instituição → região ──────────────────────────────────────────
# O dataset simulado cobre instituições do eixo Sudeste.
# Premissa documentada: campus mock não possui cobertura regional completa.

INST_TO_REGIAO: dict[str, tuple[str, int]] = {
    "USP":    ("Sudeste", 3),
    "UFRJ":   ("Sudeste", 3),
    "UFMG":   ("Sudeste", 3),
    "PUC-SP": ("Sudeste", 3),
    "FIAP":   ("Sudeste", 3),
    "FATEC":  ("Sudeste", 3),
    "Insper": ("Sudeste", 3),
}

AREA_GERAL_TIC = "Computação e Tecnologias da Informação e Comunicação (TIC)"


# ─── Utilitários ──────────────────────────────────────────────────────────────

def to_int(val: str) -> int:
    try:
        return int(val.strip()) if str(val).strip() else 0
    except (ValueError, TypeError):
        return 0


def _normalizar_genero(valor: str) -> str:
    v = str(valor).strip().upper()
    if v in ("F", "FEM", "FEMININO", "MULHER"):
        return "Feminino"
    if v in ("M", "MASC", "MASCULINO", "HOMEM"):
        return "Masculino"
    return str(valor).strip()


# ─── ETL Campus TI (base_campus_ti_brasil.csv — referência INEP) ─────────────
# Cada linha representa um estudante individualmente.
# Campos: id_estudante, genero, curso, instituicao, ano_ingresso, concluiu, trabalha_na_area
# Premissa: ingressante = 1 por linha; concluinte = linha onde concluiu = 1.
# Matrículas são aproximadas como ingressantes (mock não tem histórico anual de matrícula).

def etl_campus() -> list[dict]:
    """
    Lê base_campus_ti_brasil.csv — dataset simulado com base no INEP.
    Retorna lista de dicts com dados individuais por estudante.
    """
    rows = []

    if not CAMPUS_FILE.exists():
        logger.warning(f"Campus TI não encontrado: {CAMPUS_FILE}")
        return rows

    logger.info(f"Processando campus TI ({CAMPUS_FILE.stat().st_size / 1024:.1f} KB)...")

    with open(CAMPUS_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            inst = row.get("instituicao", "").strip()
            regiao, co_regiao = INST_TO_REGIAO.get(inst, ("Sudeste", 3))
            genero = _normalizar_genero(row.get("genero", ""))
            rows.append({
                "genero":        genero,
                "curso":         row.get("curso", "").strip(),
                "instituicao":   inst,
                "ano":           to_int(row.get("ano_ingresso", "")),
                "concluiu":      to_int(row.get("concluiu", "0")),
                "trabalha_area": to_int(row.get("trabalha_na_area", "0")),
                "regiao":        regiao,
                "co_regiao":     co_regiao,
                "area_geral":    AREA_GERAL_TIC,
            })

    n_fem  = sum(1 for r in rows if r["genero"] == "Feminino")
    n_masc = sum(1 for r in rows if r["genero"] == "Masculino")
    n_conc = sum(1 for r in rows if r["concluiu"] == 1)
    pct_fem = round(n_fem / len(rows) * 100, 2) if rows else 0

    logger.info(f"  Campus TI: {len(rows):,} estudantes | {n_fem} fem ({pct_fem}%) | {n_conc} concluíram")

    # Salva log de qualidade
    quality = {
        "dataset":          "base_campus_ti_brasil.csv",
        "tipo":             "dataset_mockado",
        "fonte_referencia": "INEP — Censo da Educação Superior",
        "total_estudantes": len(rows),
        "n_feminino":       n_fem,
        "n_masculino":      n_masc,
        "pct_feminino":     pct_fem,
        "n_concluintes":    n_conc,
        "pct_conclusao":    round(n_conc / len(rows) * 100, 2) if rows else 0,
        "instituicoes":     sorted(set(r["instituicao"] for r in rows)),
        "anos_cobertura":   sorted(set(r["ano"] for r in rows)),
        "nota_cobertura":   "Dataset simulado abrange instituições do Sudeste. Sem cobertura regional múltipla.",
        "nota_matriculas":  "Matrículas ≈ ingressantes (dado simplificado; mock não tem histórico anual de matrícula).",
    }
    with open(OUT / "qualidade_inep.json", "w", encoding="utf-8") as f:
        json.dump(quality, f, ensure_ascii=False, indent=2)

    return rows


# ─── Agregação Campus ─────────────────────────────────────────────────────────

def aggregate_campus(rows: list[dict]) -> list[dict]:
    """
    Agrega registros individuais de estudantes por Ano × Região × Área CINE.
    Produz o mesmo esquema de colunas que analise.py espera:
      qt_mat_*, qt_ing_*, qt_conc_*, pct_*, tx_evasao_*.
    """
    from collections import defaultdict

    agg: dict[tuple, dict] = defaultdict(lambda: {
        "ing_fem": 0, "ing_masc": 0,
        "conc_fem": 0, "conc_masc": 0,
    })

    for r in rows:
        key = (r["ano"], r["regiao"], r["co_regiao"], r["area_geral"])
        if r["genero"] == "Feminino":
            agg[key]["ing_fem"] += 1
            if r["concluiu"]:
                agg[key]["conc_fem"] += 1
        else:
            agg[key]["ing_masc"] += 1
            if r["concluiu"]:
                agg[key]["conc_masc"] += 1

    result = []
    for (ano, regiao, co_regiao, area_geral), vals in agg.items():
        ing_fem   = vals["ing_fem"]
        ing_masc  = vals["ing_masc"]
        conc_fem  = vals["conc_fem"]
        conc_masc = vals["conc_masc"]

        # Matrículas ≈ ingressantes (simplificação do mock — sem histórico longitudinal)
        mat_fem  = ing_fem
        mat_masc = ing_masc

        tot_mat  = mat_fem  + mat_masc
        tot_ing  = ing_fem  + ing_masc
        tot_conc = conc_fem + conc_masc

        pct_mat_fem  = round(mat_fem  / tot_mat  * 100, 2) if tot_mat  > 0 else 0
        pct_ing_fem  = round(ing_fem  / tot_ing  * 100, 2) if tot_ing  > 0 else 0
        pct_conc_fem = round(conc_fem / tot_conc * 100, 2) if tot_conc > 0 else 0

        tx_evasao_fem  = round((ing_fem  - conc_fem)  / ing_fem  * 100, 2) if ing_fem  > 0 else None
        tx_evasao_masc = round((ing_masc - conc_masc) / ing_masc * 100, 2) if ing_masc > 0 else None

        result.append({
            "ano":             ano,
            "regiao":          regiao,
            "co_regiao":       co_regiao,
            "area_geral":      area_geral,
            "qt_mat_fem":      mat_fem,
            "qt_mat_masc":     mat_masc,
            "qt_ing_fem":      ing_fem,
            "qt_ing_masc":     ing_masc,
            "qt_conc_fem":     conc_fem,
            "qt_conc_masc":    conc_masc,
            "qt_mat_total":    tot_mat,
            "qt_ing_total":    tot_ing,
            "qt_conc_total":   tot_conc,
            "pct_mat_fem":     pct_mat_fem,
            "pct_ing_fem":     pct_ing_fem,
            "pct_conc_fem":    pct_conc_fem,
            "tx_evasao_fem_pct":  tx_evasao_fem,
            "tx_evasao_masc_pct": tx_evasao_masc,
        })

    return sorted(result, key=lambda r: (r["ano"], r["regiao"]))


# ─── ETL Base de Mercado Mundial (comparação global) ─────────────────────────
# Fonte: compilado WomenHack (2026) + Brasscom (2024/25) + McKinsey/LeanIn (2025)
# Usado APENAS para comparações globais (pay gap, liderança, retenção).
# Colunas: genero, cargo, setor, salario_base, anos_experiencia,
#           tempo_empresa_meses, promovido_ultimo_ano, transicao_carreira

def etl_mercado_mundial() -> list[dict]:
    """
    Lê base_mercado_tech_mundial.csv — compilado de dados globais de mercado.
    WomenHack 2026: 29% C-Suite mulheres, 15% CTOs, retenção 3,1 vs 4,2 anos.
    Brasscom 2024/25: 34,2% mulheres em TIC no Brasil, gap salarial ~27%.
    McKinsey/LeanIn 2025: broken rung — 87 mulheres promovidas p/ gerência vs 100 homens.
    """
    rows = []

    if not MERCADO_FILE.exists():
        logger.warning(f"Base de mercado mundial não encontrada: {MERCADO_FILE}")
        return rows

    logger.info(f"Processando base de mercado mundial ({MERCADO_FILE.stat().st_size / 1024:.1f} KB)...")

    salaries = []
    with open(MERCADO_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
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

    # Winsorização p99 — remove efeito de outliers extremos sem descartar linhas
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
            "dataset":           "base_mercado_tech_mundial.csv",
            "tipo":              "dataset_compilado_global",
            "uso":               "Comparação global — não é a base principal",
            "total_linhas":      len(rows),
            "p01_brl":           p1,
            "p99_brl":           p99,
            "linhas_winsorized": winsorized,
            "n_feminino":        n_fem,
            "n_masculino":       n_masc,
            "fontes": {
                "WomenHack_2026":      "29% C-Suite mulheres, 15% CTOs, retenção 3,1 vs 4,2 anos",
                "Brasscom_2024_25":    "34,2% mulheres em TIC no Brasil, gap salarial ~27%",
                "McKinsey_LeanIn_2025": "Broken rung: 87 mulheres promovidas p/ gerência vs 100 homens",
            },
        }, f, ensure_ascii=False, indent=2)

    return rows


# ─── Agregação Mercado ────────────────────────────────────────────────────────

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


# ─── ETL State of Data Brazil 2021 (BASE PRINCIPAL) ──────────────────────────
# Dado REAL verificado. Survey com profissionais da área de dados no Brasil.
# Colunas no formato ('P1_a', 'Label') — tratadas pelo parser abaixo.

_SALARY_MIDPOINTS = [
    ("menos de r$ 1.000", 750),
    ("de r$ 1.001", 1500),
    ("de r$ 2.001", 2500),
    ("de r$ 3.001", 3500),
    ("de r$ 4.001", 5000),
    ("de r$ 6.001", 7000),
    ("de r$ 8.001", 10000),
    ("de r$ 12.001", 14000),
    ("de r$ 16.001", 18000),
    ("de r$ 20.001", 22500),
    ("de r$ 25.001", 27500),
    ("de r$ 30.001", 35000),
    ("acima de r$ 40.001", 45000),
]

_CARGO_NORM = {
    "analista de dados":    "Data Analyst",
    "data analyst":         "Data Analyst",
    "cientista de dados":   "Data Scientist",
    "data scientist":       "Data Scientist",
    "engenheiro de dados":  "Data Engineer",
    "data engineer":        "Data Engineer",
    "analytics engineer":   "Analytics Engineer",
    "analista de bi":       "BI Analyst",
    "bi analyst":           "BI Analyst",
    "inteligência de negócio": "BI Analyst",
    "dba":                  "DBA",
    "banco de dados":       "DBA",
    "machine learning":     "ML Engineer",
    "gestor":               "Gestor/Liderança",
    "gerente":              "Gestor/Liderança",
    "coordenador":          "Gestor/Liderança",
    "líder":                "Gestor/Liderança",
    "lider":                "Gestor/Liderança",
    "head":                 "Gestor/Liderança",
    "c-level":              "C-Level",
    "cdo":                  "C-Level",
    "cio":                  "C-Level",
    "cto":                  "C-Level",
    "diretor":              "C-Level",
    "estatístico":          "Estatístico",
    "arquiteto":            "Arquiteto de Dados",
}


def _parse_salary_2021(val: str) -> float | None:
    v = str(val).lower().strip()
    for pattern, mid in _SALARY_MIDPOINTS:
        if pattern in v:
            return float(mid)
    return None


def _normalize_cargo_2021(val: str) -> str:
    v = str(val).lower().strip()
    for pattern, normalized in _CARGO_NORM.items():
        if pattern in v:
            return normalized
    return str(val).strip() if val else "Outro"


def _parse_col_name(col: str) -> tuple[str, str]:
    """Extrai (código, label) de nomes no formato ('P1_a', 'Idade')."""
    col = col.strip()
    if col.startswith("('") and "', '" in col:
        inner = col.strip("()'")
        parts = inner.split("', '")
        code  = parts[0].strip("'")
        label = parts[1].strip("'") if len(parts) > 1 else col
        return code, label
    return col, col


def etl_dados_2021() -> list[dict]:
    """
    Lê base_mercado_dados_2021_brasil.csv — State of Data Brazil 2021.
    BASE PRINCIPAL: dado real de profissionais da área de dados no Brasil.
    Extrai: gênero, cargo, faixa salarial, UF, setor, gestão, experiência.
    """
    rows = []

    if not DADOS_2021_FILE.exists():
        logger.warning(f"State of Data 2021 não encontrado: {DADOS_2021_FILE}")
        return rows

    logger.info(f"Processando State of Data 2021 ({DADOS_2021_FILE.stat().st_size / 1024:.1f} KB)...")

    with open(DADOS_2021_FILE, encoding="utf-8") as f:
        raw_headers = f.readline().rstrip("\n").split(",")

    # Mapeia índice → (code, label) para busca flexível
    col_info = [_parse_col_name(h) for h in raw_headers]
    labels_lower = [info[1].lower() for info in col_info]

    def find_idx(*patterns: str) -> int | None:
        for pat in patterns:
            for i, lbl in enumerate(labels_lower):
                if pat in lbl:
                    return i
        return None

    idx_genero  = find_idx("gênero", "genero", "gender")
    idx_cargo   = find_idx("cargo atual", "cargo")
    idx_salario = find_idx("faixa salarial", "salari")
    idx_uf      = find_idx("estado que mora", "uf", "estado")
    idx_setor   = find_idx("setor")
    idx_gestor  = find_idx("gestor", "gerencia", "manage")
    idx_exp     = find_idx("experiência na área de dado", "tempo de experiência", "anos de experiência")

    logger.info(f"  Colunas mapeadas — gênero:{idx_genero}, cargo:{idx_cargo}, salário:{idx_salario}, UF:{idx_uf}")

    with open(DADOS_2021_FILE, encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # pula header
        for raw_row in reader:
            def get(idx):
                if idx is None or idx >= len(raw_row):
                    return ""
                return raw_row[idx].strip()

            genero_raw = get(idx_genero)
            genero = _normalizar_genero(genero_raw)
            if genero not in ("Feminino", "Masculino"):
                continue

            cargo_raw = get(idx_cargo)
            if not cargo_raw:
                continue

            salario = _parse_salary_2021(get(idx_salario))
            rows.append({
                "genero":          genero,
                "cargo":           _normalize_cargo_2021(cargo_raw),
                "cargo_raw":       cargo_raw,
                "salario_midpoint": salario,
                "uf":              get(idx_uf),
                "setor":           get(idx_setor),
                "is_gestor":       1 if "sim" in get(idx_gestor).lower() else 0,
                "experiencia_raw": get(idx_exp),
            })

    n_fem  = sum(1 for r in rows if r["genero"] == "Feminino")
    n_masc = sum(1 for r in rows if r["genero"] == "Masculino")
    pct_fem = round(n_fem / len(rows) * 100, 2) if rows else 0
    logger.info(f"  State of Data 2021: {len(rows):,} respondentes | Feminino: {n_fem} ({pct_fem}%) | Masculino: {n_masc}")

    with open(OUT / "qualidade_dados_2021.json", "w", encoding="utf-8") as f:
        json.dump({
            "dataset":    "base_mercado_dados_2021_brasil.csv",
            "tipo":       "dado_real",
            "fonte":      "State of Data Brazil 2021 — Data Hackers / Bain & Company",
            "uso":        "BASE PRINCIPAL — análise de desigualdade de gênero na área de dados",
            "total":      len(rows),
            "n_feminino": n_fem,
            "n_masculino": n_masc,
            "pct_feminino": pct_fem,
            "colunas_mapeadas": {
                "genero": idx_genero, "cargo": idx_cargo,
                "salario": idx_salario, "uf": idx_uf,
            },
        }, f, ensure_ascii=False, indent=2)

    return rows


# ─── ETL Vagas LinkedIn ──────────────────────────────────────────────────────
# Fonte: generation_linkedin_vagas_tecnologia.csv — vagas coletadas pela Generation
# Classifica cada vaga por tipo D&I, nível, área e localização.

def _classify_di(description: str) -> tuple[str, int]:
    """Retorna (tipo_di, eh_di) com base em palavras-chave da descrição."""
    d = description.lower()
    if "exclusiva para mulheres" in d:
        return ("Exclusiva", 1)
    if "cis e trans" in d:
        return ("Afirmativa Trans-Inclusiva", 1)
    if "afirmativ" in d or "participacao feminina" in d or "participação feminina" in d:
        return ("Afirmativa", 1)
    return ("Aberta", 0)


def _extract_nivel(title: str) -> str:
    t = title.lower()
    if "est" in t and ("gio" in t or "ágio" in t):
        return "Estagiário"
    if "aprendiz" in t:
        return "Aprendiz"
    if "junior" in t or "júnior" in t:
        return "Júnior"
    return "Outros"


def _extract_area(title: str) -> str:
    if "Ciência de Dados" in title:
        return "Ciência de Dados"
    if "Back-end" in title:
        return "Desenvolvimento Back-end"
    if "Front-end" in title:
        return "Desenvolvimento Front-end"
    if "QA" in title:
        return "QA/Testes"
    if "Suporte" in title:
        return "Suporte Técnico"
    if "Dados" in title:
        return "Dados"
    if "TI" in title:
        return "TI Geral"
    if "Desenvolvedor" in title or "Desenvolvimento" in title:
        return "Desenvolvimento"
    return "Outros"


def _parse_location(loc: str) -> tuple[str | None, str | None, int]:
    """Retorna (cidade, uf, remoto)."""
    if "Remoto" in loc:
        return (None, None, 1)
    parts = [p.strip() for p in loc.split(",")]
    cidade = parts[0] if parts else None
    uf = parts[1] if len(parts) > 1 else None
    return (cidade, uf, 0)


def etl_linkedin() -> list[dict]:
    """
    Lê generation_linkedin_vagas_tecnologia.csv e enriquece cada vaga com:
      - tipo_di: Exclusiva | Afirmativa Trans-Inclusiva | Afirmativa | Aberta
      - eh_di: 1 se a vaga menciona iniciativa de D&I para mulheres, 0 caso contrário
      - nivel: Estagiário | Aprendiz | Júnior | Outros
      - area_tech: área técnica da vaga derivada do título
      - cidade, uf: parseados do campo location
      - remoto: 1 se for remota
      - mes_ano: YYYY-MM extraído de inserted_at (para análise temporal)
    """
    rows = []

    if not LINKEDIN_FILE.exists():
        logger.warning(f"LinkedIn vagas não encontrado: {LINKEDIN_FILE}")
        return rows

    logger.info(f"Processando vagas LinkedIn ({LINKEDIN_FILE.stat().st_size / 1024:.1f} KB)...")

    with open(LINKEDIN_FILE, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            title = row.get("job_title", "").strip()
            desc  = row.get("description", "").strip()
            loc   = row.get("location", "").strip()
            dt    = row.get("inserted_at", "")

            tipo_di, eh_di = _classify_di(desc)
            cidade, uf, remoto = _parse_location(loc)

            rows.append({
                "id":           row.get("id", "").strip(),
                "empresa":      row.get("company_name", "").strip(),
                "titulo":       title,
                "nivel":        _extract_nivel(title),
                "area_tech":    _extract_area(title),
                "cidade":       cidade,
                "uf":           uf,
                "remoto":       remoto,
                "tipo_di":      tipo_di,
                "eh_di":        eh_di,
                "mes_ano":      dt[:7] if len(dt) >= 7 else None,
                "inserted_at":  dt,
                "descricao":    desc,
            })

    n_di   = sum(r["eh_di"] for r in rows)
    n_open = len(rows) - n_di
    pct_di = round(n_di / len(rows) * 100, 1) if rows else 0

    tipos = {}
    for r in rows:
        tipos[r["tipo_di"]] = tipos.get(r["tipo_di"], 0) + 1

    logger.info(f"  LinkedIn: {len(rows):,} vagas | D&I: {n_di} ({pct_di}%) | Abertas: {n_open}")
    for tipo, n in sorted(tipos.items()):
        logger.info(f"    {tipo}: {n}")

    with open(OUT / "qualidade_linkedin.json", "w", encoding="utf-8") as f:
        json.dump({
            "dataset":       "generation_linkedin_vagas_tecnologia.csv",
            "tipo":          "dataset_simulado",
            "total_vagas":   len(rows),
            "n_di":          n_di,
            "n_abertas":     n_open,
            "pct_di":        pct_di,
            "distribuicao_tipo_di": tipos,
            "periodo":       {
                "inicio": min(r["mes_ano"] for r in rows if r["mes_ano"]),
                "fim":    max(r["mes_ano"] for r in rows if r["mes_ano"]),
            },
        }, f, ensure_ascii=False, indent=2)

    return rows


# ─── Persistência em DuckDB ───────────────────────────────────────────────────

def save_to_duckdb(campus_agg: list[dict], mercado_agg: list[dict], dados_2021: list[dict] = None, linkedin_rows: list[dict] = None) -> None:
    import duckdb

    con = duckdb.connect(str(DB))

    # ─── Tabela educação (base_campus_ti_brasil.csv — ref. INEP)
    con.execute("DROP TABLE IF EXISTS fato_educacao_tech")
    con.execute("""
        CREATE TABLE fato_educacao_tech (
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
        )
    """)
    for r in campus_agg:
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

    # ─── Tabela mercado mundial (WomenHack + Brasscom + McKinsey — comparação global)
    con.execute("DROP TABLE IF EXISTS fato_mercado_mundial")
    con.execute("""
        CREATE TABLE fato_mercado_mundial (
            cargo               VARCHAR,
            nivel               VARCHAR,
            genero              VARCHAR,
            regiao              VARCHAR,
            n                   INTEGER,
            salario_medio_brl   DOUBLE,
            salario_mediano_brl DOUBLE
        )
    """)
    for r in mercado_agg:
        con.execute(
            "INSERT INTO fato_mercado_mundial VALUES (?,?,?,?,?,?,?)",
            [r["cargo"], r["nivel"], r["genero"], r["regiao"],
             r["n"], r["salario_medio_brl"], r["salario_mediano_brl"]]
        )

    # ─── Tabela State of Data Brazil 2021 (BASE PRINCIPAL)
    if dados_2021:
        con.execute("DROP TABLE IF EXISTS fato_dados_2021")
        con.execute("""
            CREATE TABLE fato_dados_2021 (
                genero          VARCHAR,
                cargo           VARCHAR,
                cargo_raw       VARCHAR,
                salario_midpoint DOUBLE,
                uf              VARCHAR,
                setor           VARCHAR,
                is_gestor       INTEGER,
                experiencia_raw VARCHAR
            )
        """)
        for r in dados_2021:
            con.execute(
                "INSERT INTO fato_dados_2021 VALUES (?,?,?,?,?,?,?,?)",
                [r["genero"], r["cargo"], r["cargo_raw"],
                 r["salario_midpoint"], r["uf"], r["setor"],
                 r["is_gestor"], r["experiencia_raw"]]
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

    # Pay gap principal — baseado no State of Data 2021 (dado real)
    if dados_2021:
        con.execute("""
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
            WHERE salario_midpoint IS NOT NULL
            GROUP BY cargo, uf
            HAVING COUNT(*) >= 5
            ORDER BY pay_gap_pct DESC NULLS LAST
        """)

        con.execute("""
            CREATE OR REPLACE VIEW v_lideranca_dados AS
            SELECT
                cargo,
                COUNT(*) AS total,
                SUM(CASE WHEN genero = 'Feminino' THEN 1 ELSE 0 END) AS n_fem,
                ROUND(SUM(CASE WHEN genero = 'Feminino' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS pct_fem,
                SUM(is_gestor) AS n_gestores,
                ROUND(SUM(CASE WHEN genero = 'Feminino' AND is_gestor = 1 THEN 1 ELSE 0 END) * 100.0 /
                      NULLIF(SUM(is_gestor), 0), 2) AS pct_gestoras
            FROM fato_dados_2021
            GROUP BY cargo
            ORDER BY pct_fem
        """)

    # Pay gap global — comparação com dado compilado (WomenHack + Brasscom + McKinsey)
    con.execute("""
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
        GROUP BY cargo, regiao
        ORDER BY pay_gap_pct DESC
    """)

    # ─── Tabela vagas LinkedIn (vagas coletadas pela Generation — D&I signal)
    if linkedin_rows:
        con.execute("DROP TABLE IF EXISTS fato_vagas_linkedin")
        con.execute("""
            CREATE TABLE fato_vagas_linkedin (
                id          VARCHAR,
                empresa     VARCHAR,
                titulo      VARCHAR,
                nivel       VARCHAR,
                area_tech   VARCHAR,
                cidade      VARCHAR,
                uf          VARCHAR,
                remoto      INTEGER,
                tipo_di     VARCHAR,
                eh_di       INTEGER,
                mes_ano     VARCHAR,
                inserted_at VARCHAR,
                descricao   VARCHAR
            )
        """)
        for r in linkedin_rows:
            con.execute(
                "INSERT INTO fato_vagas_linkedin VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                [r["id"], r["empresa"], r["titulo"], r["nivel"], r["area_tech"],
                 r["cidade"], r["uf"], r["remoto"], r["tipo_di"], r["eh_di"],
                 r["mes_ano"], r["inserted_at"], r["descricao"]]
            )

        con.execute("""
            CREATE OR REPLACE VIEW v_vagas_di AS
            SELECT
                mes_ano,
                area_tech,
                nivel,
                uf,
                COUNT(*)                                           AS total_vagas,
                SUM(eh_di)                                         AS vagas_di,
                ROUND(SUM(eh_di) * 100.0 / NULLIF(COUNT(*), 0), 1) AS pct_di,
                COUNT(CASE WHEN tipo_di = 'Exclusiva'              THEN 1 END) AS n_exclusiva,
                COUNT(CASE WHEN tipo_di = 'Afirmativa'             THEN 1 END) AS n_afirmativa,
                COUNT(CASE WHEN tipo_di = 'Afirmativa Trans-Inclusiva' THEN 1 END) AS n_trans_inclusiva,
                COUNT(CASE WHEN tipo_di = 'Aberta'                 THEN 1 END) AS n_aberta,
                SUM(remoto)                                        AS vagas_remotas
            FROM fato_vagas_linkedin
            GROUP BY mes_ano, area_tech, nivel, uf
            ORDER BY mes_ano, area_tech
        """)

    n_edu    = con.execute("SELECT COUNT(*) FROM fato_educacao_tech").fetchone()[0]
    n_merc   = con.execute("SELECT COUNT(*) FROM fato_mercado_mundial").fetchone()[0]
    n_dados  = con.execute("SELECT COUNT(*) FROM fato_dados_2021").fetchone()[0] if dados_2021 else 0
    n_li     = con.execute("SELECT COUNT(*) FROM fato_vagas_linkedin").fetchone()[0] if linkedin_rows else 0
    con.close()

    logger.info(f"DuckDB salvo em {DB}")
    logger.info(f"  fato_educacao_tech:  {n_edu:,} linhas  (INEP — referência funil acadêmico)")
    logger.info(f"  fato_mercado_mundial:{n_merc:,} linhas  (WomenHack+Brasscom+McKinsey — comparação global)")
    logger.info(f"  fato_dados_2021:     {n_dados:,} linhas  (State of Data 2021 — BASE PRINCIPAL)")
    logger.info(f"  fato_vagas_linkedin: {n_li:,} linhas  (Generation — D&I signal)")


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


# ─── Métricas-chave no terminal ───────────────────────────────────────────────

def print_key_metrics(campus_agg: list[dict], mercado_agg: list[dict], dados_2021: list[dict] = None) -> None:
    print("\n" + "="*60)
    print("  MÉTRICAS-CHAVE — DESIGUALDADE DE GÊNERO NA ÁREA DE DADOS")
    print("="*60)

    tic  = [r for r in campus_agg if "Computa" in r["area_geral"]]
    anos = sorted(set(r["ano"] for r in tic))

    for ano in anos:
        ar = [r for r in tic if r["ano"] == ano]
        mat_fem  = sum(r["qt_mat_fem"]   for r in ar)
        mat_tot  = sum(r["qt_mat_total"] for r in ar)
        ing_fem  = sum(r["qt_ing_fem"]   for r in ar)
        ing_tot  = sum(r["qt_ing_total"] for r in ar)
        conc_fem = sum(r["qt_conc_fem"]  for r in ar)
        conc_tot = sum(r["qt_conc_total"] for r in ar)

        pct_mat  = mat_fem  / mat_tot  * 100 if mat_tot  > 0 else 0
        pct_ing  = ing_fem  / ing_tot  * 100 if ing_tot  > 0 else 0
        pct_conc = conc_fem / conc_tot * 100 if conc_tot > 0 else 0

        print(f"\n  {ano} | TIC (ref. INEP — dataset mockado):")
        print(f"    Ingressantes: {ing_tot:>5,} total | {ing_fem:>4,} fem ({pct_ing:.1f}%)")
        print(f"    Concluintes:  {conc_tot:>5,} total | {conc_fem:>4,} fem ({pct_conc:.1f}%)")
        print(f"    Matrículas*:  {mat_tot:>5,} total | {mat_fem:>4,} fem ({pct_mat:.1f}%)")

    print("\n  * Matriculas ~= ingressantes (simplificacao do mock)")

    # ── State of Data 2021 (base principal — dado real)
    if dados_2021:
        n_fem  = sum(1 for r in dados_2021 if r["genero"] == "Feminino")
        n_masc = sum(1 for r in dados_2021 if r["genero"] == "Masculino")
        n_tot  = len(dados_2021)
        pct_fem = n_fem / n_tot * 100 if n_tot > 0 else 0
        print(f"\n  STATE OF DATA BRAZIL 2021 (dado real — base principal):")
        print(f"    Respondentes: {n_tot:,} | Feminino: {n_fem} ({pct_fem:.1f}%) | Masculino: {n_masc}")

        fem_sals  = [r["salario_midpoint"] for r in dados_2021 if r["genero"] == "Feminino"  and r["salario_midpoint"]]
        masc_sals = [r["salario_midpoint"] for r in dados_2021 if r["genero"] == "Masculino" and r["salario_midpoint"]]
        if fem_sals and masc_sals:
            media_fem  = sum(fem_sals)  / len(fem_sals)
            media_masc = sum(masc_sals) / len(masc_sals)
            gap_pct    = (media_masc - media_fem) / media_masc * 100 if media_masc > 0 else 0
            print(f"    Salário médio Masculino: R${media_masc:,.0f}")
            print(f"    Salário médio Feminino:  R${media_fem:,.0f}")
            print(f"    Gap salarial (setor dados): {gap_pct:.1f}%")

        n_gestoras = sum(1 for r in dados_2021 if r["genero"] == "Feminino" and r["is_gestor"] == 1)
        n_gestores = sum(1 for r in dados_2021 if r["is_gestor"] == 1)
        if n_gestores > 0:
            pct_gestoras = n_gestoras / n_gestores * 100
            print(f"    Gestoras: {n_gestoras}/{n_gestores} posições de gestão ({pct_gestoras:.1f}%)")

    # ── Comparação global (WomenHack + Brasscom + McKinsey)
    if mercado_agg:
        fem_sals  = [r["salario_medio_brl"] for r in mercado_agg if r["genero"] == "Feminino"]
        masc_sals = [r["salario_medio_brl"] for r in mercado_agg if r["genero"] == "Masculino"]
        if fem_sals and masc_sals:
            media_fem  = sum(fem_sals)  / len(fem_sals)
            media_masc = sum(masc_sals) / len(masc_sals)
            gap_pct    = (media_masc - media_fem) / media_masc * 100 if media_masc > 0 else 0
            print(f"\n  PAY GAP GLOBAL (WomenHack + Brasscom + McKinsey — comparação):")
            print(f"    Salário médio Masculino: R${media_masc:,.0f}")
            print(f"    Salário médio Feminino:  R${media_fem:,.0f}")
            print(f"    Gap salarial: {gap_pct:.1f}%")

    print("="*60 + "\n")


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Iniciando ETL Pipeline — People Analytics & DE&I (foco: setor de dados)")

    # 1. Lê dados brutos
    campus_rows    = etl_campus()
    mercado_rows   = etl_mercado_mundial()
    dados_2021     = etl_dados_2021()
    linkedin_rows  = etl_linkedin()

    # 2. Agrega campus e mercado mundial (LinkedIn e dados_2021 ficam no nível individual)
    logger.info("Agregando dados do campus TI...")
    campus_agg  = aggregate_campus(campus_rows)
    mercado_agg = aggregate_mercado(mercado_rows)

    # 3. Persiste
    logger.info("Salvando CSVs...")
    save_csv(campus_agg,   "fato_educacao_tech_agregado")
    save_csv(mercado_agg,  "fato_mercado_mundial")
    save_csv(dados_2021,   "fato_dados_2021_brasil")
    save_csv(linkedin_rows, "fato_vagas_linkedin")

    logger.info("Salvando no DuckDB...")
    save_to_duckdb(campus_agg, mercado_agg, dados_2021, linkedin_rows)

    # 4. Mostra métricas
    print_key_metrics(campus_agg, mercado_agg, dados_2021)

    logger.info("ETL concluído. Base principal: fato_dados_2021 (State of Data Brazil 2021)")
