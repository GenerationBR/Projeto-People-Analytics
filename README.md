# People Analytics & DE&I — A Trajetória Feminina do Câmpus ao Mercado Tech

Dashboard interativo que mapeia a representação feminina no setor de tecnologia brasileiro, da educação superior ao mercado de trabalho. Cruza dados educacionais (INEP), de mercado (State of Data Brasil 2021, Brasscom 2025), benchmarks globais (WomenHack 2026) e dados reais de vagas afirmativas da Generation Brasil.

---

## Estrutura do repositório

O repositório completo — incluindo arquivos que existem apenas localmente e não sobem para o GitHub — está descrito abaixo. Itens marcados com `[local]` são ignorados pelo `.gitignore`.

```
Projeto People Analytics/
│
├── README.md                                           # Este arquivo
├── .gitignore                                          # Ignora: .venv/, data/, node_modules/, dist/, __pycache__/
│
├── DAX.txt                                             # Fórmulas DAX utilizadas no Power BI para filtrar
│                                                       # e modelar os dados pertinentes às análises de gênero
│
├── Notebook.ipynb                                      # Notebook Python com três blocos principais:
│                                                       #   1. Limpeza e tratamento dos microdados do State of Data Brasil
│                                                       #   2. Web scraping de vagas no LinkedIn com Selenium
│                                                       #   3. Teste T de Student para comprovação estatística
│                                                       #      da diferença salarial entre homens e mulheres
│
├── sqlScripts.sql                                      # Queries SQL utilizadas no banco de dados da
│                                                       # Generation Brasil para extração e filtragem
│                                                       # das vagas afirmativas por mês e tipo de ação
│
├── dicionario_dados.md                                 # Dicionário detalhado de todos os datasets
│                                                       # da pasta data/treated/, com descrição de cada coluna
│
├── People Analytics & DE&I - A Trajetória             # Documento de texto com o briefing do projeto:
│   Feminina do Câmpus ao Mercado Tech.txt             # contexto, objetivos e narrativa central da análise
│
│
├── dashboard-dei/                                      # Aplicação web React (Vite)
│   ├── .gitignore                                      # Ignora: node_modules/, dist/
│   ├── index.html                                      # Ponto de entrada HTML da aplicação
│   ├── vite.config.js                                  # Configuração do Vite (base path para GitHub Pages)
│   ├── package.json                                    # Dependências npm (React, Recharts, Lucide)
│   ├── package-lock.json                               # Lock de versões das dependências
│   ├── eslint.config.js                                # Regras de linting para o projeto React
│   │
│   ├── public/
│   │   └── logo.PNG                                    # Logo do projeto (exibida no topo do dashboard)
│   │
│   ├── src/
│   │   ├── main.jsx                                    # Entry point React — monta o componente App no DOM
│   │   ├── App.jsx                                     # Componente raiz — renderiza o Dashboard
│   │   └── Dashboard.jsx                               # Arquivo principal: todos os dados, gráficos,
│   │                                                   # páginas e estilos da aplicação estão aqui
│   │
│   ├── node_modules/                   [local]         # Pacotes npm instalados — não versionado
│   └── dist/                           [local]         # Build de produção gerado pelo Vite — não versionado
│
│
├── data/                               [local]         # Todos os dados — pasta inteira ignorada pelo git
│   │
│   ├── raw/                                            # Dados brutos, originais, sem transformação
│   │   │
│   │   ├── Microdados do Censo da Educação Superior 2019/
│   │   ├── Microdados do Censo da Educação Superior 2020/
│   │   ├── Microdados do Censo da Educação Superior 2021/
│   │   ├── microdados_educação_superior_2022/
│   │   ├── microdados_censo_da_educacao_superior_2023/
│   │   └── microdados_censo_da_educacao_superior_2024/
│   │       # Microdados oficiais do INEP (2019–2024). Cada pasta contém:
│   │       #   dados/      → CSVs com matrículas (CURSOS e IES)
│   │       #   Anexos/     → Dicionário de dados (.xlsx) e questionários (.pdf)
│   │       #   leia-me/    → Notas técnicas e informativas do INEP
│   │
│   │   ├── brasscom_salario_medio.py                   # Dados de salário médio TIC por gênero (2019–2024)
│   │   │                                               # extraídos da RAIS via relatório Brasscom 2025
│   │   ├── brasscom_escolaridade_genero.py             # Escolaridade em cargos de liderança TIC por gênero
│   │   │                                               # Brasscom 2025 — "penalidade da qualificação"
│   │   ├── brasscom_participacao_feminina_TIC.py       # Participação feminina na força de trabalho TIC
│   │   │                                               # por ano — Brasscom 2025
│   │   ├── brasscom_cargo_diretoria.py                 # Representação feminina em cargos de diretoria
│   │   │                                               # e gerência no setor TIC — Brasscom 2025
│   │   │
│   │   ├── V.1 pre programa_Java 84 (1).xlsx           # Pesquisa pré-programa da turma Java 84 (Generation)
│   │   ├── V.2 in program II_ Java 84 (1).xlsx         # Pesquisa durante o programa — módulo II
│   │   ├── V.3 in program III_Java 84 (1).xlsx         # Pesquisa durante o programa — módulo III
│   │   │                                               # Utilizadas para o gráfico de perfil socioeconômico
│   │   │                                               # dos/as alunos/as no dashboard (página A Base)
│   │   │
│   │   ├── emp_find_jobs_robot.csv                     # Output bruto do web scraping de vagas no LinkedIn
│   │   │                                               # antes do tratamento — gerado pelo Notebook.ipynb
│   │   │
│   │   ├── Relatorio-Diversidade-v3.pdf                # Relatório de Diversidade e Inclusão (referência)
│   │   ├── Women in Tech Statistics 2026 _             # Página HTML arquivada do relatório WomenHack 2026
│   │   │   Gender Gap Data, Pay Equity & Trends.html   # (compilado de BLS, WEF, Zippia, Stanford AI, etc.)
│   │   └── women_in_tech_2026_texto.txt                # Versão em texto puro do relatório WomenHack 2026
│   │
│   └── treated/                                        # Dados tratados e prontos para análise
│       ├── base_campus_ti_brasil.csv                   # [Real] Microdados INEP 2019–2024 tratados
│       │                                               # 1.200 linhas · 5 cursos de computação · 7 IES
│       ├── base_mercado_dados_2021_brasil.csv          # [Real] Microdados State of Data Brasil 2021
│       │                                               # 2.645 respondentes · profissionais de dados no BR
│       ├── generation_linkedin_vagas_tecnologia.csv    # [Real] Vagas tech mapeadas no LinkedIn
│       │                                               # 395 vagas · ago/25–abr/26 · 7 afirmativas
│       ├── base_mercado_tech_brasil.csv                # [Mockado] 1.000 linhas sintéticas do mercado BR
│       │                                               # Apenas exploratório — não usado no dashboard
│       └── base_mercado_tech_mundial.csv               # [Mockado] 500 linhas sintéticas — benchmark global
│                                                       # Apenas exploratório — não usado no dashboard
│
│
├── scripts/                                            # Scripts Python de auditoria e geração de dados
│   ├── audit_campus.py                                 # Valida e audita os microdados INEP tratados
│   ├── audit_mercado_dados_2021.py                     # Audita o dataset State of Data 2021
│   ├── audit_dados_2021_full.py                        # Auditoria completa do State of Data (todas as colunas)
│   ├── audit_mercado_mundial.py                        # Audita a base sintética mundial
│   ├── audit_raw_linkedin.py                           # Audita os dados brutos de scraping do LinkedIn
│   ├── audit_raw_linkedin_detail.py                    # Auditoria detalhada das vagas — título e empresa
│   ├── fix_linkedin_vagas.py                           # Corrige e padroniza a base de vagas do LinkedIn
│   └── gerar_csvs_tech.py                              # Gera as bases sintéticas (mockadas) de mercado
│
└── .venv/                              [local]         # Ambiente virtual Python — não versionado
                                                        # Instalar com: python -m venv .venv
```

