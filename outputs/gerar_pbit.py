"""
Gera  outputs/PeopleAnalytics.pbit  — Power BI Template pronto para abrir.

O .pbit contém:
  • 5 tabelas com Power Query M (carregam os CSVs de outputs/powerbi_data/)
  • Relacionamento fato_mercado → dim_cargo
  • 9 medidas DAX pré-criadas
  • 2 páginas em branco ("A Base" e "O Mercado") para montar os visuais

Uso:
    python outputs/gerar_pbit.py
    Depois abra  outputs/PeopleAnalytics.pbit  no Power BI Desktop.
    Na primeira abertura ele pedirá o caminho da pasta powerbi_data/ — aponte para:
        <projeto>/outputs/powerbi_data/
"""

import json
import zipfile
from pathlib import Path

ROOT    = Path(__file__).resolve().parent.parent
PBI_DIR = ROOT / "outputs" / "powerbi_data"
OUT     = ROOT / "outputs" / "PeopleAnalytics.pbit"

# ─── helpers ──────────────────────────────────────────────────────────────────

def m_load_csv(filename: str, col_types: list[tuple[str, str]]) -> list[str]:
    """Retorna expressão M (lista de linhas) que carrega um CSV via parâmetro."""
    type_list = ",\n".join(
        f'                {{"{c}", type {t}}}' for c, t in col_types
    )
    return [
        f'let',
        f'    Source = Csv.Document(',
        f'        File.Contents(PastaBase & "/{filename}"),',
        f'        [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]',
        f'    ),',
        f'    Headers = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        f'    Typed   = Table.TransformColumnTypes(Headers, {{',
        type_list,
        f'    }})',
        f'in',
        f'    Typed',
    ]


def col(name: str, dtype: str, hidden: bool = False) -> dict:
    ann = [{"name": "SummarizationSetBy", "value": "Automatic"}]
    d = {"name": name, "dataType": dtype, "sourceColumn": name, "annotations": ann}
    if hidden:
        d["isHidden"] = True
    if dtype in ("int64", "double"):
        d["summarizeBy"] = "none"
    return d


def measure(name: str, expr: str, fmt: str = "#,##0.00") -> dict:
    return {"name": name, "expression": expr, "formatString": fmt}


def partition(table_name: str, m_lines: list[str]) -> dict:
    return {
        "name": table_name,
        "mode": "import",
        "source": {"type": "m", "expression": m_lines},
    }


# ─── Parâmetro: pasta base ────────────────────────────────────────────────────

PARAM_TABLE = {
    "name": "Parâmetros",
    "isHidden": True,
    "columns": [
        {"name": "PastaBase", "dataType": "string", "sourceColumn": "PastaBase",
         "annotations": [{"name": "SummarizationSetBy", "value": "Automatic"}]}
    ],
    "partitions": [{
        "name": "Parâmetros",
        "mode": "import",
        "source": {
            "type": "m",
            "expression": [
                'let',
                f'    Caminho = "{str(PBI_DIR).replace(chr(92), "/")}",',
                '    T = #table(type table [PastaBase = text], {{Caminho}})',
                'in',
                '    T',
            ]
        }
    }],
    "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
}

# Expressão M reutilizável para pegar o parâmetro
# (cada tabela usa uma variável local PastaBase que vem desta tabela de parâmetro)
# Na prática embutimos o caminho direto e o usuário muda via "Editar Parâmetros"

# ─── Tabela: fato_mercado ─────────────────────────────────────────────────────

FATO_MERCADO_COLS = [
    ("cargo",             "text"),
    ("nivel",             "text"),
    ("genero",            "text"),
    ("regiao",            "text"),
    ("n",                 "Int64.Type"),
    ("salario_medio_brl", "number"),
    ("salario_mediano_brl","number"),
    ("nivel_hierarquico", "Int64.Type"),
    ("gap_pct",           "number"),
]

FATO_MERCADO = {
    "name": "fato_mercado",
    "columns": [
        col("cargo",              "string"),
        col("nivel",              "string"),
        col("genero",             "string"),
        col("regiao",             "string"),
        col("n",                  "int64"),
        col("salario_medio_brl",  "double"),
        col("salario_mediano_brl","double"),
        col("nivel_hierarquico",  "int64", hidden=True),
        col("gap_pct",            "double"),
    ],
    "measures": [
        measure(
            "Salario Medio Fem",
            'CALCULATE(\n    AVERAGEX(fato_mercado, fato_mercado[salario_medio_brl]),\n    fato_mercado[genero] = "Feminino"\n)',
            '"R$ "#,##0',
        ),
        measure(
            "Salario Medio Masc",
            'CALCULATE(\n    AVERAGEX(fato_mercado, fato_mercado[salario_medio_brl]),\n    fato_mercado[genero] = "Masculino"\n)',
            '"R$ "#,##0',
        ),
        measure(
            "Gender Pay Gap %",
            "DIVIDE([Salario Medio Masc] - [Salario Medio Fem], [Salario Medio Masc]) * 100",
            '0.0"%"',
        ),
        measure(
            "% Mulheres no Mercado",
            'DIVIDE(\n    CALCULATE(SUM(fato_mercado[n]), fato_mercado[genero] = "Feminino"),\n    SUM(fato_mercado[n])\n) * 100',
            '0.0"%"',
        ),
        measure(
            "% Mulheres em Lideranca",
            'DIVIDE(\n    CALCULATE(SUM(fato_mercado[n]),\n              fato_mercado[genero] = "Feminino",\n              dim_cargo[eh_lideranca] = 1),\n    CALCULATE(SUM(fato_mercado[n]),\n              dim_cargo[eh_lideranca] = 1)\n) * 100',
            '0.0"%"',
        ),
    ],
    "partitions": [partition("fato_mercado", m_load_csv("fato_mercado.csv", FATO_MERCADO_COLS))],
    "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
}

# ─── Tabela: fato_educacao ────────────────────────────────────────────────────

FATO_EDU_COLS = [
    ("ano",               "Int64.Type"),
    ("regiao",            "text"),
    ("co_regiao",         "Int64.Type"),
    ("area_geral",        "text"),
    ("qt_mat_fem",        "Int64.Type"),
    ("qt_mat_masc",       "Int64.Type"),
    ("qt_ing_fem",        "Int64.Type"),
    ("qt_ing_masc",       "Int64.Type"),
    ("qt_conc_fem",       "Int64.Type"),
    ("qt_conc_masc",      "Int64.Type"),
    ("qt_mat_total",      "Int64.Type"),
    ("qt_ing_total",      "Int64.Type"),
    ("qt_conc_total",     "Int64.Type"),
    ("pct_mat_fem",       "number"),
    ("pct_ing_fem",       "number"),
    ("pct_conc_fem",      "number"),
    ("tx_evasao_fem_pct", "number"),
    ("tx_evasao_masc_pct","number"),
    ("yoy_ing_fem_pp",    "number"),
]

FATO_EDUCACAO = {
    "name": "fato_educacao",
    "columns": [col(c, "int64" if t == "Int64.Type" else "double" if t == "number" else "string")
                for c, t in FATO_EDU_COLS],
    "measures": [
        measure(
            "Pct Ing Fem Ultimo Ano",
            "CALCULATE(\n    AVERAGE(fato_educacao[pct_ing_fem]),\n    fato_educacao[ano] = MAX(fato_educacao[ano])\n)",
            '0.0"%"',
        ),
        measure(
            "Variacao Ing Fem pp",
            "CALCULATE(\n    AVERAGE(fato_educacao[yoy_ing_fem_pp]),\n    fato_educacao[ano] = MAX(fato_educacao[ano])\n)",
            '+0.0;-0.0;0.0',
        ),
    ],
    "partitions": [partition("fato_educacao", m_load_csv("fato_educacao.csv", FATO_EDU_COLS))],
    "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
}

# ─── Tabela: fato_vagas ───────────────────────────────────────────────────────

FATO_VAGAS_COLS = [
    ("id",         "Int64.Type"),
    ("empresa",    "text"),
    ("titulo",     "text"),
    ("nivel",      "text"),
    ("area_tech",  "text"),
    ("cidade",     "text"),
    ("uf",         "text"),
    ("remoto",     "text"),
    ("tipo_di",    "text"),
    ("eh_di",      "Int64.Type"),
    ("mes_ano",    "text"),
    ("inserted_at","text"),
    ("descricao",  "text"),
]

FATO_VAGAS = {
    "name": "fato_vagas",
    "columns": [col(c, "int64" if t == "Int64.Type" else "string") for c, t in FATO_VAGAS_COLS],
    "measures": [
        measure(
            "Pct Vagas DI",
            'DIVIDE(\n    CALCULATE(COUNTROWS(fato_vagas), fato_vagas[eh_di] = 1),\n    COUNTROWS(fato_vagas)\n) * 100',
            '0.0"%"',
        ),
        measure(
            "Total Vagas DI",
            'CALCULATE(COUNTROWS(fato_vagas), fato_vagas[eh_di] = 1)',
            "0",
        ),
    ],
    "partitions": [partition("fato_vagas", m_load_csv("fato_vagas.csv", FATO_VAGAS_COLS))],
    "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
}

# ─── Tabela: dim_cargo ────────────────────────────────────────────────────────

DIM_CARGO_COLS = [
    ("cargo",               "text"),
    ("nivel_hierarquico",   "Int64.Type"),
    ("eh_lideranca",        "Int64.Type"),
    ("total_profissionais", "Int64.Type"),
    ("n_feminino",          "Int64.Type"),
    ("pct_feminino",        "number"),
    ("irf",                 "number"),
    ("gap_pct",             "number"),
]

DIM_CARGO = {
    "name": "dim_cargo",
    "columns": [col(c, "int64" if t == "Int64.Type" else "double" if t == "number" else "string")
                for c, t in DIM_CARGO_COLS],
    "partitions": [partition("dim_cargo", m_load_csv("dim_cargo.csv", DIM_CARGO_COLS))],
    "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
}

# ─── Tabela: metricas_funil ───────────────────────────────────────────────────

FUNIL_COLS = [
    ("etapa",         "text"),
    ("ordem",         "Int64.Type"),
    ("pct_feminino",  "number"),
    ("fonte",         "text"),
]

METRICAS_FUNIL = {
    "name": "metricas_funil",
    "columns": [col(c, "int64" if t == "Int64.Type" else "double" if t == "number" else "string")
                for c, t in FUNIL_COLS],
    "partitions": [partition("metricas_funil", m_load_csv("metricas_funil.csv", FUNIL_COLS))],
    "annotations": [{"name": "PBI_ResultType", "value": "Table"}],
}

# ─── DataModelSchema (TMSL) ───────────────────────────────────────────────────

DATA_MODEL_SCHEMA = {
    "name": "DataModel",
    "compatibilityLevel": 1550,
    "model": {
        "culture": "pt-BR",
        "dataAccessOptions": {
            "legacyRedirects": True,
            "returnErrorValuesAsNull": True,
        },
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "sourceQueryCulture": "pt-BR",
        "tables": [
            FATO_MERCADO,
            FATO_EDUCACAO,
            FATO_VAGAS,
            DIM_CARGO,
            METRICAS_FUNIL,
        ],
        "relationships": [
            {
                "name": "rel_mercado_cargo",
                "fromTable": "fato_mercado",
                "fromColumn": "cargo",
                "toTable": "dim_cargo",
                "toColumn": "cargo",
            }
        ],
        "annotations": [
            {"name": "PBIDesktopVersion", "value": "2.130.0.0"},
            {"name": "__PBI_TimeIntelligenceEnabled", "value": "0"},
        ],
    },
}

# ─── Report/Layout — 2 páginas em branco ─────────────────────────────────────

def blank_page(section_id: int, name: str, display_name: str, ordinal: int) -> dict:
    return {
        "id": section_id,
        "name": name,
        "displayName": display_name,
        "filters": "[]",
        "ordinal": ordinal,
        "visualContainers": [],
        "config": json.dumps({
            "relationships": [],
            "objects": {
                "section": [{"properties": {"background": {"solid": {"color": {"solid": {"color": "#FFFFFF"}}}}}}]
            }
        }),
        "width": 1280,
        "height": 720,
        "displayOption": 0,
    }


REPORT_LAYOUT = {
    "id": 0,
    "resourcePackages": [],
    "sections": [
        blank_page(0, "ABase",     "A Base (Educacao)",   0),
        blank_page(1, "OMercado",  "O Mercado",            1),
    ],
    "config": json.dumps({
        "version": "5.43",
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU09",
                "version": "5.43",
                "type": 2,
            }
        },
        "activeSectionIndex": 0,
        "objects": {
            "section": [
                {"properties": {"verticalAlignment": {"expr": {"Literal": {"Value": "'Top'"}}}}}
            ]
        },
        "settings": {},
        "isSoftwareRendered": True,
    }),
    "layoutOptimization": 0,
}

# ─── [Content_Types].xml ─────────────────────────────────────────────────────

CONTENT_TYPES = """<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="json" ContentType="application/json"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/Report/Layout" ContentType="application/json"/>
  <Override PartName="/DataModelSchema" ContentType="application/json"/>
  <Override PartName="/DiagramLayout" ContentType="application/json"/>
  <Override PartName="/Connections" ContentType="application/json"/>
</Types>"""

# ─── DiagramLayout ───────────────────────────────────────────────────────────

DIAGRAM_LAYOUT = {
    "version": 1,
    "diagrams": [
        {
            "ordinal": 0,
            "scrollPosition": {"x": 0, "y": 0},
            "nodes": [
                {"location": {"x": 0,   "y": 0},   "nodeIndex": f"'{t}'"}
                for i, t in enumerate(
                    ["fato_mercado", "fato_educacao", "fato_vagas", "dim_cargo", "metricas_funil"]
                )
            ],
        }
    ],
}

# ─── Gerar o .pbit ───────────────────────────────────────────────────────────

def build():
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml",  CONTENT_TYPES.strip())
        zf.writestr("Version",              "4.0")
        zf.writestr("DataModelSchema",      json.dumps(DATA_MODEL_SCHEMA, ensure_ascii=False, indent=2))
        zf.writestr("DiagramLayout",        json.dumps(DIAGRAM_LAYOUT, ensure_ascii=False))
        zf.writestr("Connections",          json.dumps({"Version": 3, "Connections": []}, ensure_ascii=False))
        zf.writestr("Report/Layout",        json.dumps(REPORT_LAYOUT, ensure_ascii=False, indent=2))

    size_kb = OUT.stat().st_size // 1024
    print(f"[OK] {OUT.relative_to(ROOT)}  ({size_kb} KB)")
    print()
    print("Proximo passo:")
    print(f"  1. Abra o arquivo no Power BI Desktop")
    print(f"  2. Se pedir caminho dos dados, aponte para:")
    print(f"       {PBI_DIR}")
    print(f"  3. As 9 medidas DAX ja estao criadas — arraste os campos para montar os visuais")


if __name__ == "__main__":
    build()
