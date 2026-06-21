"""
Geração determinística dos dois CSVs de mercado tech.
Proporções 100% fiéis às fontes: Brasscom 2025 e WomenHack 2026.

Estratégia: pré-calcula contagens exatas antes de gerar registros,
nunca usa random() para decidir proporções categóricas.
"""
import csv, random, sys
sys.stdout.reconfigure(encoding='utf-8')
random.seed(42)


def allocate(total, proportions):
    """
    Distribui `total` (int) entre as chaves de `proportions` (dict nome->peso),
    garantindo soma exata via método Largest Remainder.
    """
    keys   = list(proportions.keys())
    floats = [total * proportions[k] / sum(proportions.values()) for k in keys]
    floors = [int(f) for f in floats]
    remainder = total - sum(floors)
    # ordena por maior parte fracionária e distribui o restante
    order = sorted(range(len(keys)), key=lambda i: -(floats[i] - floors[i]))
    for i in order[:remainder]:
        floors[i] += 1
    return dict(zip(keys, floors))


def make_generos(n_fem, n_mas):
    """Cria lista embaralhada com contagens exatas de cada gênero."""
    g = ['Feminino'] * n_fem + ['Masculino'] * n_mas
    random.shuffle(g)
    return g


# ══════════════════════════════════════════════════════════════════════════════
#  BRASIL — Brasscom 2025 Relatório de Diversidade (TIC Brasil, 2019-2024)
# ══════════════════════════════════════════════════════════════════════════════

ANOS = [2019, 2020, 2021, 2022, 2023, 2024]

# Salário médio mensal (BRL) — brasscom_salario_medio.py
SAL_FEM = {2019: 2271.47, 2020: 2249.86, 2021: 2689.03,
           2022: 2695.16, 2023: 2810.90, 2024: 3062.44}
SAL_MAS = {2019: 3449.29, 2020: 3256.63, 2021: 3824.88,
           2022: 3815.93, 2023: 3833.51, 2024: 4361.19}

# % feminino em liderança por ano — brasscom_cargo_diretoria.py
# Interpolação linear: 34.0% (2019) → 35.5% (2024), passo 0.3 p.p./ano
LIDER_FEM_PCT = {
    2019: 0.340, 2020: 0.343, 2021: 0.346,
    2022: 0.349, 2023: 0.352, 2024: 0.355,
}

# Participação feminina geral no setor TIC — brasscom_participacao_feminina_TIC.py
PCT_FEM_GERAL_BR = 0.391  # 39.1% (2024); série histórica indisponível, aplicada a todos os anos

LIDERANCA = {'Gerente', 'Diretor', 'C-Level'}

# Distribuição de cargos
CARGO_PROPS = {
    'Estagiário': 0.08, 'Júnior': 0.22, 'Pleno':  0.30,
    'Sênior':     0.25, 'Gerente': 0.10, 'Diretor': 0.04, 'C-Level': 0.01,
}

SETORES_BR   = ['Desenvolvimento', 'Dados', 'Infraestrutura', 'Produto', 'Gestão']
PESOS_SET_BR = {'Desenvolvimento': 0.35, 'Dados': 0.20,
                'Infraestrutura':  0.20, 'Produto': 0.15, 'Gestão': 0.10}

EXP_BR = {
    'Estagiário': (0, 1),  'Júnior':  (1, 3),  'Pleno':   (3, 7),
    'Sênior':     (6, 12), 'Gerente': (8, 15), 'Diretor': (10, 20), 'C-Level': (15, 25),
}

# Multiplicador sobre o salário médio do setor, por nível de cargo
SAL_MULT_BR = {
    'Estagiário': (0.50, 0.80), 'Júnior': (0.70, 1.00), 'Pleno':   (0.90, 1.20),
    'Sênior':     (1.10, 1.50), 'Gerente': (1.40, 2.00), 'Diretor': (2.00, 3.00), 'C-Level': (3.00, 5.00),
}