---

## Fontes de dados

| Fonte | Cobertura | Uso no dashboard |
|---|---|---|
| INEP — Censo da Educação Superior | 2019–2024 | Página "A Base" |
| State of Data Brasil 2021 (Data Hackers) | n = 2.645 | Página "O Mercado" |
| Brasscom — Relatório DEI TIC 2025 | Brasil, 2024 | O Mercado / TIC no Brasil / gap salarial no Simulador RH |
| WomenHack — Women in Tech Report 2026 | Global (compilado) | Comparativo global |
| Generation Brasil — webscraping LinkedIn | ago/25–abr/26 | Vagas afirmativas |
| Robert Half — Guia Salarial 2025 | Brasil | Salários base por nível no Simulador RH |
| BCB — Banco Central do Brasil (série 433) | 2015–presente | Simulador RH — correção inflacionária / poder de compra |
| PwC Global Tech Report 2025 | Global | Funil / interesse de carreira |
| Accenture — Women in the Workplace 2024 | Global | Funil / saída de carreira |
| ISACA — State of Cybersecurity 2024 | Global | Funil / cultura organizacional |
| NBER 2024 | Global | Funil / viés de seleção |

> O WomenHack 2026 é um relatório compilado — cada estatística tem fonte própria (BLS, WEF, Zippia, Stanford AI, McKinsey, Deloitte, etc.). As fontes primárias são citadas individualmente em cada rodapé de gráfico no dashboard.

