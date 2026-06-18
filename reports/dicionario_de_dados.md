# Dicionário de Dados — Projeto People Analytics & DE&I
**A Trajetória Feminina do Câmpus ao Mercado Tech**

> **Versão:** 1.0 | **Data:** 2026-06-18
> **Pipeline:** `etl_pipeline.py` → `data/treated/` + `analytics.duckdb` → `analise.py` → `reports/`

---

## 1. Visão Geral da Arquitetura

```
data/raw/                          etl_pipeline.py           data/treated/
├── base_campus_ti_brasil.csv  ──► etl_campus()          ──► fato_educacao_tech_agregado.csv
├── base_mercado_tech_brasil.csv ► etl_mercado_brasil()  ──► fato_mercado_tech_brasil.csv
└── generation_linkedin_vagas_  ► etl_linkedin()         ──► fato_vagas_linkedin.csv
    tecnologia.csv
                                        │
                                        ▼
                                 analytics.duckdb
                                 ├── fato_educacao_tech      (tabela)
                                 ├── fato_mercado_tech_brasil (tabela)
                                 ├── fato_vagas_linkedin      (tabela)
                                 ├── v_funil_nacional         (view)
                                 ├── v_funil_por_regiao       (view)
                                 ├── v_pay_gap                (view)
                                 └── v_vagas_di               (view)
                                        │
                                        ▼
                                   analise.py
                                 ├── reports/analise_funil.md
                                 ├── reports/grafico_funil.html
                                 ├── reports/grafico_evasao.html
                                 ├── reports/grafico_regioes.html
                                 └── reports/metricas_funil.json
```

---

## 2. Dados Brutos (`data/raw/`)

### 2.1 `base_campus_ti_brasil.csv`
**Descrição:** Registros individuais de estudantes de cursos de TIC em instituições do Sudeste.
**Formato:** CSV, 1.000 linhas, 7 colunas.
**Fonte de referência:** INEP — Censo da Educação Superior (dataset simulado para fins pedagógicos).
**Cobertura:** Anos de ingresso 2019–2022 | Apenas instituições do Sudeste.

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| `id_estudante` | INTEGER | Identificador único do estudante (sem dado pessoal real) | 1–1000 |
| `genero` | VARCHAR | Gênero autodeclarado | `Masculino`, `Feminino` |
| `curso` | VARCHAR | Nome do curso de graduação | Análise e Desenvolvimento de Sistemas, Ciência da Computação, Data Science, Engenharia de Software, Sistemas de Informação |
| `instituicao` | VARCHAR | Sigla da instituição de ensino | USP, UFRJ, UFMG, PUC-SP, FIAP, FATEC, Insper |
| `ano_ingresso` | INTEGER | Ano em que o estudante ingressou no curso | 2019, 2020, 2021, 2022 |
| `concluiu` | INTEGER | Flag de conclusão do curso | `1` = concluiu, `0` = não concluiu (inclui cursando) |
| `trabalha_na_area` | INTEGER | Flag de atuação profissional na área de TIC | `1` = sim, `0` = não |

**Limitação documentada:** Todas as instituições pertencem à região Sudeste. Não há cobertura das demais regiões do Brasil.

---

### 2.2 `base_mercado_tech_brasil.csv`
**Descrição:** Registros individuais de profissionais de tecnologia, com salários, cargos e indicadores de carreira.
**Formato:** CSV, 800 linhas, 9 colunas.
**Fontes de referência:**
- Brasscom — Relatório de Diversidade (variável `salario_base`: gap intencional de ~27% entre gêneros)
- Tech4Humans — Artigo Mulheres na Tecnologia (variáveis `cargo`, `nivel`/`setor`)
- McKinsey — Women in the Workplace (variáveis `promovido_ultimo_ano`, lógica de sub-representação em Diretoria/CTO)

| Coluna | Tipo | Descrição | Valores possíveis |
|---|---|---|---|
| `id_profissional` | INTEGER | Identificador único do profissional | 1–800 |
| `genero` | VARCHAR | Gênero autodeclarado | `Masculino`, `Feminino` |
| `cargo` | VARCHAR | Nível hierárquico atual | Estagiário, Júnior, Pleno, Sênior, Especialista, Gerente, Diretor, CTO/CIO |
| `setor` | VARCHAR | Área de atuação dentro da empresa | Dados, Desenvolvimento, Gestão, Infraestrutura, Produto, UX/UI |
| `salario_base` | FLOAT | Salário bruto mensal em R$ (após winsorização p99 no ETL) | Valores contínuos; outliers acima do p99 substituídos pelo p99 |
| `anos_experiencia` | INTEGER | Anos totais de experiência profissional em tech | 0–n |
| `tempo_empresa_meses` | INTEGER | Tempo de permanência na empresa atual, em meses | 0–n |
| `promovido_ultimo_ano` | VARCHAR | Indica se o profissional foi promovido nos últimos 12 meses | `Sim`, `Não` |
| `transicao_carreira` | VARCHAR | Indica se o profissional migrou de outra área para tech | `Sim`, `Não` |

