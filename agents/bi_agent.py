"""Agente 5 — Engenheiro de BI (Dashboard Agent — copiloto Power BI)."""

import logging
from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)


_DAX_TEMPLATES = """
## Medidas DAX — Dashboard People Analytics

### Visão "A Base" (Educação)

```dax
% Mulheres Matriculadas =
DIVIDE(
    CALCULATE([Total Matrículas], dim_genero[genero] = "Feminino"),
    [Total Matrículas]
)

Total Matrículas = SUM(fato_educacao[qt_matriculas])

Taxa de Evasão Feminina % =
DIVIDE(
    CALCULATE(SUM(fato_educacao[qt_evasao]), dim_genero[genero] = "Feminino"),
    CALCULATE(SUM(fato_educacao[qt_matriculas]), dim_genero[genero] = "Feminino")
) * 100

YoY Matrículas Femininas =
VAR AnoAtual = CALCULATE([Total Matrículas], dim_genero[genero] = "Feminino")
VAR AnoAnterior = CALCULATE(
    [Total Matrículas],
    dim_genero[genero] = "Feminino",
    DATEADD(dim_tempo[ano], -1, YEAR)
)
RETURN DIVIDE(AnoAtual - AnoAnterior, AnoAnterior) * 100
```

### Visão "O Mercado"

```dax
Gender Pay Gap % =
VAR SalarioH = CALCULATE([Salário Médio], dim_genero[genero] = "Masculino")
VAR SalarioM = CALCULATE([Salário Médio], dim_genero[genero] = "Feminino")
RETURN DIVIDE(SalarioH - SalarioM, SalarioH) * 100

Salário Médio = AVERAGE(fato_mercado[salario_medio])

% Mulheres em Liderança =
DIVIDE(
    CALCULATE(SUM(fato_mercado[qt_empregados]),
              dim_genero[genero] = "Feminino",
              dim_cargo[eh_lideranca] = TRUE),
    CALCULATE(SUM(fato_mercado[qt_empregados]),
              dim_cargo[eh_lideranca] = TRUE)
) * 100

% Mulheres Empregadas em Tech =
DIVIDE(
    CALCULATE(SUM(fato_mercado[qt_empregados]), dim_genero[genero] = "Feminino"),
    SUM(fato_mercado[qt_empregados])
) * 100
```
"""


class BIAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o Engenheiro de BI (copiloto de Power BI). A partir do modelo de dados e das
métricas validadas, especifique um dashboard com DUAS visões: "A Base" (educação) e
"O Mercado".

Entregue:
- Modelo semântico (relacionamentos entre fatos e dimensões).
- Medidas DAX prontas (% mulheres matriculadas/formadas, taxa de evasão, % liderança,
  Gender Pay Gap %).
- Layout de cada página (visuais, filtros/segmentações, hierarquias ano>região).
- Recomendações de UX e acessibilidade de cores.
Você NÃO opera a interface do Power BI: produza especificação e código DAX que um analista
implementa, ou gere os artefatos suportados. Garanta que toda métrica venha de fonte
validada — sem números inventados.
"""

    def __init__(self, output_dir: str = "outputs"):
        super().__init__("bi", output_dir=output_dir)

    def generate_dashboard_spec(self) -> str:
        return self.ask_llm(
            """Crie a especificação completa do dashboard Power BI para o projeto People Analytics
sobre trajetória feminina na tecnologia.

ESTRUTURA OBRIGATÓRIA (2 visões):

VISÃO 1 — "A Base" (Dados Educacionais INEP):
- Evolução temporal de matrículas femininas em cursos Tech (linha por ano)
- Funil: matriculadas → ingressantes → concluintes → evasão (gráfico de funil)
- Heatmap por região e gênero
- Filtros: Ano (segmentação), Região, Categoria de curso Tech

VISÃO 2 — "O Mercado" (RAIS + Kaggle):
- % Mulheres em Tech vs total (cartão KPI + tendência)
- Gender Pay Gap por cargo e região (barras divergentes)
- Participação feminina em liderança (medidor/gauge)
- Top 10 cargos com maior gap (tabela ranqueada)
- Filtros: Ano, Região, Cargo, Nível hierárquico

Para cada página forneça:
1. Lista de visuais com tipo (gráfico de linha, barras, cartão KPI, etc.)
2. Campos de cada visual (eixos, valores, legenda)
3. Filtros/segmentações
4. Paleta de cores acessível (contrast ratio ≥ 4.5:1) com hex codes
5. Relacionamentos Power BI (fato-dimensão)

Inclua aviso: "Este agente não opera a interface do Power BI. Implemente conforme especificação." """
        )

    def generate_semantic_model(self) -> str:
        return self.ask_llm(
            """Descreva o modelo semântico do Power BI para este projeto:

Tabelas disponíveis no DuckDB (data/analytics.duckdb):
- fato_educacao, fato_mercado (fatos)
- dim_tempo, dim_regiao, dim_genero, dim_curso_tech, dim_cargo (dimensões)
- v_funil_educacao, v_pay_gap, v_lideranca (views)

Forneça:
1. Como importar as tabelas do DuckDB para o Power BI (via ODBC ou conector)
2. Diagrama de relacionamentos (texto, formato: Tabela[coluna] → Tabela[coluna])
3. Configurações de relacionamento: cardinalidade e direção de filtro cruzado
4. Quais views usar diretamente vs quais fatos + DAX são preferíveis"""
        )

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("BI Agent iniciado")

        spec = self.generate_dashboard_spec()
        spec_path = self.save_output("dashboard_spec.md", spec)

        dax_path = self.save_output("medidas_dax.md", _DAX_TEMPLATES)

        semantic = self.generate_semantic_model()
        semantic_path = self.save_output("modelo_semantico_powerbi.md", semantic)

        return self.build_message(
            to_agent="docs",
            task_id="T-005",
            status="done",
            artifacts=[
                {"type": "spec", "path": str(spec_path)},
                {"type": "dax", "path": str(dax_path)},
                {"type": "semantic_model", "path": str(semantic_path)},
            ],
            assumptions=[
                "Agente de BI é COPILOTO — não opera a interface do Power BI",
                "Toda métrica tem origem rastreável no banco analítico validado",
                "Paleta de cores com acessibilidade (contrast ratio ≥ 4.5:1)",
                "Zero dados inventados — placeholders usados onde dados ainda não estão disponíveis",
            ],
            open_questions=[
                "Confirmar se a equipe tem licença Power BI Pro para publicar online",
                "Validar paleta de cores com time antes de implementar",
            ],
        )