---

## Dados reais vs. dados mockados

| Arquivo | Status | Observação |
|---|---|---|
| `data/treated/base_mercado_dados_2021_brasil.csv` | **Real** | Microdados State of Data Brasil 2021 |
| `data/treated/base_campus_ti_brasil.csv` | **Real** | Microdados INEP 2019–2024 (tratados) |
| `data/treated/generation_linkedin_vagas_tecnologia.csv` | **Real** | Dado cedido pela Generation Brasil |
| `data/treated/base_mercado_tech_brasil.csv` | **Mockado** | 1.000 linhas sintéticas — uso exploratório apenas |
| `data/treated/base_mercado_tech_mundial.csv` | **Mockado** | 500 linhas sintéticas — uso exploratório apenas |
| `data/raw/brasscom_*.py` | **Real** | Salários e escolaridade TIC — RAIS via Brasscom 2025 |

> Os arquivos mockados foram gerados com distribuições baseadas em proporções reais, mas **não devem ser citados como dados primários**. Nenhuma estatística do dashboard é derivada deles.

---

## Premissas metodológicas

### 1. Cursos INEP considerados

Foram selecionados apenas 5 cursos de computação diretamente ligados ao mercado de tecnologia:

| Sigla | Nome completo |
|---|---|
| ADS | Análise e Desenvolvimento de Sistemas |
| CC | Ciência da Computação |
| SI | Sistemas de Informação |
| ES | Engenharia de Software |
| CD | Ciência de Dados |

**Cursos excluídos:** Engenharia de Computação, Redes de Computadores, Jogos Digitais e demais habilitações fora do escopo direto de software/dados.

### 2. Modalidade de ensino por curso (INEP)

- **Presencial:** ADS, CC, SI, ES
- **EaD:** CD (Ciência de Dados)

**Razão:** Ciência de Dados é majoritariamente ofertada a distância no Brasil. Usar presencial para CD reduziria artificialmente a amostra e distorceria o percentual feminino.

### 3. Baseline TIC — denominador do IRF

O **Índice de Representatividade Feminina (IRF)** usa como denominador fixo:

> **39,1%** — participação feminina na força de trabalho do setor TIC no Brasil (Brasscom, 2025, dados 2024).

**Fórmula:**
```
IRF = % feminino na categoria ÷ 39,1%
```
- IRF = 1,0 → representação igual ao setor TIC em geral
- IRF < 1,0 → sub-representada em relação ao setor
- IRF > 1,0 → sobre-representada em relação ao setor

### 4. Liderança em TIC (Brasscom)

