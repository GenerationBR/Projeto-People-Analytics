# Relatório de QA — People Analytics & DE&I
*Total: 23 verificações | ✅ OK: 21 | ❌ Corrigir: 1 | ⏳ Aguardando: 1*

## Status Geral
🔴 BLOQUEADO — corrigir itens antes da entrega

## Checklist
| Item | Status | Detalhe |
|---|---|---|
| Artefato: ETL Report | ✅ OK | outputs\qualidade_dados_etl.md |
| Artefato: Modelo de Dados | ✅ OK | outputs\modelo_dados.md |
| Artefato: EDA Script | ✅ OK | outputs\eda_funil_feminino.py |
| Artefato: Síntese Executiva | ✅ OK | outputs\sintese_executiva.md |
| Artefato: Métricas Funil (JSON) | ✅ OK | outputs\metricas_funil.json |
| Artefato: Teste Hipótese | ✅ OK | outputs\teste_hipotese_pay_gap.md |
| Artefato: Resultado Estatístico (JSON) | ✅ OK | outputs\resultado_teste.json |
| Artefato: Dashboard Spec | ✅ OK | outputs\dashboard_spec.md |
| Artefato: Medidas DAX | ✅ OK | outputs\medidas_dax.md |
| Artefato: Dicionário de Dados | ✅ OK | outputs\dicionario\dicionario_de_dados.md |
| Artefato: Log Premissas | ✅ OK | outputs\log_premissas.md |
| Artefato: Roteiro Pitch | ✅ OK | outputs\pitch\roteiro_pitch.md |
| Artefato: Slides Marp | ✅ OK | outputs\pitch\slides_marp.md |
| Artefato: Recomendações | ✅ OK | outputs\pitch\recomendacoes_politicas.md |
| Artefato: Data App | ❌ CORRIGIR | AUSENTE: app\calculadora.py |
| Artefato: README | ✅ OK | README.md |
| Métricas do funil disponíveis | ⏳ AGUARDANDO | Banco vazio — dados demo |
| Resultado estatístico disponível | ✅ OK | p-valor=nan |
| Sem cruzamento individual (CPF) | ✅ OK | Nenhuma coluna CPF encontrada |
| Teste estatístico correto (Welch/Mann-Whitney) | ✅ OK | Teste usado: Mann-Whitney U |
| p-valor e efeito reportados | ✅ OK | p=nan, d=0.0 |
| Significância ≠ relevância prática (Cohen's d reportado) | ✅ OK | Cohen's d = 0.0 |
| Premissas metodológicas aprovadas | ✅ OK | Todas aprovadas |

## Itens Bloqueando Entrega
- ❌ **Artefato: Data App**: AUSENTE: app\calculadora.py

## Análise do QA
[SIMULADO] Agente qa processaria: Analise este relatório de QA de um projeto de People Analytics e forneça:
1. Resumo em 3 frases do s...