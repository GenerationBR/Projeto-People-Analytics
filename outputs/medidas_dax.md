
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