Consideramos como **cargos de liderança** apenas Diretoria e Gerência no setor TIC, conforme definição do Relatório DEI Brasscom 2025.

### 5. Cálculo do gap salarial — State of Data Brasil 2021

O State of Data coleta **faixas salariais declaradas**, não salários exatos. O gap de 17,1% foi estimado calculando a **média dos pontos médios de cada faixa** para mulheres e homens separadamente. Valor deve ser lido como estimativa conservadora.

Para a comprovação estatística da diferença salarial, foi aplicado um **Teste T de Student** (bicaudal, variâncias independentes) no `Notebook.ipynb`, resultando em rejeição da hipótese nula (p < 0,05).

### 6. Cálculo do degrau quebrado (Broken Rung)

Calculado diretamente sobre a base do State of Data Brasil 2021 (n = 2.645):

- **13,6%** das profissionais de Dados declararam cargo de gestão
- **20,6%** dos profissionais de Dados declararam cargo de gestão

Resultado: para cada 100 homens promovidos a gestão, **~66 mulheres** chegam ao mesmo nível.

### 7. Funil de trajetória — etapas e fontes

O gráfico de trajetória mistura populações e momentos distintos. Cada etapa é independente:

| Etapa | Fonte | % feminino |
|---|---|---|
| Ingressantes em Computação | INEP 2024 | 18,4% |
| Profissionais na área de Dados | State of Data Brasil 2021 (n = 2.645) | 18,7% |
| Cargos de gestão em Dados | State of Data Brasil 2021 (n = 508 gestores) | 13,2% |

C-Suite e CTO/liderança técnica foram **removidos** do funil: vêm de benchmark global incompatível com as demais etapas e criavam falsa impressão de "recuperação" que não corresponde à realidade brasileira.

### 8. Mercado de Dados — State of Data Brasil 2021

- **n total:** 2.645 respondentes · **n mulheres:** 493 · **n homens:** 2.144
- Edição de 2021 utilizada (não edições mais recentes) por ser a única com microdados disponíveis e auditados pela equipe.

### 9. Salário TIC — série histórica Brasscom (2019–2024)

Dados reais extraídos da RAIS (Ministério do Trabalho) via Brasscom. Não são estimativas.

- **2023:** equidade atingiu 73,3% — crescimento feminino +4,3% vs. +0,5% masculino
- **2024:** equidade recuou para 70,2% — crescimento masculino +13,8% vs. +8,9% feminino

### 10. Escolaridade em liderança TIC — a "penalidade da qualificação"

Mulheres em cargos de Diretoria/Gerência TIC são mais escolarizadas do que os homens nas mesmas funções:

| Nível | Mulheres | Homens |
|---|---|---|
| Pós-grad. / Mestrado / Doutorado | 12% | 10% |
| Superior Completo | 72% | 69% |
| Superior Incompleto | 8% | 10% |
| Ensino Médio | 7% | 6% |

### 11. % feminino por função — benchmark global (WomenHack 2026)

Utilizado exclusivamente como **comparativo global**, sem extrapolação para o mercado brasileiro.

| Função | % feminino | Fonte primária |
|---|---|---|
| UX/UI Design | 46% | Zippia 2025 |
| Product Management | 35% | Hired 2025 |
| Data Science | 30% | WEF 2025 |
| Software Engineering | 22% | BLS 2025 |
| AI / Machine Learning | 22% | Stanford AI Index 2025 |
| DevOps / Cloud | 14% | Statista 2025 |
| Cibersegurança | 12% | (ISC)² 2025 |

### 12. Saída de carreira — Accenture 2024 e ISACA 2024

- **50% das mulheres** saem da tech antes dos 35 anos — Accenture, Women in the Workplace 2024
- **+45% de velocidade de saída feminina** vs. masculina — Accenture 2024
- **56% citam cultura organizacional** como razão — ISACA, State of Cybersecurity 2024

### 13. Interesse de carreira — PwC 2025 e NBER 2024

- **27% das jovens mulheres** consideram carreira em tech vs. **62% dos jovens homens** — PwC Global Tech Report 2025
- **−30% de callbacks** para currículos com nome feminino vs. masculino em experimento controlado — NBER 2024

