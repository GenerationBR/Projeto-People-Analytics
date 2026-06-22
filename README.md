# People Analytics & DE&I — Desigualdade de Gênero no Setor de Tecnologia

Dashboard interativo que mapeia a representação feminina no setor de tecnologia brasileiro, da educação superior ao mercado de trabalho, cruzando dados educacionais (INEP), de mercado (State of Data Brasil 2021, Brasscom 2025) e benchmarks globais (WomenHack 2026).

---

## Estrutura do repositório

```
.
├── dashboard-dei/          # Aplicação React (Vite)
│   └── src/
│       └── Dashboard.jsx   # Arquivo principal — dados e visualizações
├── data/
│   ├── raw/                # Microdados INEP (2019–2024), scripts Brasscom, WomenHack
│   └── treated/            # CSVs tratados prontos para análise
├── scripts/                # Scripts de auditoria e geração de dados
└── README.md
```

---

## Fontes de dados

| Fonte | Cobertura | Uso no dashboard |
|---|---|---|
| INEP — Censo da Educação Superior | 2019–2024 | Página "A Base" |
| State of Data Brasil 2021 (Data Hackers) | n = 2.645 | Página "O Mercado" |
| Brasscom — Relatório DEI TIC 2025 | Brasil, 2024 | O Mercado / TIC no Brasil |
| WomenHack — Women in Tech Report 2026 | Global (compilado) | Comparativo Global |
| Generation Brasil — webscraping LinkedIn | ago/25–abr/26 | Vagas afirmativas |
| PwC Global Tech Report 2025 | Global | Funil / interesse de carreira |
| Accenture — Women in the Workplace 2024 | Global | Funil / saída de carreira |
| ISACA — State of Cybersecurity 2024 | Global | Funil / cultura como razão |
| NBER 2024 | Global | Funil / viés de seleção |

> O WomenHack 2026 é um relatório compilado — cada estatística tem fonte própria (BLS, WEF, Zippia, Stanford AI, McKinsey, Deloitte, etc.). As fontes primárias são citadas individualmente em cada rodapé de gráfico no dashboard.

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

**Cursos excluídos:** Engenharia de Computação, Redes de Computadores, Jogos Digitais e demais habilitações fora do escopo direto de software/dados foram desconsiderados para manter foco e comparabilidade com as demais fontes (State of Data, Brasscom), que também não os abrangem de forma homogênea.

### 2. Modalidade de ensino por curso (INEP)

A filtragem de modalidade foi diferenciada por curso:

- **Presencial:** ADS, CC, SI, ES
- **EaD:** CD (Ciência de Dados)

**Razão:** Ciência de Dados é um curso majoritariamente ofertado a distância no Brasil. Usar apenas a modalidade presencial para CD reduziria artificialmente a amostra e distorceria o % feminino (o perfil de gênero difere entre modalidades). Para os demais cursos, a oferta presencial é dominante e mais comparável ao mercado de trabalho tradicional.

### 3. Baseline TIC — denominador do IRF

O **Índice de Representatividade Feminina (IRF)** usa como denominador fixo:

> **39,1%** — participação feminina na força de trabalho do setor TIC no Brasil (Brasscom, 2025, dados 2024).

**Razão:** representa o "teto de vidro esperado" do setor — o quanto de representação seria esperado se não houvesse nenhuma barreira adicional além do acesso ao emprego. Usar esse número como base permite comparar subgrupos (por função, cargo ou área) em relação ao que o próprio setor já oferece, e não em relação à população geral.

**Fórmula:**
```
IRF = % feminino na categoria ÷ 39,1%
```
- IRF = 1,0 → representação igual ao setor TIC em geral
- IRF < 1,0 → sub-representada em relação ao setor
- IRF > 1,0 → sobre-representada em relação ao setor

### 4. Liderança em TIC (Brasscom)

Consideramos como **cargos de liderança** apenas Diretoria e Gerência no setor TIC, conforme definição do próprio Relatório DEI Brasscom 2025 (segmenta os dados dessa forma). Cargos de nível Sênior ou Staff não foram incluídos nessa definição por ausência de dados granulares nessa fonte.

### 5. Cálculo do gap salarial — State of Data Brasil 2021