**Padrão embutido (intencional):** Gap salarial médio de ~27% entre gêneros (ref. Brasscom) e sub-representação feminina progressiva nos níveis Diretor e CTO/CIO (ref. McKinsey).

---

### 2.3 `generation_linkedin_vagas_tecnologia.csv`
**Descrição:** Anúncios de vagas de emprego em tecnologia obtidos via web scraping do LinkedIn e cedidos pela **Generation Brasil** à equipe do projeto para fins de análise.
**Formato:** CSV, 200 linhas, 6 colunas.
**Origem:** O dataset foi coletado e disponibilizado pela Generation Brasil — organização sem fins lucrativos que atua na formação de profissionais de tecnologia. A coleta foi realizada pela própria Generation e entregue à equipe já estruturada; nenhum scraping foi executado diretamente pela equipe do projeto.
**Cobertura temporal:** Agosto de 2025 a maio de 2026.

| Coluna | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `id` | INTEGER | Identificador sequencial da vaga | 1–200 |
| `company_name` | VARCHAR | Nome fictício da empresa anunciante | Pixel Systems, CodeWave |
| `job_title` | VARCHAR | Título da vaga conforme anunciado | Desenvolvedor(a) Back-end Júnior |
| `location` | VARCHAR | Localização ou modalidade de trabalho | São Paulo, SP / Remoto - Brasil |
| `description` | VARCHAR | Texto da descrição da vaga (curto, 1–2 frases) | "Programa afirmativo para mulheres." |
| `inserted_at` | DATETIME | Data e hora de inserção no dataset | 2025-08-02 10:54:00 |

> **Nota de origem:** Este dataset foi cedido pela Generation Brasil à equipe do projeto. A coleta no LinkedIn foi realizada pela Generation; a equipe recebeu o arquivo já estruturado e não executou scraping diretamente.

---

## 3. Dados Tratados (`data/treated/`)

### 3.1 `fato_educacao_tech_agregado.csv`
**Origem:** Agregação de `base_campus_ti_brasil.csv` via `etl_pipeline.py → aggregate_campus()`.
**Grão:** Uma linha por combinação de Ano × Região × Área CINE.
**Formato:** CSV, 4 linhas (1 por ano × 1 região Sudeste × 1 área TIC).

| Coluna | Tipo | Descrição |
|---|---|---|
| `ano` | INTEGER | Ano de ingresso da coorte |
| `regiao` | VARCHAR | Nome da região geográfica (ex.: Sudeste) |
| `co_regiao` | INTEGER | Código numérico da região (3 = Sudeste) |
| `area_geral` | VARCHAR | Área CINE completa: "Computação e Tecnologias da Informação e Comunicação (TIC)" |
| `qt_mat_fem` | INTEGER | Quantidade de matrículas femininas\* |
| `qt_mat_masc` | INTEGER | Quantidade de matrículas masculinas\* |
| `qt_ing_fem` | INTEGER | Quantidade de ingressantes femininas |
| `qt_ing_masc` | INTEGER | Quantidade de ingressantes masculinos |
| `qt_conc_fem` | INTEGER | Quantidade de concluintes femininas |
| `qt_conc_masc` | INTEGER | Quantidade de concluintes masculinos |
| `qt_mat_total` | INTEGER | Total de matrículas (fem + masc)\* |
| `qt_ing_total` | INTEGER | Total de ingressantes (fem + masc) |
| `qt_conc_total` | INTEGER | Total de concluintes (fem + masc) |
| `pct_mat_fem` | FLOAT | % de matrículas femininas sobre o total\* |
| `pct_ing_fem` | FLOAT | % de ingressantes femininas sobre o total |
| `pct_conc_fem` | FLOAT | % de concluintes femininas sobre o total |
| `tx_evasao_fem_pct` | FLOAT | Taxa de evasão estimada feminina: `(ing_fem − conc_fem) / ing_fem × 100` |
| `tx_evasao_masc_pct` | FLOAT | Taxa de evasão estimada masculina: `(ing_masc − conc_masc) / ing_masc × 100` |

> **\* Premissa:** `qt_mat_* = qt_ing_*` — matrículas aproximadas por ingressantes (o mock não possui histórico longitudinal anual de matrícula).

