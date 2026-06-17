"""
Análise Exploratória — Funil da Mulher na Tech (dados reais INEP 2019-2024)
Gera gráficos HTML interativos e relatório de métricas.

Uso: python analise.py
"""

import csv
import json
import logging
from pathlib import Path
from collections import defaultdict

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("analise")

BASE    = Path(__file__).parent
TREATED = BASE / "data" / "treated"
REPORTS = BASE / "reports"
REPORTS.mkdir(exist_ok=True)

# ─── Carrega dados ────────────────────────────────────────────────────────────

def load_inep() -> list[dict]:
    path = TREATED / "fato_educacao_tech_agregado.csv"
    with open(path, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def to_float(v) -> float:
    try:
        return float(v) if v not in ("", None) else 0.0
    except (ValueError, TypeError):
        return 0.0


def to_int(v) -> int:
    try:
        return int(float(v)) if v not in ("", None) else 0
    except (ValueError, TypeError):
        return 0


# ─── Análise 1: Funil nacional TIC por ano ───────────────────────────────────

def funil_nacional_tic(rows: list[dict]) -> dict:
    tic = [r for r in rows if "Computa" in r.get("area_geral", "")]

    anos = sorted(set(to_int(r["ano"]) for r in tic))
    result = {}
    for ano in anos:
        ar = [r for r in tic if to_int(r["ano"]) == ano]
        result[ano] = {
            "mat_fem":  sum(to_int(r["qt_mat_fem"])  for r in ar),
            "mat_masc": sum(to_int(r["qt_mat_masc"]) for r in ar),
            "ing_fem":  sum(to_int(r["qt_ing_fem"])  for r in ar),
            "ing_masc": sum(to_int(r["qt_ing_masc"]) for r in ar),
            "conc_fem": sum(to_int(r["qt_conc_fem"]) for r in ar),
            "conc_masc":sum(to_int(r["qt_conc_masc"])for r in ar),
        }
        tot = lambda k: result[ano][f"{k}_fem"] + result[ano][f"{k}_masc"]
        for k in ["mat","ing","conc"]:
            result[ano][f"pct_{k}_fem"] = round(
                result[ano][f"{k}_fem"] / tot(k) * 100, 1
            ) if tot(k) > 0 else 0

    return result


# ─── Análise 2: Evasão por gênero ────────────────────────────────────────────

def evasao_por_ano(rows: list[dict]) -> dict:
    tic = [r for r in rows if "Computa" in r.get("area_geral", "")]
    anos = sorted(set(to_int(r["ano"]) for r in tic))
    result = {}
    for ano in anos:
        ar = [r for r in tic if to_int(r["ano"]) == ano]
        ing_fem  = sum(to_int(r["qt_ing_fem"])  for r in ar)
        ing_masc = sum(to_int(r["qt_ing_masc"]) for r in ar)
        conc_fem  = sum(to_int(r["qt_conc_fem"])  for r in ar)
        conc_masc = sum(to_int(r["qt_conc_masc"]) for r in ar)
        result[ano] = {
            "tx_evasao_fem":  round((ing_fem  - conc_fem)  / ing_fem  * 100, 1) if ing_fem  > 0 else None,
            "tx_evasao_masc": round((ing_masc - conc_masc) / ing_masc * 100, 1) if ing_masc > 0 else None,
        }
    return result


# ─── Análise 3: % mulheres por região (último ano disponível) ────────────────

def distribuicao_regional(rows: list[dict], ano: int = 2024) -> list[dict]:
    tic = [r for r in rows if "Computa" in r.get("area_geral","") and to_int(r["ano"]) == ano]

    regioes: dict[str, dict] = defaultdict(lambda: {"fem": 0, "tot": 0})
    for r in tic:
        reg = r["regiao"]
        regioes[reg]["fem"] += to_int(r["qt_mat_fem"])
        regioes[reg]["tot"] += to_int(r["qt_mat_total"])

    return sorted([
        {
            "regiao": reg,
            "mat_fem": v["fem"],
            "mat_total": v["tot"],
            "pct_fem": round(v["fem"] / v["tot"] * 100, 1) if v["tot"] > 0 else 0,
        }
        for reg, v in regioes.items()
    ], key=lambda x: -x["pct_fem"])


# ─── Análise 4: Tendência — crescimento % fem ────────────────────────────────

def tendencia_crescimento(funil: dict) -> dict:
    anos = sorted(funil.keys())
    primeiro = anos[0]
    ultimo   = anos[-1]
    return {
        "pct_mat_fem_inicial": funil[primeiro]["pct_mat_fem"],
        "pct_mat_fem_final":   funil[ultimo]["pct_mat_fem"],
        "variacao_pp":         round(funil[ultimo]["pct_mat_fem"] - funil[primeiro]["pct_mat_fem"], 1),
        "periodo":             f"{primeiro}–{ultimo}",
    }


# ─── Geração de gráficos HTML (Plotly via template simples) ──────────────────

def gerar_html_funil(funil: dict) -> str:
    anos = sorted(funil.keys())
    pct_mat  = [funil[a]["pct_mat_fem"]  for a in anos]
    pct_ing  = [funil[a]["pct_ing_fem"]  for a in anos]
    pct_conc = [funil[a]["pct_conc_fem"] for a in anos]

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Funil Feminino — TIC Brasil</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
</head><body style="font-family:Inter,sans-serif;background:#f9f9f9;padding:20px">
<h1 style="color:#1E3A5F">Funil da Mulher na TIC — Brasil {anos[0]}–{anos[-1]}</h1>
<p style="color:#555">Fonte: INEP Censo da Educação Superior | Dados: INEP/MEC</p>
<div id="chart1"></div>
<script>
var anos = {anos};
var data = [
  {{x: anos, y: {pct_mat},  name: '% Matrículas',   mode:'lines+markers',
    line:{{color:'#1E3A5F', width:3}}, marker:{{size:8}}}},
  {{x: anos, y: {pct_ing},  name: '% Ingressantes', mode:'lines+markers',
    line:{{color:'#E91E8C', width:3, dash:'dot'}}, marker:{{size:8}}}},
  {{x: anos, y: {pct_conc}, name: '% Concluintes',  mode:'lines+markers',
    line:{{color:'#FF6B35', width:3, dash:'dash'}}, marker:{{size:8}}}},
];
var layout = {{
  title:'Participação Feminina na TIC por Etapa do Funil (%)',
  xaxis:{{title:'Ano', tickvals:{anos}}},
  yaxis:{{title:'% do total', range:[0,30]}},
  plot_bgcolor:'white', paper_bgcolor:'#f9f9f9',
  legend:{{orientation:'h', y:-0.2}},
  annotations:[{{
    x:{anos[-1]}, y:{pct_mat[-1]}, xref:'x', yref:'y',
    text:'<b>{pct_mat[-1]}% mat.</b>', showarrow:true, arrowhead:2,
    ax:30, ay:-30, font:{{color:'#1E3A5F', size:13}}
  }}]
}};
Plotly.newPlot('chart1', data, layout);
</script>
</body></html>"""


def gerar_html_evasao(evasao: dict) -> str:
    anos = sorted(evasao.keys())
    tx_fem  = [evasao[a]["tx_evasao_fem"]  for a in anos]
    tx_masc = [evasao[a]["tx_evasao_masc"] for a in anos]

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Evasão por Gênero — TIC</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
</head><body style="font-family:Inter,sans-serif;background:#f9f9f9;padding:20px">
<h1 style="color:#1E3A5F">Taxa de Evasão por Gênero — TIC Brasil</h1>
<p style="color:#888;font-size:12px">Nota: Evasão calculada como (Ingressantes − Concluintes) / Ingressantes × 100.
Pode incluir alunos que ainda estão cursando (interpretação conservadora).</p>
<div id="chart2"></div>
<script>
var data = [
  {{x:{anos}, y:{tx_fem},  name:'Feminino',  type:'bar', marker:{{color:'#E91E8C'}}}},
  {{x:{anos}, y:{tx_masc}, name:'Masculino', type:'bar', marker:{{color:'#1E3A5F'}}}},
];
var layout = {{
  barmode:'group',
  title:'Taxa de Evasão Estimada por Gênero (%)',
  xaxis:{{title:'Ano'}}, yaxis:{{title:'Taxa (%)', range:[0,100]}},
  plot_bgcolor:'white', paper_bgcolor:'#f9f9f9',
}};
Plotly.newPlot('chart2', data, layout);
</script></body></html>"""


def gerar_html_regioes(regional: list[dict], ano: int) -> str:
    regioes = [r["regiao"] for r in regional]
    pcts    = [r["pct_fem"] for r in regional]
    tots    = [r["mat_total"] for r in regional]

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<title>Distribuição Regional</title>
<script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
</head><body style="font-family:Inter,sans-serif;background:#f9f9f9;padding:20px">
<h1 style="color:#1E3A5F">% Mulheres Matriculadas em TIC por Região — {ano}</h1>
<div id="chart3"></div>
<script>
var data = [{{
  x:{regioes},
  y:{pcts},
  type:'bar',
  text:{pcts}.map(v => v+'%'),
  textposition:'outside',
  marker:{{color:{pcts}.map(v => v < 18 ? '#FF6B35' : v < 20 ? '#F5A623' : '#27AE60')}},
  customdata:{tots},
  hovertemplate:'%{{x}}<br>%Fem: %{{y}}%<br>Total matriculados: %{{customdata:,}}<extra></extra>'
}}];
var layout = {{
  title:'Participação Feminina em TIC por Região (%)',
  xaxis:{{title:'Região'}}, yaxis:{{title:'% Feminino', range:[0,30]}},
  plot_bgcolor:'white', paper_bgcolor:'#f9f9f9',
  shapes:[{{type:'line',x0:-0.5,x1:4.5,y0:19.2,y1:19.2,
    line:{{color:'#1E3A5F',width:1.5,dash:'dot'}}}}],
  annotations:[{{x:0,y:19.5,xref:'x',yref:'y',text:'média nacional 19.2%',
    showarrow:false,font:{{color:'#1E3A5F',size:11}}}}]
}};
Plotly.newPlot('chart3', data, layout);
</script></body></html>"""


# ─── Relatório Markdown de métricas ──────────────────────────────────────────

def gerar_relatorio_md(funil: dict, evasao: dict, regional: list[dict], tendencia: dict) -> str:
    anos = sorted(funil.keys())
    linhas = [
        "# Relatório de Análise — Funil da Mulher na Tech",
        "**Fonte:** INEP Censo da Educação Superior 2019–2024",
        "**Filtro:** Cursos de TIC (Computação e Tecnologias da Informação e Comunicação)",
        "",
        "## 1. Tendência de Participação Feminina",
        f"- **{tendencia['periodo']}:** de **{tendencia['pct_mat_fem_inicial']}%** para **{tendencia['pct_mat_fem_final']}%** de matrículas femininas",
        f"- Crescimento de **{tendencia['variacao_pp']} pontos percentuais** no período",
        "",
        "## 2. Funil por Ano — TIC Nacional",
        "| Ano | Mat. Total | % Fem Mat | Ing. Total | % Fem Ing | Conc. Total | % Fem Conc |",
        "|---|---|---|---|---|---|---|",
    ]

    for ano in anos:
        f = funil[ano]
        mat_tot  = f["mat_fem"]  + f["mat_masc"]
        ing_tot  = f["ing_fem"]  + f["ing_masc"]
        conc_tot = f["conc_fem"] + f["conc_masc"]
        linhas.append(
            f"| {ano} | {mat_tot:,} | **{f['pct_mat_fem']}%** | {ing_tot:,} | **{f['pct_ing_fem']}%** | {conc_tot:,} | **{f['pct_conc_fem']}%** |"
        )

    linhas += [
        "",
        "## 3. Evasão Estimada (Ingressantes → Concluintes)",
        "| Ano | Evasão Feminina | Evasão Masculina | Diferença |",
        "|---|---|---|---|",
    ]
    for ano in sorted(evasao.keys()):
        ef = evasao[ano]["tx_evasao_fem"]
        em = evasao[ano]["tx_evasao_masc"]
        if ef is not None and em is not None:
            diff = round(ef - em, 1)
            sinal = "+" if diff > 0 else ""
            linhas.append(f"| {ano} | {ef}% | {em}% | {sinal}{diff}pp |")

    linhas += [
        "",
        "> **Nota:** Taxa de evasão calculada como (Ingressantes − Concluintes) / Ingressantes.",
        "> Inclui alunos que ainda estão cursando — interpretação conservadora.",
        "",
        "## 4. Distribuição Regional (2024)",
        "| Região | % Feminino | Matrículas Femininas | Total |",
        "|---|---|---|---|",
    ]
    for r in regional:
        linhas.append(f"| {r['regiao']} | **{r['pct_fem']}%** | {r['mat_fem']:,} | {r['mat_total']:,} |")

    linhas += [
        "",
        "## 5. Narrativa do Funil (para o Pitch)",
        "",
        f"Enquanto as mulheres representam **{funil[anos[-1]]['pct_mat_fem']}% das matrículas** em cursos de TIC em {anos[-1]},",
        f"a participação cai para **{funil[anos[-1]]['pct_conc_fem']}% entre os concluintes**,",
        "evidenciando um gargalo na permanência e conclusão do curso.",
        f"O período {tendencia['periodo']} mostra crescimento de {tendencia['variacao_pp']} pontos percentuais",
        f"na entrada (de {tendencia['pct_mat_fem_inicial']}% para {tendencia['pct_mat_fem_final']}%), mas",
        "a conversão em conclusão ainda é proporcionalmente menor.",
        "",
        "## 6. Limitações e Próximos Passos",
        "- **Pay gap:** O Kaggle Salaries não possui coluna de gênero. Para análise de disparidade salarial,",
        "  adicionar RAIS/CAGED em `data/raw/` e reprocessar.",
        "- **Engenharia:** Os dados incluem 'Engenharia e profissões correlatas' — validar com o time se",
        "  cursos como Engenharia Civil devem ser excluídos.",
        "- **Evasão:** A métrica (ingressantes − concluintes) é cross-sectional, não longitudinal.",
        "  Idealmente rastrear coortes, mas INEP não disponibiliza dado individual (LGPD).",
    ]

    return "\n".join(linhas)


# ─── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Carregando dados tratados...")
    rows = load_inep()
    logger.info(f"  {len(rows)} linhas carregadas")

    logger.info("Calculando métricas...")
    funil     = funil_nacional_tic(rows)
    evasao    = evasao_por_ano(rows)
    regional  = distribuicao_regional(rows, ano=2024)
    tendencia = tendencia_crescimento(funil)

    logger.info("Gerando relatório Markdown...")
    relatorio = gerar_relatorio_md(funil, evasao, regional, tendencia)
    (REPORTS / "analise_funil.md").write_text(relatorio, encoding="utf-8")

    logger.info("Gerando gráficos HTML interativos...")
    (REPORTS / "grafico_funil.html").write_text(gerar_html_funil(funil), encoding="utf-8")
    (REPORTS / "grafico_evasao.html").write_text(gerar_html_evasao(evasao), encoding="utf-8")
    (REPORTS / "grafico_regioes.html").write_text(gerar_html_regioes(regional, 2024), encoding="utf-8")

    logger.info("Salvando métricas em JSON...")
    metricas = {
        "funil_tic": {str(k): v for k, v in funil.items()},
        "evasao":    {str(k): v for k, v in evasao.items()},
        "regional_2024": regional,
        "tendencia": tendencia,
    }
    (REPORTS / "metricas_funil.json").write_text(
        json.dumps(metricas, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Imprime resumo no terminal
    print("\n" + "="*60)
    print("  ANÁLISE CONCLUÍDA")
    print("="*60)
    print(f"\n  Tendência {tendencia['periodo']}:")
    print(f"    % Matriculas femininas: {tendencia['pct_mat_fem_inicial']}% -> {tendencia['pct_mat_fem_final']}%")
    print(f"    Crescimento: +{tendencia['variacao_pp']} pontos percentuais")
    print(f"\n  2024 — TIC (Computação):")
    f24 = funil[2024]
    print(f"    Matrículas:   {f24['mat_fem']+f24['mat_masc']:,} total | {f24['mat_fem']:,} fem ({f24['pct_mat_fem']}%)")
    print(f"    Ingressantes: {f24['ing_fem']+f24['ing_masc']:,} total | {f24['ing_fem']:,} fem ({f24['pct_ing_fem']}%)")
    print(f"    Concluintes:  {f24['conc_fem']+f24['conc_masc']:,} total | {f24['conc_fem']:,} fem ({f24['pct_conc_fem']}%)")
    print(f"\n  Arquivos gerados em reports/:")
    print("    - analise_funil.md       (relatório completo)")
    print("    - grafico_funil.html     (evolução do funil)")
    print("    - grafico_evasao.html    (evasão por gênero)")
    print("    - grafico_regioes.html   (distribuição regional)")
    print("    - metricas_funil.json    (dados para o dashboard)")
    print("="*60 + "\n")