O State of Data Brasil 2021 coleta **faixas salariais declaradas** (ex: "R$ 6.001 a R$ 8.000"), não salários exatos. O gap de 17,1% foi estimado calculando a **média dos pontos médios de cada faixa** para mulheres e para homens separadamente.

**Limitação reconhecida:** o salário mediano de ambos os gêneros cai dentro da mesma faixa (R$ 6–8k), o que subestima o gap real. O valor deve ser lido como estimativa conservadora.

### 6. Cálculo do degrau quebrado (Broken Rung)

Calculado diretamente sobre a base do State of Data Brasil 2021 (n = 2.645):

- **13,6%** das profissionais de Dados declararam ocupar cargo de gestão
- **20,6%** dos profissionais de Dados declararam ocupar cargo de gestão

Resultado: para cada 100 homens promovidos a cargos de gestão em Dados, **apenas ~66 mulheres** chegam ao mesmo nível — a "66 em 100" usada no dashboard.

### 7. Funil de trajetória — etapas e fontes

O gráfico de trajetória mistura populações e momentos distintos. Cada etapa é independente:

| Etapa | Fonte | % feminino |
|---|---|---|
| Ingressantes em Computação | INEP 2024 (5 cursos, filtro de modalidade) | 18,4% |
| Profissionais na área de Dados | State of Data Brasil 2021 (n = 2.645) | 18,7% |
| Cargos de gestão em Dados | State of Data Brasil 2021 (n = 508 gestores) | 13,2% |

**Decisão tomada em conjunto:** C-Suite em tecnologia (29%, WomenHack 2026) e CTO/liderança técnica (15%, WomenHack 2026) foram **removidos** do gráfico de trajetória. O motivo é metodológico: essas estatísticas vêm de benchmark global (não nacional), de populações incompatíveis com as demais etapas, e criavam uma falsa impressão de "recuperação" ao final do funil que não corresponde à realidade do mercado brasileiro de dados.

**O funil não é uma coorte** — não é o mesmo grupo de pessoas acompanhado ao longo do tempo. É uma leitura transversal de hiatos de representação em diferentes etapas da trajetória típica.

### 8. Mercado de Dados (State of Data Brasil 2021)

- **n total:** 2.645 respondentes
- **n mulheres:** 493 (para análises de modelo de trabalho e experiência)
- **n homens:** 2.144
- **Recorte:** profissionais que atuam com Dados no Brasil

O State of Data 2021 foi usado (e não edições mais recentes) porque é a edição com os microdados disponíveis e auditados pela equipe.

### 9. Salário TIC — série histórica Brasscom (S1)

Os salários médios TIC por gênero (2019–2024) são dados reais extraídos da RAIS (Relação Anual de Informações Sociais, Ministério do Trabalho) via Brasscom. **Não são estimativas nem dados de pesquisa amostral.**

**Narrativa-chave validada:**
- 2023: equidade atingiu 73,3% (melhor marca histórica) — crescimento feminino de +4,3% vs +0,5% masculino
- 2024: equidade recuou para 70,2% — crescimento masculino de +13,8% vs +8,9% feminino

### 10. Escolaridade em liderança TIC — a "penalidade da qualificação"

Mulheres em cargos de Diretoria/Gerência TIC são mais escolarizadas do que os homens nas mesmas funções:

| Nível | Mulheres | Homens |
|---|---|---|
| Pós-grad. / Mestrado / Doutorado | 12% | 10% |
| Superior Completo | 72% | 69% |
| Superior Incompleto | 8% | 10% |
| Ensino Médio | 7% | 6% |

Isso evidencia que mulheres precisam de mais qualificação para ocupar os mesmos cargos — fenômeno que denominamos "penalidade da qualificação".

### 11. % feminino por função (benchmark global — WomenHack 2026)

Utilizado exclusivamente como **comparativo global**, sem extrapolação para o mercado brasileiro. As funções e percentuais são:

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

- **50% das mulheres saem da tech antes dos 35 anos** — Accenture, Women in the Workplace 2024 (pesquisa global)
- **+45% de velocidade de saída feminina vs. masculina** — taxa de rotatividade comparada proporcionalmente (Accenture 2024)
- **56% citam cultura organizacional** — ISACA, State of Cybersecurity 2024 (extrapolado para tech em geral)