---

### 3.2 `fato_mercado_tech_brasil.csv`
**Origem:** Agregação de `base_mercado_tech_brasil.csv` via `etl_pipeline.py → aggregate_mercado()`.
**Grão:** Uma linha por combinação de Cargo × Nível × Gênero × Região.
**Formato:** CSV, 13 linhas.

| Coluna | Tipo | Descrição |
|---|---|---|
| `cargo` | VARCHAR | Nível hierárquico (Júnior, Pleno, Sênior, etc.) |
| `nivel` | VARCHAR | Campo de nível adicional do dataset bruto (pode ser vazio) |
| `genero` | VARCHAR | Gênero do grupo agregado (`Feminino`, `Masculino`) |
| `regiao` | VARCHAR | Região geográfica dos profissionais agregados |
| `n` | INTEGER | Quantidade de profissionais no grupo |
| `salario_medio_brl` | FLOAT | Média salarial do grupo em R$ (pós-winsorização) |
| `salario_mediano_brl` | FLOAT | Mediana salarial do grupo em R$ (pós-winsorização) |

> **Aviso:** A média de médias desta tabela diverge do gap individual de ~27% embutido no raw. Para análise precisa do pay gap, usar os dados brutos diretamente ou a view `v_pay_gap` com controle de cargo.

---

### 3.3 `fato_vagas_linkedin.csv`
**Origem:** Leitura e enriquecimento de `generation_linkedin_vagas_tecnologia.csv` via `etl_pipeline.py → etl_linkedin()`.
**Grão:** Uma linha por vaga (nível individual — sem agregação).
**Formato:** CSV, 200 linhas, 13 colunas.

| Coluna | Tipo | Origem | Descrição |
|---|---|---|---|
| `id` | VARCHAR | Bruto | Identificador da vaga (do CSV original) |
| `empresa` | VARCHAR | Bruto | Nome da empresa anunciante |
| `titulo` | VARCHAR | Bruto | Título original da vaga |
| `nivel` | VARCHAR | **Derivado** | Nível hierárquico extraído do título | `Estagiário`, `Aprendiz`, `Júnior`, `Outros` |
| `area_tech` | VARCHAR | **Derivado** | Área tecnológica extraída do título | Veja mapeamento §5.2 |
| `cidade` | VARCHAR | **Derivado** | Cidade extraída de `location` (`null` se remota) |
| `uf` | VARCHAR | **Derivado** | Unidade Federativa extraída de `location` (`null` se remota) |
| `remoto` | INTEGER | **Derivado** | Flag: `1` se "Remoto" em `location`, `0` caso contrário |
| `tipo_di` | VARCHAR | **Derivado** | Classificação D&I por NLP de palavras-chave | `Exclusiva`, `Afirmativa Trans-Inclusiva`, `Afirmativa`, `Aberta` |
| `eh_di` | INTEGER | **Derivado** | Flag D&I: `1` se `tipo_di ≠ Aberta`, `0` caso contrário |
| `mes_ano` | VARCHAR | **Derivado** | YYYY-MM extraído de `inserted_at` (para análise temporal) |
| `inserted_at` | VARCHAR | Bruto | Timestamp original da vaga |
| `descricao` | VARCHAR | Bruto | Texto da descrição da vaga |

---

## 4. Banco de Dados Analítico (`analytics.duckdb`)

### 4.1 Tabelas

| Tabela | Linhas | Grão | Origem |
|---|---|---|---|
| `fato_educacao_tech` | 4 | Ano × Região × Área CINE | `fato_educacao_tech_agregado.csv` |
| `fato_mercado_tech_brasil` | 13 | Cargo × Nível × Gênero × Região | `fato_mercado_tech_brasil.csv` |
| `fato_vagas_linkedin` | 200 | Vaga individual | `fato_vagas_linkedin.csv` |

### 4.2 Views analíticas

#### `v_funil_nacional`
Agrega o funil de participação feminina por ano, consolidando todas as regiões.
Usada na página **"A Base"** do dashboard.

| Coluna | Descrição |
|---|---|
| `ano` | Ano de referência |
| `area_geral` | Área CINE |
| `total_mat_fem / masc` | Total de matrículas por gênero |
| `total_ing_fem / masc` | Total de ingressantes por gênero |
| `total_conc_fem / masc` | Total de concluintes por gênero |
| `total_mat` | Total de matrículas (ambos os gêneros) |
| `pct_mat_fem` | % matrículas femininas |
| `pct_ing_fem` | % ingressantes femininas |
| `pct_conc_fem` | % concluintes femininas |
| `media_evasao_fem` | Taxa de evasão média feminina (%) |
| `media_evasao_masc` | Taxa de evasão média masculina (%) |