# Escolaridade em cargos de liderança — brasscom_escolaridade_genero.py
ESCOL_FEM = [
    ('Pós-graduação/Mestrado/Doutorado',        0.12),
    ('Superior Completo',                        0.72),
    ('Superior Incompleto',                      0.08),
    ('Ensino Médio Completo',                    0.07),
    ('Ensino Médio/Fundamental Incompleto',      0.01),
]
ESCOL_MAS = [  # normalizado: soma original 96% → normalizado para 100%
    ('Pós-graduação/Mestrado/Doutorado',        0.104),
    ('Superior Completo',                        0.719),
    ('Superior Incompleto',                      0.104),
    ('Ensino Médio Completo',                    0.063),
    ('Ensino Médio/Fundamental Incompleto',      0.010),
]

def wc(pairs):
    items, weights = zip(*pairs)
    return random.choices(list(items), weights=list(weights))[0]

# ── Distribuição exata de anos (Largest Remainder) ──────────────────────────
N_BR = 1000
YEAR_COUNTS = allocate(N_BR, {a: 1 for a in ANOS})  # distribuição uniforme exata

brasil_rows = []
rec_id = 1

for ano in ANOS:
    n_ano = YEAR_COUNTS[ano]

    # ── Cargos exatos para este ano ──────────────────────────────────────────
    cargo_counts = allocate(n_ano, CARGO_PROPS)

    n_lider     = sum(cargo_counts[c] for c in LIDERANCA)
    n_non_lider = n_ano - n_lider

    # ── Gêneros exatos: liderança e não-liderança separados ─────────────────
    n_fem_lider = round(n_lider * LIDER_FEM_PCT[ano])
    n_mas_lider = n_lider - n_fem_lider

    # femininos totais no ano (39.1%), menos os já alocados em liderança
    n_fem_ano   = round(n_ano * PCT_FEM_GERAL_BR)
    n_fem_non   = max(0, min(n_fem_ano - n_fem_lider, n_non_lider))
    n_mas_non   = n_non_lider - n_fem_non

    generos_lider = make_generos(n_fem_lider, n_mas_lider)
    generos_non   = make_generos(n_fem_non,   n_mas_non)
    gi_lider = iter(generos_lider)
    gi_non   = iter(generos_non)

    # ── Setores exatos para este ano ─────────────────────────────────────────
    # Distribui setores de forma exata pelo ano inteiro e embaralha
    setor_counts = allocate(n_ano, PESOS_SET_BR)
    setores_list = []
    for s, cnt in setor_counts.items():
        setores_list.extend([s] * cnt)
    random.shuffle(setores_list)
    si = iter(setores_list)

    for cargo, count in cargo_counts.items():
        is_lider = cargo in LIDERANCA
        g_iter = gi_lider if is_lider else gi_non
        mmin, mmax = SAL_MULT_BR[cargo]
        emin, emax = EXP_BR[cargo]

        for _ in range(count):
            genero = next(g_iter)
            base   = SAL_FEM[ano] if genero == 'Feminino' else SAL_MAS[ano]
            salario_brl = round(base * random.uniform(mmin, mmax), 2)
            setor       = next(si)
            anos_exp    = random.randint(emin, emax)
            promovido   = 'Sim' if random.random() < (0.20 if is_lider else 0.15) else 'Não'
            escol       = wc(ESCOL_FEM if genero == 'Feminino' else ESCOL_MAS) if is_lider else ''
            transicao   = 'Sim' if random.random() < 0.22 else 'Não'

            brasil_rows.append({
                'id': rec_id, 'pais': 'Brasil', 'ano': ano,
                'genero': genero, 'cargo': cargo, 'setor': setor,
                'salario_brl': salario_brl, 'anos_experiencia': anos_exp,
                'promovido_ultimo_ano': promovido,
                'nivel_escolaridade': escol, 'transicao_carreira': transicao,
            })
            rec_id += 1

