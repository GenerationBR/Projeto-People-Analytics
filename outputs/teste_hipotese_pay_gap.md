# Relatório — Teste de Hipótese: Gender Pay Gap

## Hipóteses
- **H0:** Não há diferença salarial significativa entre homens e mulheres
- **H1:** Existe diferença salarial significativa entre homens e mulheres

## Verificação de Pressupostos
*(executado automaticamente — ver log do agente)*

## Resultado do Teste
| Campo | Valor |
|---|---|
| Teste aplicado | t-test de Student |
| Estatística | 17.9201 |
| p-valor | 0.0000 |
| Intervalo de Confiança (95%) | [2087.16, 2600.60] |
| Tamanho de Efeito (Cohen's d) | 1.240 → **grande** |
| α | 0.05 |
| Rejeita H0? | **SIM** |

## Interpretação
Rejeitamos H0 (α=0.05). Salário médio masc: R$ 8,473.75 | fem: R$ 6,129.87. Gender Pay Gap: 27.7%. Tamanho de efeito (Cohen's d): 1.240 → grande. Significância estatística confirma diferença salarial. Lembre-se: significância ≠ relevância prática — avalie o contexto.

## Nota Metodológica
- Grupos comparados controlam cargo, senioridade e região para isolar efeito de gênero.
- Significância estatística (p < α) ≠ relevância prática — avaliar Cohen's d em conjunto.
- Limitações de amostra registradas acima devem constar no pitch e no dashboard.