#### `v_funil_por_regiao`
Funil com abertura por região. Limitado ao Sudeste no mock atual.

| Coluna | Descrição |
|---|---|
| `ano` | Ano de referência |
| `regiao` | Nome da região |
| `area_geral` | Área CINE |
| `total_mat_fem` | Matrículas femininas |
| `total_mat` | Total de matrículas |
| `pct_mat_fem` | % matrículas femininas |
| `pct_conc_fem` | % concluintes femininas |
| `media_evasao_fem` | Taxa de evasão feminina (%) |

#### `v_pay_gap`
Gap salarial por cargo × nível × região, calculado a partir das médias agregadas.
Usada na página **"O Mercado"** do dashboard.

| Coluna | Descrição |
|---|---|
| `cargo` | Nível hierárquico |
| `nivel` | Sublevel adicional |
| `regiao` | Região |
| `salario_medio_masc` | Salário médio masculino no grupo (R$) |
| `salario_medio_fem` | Salário médio feminino no grupo (R$) |
| `pay_gap_pct` | `(masc − fem) / masc × 100` — % do gap em favor do masculino |

#### `v_vagas_di`
Agrega vagas LinkedIn por mês × área × nível × UF com sinais de D&I.
Usada no componente de **análise de vagas** do dashboard.

| Coluna | Descrição |
|---|---|
| `mes_ano` | Mês de referência (YYYY-MM) |
| `area_tech` | Área tecnológica da vaga |
| `nivel` | Nível hierárquico da vaga |
| `uf` | Estado (`null` para remotas) |
| `total_vagas` | Total de vagas no grupo |
| `vagas_di` | Vagas com iniciativa D&I (`eh_di = 1`) |
| `pct_di` | `vagas_di / total_vagas × 100` |
| `n_exclusiva` | Vagas exclusivas para mulheres |
| `n_afirmativa` | Vagas afirmativas para mulheres |
| `n_trans_inclusiva` | Vagas afirmativas trans-inclusivas |
| `n_aberta` | Vagas sem menção a D&I |
| `vagas_remotas` | Vagas com modalidade remota |

---

## 5. Mapeamentos e Regras de Transformação

### 5.1 Instituição → Região (`INST_TO_REGIAO`)

| Instituição | Região | Código |
|---|---|---|
| USP | Sudeste | 3 |
| UFRJ | Sudeste | 3 |
| UFMG | Sudeste | 3 |
| PUC-SP | Sudeste | 3 |
| FIAP | Sudeste | 3 |
| FATEC | Sudeste | 3 |
| Insper | Sudeste | 3 |

> Todas as instituições do mock pertencem ao Sudeste. Análises regionais refletem apenas essa região.

---

### 5.2 Título da vaga → `nivel` e `area_tech`

**Extração de `nivel`** (baseada em palavras-chave no `job_title`):

| Palavra-chave no título | `nivel` atribuído |
|---|---|
| "Estágio" / "estagio" | Estagiário |
| "Aprendiz" | Aprendiz |
| "Júnior" / "Junior" | Júnior |
| Nenhuma das anteriores | Outros |

**Extração de `area_tech`** (por prioridade de ocorrência no `job_title`):

| Trecho no título | `area_tech` atribuída |
|---|---|
| "Ciência de Dados" | Ciência de Dados |
| "Back-end" | Desenvolvimento Back-end |
| "Front-end" | Desenvolvimento Front-end |
| "QA" | QA/Testes |
| "Suporte" | Suporte Técnico |
| "Dados" | Dados |
| "TI" | TI Geral |
| "Desenvolvedor" ou "Desenvolvimento" | Desenvolvimento |
| Nenhuma das anteriores | Outros |

---

### 5.3 Descrição da vaga → `tipo_di` (classificação D&I)

| Palavra-chave na descrição | `tipo_di` | `eh_di` |
|---|---|---|
| "exclusiva para mulheres" | Exclusiva | 1 |
| "cis e trans" | Afirmativa Trans-Inclusiva | 1 |
| "afirmativ" ou "participação feminina" | Afirmativa | 1 |
| Nenhuma das anteriores | Aberta | 0 |

**Distribuição no dataset atual (200 vagas):**

| `tipo_di` | N | % |
|---|---|---|
| Aberta | 179 | 89,5% |
| Afirmativa | 8 | 4,0% |
| Exclusiva | 7 | 3,5% |
| Afirmativa Trans-Inclusiva | 6 | 3,0% |
| **Total D&I** | **21** | **10,5%** |

---

### 5.4 Normalização de gênero (`_normalizar_genero`)

