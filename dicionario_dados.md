# Dicionário de Dados — People Analytics DEI

Documentação de todos os datasets na pasta `data/treated/`, com descrição de cada coluna, valores possíveis e origem.

---

## Índice

1. [base_mercado_tech_brasil.csv](#1-base_mercado_tech_brasilcsv)
2. [base_mercado_tech_mundial.csv](#2-base_mercado_tech_mundialcsv)
3. [base_campus_ti_brasil.csv](#3-base_campus_ti_brasilcsv)
4. [base_mercado_dados_2021_brasil.csv](#4-base_mercado_dados_2021_brasilcsv)
5. [generation_linkedin_vagas_tecnologia.csv](#5-generation_linkedin_vagas_tecnologiacsv)

---

## 1. `base_mercado_tech_brasil.csv`

**Status:** Mockado (sintético)
**Volume:** 1.000 linhas
**Período:** 2019–2024
**Descrição:** Base sintética gerada com distribuições baseadas em proporções reais do mercado de tecnologia brasileiro. Usada exclusivamente para análise exploratória. Nenhuma estatística do dashboard é derivada deste arquivo.

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| `id` | Inteiro | Identificador único do registro | 1 a 1000 |
| `pais` | Texto | País de referência da observação | `Brasil` |
| `ano` | Inteiro | Ano da observação | `2019`, `2020`, `2021`, `2022`, `2023`, `2024` |
| `genero` | Texto | Gênero declarado do/a profissional | `Feminino`, `Masculino` |
| `cargo` | Texto | Nível hierárquico na carreira de tecnologia | `Estagiário`, `Júnior`, `Pleno`, `Sênior`, `Gerente`, `Diretor`, `C-Level` |
| `setor` | Texto | Área de atuação dentro de tecnologia | `Dados`, `Desenvolvimento`, `Gestão`, `Infraestrutura`, `Produto` |
| `salario_brl` | Decimal | Salário mensal bruto em reais (R$) | Numérico contínuo (ex: `1592.11`, `11534.17`) |
| `anos_experiencia` | Inteiro | Tempo de experiência profissional acumulado na área | `0` a `20+` |
| `promovido_ultimo_ano` | Texto | Indica se o/a profissional foi promovido/a nos últimos 12 meses | `Sim`, `Não` |
| `nivel_escolaridade` | Texto | Grau de formação acadêmica mais alto concluído | `Ensino Médio/Fundamental Incompleto`, `Ensino Médio Completo`, `Superior Incompleto`, `Superior Completo`, `Pós-graduação/Mestrado/Doutorado` |
| `transicao_carreira` | Texto | Indica se o/a profissional migrou de outra área para tecnologia | `Sim`, `Não` |

---

## 2. `base_mercado_tech_mundial.csv`

**Status:** Mockado (sintético)
**Volume:** 500 linhas
**Período:** 2024 (snapshot único)
**Descrição:** Base sintética com dados globais de mercado para comparação internacional. Representa quatro contextos geográficos: EUA, União Europeia, Reino Unido e uma agregação global. Uso estritamente exploratório.

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| `id` | Inteiro | Identificador único do registro | 1 a 500 |
| `pais` | Texto | Região geográfica de referência | `Global`, `EUA`, `UE`, `UK` |
| `ano` | Inteiro | Ano da observação | `2024` |
| `genero` | Texto | Gênero declarado do/a profissional | `Feminino`, `Masculino` |
| `cargo` | Texto | Função/cargo na área de tecnologia | `Designer UX/UI`, `Cientista de Dados`, `Desenvolvedor de Software`, `Engenheiro de IA/ML`, `Engenheiro DevOps`, `Analista de Cibersegurança`, `CTO/CIO`, `C-Level` |
| `setor` | Texto | Área de atuação dentro de tecnologia | `Dados`, `Desenvolvimento`, `Gestão`, `Infraestrutura`, `Produto` |
| `salario_usd` | Inteiro | Salário anual bruto em dólares americanos (US$) | Numérico contínuo (ex: `82719`, `114769`) |
| `anos_experiencia` | Inteiro | Tempo de experiência profissional acumulado na área | `1` a `20+` |
| `promovido_ultimo_ano` | Texto | Indica se o/a profissional foi promovido/a nos últimos 12 meses | `Sim`, `Não` |
| `transicao_carreira` | Texto | Indica se o/a profissional migrou de outra área para tecnologia | `Sim`, `Não` |

> **Atenção:** O salário neste arquivo está em dólares anuais (USD/ano), diferente da base brasileira que usa reais mensais (BRL/mês).

---

## 3. `base_campus_ti_brasil.csv`

**Status:** Real
**Fonte:** INEP — Censo da Educação Superior (microdados tratados)
**Volume:** 1.200 linhas
**Período:** Ingressantes de 2019 a 2024
**Descrição:** Cada linha representa um/a estudante de curso de tecnologia em uma das instituições monitoradas. Os dados foram filtrados para os 5 cursos de computação relevantes ao mercado de software/dados, com recorte de modalidade diferenciado por curso (presencial para ADS/CC/SI/ES; EaD para Ciência de Dados).

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| `id_estudante` | Inteiro | Identificador único do registro de matrícula | 1 a 1200 |
| `genero` | Texto | Gênero declarado no Censo INEP | `Feminino`, `Masculino` |
| `curso` | Texto | Nome do curso de graduação | `Análise e Desenvolvimento de Sistemas`, `Ciência da Computação`, `Ciência de Dados`, `Engenharia de Software`, `Sistemas de Informação` |
| `instituicao` | Texto | Instituição de ensino superior | `FATEC`, `FIAP`, `Insper`, `PUC-SP`, `UFMG`, `UFRJ`, `USP` |
| `ano_ingresso` | Inteiro | Ano de ingresso no curso | `2019`, `2020`, `2021`, `2022`, `2023`, `2024` |
| `concluiu` | Inteiro | Indica se o/a estudante concluiu o curso até a última atualização disponível | `1` (concluiu), `0` (não concluiu / em andamento) |

> **Nota metodológica:** Cursos excluídos do escopo: Engenharia de Computação, Redes de Computadores, Jogos Digitais e demais habilitações fora do eixo direto de software/dados. Ciência de Dados usa modalidade EaD por ser majoritariamente ofertada nessa modalidade no Brasil.

---

## 4. `base_mercado_dados_2021_brasil.csv`

**Status:** Real
**Fonte:** State of Data Brasil 2021 — Data Hackers (microdados públicos)
**Volume:** 2.645 respondentes
**Período:** 2021
**Descrição:** Pesquisa de mercado com profissionais de dados no Brasil. Cada linha é um/a respondente. As colunas seguem a numeração original do questionário (P0, P1, P2...), com o nome da pergunta embutido no cabeçalho no formato `('código', 'Texto da pergunta')`. A seguir, as seções e colunas mais relevantes para a análise DEI.

### Identificação do respondente

| Código | Pergunta | Descrição | Exemplos de resposta |
|---|---|---|---|
| `P0 / id` | ID | Identificador único do respondente | Alfanumérico |
| `P1_a` | Idade | Idade em anos | `25`, `38`, `42` |
| `P1_a_a` | Faixa de idade | Faixa etária agrupada | `25-29`, `30-34`, `35-39` |
| `P1_b` | Gênero | Gênero declarado | `Masculino`, `Feminino`, `Prefiro não informar`, `Outro` |
| `P1_e` | Estado onde mora | Estado de residência atual | `São Paulo (SP)`, `Rio de Janeiro (RJ)` |
| `P1_e_a` | UF | Sigla da unidade federativa | `SP`, `RJ`, `MG` |
| `P1_e_b` | Região | Macrorregião do Brasil | `Sudeste`, `Nordeste`, `Sul`, `Norte`, `Centro-Oeste` |
| `P1_g_b` | Região de origem | Macrorregião onde cresceu | `Sudeste`, `Nordeste`, etc. |
| `P1_g_c` | Mudou de Estado? | Se mudou de estado para trabalhar | `0` (não), `1` (sim) |
| `P1_h` | Nível de ensino | Grau de escolaridade mais alto concluído | `Pós-graduação`, `Superior Completo`, `Ensino Médio` |
| `P1_i` | Área de formação | Curso ou área de graduação | `Ciência da Computação`, `Engenharia`, `Economia`, `Química` |

### Situação profissional

| Código | Pergunta | Descrição | Exemplos de resposta |
|---|---|---|---|
| `P2_a` | Situação atual de trabalho | Vínculo empregatício atual | `Empregado (CLT)`, `Empreendedor ou Empregado (CNPJ)`, `Desempregado` |
| `P2_b` | Setor | Setor de atuação da empresa | `Financeiro`, `Tecnologia`, `Saúde`, `Varejo`, `Governo`, `Consultoria` |
| `P2_c` | Número de funcionários | Porte da empresa | `de 1 a 5`, `de 6 a 10`, `de 101 a 500`, `mais de 3.000` |
| `P2_d` | Gestor? | Ocupa cargo de gestão | `1` (sim), vazio (não) |
| `P2_e` | Cargo como gestor | Nível do cargo de gestão | `Supervisor/Coordenador`, `Gerente`, `Sócio ou C-level` |
| `P2_f` | Cargo atual | Cargo formal na empresa | Texto livre |
| `P2_g` | Nível | Senioridade | `Júnior`, `Pleno`, `Sênior`, `Especialista` |
| `P2_h` | Faixa salarial | Remuneração mensal bruta declarada (faixas) | `de R$ 1.001/mês a R$ 2.000/mês`, `de R$ 8.001/mês a R$ 12.000/mês`, `Acima de R$ 40.001/mês` |
| `P2_i` | Tempo de experiência em dados | Anos na área de dados | `Menos de 1 ano`, `de 1 a 2 anos`, `Mais de 10 anos` |
| `P2_j` | Experiência prévia em TI | Tempo em TI/Engenharia de Software antes de dados | `Não tive experiência em TI`, `de 1 a 2 anos`, `Mais de 10 anos` |
| `P2_k` | Satisfação na empresa | Nível de satisfação geral com o empregador atual | `1` (satisfeito), texto alternativo (insatisfeito) |
| `P2_q` | Forma de trabalho atual | Modalidade de trabalho praticada | `Modelo 100% presencial`, `Modelo híbrido flexível`, `Modelo 100% remoto` |
| `P2_r` | Forma de trabalho ideal | Modalidade de trabalho preferida | Mesmos valores de `P2_q` |

### Insatisfação e motivos de troca

| Código | Pergunta | Descrição |
|---|---|---|
| `P2_l` | Principal motivo de insatisfação | Razão principal de insatisfação com o empregador atual |
| `P2_l_a` | Falta de crescimento | Ausência de oportunidade de crescimento no emprego atual (0/1) |
| `P2_l_b` | Salário abaixo do mercado | Salário não compatível com o mercado (0/1) |
| `P2_l_c` | Relação com líder | Má relação com líder ou gestor (0/1) |
| `P2_l_f` | Clima de trabalho ruim | Ambiente ou clima organizacional negativo (0/1) |
| `P2_l_g` | Falta de maturidade analítica | Empresa sem cultura de dados consolidada (0/1) |
| `P2_m` | Participou de entrevistas? | Se participou de processos seletivos nos últimos 6 meses | `Sim, fui aprovado e mudei de emprego`, `Não participei` |
| `P2_n` | Pretende mudar de emprego? | Intenção de troca de emprego nos próximos 6 meses | `Sim`, `Não estou buscando`, `Não, pretendo ficar` |

### Critérios de decisão sobre onde trabalhar

Colunas binárias (`0`/`1`) que indicam se o critério é considerado importante pelo/a respondente:

| Código | Critério |
|---|---|
| `P2_o_a` | Remuneração / Salário |
| `P2_o_b` | Benefícios |
| `P2_o_c` | Propósito do trabalho e da empresa |
| `P2_o_d` | Flexibilidade de trabalho remoto |
| `P2_o_e` | Ambiente e clima de trabalho |
| `P2_o_f` | Oportunidade de aprendizado |
| `P2_o_g` | Plano de carreira e crescimento profissional |
| `P2_o_h` | Maturidade da empresa em tecnologia e dados |
| `P2_o_i` | Qualidade dos gestores e líderes |
| `P2_o_j` | Reputação da empresa no mercado |

### Tecnologias e ferramentas utilizadas

| Código | Pergunta | Descrição |
|---|---|---|
| `P4_a` | Atuação principal | Função efetiva no dia a dia (nem sempre igual ao cargo formal) | `Analista de Dados`, `Cientista de Dados`, `Engenheiro de Dados`, `Gestor` |
| `P4_d_*` | Linguagens utilizadas | Colunas binárias para cada linguagem (Python, SQL, R, Java, Scala…) |
| `P4_e` | Linguagem mais usada | Linguagem de programação predominante no trabalho |
| `P4_f_*` | Bancos de dados utilizados | Colunas binárias (MySQL, PostgreSQL, BigQuery, Snowflake, MongoDB…) |
| `P4_g_*` | Cloud utilizada | Colunas binárias (AWS, GCP, Azure, On Premise…) |
| `P4_h_*` | Ferramentas de BI utilizadas | Colunas binárias (Power BI, Tableau, Looker, Metabase…) |

### Seções especializadas por perfil

| Seção | Público-alvo | Conteúdo |
|---|---|---|
| `P3_*` | Gestores | Desafios de gestão, responsabilidades, papéis no time de dados |
| `P5_*` | Desempregados em busca | Oportunidade buscada, tempo de busca, dificuldades |
| `P6_*` | Engenheiros de Dados | Pipelines, ETL, Data Lake, Data Warehouse, ferramentas |
| `P7_*` | Analistas de Dados | Dashboards, ETL, ferramentas de análise, autonomia das áreas de negócio |
| `P8_*` | Cientistas de Dados | Técnicas de ML, deploy, MLOps, ferramentas de ciência de dados |
| `P9_*` | Todos | Canais Data Hackers acompanhados (blog, podcast, newsletter) |

> **Nota:** O uso desta base no dashboard se limita a análises de gênero (`P1_b`), faixa salarial (`P2_h`), cargo de gestão (`P2_d`, `P2_e`, `P2_g`) e tempo de experiência (`P2_i`). As colunas P3 a P9 não são utilizadas no dashboard atual.

---

## 5. `generation_linkedin_vagas_tecnologia.csv`

**Status:** Real
**Fonte:** Webscraping do LinkedIn, cedido pela Generation Brasil
**Volume:** 395 linhas (vagas de tecnologia)
**Período:** agosto/2025 a abril/2026
**Descrição:** Cada linha representa uma vaga de emprego mapeada no LinkedIn. O dataset foi filtrado para incluir **somente vagas de tecnologia** — foram excluídas vagas de Comercial e Suporte Técnico. Das 395 vagas, 7 são afirmativas (1,8%): 5 para PCD e 2 para mulheres.

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| `id` | Inteiro | Identificador único da vaga | 1 a 395 |
| `company_name` | Texto | Nome da empresa que publicou a vaga | Texto livre (ex: `SulAmérica`, `Mobly`, `Accenture Brasil`) |
| `job_title` | Texto | Título da vaga como publicado no LinkedIn | Texto livre (ex: `Analista de Dados`, `Desenvolvedor Java Junior`) |
| `location` | Texto | Localização da vaga (cidade e estado) | Texto livre — pode estar vazio para vagas remotas (ex: `São Paulo, SP`, `Fortaleza, Ceará`) |
| `description` | Texto | Conteúdo completo da página da vaga no LinkedIn | Texto bruto capturado por scraping — inclui descrição, requisitos e vagas relacionadas; pode estar vazio para vagas importadas diretamente de planilha |
| `inserted_at` | Data/hora | Data e hora em que a vaga foi coletada | Formato `YYYY-MM-DD HH:MM:SS` — meses coletados: ago/25, set/25, out/25, mar/26, abr/26 |
| `search_title` | Texto | Termo de busca usado no LinkedIn para encontrar a vaga | `Analista de Dados`, `Desenvolvedor Java`, `Desenvolvedor JavaScript`, `Java`, `Javascript` — vazio para vagas importadas de planilha |
| `afirmativa` | Inteiro | Indica se a vaga é explicitamente afirmativa para grupos minorizados | `1` (vaga afirmativa), `0` (vaga convencional) |
| `tipo_di` | Texto | Tipo de ação afirmativa quando `afirmativa = 1` | `Mulheres`, `PCD` (Pessoa com Deficiência) — vazio quando `afirmativa = 0` |

### Distribuição por mês (`inserted_at`)

| Mês | Total de vagas | Vagas afirmativas |
|---|---|---|
| Agosto / 2025 | 177 | 3 |
| Setembro / 2025 | 17 | 0 |
| Outubro / 2025 | 11 | 0 |
| Março / 2026 | 3 | 0 |
| Abril / 2026 | 187 | 4 |
| **Total** | **395** | **7** |

---

*Última atualização: junho/2026 · People Analytics & DEI — Generation Brasil*