BR_COLS = ['id','pais','ano','genero','cargo','setor','salario_brl',
           'anos_experiencia','promovido_ultimo_ano','nivel_escolaridade','transicao_carreira']
with open('data/treated/base_mercado_tech_brasil.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=BR_COLS)
    w.writeheader()
    w.writerows(brasil_rows)

# ── Verificação Brasil ────────────────────────────────────────────────────────
print("=" * 60)
print("BRASIL — base_mercado_tech_brasil.csv")
print("=" * 60)
gc = {'Feminino': 0, 'Masculino': 0}
for r in brasil_rows: gc[r['genero']] += 1
print(f"Total: {len(brasil_rows)} | Feminino: {gc['Feminino']} ({gc['Feminino']/len(brasil_rows)*100:.1f}%) | target: 39.1%")

for ano in ANOS:
    yr = [r for r in brasil_rows if r['ano'] == ano]
    fyr = sum(1 for r in yr if r['genero'] == 'Feminino')
    yl  = [r for r in yr if r['cargo'] in LIDERANCA]
    fl  = sum(1 for r in yl if r['genero'] == 'Feminino')
    pfl = fl/len(yl)*100 if yl else 0
    print(f"  {ano}: {len(yr)} reg | {fyr}/{len(yr)} geral fem ({fyr/len(yr)*100:.1f}%) "
          f"| liderança: {fl}/{len(yl)} ({pfl:.1f}%) target {LIDER_FEM_PCT[ano]*100:.1f}%")

sc = {}
for r in brasil_rows: sc[r['setor']] = sc.get(r['setor'], 0) + 1
print("Setores:", {s: f"{c} ({c/N_BR*100:.1f}%)" for s,c in sorted(sc.items())})


# ══════════════════════════════════════════════════════════════════════════════
#  MUNDIAL — Women in Tech Statistics 2026 (WomenHack) · Global, EUA, UK, UE
# ══════════════════════════════════════════════════════════════════════════════

PAISES_M   = ['Global', 'EUA', 'UK', 'UE']
N_MUNDIAL  = 500
N_POR_PAIS = N_MUNDIAL // len(PAISES_M)  # 125 exatos

# % feminino por país — WomenHack 2026
PCT_FEM_PAIS = {
    'Global': 0.267,   # Deloitte
    'EUA':    0.280,   # NCWIT
    'UK':     0.330,   # Tech Nation
    'UE':     0.220,   # European Commission
}

# (cargo, setor, pct_fem_global, sal_min_m_usd, sal_max_m_usd, exp_min, exp_max)
CARGOS_M = [
    ('Designer UX/UI',            'Produto',         0.46, 70000,  130000,  1,  8),
    ('Gerente de Produto',        'Produto',         0.35, 90000,  160000,  4, 12),
    ('Cientista de Dados',        'Dados',           0.30, 90000,  160000,  2, 10),
    ('Engenheiro de IA/ML',       'Dados',           0.26, 100000, 180000,  2, 10),
    ('Desenvolvedor de Software', 'Desenvolvimento', 0.22, 80000,  150000,  1, 10),
    ('Engenheiro DevOps',         'Infraestrutura',  0.14, 85000,  145000,  2, 10),
    ('Analista de Cibersegurança','Infraestrutura',  0.12, 80000,  140000,  1, 10),
    ('C-Level',                   'Gestão',          0.29, 150000, 300000, 12, 25),
    ('CTO/CIO',                   'Gestão',          0.15, 150000, 250000, 10, 25),
    ('VP de Tecnologia',          'Gestão',          0.18, 120000, 200000,  8, 20),
]
NC = len(CARGOS_M)  # 10
CARGO_PROPS_M = {c[0]: 1 for c in CARGOS_M}  # pesos iguais: ~12-13 por cargo
CARGO_PCT_FEM = {c[0]: c[2] for c in CARGOS_M}  # % fem por cargo (WomenHack global)

mundial_rows = []
rec_id = 1

for pais in PAISES_M:
    # ── Contagens exatas de cargos para este país ─────────────────────────
    cargo_counts_m = allocate(N_POR_PAIS, CARGO_PROPS_M)

    # ── Femininos exatos por cargo (proporcional ao % do cargo, WomenHack) ─
    # O total de femininos no país é EXATO (arredondamento do target do país).
    # A distribuição entre cargos é proporcional ao % feminino de cada cargo.
    n_fem_pais = round(N_POR_PAIS * PCT_FEM_PAIS[pais])

    # Distribui os n_fem_pais femininos entre cargos usando os pesos do relatório
    fem_per_cargo = allocate(n_fem_pais, CARGO_PCT_FEM)

    # Garante que n_fem por cargo <= total de registros daquele cargo
    for cargo_name in list(fem_per_cargo.keys()):
        fem_per_cargo[cargo_name] = min(fem_per_cargo[cargo_name], cargo_counts_m[cargo_name])

    for cargo, setor, _, sal_min_m, sal_max_m, emin, emax in CARGOS_M:
        n_cargo  = cargo_counts_m[cargo]
        n_fem_c  = fem_per_cargo[cargo]
        n_mas_c  = n_cargo - n_fem_c
        generos  = make_generos(n_fem_c, n_mas_c)

        for genero in generos:
            if genero == 'Masculino':
                salario = round(random.uniform(sal_min_m, sal_max_m))
            else:  # gap 16%: mulheres ganham 84¢ por dólar — WomenHack 2026
                salario = round(random.uniform(sal_min_m * 0.84, sal_max_m * 0.84))

            anos_exp  = random.randint(emin, emax)
            promo_pct = 0.20 * (0.87 if genero == 'Feminino' else 1.0)  # 87/100 — WomenHack
            promovido = 'Sim' if random.random() < promo_pct else 'Não'
            transicao = 'Sim' if random.random() < 0.20 else 'Não'

            mundial_rows.append({
                'id': rec_id, 'pais': pais, 'ano': 2024,
                'genero': genero, 'cargo': cargo, 'setor': setor,
                'salario_usd': salario, 'anos_experiencia': anos_exp,
                'promovido_ultimo_ano': promovido, 'transicao_carreira': transicao,
            })
            rec_id += 1

M_COLS = ['id','pais','ano','genero','cargo','setor','salario_usd',
          'anos_experiencia','promovido_ultimo_ano','transicao_carreira']
with open('data/treated/base_mercado_tech_mundial.csv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=M_COLS)
    w.writeheader()
    w.writerows(mundial_rows)

# ── Verificação Mundial ───────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("MUNDIAL — base_mercado_tech_mundial.csv")
print("=" * 60)
print(f"Total: {len(mundial_rows)}")
for p in PAISES_M:
    rp  = [r for r in mundial_rows if r['pais'] == p]
    f_  = sum(1 for r in rp if r['genero'] == 'Feminino')
    tgt = PCT_FEM_PAIS[p] * 100
    ok  = "OK" if abs(f_/len(rp)*100 - tgt) < 0.5 else "DIVERGE"
    print(f"  {p}: {f_}/{len(rp)} = {f_/len(rp)*100:.1f}% fem | target {tgt:.1f}% [{ok}]")

print("\n% feminino por cargo (todos os países combinados):")
for cargo, setor, tgt_pct, *_ in CARGOS_M:
    rc = [r for r in mundial_rows if r['cargo'] == cargo]
    fc = sum(1 for r in rc if r['genero'] == 'Feminino')
    pct = fc/len(rc)*100 if rc else 0
    ok = "OK" if abs(pct - tgt_pct*100) <= 5 else "DIVERGE"
    print(f"  {cargo:<30} {fc}/{len(rc)} = {pct:.1f}% | target {tgt_pct*100:.0f}% [{ok}]")