Esses dados foram posicionados no **Funil**, não no Mercado, porque explicam *por que o funil estreita no meio* — são dados de saída da trajetória, não de perfil de mercado.

### 13. Interesse de carreira — PwC 2025 e NBER 2024

- **27% das jovens mulheres** consideram carreira em tech, vs. **62% dos jovens homens** — PwC Global Tech Report 2025
- **−30% de callbacks** para currículos com nome feminino vs. masculino, em experimento controlado — NBER 2024

Posicionados no Funil como "causas raiz antes da trajetória" — ocorrem antes mesmo da entrada no ensino superior.

### 14. Vagas afirmativas — Generation Brasil

- Fonte: webscraping de vagas no LinkedIn, cedido pela Generation Brasil
- Escopo: **somente vagas de tecnologia** (excluídas Comercial e Suporte Técnico)
- Meses com dados disponíveis: ago/25, set/25, out/25, mar/26, abr/26
- Total analisado: **395 vagas tech**, das quais **7 afirmativas (1,8%)**
- Distribuição: PCD = 5 vagas, Mulheres = 2 vagas

---

## Dados reais vs. dados mockados

| Arquivo | Status | Observação |
|---|---|---|
| `data/treated/base_mercado_dados_2021_brasil.csv` | **Real** | Microdados State of Data Brasil 2021 |
| `data/treated/base_campus_ti_brasil.csv` | **Real** | Microdados INEP 2019–2024 (tratados) |
| `data/treated/generation_linkedin_vagas_tecnologia.csv` | **Real** | Dado cedido pela Generation Brasil |
| `data/treated/base_mercado_tech_brasil.csv` | **Mockado** | 1.000 linhas sintéticas geradas com proporções reais — uso analítico/exploratório apenas |
| `data/treated/base_mercado_tech_mundial.csv` | **Mockado** | 500 linhas sintéticas (2024, "Global") — uso analítico/exploratório apenas |
| `data/raw/brasscom_salario_medio.py` | **Real** | Salários RAIS/MTE via Brasscom 2025 |
| `data/raw/brasscom_escolaridade_genero.py` | **Real** | Escolaridade em liderança TIC, Brasscom 2025 |
| `data/raw/brasscom_participacao_feminina_TIC.py` | **Real** | Participação feminina TIC, Brasscom 2025 |

> Os arquivos mockados (`base_mercado_tech_brasil.csv` e `base_mercado_tech_mundial.csv`) foram gerados com distribuições baseadas em proporções reais, mas **não devem ser citados como dados primários**. Nenhuma estatística do dashboard é derivada deles.

---

## Decisões de design e produto

- **Toda estatística tem fonte citada** no rodapé do gráfico ou no `sub` do card — nenhum número aparece sem atribuição.
- **Captions curtos e explicativos** acompanham cada gráfico para que o dado seja compreensível sem contexto prévio.
- **Jargão técnico é sempre traduzido** — ex: "taxa de attrition" é apresentada como "velocidade de saída da área" com explicação do que significa proporcionalmente.
- **Dados nacionais e globais são separados** em seções distintas ("TIC no Brasil" vs. "Comparativo global") para evitar que benchmarks internacionais sejam lidos como realidade brasileira.
- **C-Suite e CTO foram removidos do funil** de trajetória por inconsistência metodológica (fonte global + população incompatível), mesmo sendo dados válidos — foram realocados para a seção de comparativo global no Mercado.

---

## Como rodar

### Dashboard (React)

```bash
cd dashboard-dei
npm install
npx vite          # desenvolvimento — http://localhost:5173
npx vite build    # build de produção
```

> Nota: o build de produção tem um erro pré-existente com `react-is` no Rolldown. O servidor de desenvolvimento funciona normalmente com ESBuild.

### Scripts Python (análises)

```bash
# Criar ambiente virtual
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac

pip install -r requirements.txt   # se houver

# Exemplo: rodar script de auditoria do State of Data
python scripts/audit_mercado_dados_2021.py
```

---

## Equipe

Projeto desenvolvido como parte do programa **Generation Brasil** — trilha de People Analytics e Diversidade, Equidade & Inclusão.
