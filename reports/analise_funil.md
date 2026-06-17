# Relatório de Análise — Funil da Mulher na Tech
**Fonte:** INEP Censo da Educação Superior 2019–2024
**Filtro:** Cursos de TIC (Computação e Tecnologias da Informação e Comunicação)

## 1. Tendência de Participação Feminina
- **2019–2024:** de **13.5%** para **19.2%** de matrículas femininas
- Crescimento de **5.7 pontos percentuais** no período

## 2. Funil por Ano — TIC Nacional
| Ano | Mat. Total | % Fem Mat | Ing. Total | % Fem Ing | Conc. Total | % Fem Conc |
|---|---|---|---|---|---|---|
| 2019 | 354,160 | **13.5%** | 183,895 | **14.6%** | 44,891 | **13.6%** |
| 2020 | 399,675 | **14.8%** | 227,281 | **16.6%** | 51,567 | **14.0%** |
| 2021 | 464,269 | **16.3%** | 272,329 | **19.0%** | 54,596 | **14.8%** |
| 2022 | 594,580 | **17.9%** | 410,454 | **20.4%** | 61,760 | **15.3%** |
| 2023 | 724,485 | **18.7%** | 472,830 | **20.6%** | 80,316 | **17.5%** |
| 2024 | 800,222 | **19.2%** | 489,067 | **21.3%** | 100,488 | **19.2%** |

## 3. Evasão Estimada (Ingressantes → Concluintes)
| Ano | Evasão Feminina | Evasão Masculina | Diferença |
|---|---|---|---|
| 2019 | 77.3% | 75.3% | +2.0pp |
| 2020 | 80.9% | 76.6% | +4.3pp |
| 2021 | 84.3% | 78.9% | +5.4pp |
| 2022 | 88.7% | 84.0% | +4.7pp |
| 2023 | 85.6% | 82.3% | +3.3pp |
| 2024 | 81.5% | 78.9% | +2.6pp |

> **Nota:** Taxa de evasão calculada como (Ingressantes − Concluintes) / Ingressantes.
> Inclui alunos que ainda estão cursando — interpretação conservadora.

## 4. Distribuição Regional (2024)
| Região | % Feminino | Matrículas Femininas | Total |
|---|---|---|---|
|  | **38.9%** | 164 | 422 |
| Sudeste | **20.1%** | 82,920 | 412,969 |
| Norte | **19.5%** | 7,282 | 37,350 |
| Centro-Oeste | **19.0%** | 14,500 | 76,416 |
| Nordeste | **18.0%** | 24,999 | 138,779 |
| Sul | **17.9%** | 24,066 | 134,286 |

## 5. Narrativa do Funil (para o Pitch)

Enquanto as mulheres representam **19.2% das matrículas** em cursos de TIC em 2024,
a participação cai para **19.2% entre os concluintes**,
evidenciando um gargalo na permanência e conclusão do curso.
O período 2019–2024 mostra crescimento de 5.7 pontos percentuais
na entrada (de 13.5% para 19.2%), mas
a conversão em conclusão ainda é proporcionalmente menor.

## 6. Limitações e Próximos Passos
- **Pay gap:** O Kaggle Salaries não possui coluna de gênero. Para análise de disparidade salarial,
  adicionar RAIS/CAGED em `data/raw/` e reprocessar.
- **Engenharia:** Os dados incluem 'Engenharia e profissões correlatas' — validar com o time se
  cursos como Engenharia Civil devem ser excluídos.
- **Evasão:** A métrica (ingressantes − concluintes) é cross-sectional, não longitudinal.
  Idealmente rastrear cortes, mas INEP não disponibiliza dado individual (LGPD).