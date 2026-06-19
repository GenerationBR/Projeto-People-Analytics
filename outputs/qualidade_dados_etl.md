# Relatório de Qualidade de Dados — ETL

## Tabela: `fato_mercado_basemercadobrasil (brasscom+stateofdata+mckinsey)_raw`
- Linhas: 500
- Colunas: 9

## Tratamento de Outliers Salariais

### Fonte: BaseMercadoBrasil (Brasscom+StateOfData+McKinsey)
- Método: winsorization_p99
- Ação: Valores clampados para [1694.00, 45704.00]
- Linhas afetadas: 10
- P01: 1694.00 | P99: 45704.00