### 14. Vagas afirmativas — Generation Brasil

- Fonte: webscraping de vagas no LinkedIn (Selenium) cedido pela Generation Brasil
- Escopo: **somente vagas de tecnologia** (excluídas Comercial e Suporte Técnico)
- Meses: ago/25, set/25, out/25, mar/26, abr/26
- Total analisado: **395 vagas tech**, das quais **7 afirmativas (1,8%)**
- Distribuição: PCD = 5 vagas, Mulheres = 2 vagas

### 15. Simulador RH — salários base e gap salarial

O Simulador RH combina duas fontes independentes para calcular os salários estimados por cargo e área:

**Salários base (masculino de referência):** Robert Half — Guia Salarial 2025, mercado tech Brasil. Utiliza o ponto médio da faixa reportada para cada nível de senioridade:

| Cargo | Salário base (M) · referência Robert Half 2025 |
|---|---|
| Estagiário | R$ 2.000 |
| Júnior | R$ 5.000 |
| Pleno | R$ 8.500 |
| Sênior | R$ 13.000 |
| Gerente | R$ 18.000 |
| Diretor | R$ 28.000 |
| CTO/CIO | R$ 42.000 |

Um **multiplicador por área** ajusta o salário base conforme o posicionamento relativo de cada área dentro do setor TIC (derivado de dados estruturais Brasscom 2025):

| Área | Multiplicador |
|---|---|
| Dados | 1,00 |
| Desenvolvimento | 0,92 |
| Gestão | 1,15 |
| Infraestrutura | 0,88 |
| UX/UI | 0,80 |

**Gap de gênero (Brasscom 2025 · RAIS/MTE):** aplicado sobre o salário masculino ajustado para estimar o salário feminino. Fórmula:

```
salário_F = salário_M × (1 − gap)
```

- **Área de Dados:** gap de 17,1% — State of Data Brasil 2021 (n = 2.645)
- **Demais áreas:** gap de 29,8% — Brasscom 2025 (TIC geral · RAIS/MTE)

### 16. Simulador RH — poder de compra (BCB/IPCA)

O Simulador conecta em tempo real a **API do Banco Central do Brasil** (série 433 — IPCA variação mensal) para calcular a perda de poder de compra do salário feminino estimado desde 2022:

- **Endpoint:** `api.bcb.gov.br/dados/serie/bcdata.sgs.433/dados`
- **Período:** janeiro/2022 até o último mês disponível
- **Cálculo:** fator de correção acumulado = produto de `(1 + IPCA_mensal/100)` para cada mês do período
- **Aplicação:** o salário feminino calculado é corrigido pelo fator acumulado para mostrar o equivalente em valores atuais — indicando o reajuste mínimo necessário para preservar poder de compra

---

## Decisões de design e produto

- **Toda estatística tem fonte citada** no rodapé do gráfico ou no subtítulo do card.
- **Dados nacionais e globais são separados** em seções distintas para evitar que benchmarks internacionais sejam lidos como realidade brasileira.
- **Jargão técnico é sempre traduzido** — ex: "taxa de attrition" → "velocidade de saída da área".
- **C-Suite e CTO foram removidos do funil** por inconsistência metodológica (fonte global + população incompatível).

---

## Como rodar

### Dashboard React

```bash
cd dashboard-dei
npm install
npx vite              # desenvolvimento → http://localhost:5173
npx vite build        # build de produção (pasta dist/)
```

### Scripts Python

```bash
# Criar e ativar ambiente virtual
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac

# Exemplos
python scripts/audit_campus.py
python scripts/audit_mercado_dados_2021.py

# Para o Notebook (scraping + análise estatística)
jupyter notebook Notebook.ipynb
```

> O web scraping do LinkedIn (Notebook.ipynb) requer o ChromeDriver instalado e compatível com a versão do Chrome.

---

## Equipe

Projeto desenvolvido como parte do programa **Generation Brasil** — People Analytics e Diversidade, Equidade & Inclusão.