| Valor bruto | Valor normalizado |
|---|---|
| F, FEM, FEMININO, MULHER | Feminino |
| M, MASC, MASCULINO, HOMEM | Masculino |
| Outros | Mantido como está |

---

### 5.5 Outliers salariais — Winsorização p99

Aplicada em `etl_mercado_brasil()` sobre a coluna `salario_base`.

- **Método:** Substituição dos valores abaixo do percentil 1 pelo valor do p01 e acima do percentil 99 pelo valor do p99.
- **Objetivo:** Reduzir o efeito de salários extremos sem descartar linhas.
- **Log:** Quantidade de linhas afetadas registrada em `data/treated/qualidade_mercado.json`.
- **Valores p01 e p99 no dataset atual:** R$ 1.438 e R$ 54.968 (15 linhas winsorized).

---

## 6. Premissas Metodológicas

| # | Premissa | Impacto | Status |
|---|---|---|---|
| P1 | Matrículas ≈ Ingressantes — o mock não tem histórico longitudinal | `qt_mat_*` é idêntico a `qt_ing_*` em todos os anos | Aprovado (documentado) |
| P2 | Taxa de evasão = (ingressantes − concluintes) / ingressantes | Métrica cross-sectional; inclui quem ainda está cursando | Aprovado |
| P3 | Cruzamento educação × mercado é exclusivamente agregado | Não há CPF; joins apenas por Ano × Região × Gênero | Aprovado |
| P4 | Gap salarial de ~27% intencional no mock (ref. Brasscom) | Padrão detectável na análise — objetivo pedagógico | Aprovado |
| P5 | Gargalo de liderança: sub-representação feminina em Diretor/CTO (ref. McKinsey) | Padrão detectável em `fato_mercado_tech_brasil` filtrando `cargo IN ('Diretor','CTO/CIO')` | Aprovado |
| P6 | Liderança definida como: Sênior, Especialista, Gerente, Diretor, CTO/CIO | Aguarda validação final pelo time para uso no pitch | **AGUARDA_APROVACAO_HUMANA** |
| P7 | Classificação D&I por palavras-chave simples (sem ML) | Pode ter falsos negativos em descrições com linguagem variante | Aprovado para fins pedagógicos |

---

## 7. Arquivos de Qualidade e Metadados

| Arquivo | Conteúdo |
|---|---|
| `data/treated/qualidade_inep.json` | Estatísticas do processamento do `base_campus_ti_brasil.csv`: total de estudantes, distribuição por gênero, anos cobertos, instituições, limitações |
| `data/treated/qualidade_mercado.json` | Estatísticas do `base_mercado_tech_brasil.csv`: total de linhas, p01/p99 salariais, linhas winsorizadas, distribuição por gênero |
| `data/treated/qualidade_linkedin.json` | Estatísticas do `generation_linkedin_vagas_tecnologia.csv`: total de vagas, n D&I, % D&I, distribuição por tipo, período coberto |
| `config/premises.json` | Todas as premissas metodológicas aprovadas e pendentes de aprovação humana, incluindo metodologia das três bases |

---

## 8. Glossário

| Termo | Definição no contexto do projeto |
|---|---|
| **Funil da mulher na tech** | Sequência Matrícula → Ingresso → Conclusão → Mercado → Liderança; cada etapa reduz a participação feminina |
| **Ingressante** | Estudante que iniciou o curso em determinado ano |
| **Concluinte** | Estudante que concluiu o curso (flag `concluiu = 1`) |
| **Evasão (estimada)** | `(ingressantes − concluintes) / ingressantes` — inclui quem ainda está cursando |
| **Pay gap** | Diferença percentual entre o salário médio masculino e feminino: `(masc − fem) / masc × 100` |
| **Vaga afirmativa** | Vaga aberta, mas com incentivo explícito à candidatura feminina |
| **Vaga exclusiva** | Vaga reservada exclusivamente para mulheres |
| **Winsorização p99** | Substituição de valores extremos pelo percentil 99, sem remover linhas |
| **Dataset mockado** | Dataset criado com dados fictícios que refletem padrões reais extraídos de relatórios de mercado; adequado para fins pedagógicos, não representa nenhuma empresa ou pessoa real |
| **D&I** | Diversidade, Equidade e Inclusão |
| **TIC** | Tecnologias da Informação e Comunicação — categoria CINE usada para filtrar cursos tech |
| **CINE** | Classificação Internacional Normalizada da Educação — sistema de categorização do INEP |

---

*Dicionário de Dados — Projeto People Analytics & DE&I. Manter atualizado a cada alteração de schema ou premissa.*
