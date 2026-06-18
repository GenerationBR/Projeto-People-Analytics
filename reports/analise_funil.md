# Relatório de Análise — Funil da Mulher na Tech
**Fonte educacional:** base_campus_ti_brasil.csv — dataset simulado (referência: INEP — Censo da Educação Superior)
**Filtro:** Cursos de TIC (Computação e Tecnologias da Informação e Comunicação)
**Cobertura:** Instituições do eixo Sudeste — sem cobertura regional múltipla (limitação do mock)
**Fonte de mercado:** base_mercado_tech_brasil.csv — dataset simulado (Brasscom + Tech4Humans + McKinsey)

## 1. Tendência de Participação Feminina
- **2019–2022:** de **23.0%** para **21.7%** de matrículas femininas
- Variação de **-1.3 pp (queda)** no período

## 2. Funil por Ano — TIC Nacional
| Ano | Mat. Total | % Fem Mat | Ing. Total | % Fem Ing | Conc. Total | % Fem Conc |
|---|---|---|---|---|---|---|
| 2019 | 261 | **23.0%** | 261 | **23.0%** | 67 | **25.4%** |
| 2020 | 237 | **18.6%** | 237 | **18.6%** | 70 | **22.9%** |
| 2021 | 249 | **18.1%** | 249 | **18.1%** | 71 | **14.1%** |
| 2022 | 253 | **21.7%** | 253 | **21.7%** | 69 | **13.0%** |

## 3. Evasão Estimada (Ingressantes → Concluintes)
| Ano | Evasão Feminina | Evasão Masculina | Diferença |
|---|---|---|---|
| 2019 | 71.7% | 75.1% | -3.4pp |
| 2020 | 63.6% | 72.0% | -8.4pp |
| 2021 | 77.8% | 70.1% | +7.7pp |
| 2022 | 83.6% | 69.7% | +13.9pp |

> **Nota:** Taxa de evasão calculada como (Ingressantes − Concluintes) / Ingressantes.
> Inclui alunos que ainda estão cursando — interpretação conservadora.

## 4. Distribuição Regional (2022)
| Região | % Feminino | Matrículas Femininas | Total |
|---|---|---|---|
| Sudeste | **21.7%** | 55 | 253 |

## 5. Narrativa do Funil (para o Pitch)

Enquanto as mulheres representam **21.7% das matrículas** em cursos de TIC em 2022,
a participação cai para **13.0% entre os concluintes**,
evidenciando um gargalo na permanência e conclusão do curso.
O período 2019–2022 registrou variação de -1.3 pp (queda)
na participação feminina entre ingressantes (de 23.0% para 21.7%),
mas a conversão em conclusão ainda é proporcionalmente menor.

## 6. Limitações e Próximos Passos

### Limitações do dataset atual

- **Cobertura regional restrita:** `base_campus_ti_brasil.csv` cobre apenas instituições do Sudeste  (USP, UFRJ, UFMG, PUC-SP, FIAP, FATEC, Insper). A seção 4 reflete apenas essa região —  conclusões sobre distribuição nacional de gênero não são generalizáveis sem dados das demais regiões.
- **Matrículas ≈ Ingressantes:** O mock não possui histórico longitudinal de matrícula anual.  A coluna `qt_mat_*` é aproximada pelos ingressantes de cada coorte, o que sub-representa  estudantes que permanecem matriculados em anos subsequentes.
- **Evasão cross-sectional:** A taxa `(ingressantes − concluintes) / ingressantes` compara coortes  diferentes em vez de rastrear o mesmo grupo ao longo do tempo. O valor inclui alunos que ainda  estão cursando, o que infla a evasão aparente — interpretação conservadora.
- **Gap salarial na `v_pay_gap`:** A view agrega médias por cargo × nível × gênero. A média de médias  diverge do gap calculado em nível individual (~27% embutido no mock — ref. Brasscom).  Para análise precisa, usar os microdados de `base_mercado_tech_brasil.csv` diretamente.

### Próximos passos

- **Gargalo de liderança (McKinsey):** `fato_mercado_tech_brasil` no DuckDB modela sub-representação  feminina progressiva em Diretor e CTO/CIO.  Consulta sugerida: `SELECT nivel, genero, SUM(n) FROM fato_mercado_tech_brasil GROUP BY nivel, genero ORDER BY nivel;`
- **Análise D&I em vagas LinkedIn:** `fato_vagas_linkedin.csv` e a view `v_vagas_di` estão prontos no DuckDB.  Dos 200 anúncios (ago/2025–mai/2026), **21 (10,5%)** têm iniciativa D&I —  8 afirmativas, 7 exclusivas e 6 afirmativas trans-inclusivas.
- **Teste T de significância salarial:** Aplicar `scipy.stats.ttest_ind` (Welch) nos salários individuais  de `base_mercado_tech_brasil.csv`, controlando por cargo e nível, para validar estatisticamente  o gap de ~27% (ref. Brasscom).
- **Integração Power BI:** As views `v_funil_nacional`, `v_pay_gap` e `v_vagas_di` do DuckDB  alimentam as duas visões do dashboard — 'A Base' (funil educacional) e 'O Mercado'  (pay gap + liderança + D&I em vagas).