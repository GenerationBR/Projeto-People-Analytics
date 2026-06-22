import { useState } from "react";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, PieChart, Pie, Cell, LabelList, ReferenceLine,
} from "recharts";
import {
  GraduationCap, Briefcase, Filter, BarChart3, Calculator,
  Home as HomeIcon, ArrowUpRight, Megaphone, Globe, TrendingDown,
} from "lucide-react";

/* ---------------------------------------------------------------- */
/* PALETA                                                            */
/* ---------------------------------------------------------------- */

const C = {
  white: "#ffffff",
  bg: "#fffafb",
  pale: "#fdf2f6",
  pale2: "#f7e0e8",
  light: "#f3c4d3",
  mid: "#e8a0b9",
  taupe: "#c3a7af",
  dark: "#9c2f5c",
  deep: "#7d2249",
  deepest: "#5c1638",
  ink: "#2b1620",
  inkMuted: "#8a6e78",
};

const NAV_ITEMS = [
  { id: "home", label: "Home", icon: HomeIcon },
  { id: "base", label: "A Base", icon: GraduationCap },
  { id: "mercado", label: "O Mercado", icon: Briefcase },
  { id: "funil", label: "Funil", icon: Filter },
  { id: "irf", label: "IRF", icon: BarChart3 },
  { id: "simulador", label: "Simulador RH", icon: Calculator },
];

/* Taxonomias oficiais usadas ao longo do relatório (seniority + área ampla) */
const AREAS = ["Dados", "Desenvolvimento", "Gestão", "Infraestrutura", "UX/UI"];
const CARGOS = ["Estagiário", "Júnior", "Pleno", "Sênior", "Gerente", "Diretor", "CTO/CIO"];
const ANOS = ["2019", "2020", "2021", "2022", "2023", "2024"];

const FONTE_COLOR = { inep: C.deepest, datahackers: C.dark, global: C.mid };

function pctBR(v) { return `${String(v).replace(".", ",")}%`; }
function brl(n) { return "R$ " + Math.round(n).toLocaleString("pt-BR"); }
function interp(start, end, n) {
  return Array.from({ length: n }, (_, i) => Math.round((start + ((end - start) * i) / (n - 1)) * 10) / 10);
}

/* ---------------------------------------------------------------- */
/* DADOS                                                              */
/* Quatro linhagens, cada uma com proveniência distinta:              */
/*  · INEP — Censo da Educação Superior (mockado dentro da faixa real */
/*    informada: 18%–21% de mulheres entre ingressantes em Computação)*/
/*  · State of Data Brasil 2021 (Data Hackers) — base oficial/real do */
/*    nicho de Dados; quebras de cargo/nível/faixa são estimativas    */
/*    ilustrativas a recalcular no Power BI a partir da base real     */
/*  · Brasscom / WomenHack / McKinsey & LeanIn — benchmarks globais e */
/*    nacionais citados tal qual fornecidos (não são mock)            */
/*  · Generation — vagas afirmativas (dado cedido, webscraping)       */
/* ---------------------------------------------------------------- */

/* A Base — INEP (5 cursos: SI/CC/ADS/ES presencial + CD pres+EaD) */
const inepIngressantes = [
  { ano: "2019", total: 75455,  pctFem: 13.9 },
  { ano: "2020", total: 78381,  pctFem: 15.8 },
  { ano: "2021", total: 67246,  pctFem: 18.2 },
  { ano: "2022", total: 105168, pctFem: 17.9 },
  { ano: "2023", total: 122416, pctFem: 18.1 },
  { ano: "2024", total: 125899, pctFem: 18.4 },
];
const mulheresIngressantes2024 = 104176; // INEP 2024 real · CINE 06 pres+EaD
const mulheresConcluintes2024 = 19253;  // INEP 2024 real · CINE 06 pres+EaD

const distribuicaoCurso = [
  { name: "Análise e Desenv. de Sistemas", value: 44.2 },
  { name: "Ciência da Computação", value: 23.8 },
  { name: "Sistemas de Informação", value: 17.4 },
  { name: "Ciência de Dados", value: 8.2 },
  { name: "Engenharia de Software", value: 6.3 },
];
const donutColors = [C.deepest, C.deep, C.dark, C.mid, C.light];

const evasaoPorCurso = [
  { curso: "SI", cursoFull: "Sistemas de Informação", mulheres: 77.8, homens: 69.6 },
  { curso: "CC", cursoFull: "Ciência da Computação", mulheres: 85.7, homens: 75.4 },
  { curso: "ADS", cursoFull: "Análise e Desenvolvimento de Sistemas", mulheres: 67.6, homens: 70.8 },
  { curso: "ES", cursoFull: "Engenharia de Software", mulheres: 50.0, homens: 72.2 },
  { curso: "CD", cursoFull: "Ciência de Dados", mulheres: 83.3, homens: 97.4 },
];

const rankingInstituicoes = [
  { nome: "USP", pct: 17.7 }, { nome: "Insper", pct: 17.0 },
  { nome: "FIAP", pct: 16.7 }, { nome: "PUC-SP", pct: 16.4 },
  { nome: "UFMG", pct: 14.4 },
];

/* A Base — % FEM ingressantes por curso · presencial (ADS/CC/SI/ES) + EaD (CD) · INEP 2019–2024 */
const CURSO_LINE_COLORS = { CD: C.deepest, SI: C.deep, ADS: C.dark, CC: C.inkMuted, ES: C.taupe };
const inepPorCurso = [
  { ano: "2019", ADS: 15.3, CC: 11.5, SI: 14.4, ES: 12.6, CD: 18.1 },
  { ano: "2020", ADS: 17.5, CC: 11.8, SI: 15.1, ES: 11.4, CD: 23.2 },
  { ano: "2021", ADS: 20.6, CC: 12.9, SI: 17.1, ES: 13.7, CD: 25.9 },
  { ano: "2022", ADS: 18.3, CC: 13.4, SI: 18.0, ES: 13.1, CD: 29.0 },
  { ano: "2023", ADS: 17.8, CC: 14.9, SI: 19.3, ES: 15.7, CD: 27.4 },
  { ano: "2024", ADS: 18.3, CC: 15.6, SI: 19.7, ES: 13.9, CD: 28.2 },
];
/* A Base — ingressantes × concluintes 2024 · snapshot INEP · coortes distintas */
const ingConclPorCurso = [
  { curso: "ADS", ing: 18.3, conc: 18.8 },
  { curso: "CC",  ing: 15.6, conc: 12.7 },
  { curso: "SI",  ing: 19.7, conc: 15.9 },
  { curso: "ES",  ing: 13.9, conc: 15.2 },
  { curso: "CD",  ing: 28.2, conc: 23.8 },
];

/* O Mercado — State of Data Brasil 2021 (Data Hackers), n = 2.645 · valores calculados sobre microdados */
/* "Analista de Dados/Business Analyst" agrupados (mesma função no CSV): (25+83)/(96+324)=25,7% */
/* "Analista de BI/Analytics Engineer" já eram a mesma categoria no State of Data 2021 */
const representacaoFuncaoDados = [
  { funcao: "Analista de Dados / Business Analyst", pct: 25.7 },
  { funcao: "Analista de BI / Analytics Engineer", pct: 19.8 },
  { funcao: "Cientista de Dados", pct: 19.0 },
  { funcao: "Engenheiro de Dados", pct: 13.4 },
  { funcao: "DBA", pct: 7.1 },
];

const nivelGeneroDados = [
  { nivel: "Júnior", mulheres: 39.0, homens: 32.0 },
  { nivel: "Pleno", mulheres: 35.5, homens: 35.4 },
  { nivel: "Sênior", mulheres: 25.5, homens: 32.6 },
];

const faixaSalarialDados = [
  { faixa: "Até R$4k", mulheres: 24.8, homens: 21.4 },
  { faixa: "R$4–8k", mulheres: 37.4, homens: 32.7 },
  { faixa: "R$8–12k", mulheres: 22.2, homens: 19.9 },
  { faixa: "R$12–16k", mulheres: 7.8, homens: 11.9 },
  { faixa: "R$16–20k", mulheres: 3.7, homens: 5.9 },
  { faixa: "Acima de R$20k", mulheres: 4.1, homens: 8.2 },
];

const brokenRung = [
  { label: "Homens promovidos a gestão", value: 100 },
  { label: "Mulheres promovidas a gestão", value: 66 },
];

const gapComparativoSalarial = [
  { escopo: "Dados (Brasil)", pct: 17.1, fonte: "datahackers" },
  { escopo: "TIC geral (Brasil)", pct: 29.8, fonte: "global" },
];

/* O Mercado — modelo de trabalho × gênero · State of Data Brasil 2021 */
const modeloTrabalhoDados = [
  { modalidade: "Remoto",        mulheres: 64.4, homens: 54.6 },
  { modalidade: "Híbrido flex.", mulheres: 17.7, homens: 19.9 },
  { modalidade: "Híbrido fixo",  mulheres:  8.0, homens: 10.7 },
  { modalidade: "Presencial",    mulheres:  9.9, homens: 14.8 },
];
/* O Mercado — tempo de experiência na área de Dados × gênero · State of Data Brasil 2021 */
const experienciaDados = [
  { faixa: "< 1 ano",   mulheres: 22.3, homens: 16.0 },
  { faixa: "1–2 anos",  mulheres: 21.3, homens: 19.5 },
  { faixa: "2–3 anos",  mulheres: 20.1, homens: 22.1 },
  { faixa: "4–5 anos",  mulheres: 17.2, homens: 17.4 },
  { faixa: "6–10 anos", mulheres: 10.0, homens: 12.8 },
  { faixa: "10+ anos",  mulheres:  9.1, homens: 12.2 },
];
/* O Mercado — TIC Nacional: evolução salarial × gênero · Brasscom 2025 (dados reais, RAIS/Ministério do Trabalho) */
const evolucaoSalarialTIC = [
  { ano: "2019", feminino: 2271, masculino: 3449 },
  { ano: "2020", feminino: 2250, masculino: 3257 },
  { ano: "2021", feminino: 2689, masculino: 3825 },
  { ano: "2022", feminino: 2695, masculino: 3816 },
  { ano: "2023", feminino: 2811, masculino: 3834 },
  { ano: "2024", feminino: 3062, masculino: 4361 },
];
/* O Mercado — TIC Nacional: escolaridade em liderança (Diretoria/Gerência) × gênero · Brasscom 2025 (dados reais) */
const escolaridadeLiderancaTIC = [
  { nivel: "Pós-grad./Mest./Dout.", mulheres: 12, homens: 10 },
  { nivel: "Superior Completo",     mulheres: 72, homens: 69 },
  { nivel: "Superior Incompleto",   mulheres:  8, homens: 10 },
  { nivel: "Ensino Médio",          mulheres:  7, homens:  6 },
];
/* O Mercado — Global: % feminino por função em tech · WomenHack 2026 (BLS / WEF / Zippia / Stanford AI) */
const representacaoFuncaoGlobal = [
  { funcao: "UX/UI Design",          pct: 46 },
  { funcao: "Product Management",    pct: 35 },
  { funcao: "Data Science",          pct: 30 },
  { funcao: "Software Engineering",  pct: 22 },
  { funcao: "AI / Machine Learning", pct: 22 },
  { funcao: "DevOps / Cloud",        pct: 14 },
  { funcao: "Cibersegurança",        pct: 12 },
];

/* Generation Brasil — Turma Java 84 · dado cedido · gênero inferido por nome (1 aluno/a excluído/a por nome ambíguo; n=41) · início = V1 pré-programa · conclusão = V3 Módulo III */
const java84Evasao = [
  { modulo: "Pré-programa", mulheres: 29, homens: 12 },
  { modulo: "Módulo III",   mulheres: 14, homens:  5 },
];
/* Generation Brasil — Turma Java 84 · perfil de vulnerabilidade no ingresso (V1 pré-programa, n=42, excl. "prefiro não responder") */
const java84Vulnerabilidade = [
  { fator: "Periférico/a",           pct: 62 },
  { fator: "Saúde mental afetada",   pct: 32 },
  { fator: "Cadastro Único",         pct: 28 },
  { fator: "Financ. limitada",       pct: 15 },
  { fator: "Com filhos/dependentes", pct: 14 },
];

/* Vagas afirmativas — dado cedido pela Generation (webscraping LinkedIn) · vagas de tecnologia (excl. Comercial e Suporte Técnico) · meses com dados disponíveis: ago/25, set/25, out/25, mar/26, abr/26 */
const vagasGeneration = [
  { mes: "ago/25", total: 177, afirmativas: 3 },
  { mes: "set/25", total: 17,  afirmativas: 0 },
  { mes: "out/25", total: 11,  afirmativas: 0 },
  { mes: "mar/26", total: 3,   afirmativas: 0 },
  { mes: "abr/26", total: 187, afirmativas: 4 },
].map((d) => ({ ...d, naoAfirmativas: d.total - d.afirmativas }));

const tipoDiBreakdown = [
  { tipo: "PCD",                    n: 5 },
  { tipo: "Mulheres na Tecnologia", n: 2 },
];

/* Home — comparativo de representação entre recortes (o que é comparável) */
const representacaoComparativa = [
  { recorte: "Ingressantes (Computação)", pct: 18.4, fonte: "inep" },
  { recorte: "Profissionais de Dados", pct: 18.7, fonte: "datahackers" },
  { recorte: "Força de trabalho em TIC", pct: 39.1, fonte: "global" },
  { recorte: "C-Suite em tecnologia", pct: 29.0, fonte: "global" },
  { recorte: "CTO / liderança técnica", pct: 15.0, fonte: "global" },
];

/* Funil — trajetória por etapa (fontes e populações distintas) */
const trajectoryStages = [
  { name: "Ingressantes em Computação", pctFem: 18.4, tag: "INEP · 5 cursos (SI/CC/ADS/ES/CD) · 2024" },
  { name: "Profissionais na área de Dados", pctFem: 18.7, tag: "State of Data Brasil 2021 · n=2.645" },
  { name: "Cargos de gestão em Dados", pctFem: 13.2, tag: "State of Data Brasil 2021 · n=508 gestores" },
];

/* IRF — área (estimativa de mercado, exceto Dados = real) e cargo (fontes reais) */
/* pctMulheresPorArea: Dados=State of Data 2021 · Desenvolvimento/UX/UI=WomenHack 2026 · Infraestrutura=WomenHack 2026 · Gestão=Brasscom 2025 */
const pctMulheresPorArea = { Dados: 18.7, Desenvolvimento: 22.0, Gestão: 35.5, Infraestrutura: 14.0, "UX/UI": 46.0 };
const BASELINE_TIC = 39.1; // Brasscom 2025 — % mulheres na força de trabalho em TIC (Brasil, 2024)
const irfArea = AREAS.map((a) => ({ name: a, v: Math.round((pctMulheresPorArea[a] / BASELINE_TIC) * 100) / 100 }));

/* pctMulheresPorCargo: apenas níveis com fonte real disponível */
/* Gerente/Diretor = Brasscom 2025 (Diretoria/Gerência TIC, 2024) · CTO/CIO = WomenHack 2026 (McKinsey, 2025) */
const CARGOS_IRF = ["Gerente", "Diretor", "CTO/CIO"];
const pctMulheresPorCargo = {
  "Gerente": 35.5, "Diretor": 35.5, "CTO/CIO": 15.0,
};
const irfCargo = CARGOS_IRF.map((c) => ({ name: c, v: Math.round((pctMulheresPorCargo[c] / BASELINE_TIC) * 100) / 100 }));
function irfColor(v) {
  if (v >= 1.05) return C.deepest;
  if (v >= 0.9) return C.dark;
  if (v >= 0.65) return C.mid;
  return C.light;
}

/* Simulador RH — área x cargo, sem filtro de região */
/* Salários: médias masculinas por nível · Brasscom 2025 (base_mercado_tech_brasil.csv) */
const baseSalaryByCargo = {
  "Estagiário": 2425, "Júnior": 3187, "Pleno": 3962, "Sênior": 4824,
  "Gerente": 6291, "Diretor": 9505, "CTO/CIO": 16474,
};
/* Gap para demais áreas (não-Dados): 29,8% uniforme · Brasscom 2025 */
const gapPctByCargo = {
  "Estagiário": 0.298, "Júnior": 0.298, "Pleno": 0.298, "Sênior": 0.298,
  "Gerente": 0.298, "Diretor": 0.298, "CTO/CIO": 0.298,
};
/* Gap para área de Dados: State of Data Brasil 2021 · n=2.645 */
const GAP_DADOS = 0.171;
const areaMultiplier = { Dados: 1.00, Desenvolvimento: 0.92, Gestão: 1.15, Infraestrutura: 0.88, "UX/UI": 0.80 };
const areaTrendRange = {
  Dados: [16, 28], Desenvolvimento: [14, 22], Gestão: [26, 38],
  Infraestrutura: [9, 16], "UX/UI": [30, 42],
};

/* ---------------------------------------------------------------- */
/* COMPONENTES BASE                                                  */
/* ---------------------------------------------------------------- */

function BrandMark() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="6" r="4" stroke={C.deepest} strokeWidth="1.3" />
      <circle cx="12" cy="18" r="4" stroke={C.deepest} strokeWidth="1.3" />
      <circle cx="6" cy="12" r="4" stroke={C.deepest} strokeWidth="1.3" />
      <circle cx="18" cy="12" r="4" stroke={C.deepest} strokeWidth="1.3" />
      <circle cx="12" cy="12" r="2.3" fill={C.deepest} />
    </svg>
  );
}

function KpiCard({ label, value, sub, trend }) {
  return (
    <div className="kpi-card">
      <span className="kpi-label">{label}</span>
      <span className="kpi-value">{value}</span>
      <div className="kpi-foot">
        <span className="kpi-sub">{sub}</span>
        {trend && (
          <span className="kpi-trend">
            <ArrowUpRight size={12} strokeWidth={2.5} /> {trend}
          </span>
        )}
      </div>
    </div>
  );
}

function ChartCard({ title, sub, isNew, height = 280, children, legend, footer }) {
  return (
    <div className="chart-card">
      <div className="chart-card-head">
        <div>
          <div className="chart-card-title-row">
            <span className="chart-card-title">{title}</span>
            {isNew && <span className="badge-new">novo</span>}
          </div>
          {sub && <span className="chart-card-sub">{sub}</span>}
        </div>
        {legend && (
          <div className="legend-row">
            {legend.map((l) => (
              <span className="legend-item" key={l.label}>
                <span className="legend-dot" style={{ background: l.color }} />
                {l.label}
              </span>
            ))}
          </div>
        )}
      </div>
      <div style={height === "auto" ? undefined : { height }}>{children}</div>
      {footer && <div className="chart-card-footer">{footer}</div>}
    </div>
  );
}

function SectionDivider({ label, tag, icon: Icon = Megaphone }) {
  return (
    <div className="section-divider">
      <span className="section-divider-label"><Icon size={15} strokeWidth={2} /> {label}</span>
      {tag && <span className="section-divider-tag">{tag}</span>}
    </div>
  );
}

function PageHeader({ title, sub }) {
  return (
    <div className="page-header">
      <h1 className="page-title">{title}</h1>
      <p className="page-sub">{sub}</p>
    </div>
  );
}

function PageFooter({ children }) {
  return <p className="page-footer">{children}</p>;
}

function NoteBanner({ children }) {
  return <div className="note-banner">{children}</div>;
}

const tooltipStyle = {
  contentStyle: { background: C.white, border: `1px solid ${C.light}`, borderRadius: 10, fontSize: 12, padding: "8px 12px" },
  labelStyle: { color: C.deepest, fontWeight: 600, marginBottom: 2 },
  cursor: { fill: C.pale },
};
const axisProps = { tick: { fontSize: 11, fill: C.inkMuted }, axisLine: { stroke: C.pale2 }, tickLine: false };

/* Barra horizontal genérica — reutilizada por IRF, Home (comparativo) e O Mercado (funções) */
function HBars({ data, xKey, yKey, domain = [0, 40], height = 240, colorFn, refLine, suffix = "%", width = 130, barSize = 14 }) {
  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ top: refLine != null ? 26 : 8, right: 30, left: 8, bottom: 0 }}>
        <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" horizontal={false} />
        <XAxis type="number" domain={domain} {...axisProps} tickFormatter={(v) => `${v}${suffix}`} />
        <YAxis type="category" dataKey={yKey} {...axisProps} width={width} />
        <Tooltip {...tooltipStyle} formatter={(v) => `${v}${suffix}`} />
        {refLine != null && (
          <ReferenceLine x={refLine} stroke={C.inkMuted} strokeDasharray="4 4" label={{ value: "média", position: "top", fontSize: 10, fill: C.inkMuted }} />
        )}
        <Bar dataKey={xKey} radius={[0, 6, 6, 0]} barSize={barSize}>
          {data.map((d, i) => <Cell key={i} fill={colorFn ? colorFn(d, i) : C.dark} />)}
          <LabelList dataKey={xKey} position="right" formatter={(v) => `${v}${suffix}`} fill={C.ink} fontSize={11} />
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}

/* Barras de trajetória — largura proporcional ao % feminino em cada etapa */
function TrajectoryBars({ stages }) {
  const maxPct = Math.max(...stages.map((s) => s.pctFem));
  const palette = [C.mid, C.dark, C.deep, C.deepest, "#3a141f"];
  return (
    <div className="funnel-wrap">
      {stages.map((s, i) => {
        const widthPct = 34 + 66 * (s.pctFem / maxPct);
        return (
          <div key={s.name} className="funnel-row" style={{ width: `${widthPct}%`, background: palette[i % palette.length] }}>
            <span className="funnel-name">{s.name}</span>
            <span className="funnel-value">{pctBR(s.pctFem)} mulheres</span>
            <span className="funnel-sub">{s.tag}</span>
          </div>
        );
      })}
    </div>
  );
}

/* Visual minimalista do "degrau quebrado" (broken rung) */
function BrokenRungBars({ data }) {
  return (
    <div className="rung-wrap">
      {data.map((d) => (
        <div key={d.label} className="rung-row">
          <span className="rung-label">{d.label}</span>
          <div className="rung-track">
            <div
              className="rung-fill"
              style={{ width: `${d.value}%`, background: d.label.startsWith("Mulheres") ? C.dark : C.taupe }}
            />
          </div>
          <span className="rung-value">{d.value}</span>
        </div>
      ))}
    </div>
  );
}

/* ---------------------------------------------------------------- */
/* PÁGINAS                                                            */
/* ---------------------------------------------------------------- */

function HomePage() {
  return (
    <div className="page">
      <PageHeader title="Visão geral" sub="Educação, mercado de Dados e benchmarks globais · panorama consolidado · 2019–2024" />
      <div className="kpi-grid">
        <KpiCard label="% mulheres entre ingressantes" value="18,4%" sub="5 cursos de Computação · INEP, 2024" trend="+4,5 p.p. desde 2019" />
        <KpiCard label="% mulheres na área de Dados" value="18,7%" sub="State of Data Brasil 2021 · n = 2.645" />
        <KpiCard label="Gap salarial em Dados (Brasil)" value="17,1%" sub="vs. 29,8% no setor de TIC geral (Brasscom)" />
        <KpiCard label="Mulheres em C-Suite tech" value="29%" sub="WomenHack 2026 · cai para 15% em CTO" />
      </div>
      <div className="chart-grid cols-2">
        <ChartCard title="Evolução da % de mulheres entre ingressantes" sub="Cursos de Computação · INEP, 2019–2024">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={inepIngressantes} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="ano" {...axisProps} />
              <YAxis domain={[10, 22]} {...axisProps} tickFormatter={(v) => `${v}%`} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              <Line type="monotone" dataKey="pctFem" stroke={C.deepest} strokeWidth={2.4} dot={{ r: 3, fill: C.deepest }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard
          title="Representação feminina por recorte"
          sub="Comparação entre fontes, no que é comparável"
          footer={
            <div className="legend-row">
              <span className="legend-item"><span className="legend-dot" style={{ background: FONTE_COLOR.inep }} /> INEP (população)</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: FONTE_COLOR.datahackers }} /> State of Data 2021 (amostra)</span>
              <span className="legend-item"><span className="legend-dot" style={{ background: FONTE_COLOR.global }} /> Benchmark global/nacional</span>
            </div>
          }
        >
          <HBars
            data={representacaoComparativa}
            xKey="pct" yKey="recorte" domain={[0, 40]} height={210} width={150}
            colorFn={(d) => FONTE_COLOR[d.fonte]}
          />
        </ChartCard>
      </div>
      <PageFooter>Fontes: INEP — Censo da Educação Superior (2019–2024) · State of Data Brasil 2021 (Data Hackers, n = 2.645) · Brasscom — Relatório de Diversidade (2024/2025) · WomenHack (2026) · McKinsey &amp; LeanIn — Women in the Workplace (2025).</PageFooter>
    </div>
  );
}

function BasePage() {
  return (
    <div className="page">
      <PageHeader title="A Base" sub="Educação Superior · Censo da Educação Superior (INEP) · 2019–2024" />
      <div className="kpi-grid">
        <KpiCard label="Mulheres ingressantes" value={mulheresIngressantes2024.toLocaleString("pt-BR")} sub="Computação e TIC · pres+EaD · INEP, 2024" />
        <KpiCard label="Mulheres concluintes" value={mulheresConcluintes2024.toLocaleString("pt-BR")} sub="Computação e TIC · pres+EaD · INEP, 2024" />
        <KpiCard label="Taxa de não-conclusão no prazo" value="62,6%" sub="Média geral · 5 cursos · cohorts 2019–2020" />
        <KpiCard label="Participação feminina entre ingressantes" value="18,4%" sub="5 cursos de Computação · INEP, 2024 · série 2019–2024: 14%→18%" />
      </div>
      <div className="chart-grid cols-2">
        <ChartCard title="Evolução da % de mulheres entre ingressantes" sub="Cursos de Computação · 2019–2024">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={inepIngressantes} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="ano" {...axisProps} />
              <YAxis domain={[10, 22]} {...axisProps} tickFormatter={(v) => `${v}%`} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              <Line type="monotone" dataKey="pctFem" stroke={C.deepest} strokeWidth={2.4} dot={{ r: 3, fill: C.deepest }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard
          title="Distribuição por curso"
          sub="% de matriculadas, 2024"
          height={195}
          footer={
            <div className="donut-legend">
              {distribuicaoCurso.map((d, i) => (
                <span className="legend-item" key={d.name}>
                  <span className="legend-dot" style={{ background: donutColors[i] }} /> {d.name} · {d.value}%
                </span>
              ))}
            </div>
          }
        >
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={distribuicaoCurso} dataKey="value" nameKey="name" innerRadius={52} outerRadius={80} paddingAngle={1.5}>
                {distribuicaoCurso.map((_, i) => <Cell key={i} fill={donutColors[i]} stroke={C.white} strokeWidth={2} />)}
              </Pie>
              <Tooltip {...tooltipStyle} formatter={(v, n) => [`${v}%`, n]} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <div className="chart-grid cols-2">
        <ChartCard
          title="% de mulheres ingressantes por curso"
          sub="Evolução 2019–2024 · presencial (ADS/CC/SI/ES) + EaD (CD) · INEP"
          isNew
          height={250}
          legend={[
            { label: "CD", color: CURSO_LINE_COLORS.CD },
            { label: "SI", color: CURSO_LINE_COLORS.SI },
            { label: "ADS", color: CURSO_LINE_COLORS.ADS },
            { label: "CC", color: CURSO_LINE_COLORS.CC },
            { label: "ES", color: CURSO_LINE_COLORS.ES },
          ]}
          footer={<p className="abbrev-caption">CD = Ciência de Dados (EaD) · SI = Sistemas de Informação · ADS = Análise e Desenvolvimento de Sistemas · CC = Ciência da Computação · ES = Engenharia de Software</p>}
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={inepPorCurso} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="ano" {...axisProps} />
              <YAxis domain={[8, 32]} {...axisProps} tickFormatter={(v) => `${v}%`} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              {["CD", "SI", "ADS", "CC", "ES"].map((curso) => (
                <Line
                  key={curso}
                  type="monotone"
                  dataKey={curso}
                  stroke={CURSO_LINE_COLORS[curso]}
                  strokeWidth={curso === "CD" || curso === "ADS" ? 2.4 : 1.8}
                  dot={{ r: 3, fill: CURSO_LINE_COLORS[curso] }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard
          title="Ingressantes × Concluintes 2024"
          sub="% de mulheres por curso · snapshot INEP 2024 · coortes distintas"
          isNew
          height={250}
          legend={[{ label: "Ingressantes", color: C.dark }, { label: "Concluintes", color: C.taupe }]}
          footer={<p className="abbrev-caption">Ingressantes e concluintes pertencem a coortes distintas — não é rastreamento de uma mesma turma. Leitura: representação feminina em quem entrou vs. quem concluiu em 2024.</p>}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={ingConclPorCurso} margin={{ top: 8, right: 8, left: -16, bottom: 0 }} barGap={4}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="curso" {...axisProps} interval={0} />
              <YAxis {...axisProps} tickFormatter={(v) => `${v}%`} domain={[0, 32]} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              <Bar dataKey="ing" name="Ingressantes" fill={C.dark} radius={[4, 4, 0, 0]} barSize={18} />
              <Bar dataKey="conc" name="Concluintes" fill={C.taupe} radius={[4, 4, 0, 0]} barSize={18} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <div className="chart-grid cols-2">
        <ChartCard
          title="Não-conclusão no prazo, por gênero e curso"
          sub="Em SI e CC mulheres lideram; em ADS e ES os homens têm maior não-conclusão"
          isNew
          legend={[{ label: "Mulheres", color: C.dark }, { label: "Homens", color: C.taupe }]}
          footer={<p className="abbrev-caption">SI = Sistemas de Informação · CC = Ciência da Computação · ADS = Análise e Desenvolvimento de Sistemas · ES = Engenharia de Software · CD = Ciência de Dados</p>}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={evasaoPorCurso} margin={{ top: 8, right: 8, left: -16, bottom: 0 }} barGap={4}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="curso" {...axisProps} interval={0} tick={{ fontSize: 11.5, fill: C.inkMuted }} />
              <YAxis {...axisProps} tickFormatter={(v) => `${v}%`} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} labelFormatter={(label) => evasaoPorCurso.find((d) => d.curso === label)?.cursoFull || label} />
              <Bar dataKey="mulheres" fill={C.dark} radius={[4, 4, 0, 0]} barSize={16} />
              <Bar dataKey="homens" fill={C.taupe} radius={[4, 4, 0, 0]} barSize={16} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Ranking de instituições" sub="% de mulheres no corpo discente">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={rankingInstituicoes} layout="vertical" margin={{ top: 8, right: 28, left: 8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" horizontal={false} />
              <XAxis type="number" domain={[0, 22]} {...axisProps} tickFormatter={(v) => `${v}%`} />
              <YAxis type="category" dataKey="nome" {...axisProps} width={70} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              <Bar dataKey="pct" radius={[0, 6, 6, 0]} barSize={16}>
                {rankingInstituicoes.map((_, i) => <Cell key={i} fill={i === 0 ? C.deepest : C.dark} />)}
                <LabelList dataKey="pct" position="right" formatter={(v) => `${v}%`} fill={C.ink} fontSize={11} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <PageFooter>Fonte: INEP — Censo da Educação Superior (2019–2024). Contagens de ingressantes e concluintes são dados reais (CINE 06, pres+EaD). Série histórica por curso: presencial para ADS/CC/SI/ES; EaD para CD (curso predominantemente a distância). Ingressantes × Concluintes: snapshot 2024, coortes distintas. Taxa de não-conclusão: cohorts 2019–2020, prazo teórico de conclusão.</PageFooter>

      <SectionDivider label="Formação inclusiva em tecnologia" tag="dado cedido · Generation Brasil · Turma Java 84" />
      <div className="kpi-grid kpi-grid-2">
        <KpiCard
          label="Composição feminina da turma Java 84"
          value="71%"
          sub="29 de 41 alunos/as com gênero identificado · pré-programa · Generation Brasil 2025"
        />
        <KpiCard
          label="Taxa de evasão feminina × masculina"
          value="52% / 58%"
          sub="Taxas praticamente equivalentes — programa sem viés de gênero detectado · F: 52% · M: 58%"
        />
      </div>
      <div className="chart-grid cols-2">
        <ChartCard
          title="Composição por gênero: início × conclusão"
          sub="Pré-programa = quem ingressou · Módulo III = quem concluiu · Turma Java 84 · Generation Brasil 2025"
          isNew
          legend={[{ label: "Mulheres", color: C.dark }, { label: "Homens", color: C.taupe }]}
          footer={<p className="abbrev-caption">Das 29 mulheres que ingressaram, 14 concluíram o Módulo III (52% de evasão). Dos 12 homens, 5 concluíram (58% de evasão) — diferença de apenas 6 p.p., equivalente para esse n.</p>}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={java84Evasao} margin={{ top: 20, right: 16, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="modulo" {...axisProps} />
              <YAxis {...axisProps} domain={[0, 34]} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v} alunos/as`} />
              <Bar dataKey="mulheres" name="Mulheres" fill={C.dark} radius={[4, 4, 0, 0]} barSize={30}>
                <LabelList dataKey="mulheres" position="top" fill={C.ink} fontSize={11} />
              </Bar>
              <Bar dataKey="homens" name="Homens" fill={C.taupe} radius={[4, 4, 0, 0]} barSize={30}>
                <LabelList dataKey="homens" position="top" fill={C.ink} fontSize={11} />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard
          title="Perfil de vulnerabilidade da turma"
          sub="% de alunos/as com cada fator ao ingressar no programa · pesquisa pré-curso (V1) · n = 42"
          isNew
          height={290}
          footer={<p className="abbrev-caption">Dados autodeclarados antes do início do programa. Quem respondeu "prefiro não responder" foi excluído do denominador de cada indicador individualmente.</p>}
        >
          <HBars
            data={java84Vulnerabilidade}
            xKey="pct" yKey="fator" domain={[0, 80]} height={290} width={175}
            colorFn={(_, i) => [C.deepest, C.deep, C.dark, C.mid, C.taupe][i] ?? C.dark}
          />
        </ChartCard>
      </div>
      <PageFooter>Formação Generation Brasil: dado cedido pela Generation Brasil. Turma Java 84 (programa Java Developer). Composição e evasão: calculadas entre pesquisa pré-programa V1 (n=42) e Módulo III (n=29). Gênero inferido por nome — 1 aluno/a excluído/a por nome ambíguo (n analisado = 41). Perfil de vulnerabilidade: pesquisa autodeclarada pré-programa (V1, n=42). Indicadores com "prefiro não responder" excluídos do denominador individualmente.</PageFooter>
    </div>
  );
}

function MercadoPage() {
  return (
    <div className="page">
      <PageHeader title="O Mercado de Dados" sub="Base oficial: State of Data Brasil 2021 (Data Hackers) · n = 2.645 respondentes" />
      <div className="kpi-grid">
        <KpiCard label="Respondentes na pesquisa" value="2.645" sub="State of Data Brasil 2021" />
        <KpiCard label="% mulheres na área de Dados" value="18,7%" sub="Do total de respondentes" />
        <KpiCard label="Gap salarial em Dados" value="17,1%" sub="Homens × Mulheres, Brasil" />
        <KpiCard label="% mulheres em cargos de gestão" value="13,6%" sub="vs. 20,6% dos homens" />
      </div>
      <div className="chart-grid cols-2">
        <ChartCard title="Representação feminina por função" sub="% mulheres em cada função, área de Dados" isNew>
          <HBars
            data={representacaoFuncaoDados}
            xKey="pct" yKey="funcao" domain={[0, 30]} height={205} width={200}
            colorFn={() => C.dark} refLine={18.7}
          />
        </ChartCard>
        <ChartCard
          title="Distribuição por nível, segundo o gênero"
          sub="% dentro de cada gênero"
          isNew
          legend={[{ label: "Mulheres", color: C.dark }, { label: "Homens", color: C.taupe }]}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={nivelGeneroDados} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="nivel" {...axisProps} />
              <YAxis {...axisProps} tickFormatter={(v) => `${v}%`} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              <Bar dataKey="mulheres" fill={C.dark} radius={[4, 4, 0, 0]} barSize={20} />
              <Bar dataKey="homens" fill={C.taupe} radius={[4, 4, 0, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <SectionDivider label="Perfil e condições de trabalho" tag="State of Data Brasil 2021 · n = 2.645" />
      <div className="chart-grid cols-2">
        <ChartCard
          title="Modelo de trabalho atual"
          sub="% dentro de cada gênero · State of Data Brasil 2021"
          isNew
          legend={[{ label: "Mulheres", color: C.dark }, { label: "Homens", color: C.taupe }]}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={modeloTrabalhoDados} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="modalidade" {...axisProps} tick={{ fontSize: 10.5, fill: C.inkMuted }} interval={0} />
              <YAxis {...axisProps} tickFormatter={(v) => `${v}%`} domain={[0, 72]} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              <Bar dataKey="mulheres" name="Mulheres" fill={C.dark} radius={[4, 4, 0, 0]} barSize={20} />
              <Bar dataKey="homens" name="Homens" fill={C.taupe} radius={[4, 4, 0, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard
          title="Tempo de experiência na área de Dados"
          sub="% dentro de cada gênero · State of Data Brasil 2021"
          isNew
          legend={[{ label: "Mulheres", color: C.dark }, { label: "Homens", color: C.taupe }]}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={experienciaDados} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="faixa" {...axisProps} tick={{ fontSize: 10, fill: C.inkMuted }} interval={0} />
              <YAxis {...axisProps} tickFormatter={(v) => `${v}%`} domain={[0, 26]} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              <Bar dataKey="mulheres" name="Mulheres" fill={C.dark} radius={[4, 4, 0, 0]} barSize={16} />
              <Bar dataKey="homens" name="Homens" fill={C.taupe} radius={[4, 4, 0, 0]} barSize={16} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <div className="chart-grid cols-2">
        <ChartCard
          title="Faixa salarial, segundo o gênero"
          sub="% dentro de cada gênero, por faixa mensal"
          isNew
          legend={[{ label: "Mulheres", color: C.dark }, { label: "Homens", color: C.taupe }]}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={faixaSalarialDados} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="faixa" {...axisProps} tick={{ fontSize: 9.5, fill: C.inkMuted }} interval={0} />
              <YAxis {...axisProps} tickFormatter={(v) => `${v}%`} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              <Bar dataKey="mulheres" fill={C.dark} radius={[4, 4, 0, 0]} barSize={13} />
              <Bar dataKey="homens" fill={C.taupe} radius={[4, 4, 0, 0]} barSize={13} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard
          title="Degrau quebrado da liderança"
          sub="Promoções a cargos de gestão, a cada 100 homens · McKinsey & LeanIn, 2025"
          isNew
          height="auto"
        >
          <BrokenRungBars data={brokenRung} />
          <p className="rung-caption">Para cada 100 homens promovidos a cargos de gestão, apenas 66 mulheres são — cálculo direto sobre a base do State of Data Brasil 2021 (n=2.645), onde 13,6% das profissionais de Dados ocupam cargos de gestão, contra 20,6% dos homens.</p>
        </ChartCard>
      </div>
      <PageFooter>Fonte: State of Data Brasil 2021 (Data Hackers) · n = 2.645 respondentes. Percentuais calculados diretamente sobre os microdados. Gap salarial de 17,1% estimado pela média das faixas de remuneração declaradas (salário mediano feminino e masculino coincidem na faixa R$6–8k). Modelo de trabalho e experiência: calculados sobre n = 493 mulheres e n = 2.144 homens com resposta válida.</PageFooter>

      <SectionDivider label="TIC no Brasil" tag="Brasscom 2025 — Relatório de Diversidade, Equidade e Inclusão · dados reais RAIS/MTE" />
      <div className="chart-grid cols-2">
        <ChartCard
          title="Evolução salarial TIC: mulheres × homens"
          sub="Salário médio mensal no setor TIC · Brasil · Brasscom 2025"
          isNew
          legend={[{ label: "Mulheres", color: C.dark }, { label: "Homens", color: C.taupe }]}
          footer={<p className="abbrev-caption">Em 2023 a equidade atingiu 73,3% — melhor marca da série. Em 2024, o gap voltou a 29,8%: salários masculinos cresceram 13,8% vs. 8,9% dos femininos.</p>}
        >
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={evolucaoSalarialTIC} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="ano" {...axisProps} />
              <YAxis {...axisProps} tickFormatter={(v) => `R$${(v / 1000).toFixed(1)}k`} />
              <Tooltip {...tooltipStyle} formatter={(v) => `R$ ${v.toLocaleString("pt-BR")}`} />
              <Line type="monotone" dataKey="feminino" name="Mulheres" stroke={C.dark} strokeWidth={2.4} dot={{ r: 3, fill: C.dark }} />
              <Line type="monotone" dataKey="masculino" name="Homens" stroke={C.taupe} strokeWidth={2} dot={{ r: 3, fill: C.taupe }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard
          title="Escolaridade em liderança TIC"
          sub="Diretoria e Gerência TIC · % por nível de escolaridade · Brasscom 2025"
          isNew
          legend={[{ label: "Mulheres", color: C.dark }, { label: "Homens", color: C.taupe }]}
          footer={<p className="abbrev-caption">Mulheres em liderança TIC são mais escolarizadas: 84% têm Superior Completo ou mais, vs. 79% dos homens nos mesmos cargos — a "penalidade da qualificação".</p>}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={escolaridadeLiderancaTIC} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="nivel" {...axisProps} tick={{ fontSize: 9.5, fill: C.inkMuted }} interval={0} />
              <YAxis {...axisProps} tickFormatter={(v) => `${v}%`} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
              <Bar dataKey="mulheres" name="Mulheres" fill={C.dark} radius={[4, 4, 0, 0]} barSize={18} />
              <Bar dataKey="homens" name="Homens" fill={C.taupe} radius={[4, 4, 0, 0]} barSize={18} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
      <PageFooter>Brasscom — Relatório de Diversidade, Equidade e Inclusão no Setor de TIC 2025. Salários médios calculados sobre RAIS/Ministério do Trabalho via Brasscom. Escolaridade: Brasscom 2025 (Diretoria e Gerência, setor TIC).</PageFooter>

      <SectionDivider label="Comparativo global" tag="WomenHack 2026 · Brasscom 2024/2025 · McKinsey & LeanIn 2025" icon={Globe} />
      <div className="kpi-grid">
        <KpiCard label="Mulheres em C-Suite tech" value="29%" sub="WomenHack 2026 (global)" />
        <KpiCard label="Mulheres em cargos técnicos de liderança" value="15%" sub="CTO · WomenHack 2026 (global)" />
        <KpiCard label="Retenção média — mulheres" value="3,1 anos" sub="vs. 4,2 anos para homens · WomenHack 2026" />
        <KpiCard label="Mulheres na força de trabalho em TIC" value="39,1%" sub="Brasil · Brasscom 2025 (setor TIC, 2024)" />
      </div>
      <ChartCard
        title="Gap salarial: Dados (Brasil) vs. TIC geral (Brasil)"
        sub="State of Data Brasil 2021 vs. Brasscom — Relatório de Diversidade 2024/2025"
        isNew
        height={170}
      >
        <HBars
          data={gapComparativoSalarial}
          xKey="pct" yKey="escopo" domain={[0, 32]} height={170} width={150}
          colorFn={(d) => FONTE_COLOR[d.fonte]}
        />
      </ChartCard>
      <ChartCard
        title="% feminino por função em tech"
        sub="Representação feminina por área de atuação · global · WomenHack 2026 (BLS / WEF / Zippia / Stanford AI)"
        isNew
        height={290}
      >
        <HBars
          data={representacaoFuncaoGlobal}
          xKey="pct" yKey="funcao" domain={[0, 55]} height={290} width={165}
          colorFn={(_, i) => [C.mid, C.dark, C.dark, C.deep, C.deep, C.deepest, C.deepest][i] ?? C.dark}
        />
      </ChartCard>
      <PageFooter>Comparativo global: WomenHack — Women in Tech Report 2026 (compilado de Deloitte, BLS, WEF, McKinsey, PwC, Stanford AI, Zippia). C-Suite (29%), CTO (15%) e % feminino por função: WomenHack 2026. Retenção (3,1 vs. 4,2 anos): WomenHack 2026.</PageFooter>

      <SectionDivider label="Vagas afirmativas no mercado" tag="dado cedido · Generation" />
      <div className="kpi-grid kpi-grid-2">
        <KpiCard label="% de vagas afirmativas no período" value="1,8%" sub="ago/25–abr/26 · 7 de 395 vagas tech" />
        <KpiCard label="Vagas afirmativas no período" value="7" sub="PCD: 5 · Mulheres: 2 · ago/25–abr/26" />
      </div>
      <div className="chart-grid cols-2">
        <ChartCard
          title="Vagas afirmativas x vagas totais"
          sub="Vagas de tecnologia mapeadas por mês, via webscraping de LinkedIn"
          isNew
          legend={[{ label: "Vagas afirmativas", color: C.dark }, { label: "Demais vagas", color: C.pale2 }]}
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={vagasGeneration} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="mes" {...axisProps} />
              <YAxis {...axisProps} />
              <Tooltip {...tooltipStyle} formatter={(v) => `${v} vagas`} />
              <Bar dataKey="afirmativas" stackId="v" fill={C.dark} barSize={20} />
              <Bar dataKey="naoAfirmativas" stackId="v" fill={C.pale2} radius={[6, 6, 0, 0]} barSize={20} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Vagas afirmativas por tipo de ação" sub="Distribuição das 7 vagas afirmativas (vagas tech)" isNew>
          <HBars
            data={tipoDiBreakdown}
            xKey="n" yKey="tipo" domain={[0, 6]} height={210} width={130} suffix=""
            colorFn={(_, i) => [C.deepest, C.dark, C.mid, C.light][i]}
          />
        </ChartCard>
      </div>
      <PageFooter>Vagas afirmativas: dado cedido pela Generation Brasil (webscraping LinkedIn). Análise restrita a vagas de tecnologia (excl. Comercial e Suporte Técnico). Meses com dados disponíveis: ago/25, set/25, out/25, mar/26, abr/26. Total: 395 vagas tech · 7 afirmativas (1,8%).</PageFooter>
    </div>
  );
}

function FunilPage() {
  return (
    <div className="page">
      <PageHeader title="Trajetória da mulher em tecnologia" sub="Representação por etapa · INEP · State of Data Brasil 2021" />
      <div className="chart-grid cols-2">
        <ChartCard title="Representação feminina por etapa" sub="Largura da barra proporcional ao % de mulheres" height="auto">
          <TrajectoryBars stages={trajectoryStages} />
        </ChartCard>
        <div className="stacked-col">
          <ChartCard title="Degrau quebrado da liderança" sub="A cada 100 homens promovidos a gestão · McKinsey & LeanIn, 2025" isNew height="auto">
            <BrokenRungBars data={brokenRung} />
          </ChartCard>
          <div className="callout">
            <TrendingDown size={26} strokeWidth={1.6} />
            <div>
              <strong>Maior recuo: −5,5 p.p.</strong>
              <p>Entre profissionais de Dados (18,7%) e quem chega à gestão na área (13,2%) — o ponto mais agudo de perda de representatividade que medimos na base nacional.</p>
            </div>
          </div>
          <div className="callout-note">
            Cada etapa parte de uma fonte e população diferente — Censo Educacional (INEP) e pesquisa amostral com profissionais de Dados (State of Data Brasil 2021). A leitura é sobre hiatos de representação ao longo da trajetória típica, não uma coorte única acompanhada no tempo.
          </div>
        </div>
      </div>
      <SectionDivider label="Por que o funil estreita no meio?" tag="Accenture 2024 · ISACA 2024" />
      <div className="kpi-grid">
        <KpiCard
          label="Saem da área de tecnologia antes dos 35 anos"
          value="50%"
          sub="Metade das mulheres que entram na tech abandona a área ainda em plena carreira — não por falta de capacidade, mas por barreiras estruturais · Accenture 2024 (global)"
        />
        <KpiCard
          label="Mais rápido que homens na saída da área"
          value="+45%"
          sub="A cada 10 homens que deixam um emprego em tech, aproximadamente 14,5 mulheres fazem o mesmo — proporcionalmente, elas saem muito mais · Accenture 2024 (global)"
        />
        <KpiCard
          label="Apontam o ambiente de trabalho como razão"
          value="56%"
          sub="Mais da metade das profissionais que saem da tech cita cultura organizacional — clima hostil, falta de pertencimento ou ausência de representação — como motivo principal · ISACA 2024 (global)"
        />
      </div>
      <SectionDivider label="Antes da trajetória: interesse e acesso" tag="PwC 2025 · NBER 2024" />
      <div className="kpi-grid kpi-grid-2">
        <KpiCard
          label="Jovens mulheres que consideram carreira em tech"
          value="27%"
          sub="vs. 62% dos jovens homens · PwC Global Tech Report 2025"
        />
        <KpiCard
          label="Callbacks a menos com currículo de nome feminino"
          value="−30%"
          sub="Viés de gênero na triagem documentado por experimento · NBER 2024"
        />
      </div>
      <PageFooter>Fontes: INEP — Censo da Educação Superior 2024 · State of Data Brasil 2021 (Data Hackers) · Accenture — Women in the Workplace 2024 (global) · ISACA — State of Cybersecurity 2024 (extrapolado para tech em geral) · PwC Global Tech Report 2025 · NBER 2024.</PageFooter>
    </div>
  );
}

function IrfPage() {
  return (
    <div className="page">
      <PageHeader title="Índice de Representatividade Feminina" sub="IRF = % mulheres na categoria ÷ % mulheres na força de trabalho em TIC (39,1%, Brasscom 2025)" />
      <NoteBanner>
        <strong>Nota metodológica:</strong> a área <strong>Dados</strong> usa o State of Data Brasil 2021 (n = 2.645). Áreas: Desenvolvimento/UX/UI/Infraestrutura = WomenHack 2026 · Gestão = Brasscom 2025 (Diretoria/Gerência TIC, Brasil). Cargos: Gerente/Diretor = Brasscom 2025 (35,5% Diretoria/Gerência TIC) · CTO/CIO = WomenHack 2026 (McKinsey, 15%).
      </NoteBanner>
      <div className="legend-row" style={{ marginBottom: 16 }}>
        <span className="legend-item"><span className="legend-dot" style={{ background: C.deepest }} /> Acima da média (IRF ≥ 1,05)</span>
        <span className="legend-item"><span className="legend-dot" style={{ background: C.dark }} /> Próximo da média</span>
        <span className="legend-item"><span className="legend-dot" style={{ background: C.light }} /> Sub-representação (IRF &lt; 0,65)</span>
      </div>
      <div className="chart-grid cols-2">
        <ChartCard title="IRF por área" sub="Dados (real) · Desenvolvimento, Gestão, Infraestrutura e UX/UI (estimativa)" height={220}>
          <HBars data={irfArea} xKey="v" yKey="name" domain={[0, 1.6]} height={220} suffix="" refLine={1} colorFn={(d) => irfColor(d.v)} />
        </ChartCard>
        <ChartCard title="IRF por cargo" sub="Gerente/Diretor = Brasscom 2025 (TIC Brasil) · CTO/CIO = WomenHack 2026" height={180}>
          <HBars data={irfCargo} xKey="v" yKey="name" domain={[0, 1.6]} height={180} suffix="" refLine={1} width={110} colorFn={(d) => irfColor(d.v)} />
        </ChartCard>
      </div>
      <PageFooter>Fonte: cálculo próprio (% mulheres na categoria ÷ 39,1%, Brasscom 2025) com base em State of Data Brasil 2021 (Dados), WomenHack 2026 (Desenvolvimento, UX/UI, Infraestrutura, CTO/CIO) e Brasscom 2025 (Gestão, Gerente, Diretor).</PageFooter>
    </div>
  );
}

function SimuladorPage() {
  const [area, setArea] = useState("Dados");
  const [cargo, setCargo] = useState("Pleno");

  const homens = Math.round(baseSalaryByCargo[cargo] * areaMultiplier[area]);
  const gapPct = area === "Dados" ? GAP_DADOS : gapPctByCargo[cargo];
  const mulheres = Math.round(homens * (1 - gapPct));
  const [start, end] = areaTrendRange[area];
  const serieArea = interp(start, end, ANOS.length).map((v, i) => ({ ano: ANOS[i], pct: v }));

  return (
    <div className="page">
      <PageHeader title="Simulador de RH" sub="Consulta de gap salarial e formação por área e cargo" />
      <NoteBanner>
        <strong>Nota metodológica:</strong> selecione <strong>Dados</strong> para a área com lastro em pesquisa real (State of Data Brasil 2021, gap de 17,1%); as demais áreas usam estimativas <strong>Brasscom 2025</strong> (salários e gap de 29,8%).
      </NoteBanner>
      <div className="select-row">
        <label className="select-field">
          <span>Área</span>
          <select value={area} onChange={(e) => setArea(e.target.value)}>
            {AREAS.map((a) => <option key={a} value={a}>{a}</option>)}
          </select>
        </label>
        <label className="select-field">
          <span>Cargo</span>
          <select value={cargo} onChange={(e) => setCargo(e.target.value)}>
            {CARGOS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
        </label>
      </div>
      <p className="disclaimer">
        {area === "Dados"
          ? "Gap salarial: 17,1% · State of Data Brasil 2021 (n=2.645, setor de Dados). Salários base por nível: Brasscom 2025."
          : "Salários e gap salarial de 29,8%: Brasscom 2025 — Relatório de Diversidade, Equidade e Inclusão no Setor de TIC."}
      </p>
      {cargo === "Estagiário" && (
        <p className="disclaimer">⚠️ Dados de Estagiário são estimativas de mercado — nenhuma das pesquisas consultadas (State of Data Brasil 2021 / Brasscom 2025) localizou gap salarial específico para este cargo.</p>
      )}
      <div className="kpi-grid kpi-grid-3">
        <KpiCard label="Salário médio · mulheres" value={brl(mulheres)} sub={`${cargo} · ${area}`} />
        <KpiCard label="Salário médio · homens" value={brl(homens)} sub={`${cargo} · ${area}`} />
        <KpiCard
          label={area === "Dados" ? "Gap salarial em Dados" : "Gap salarial neste cargo"}
          value={`${(gapPct * 100).toFixed(1)}%`}
          sub={area === "Dados" ? "State of Data Brasil 2021" : "Brasscom 2025"}
        />
      </div>
      <ChartCard title={`Histórico de formação feminina em ${area}`} sub="% de matriculadas mulheres · INEP, 2019–2024" height={230}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={serieArea} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
            <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
            <XAxis dataKey="ano" {...axisProps} />
            <YAxis domain={[0, 45]} {...axisProps} tickFormatter={(v) => `${v}%`} />
            <Tooltip {...tooltipStyle} formatter={(v) => `${v}%`} />
            <Line type="monotone" dataKey="pct" stroke={C.deepest} strokeWidth={2.4} dot={{ r: 3 }} />
          </LineChart>
        </ResponsiveContainer>
      </ChartCard>
      <PageFooter>Salários base por nível: Brasscom 2025. Gap salarial — Dados: State of Data Brasil 2021 (17,1%); demais áreas: Brasscom 2025 (29,8%). Dados de Estagiário são estimativas de mercado.</PageFooter>
    </div>
  );
}

/* ---------------------------------------------------------------- */
/* APP                                                                */
/* ---------------------------------------------------------------- */

export default function App() {
  const [page, setPage] = useState("home");

  return (
    <div className="dei-dashboard">
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Sora:wght@400;500;600;700&display=swap');

        .dei-dashboard {
          --white:${C.white}; --bg:${C.bg}; --pale:${C.pale}; --pale2:${C.pale2};
          --light:${C.light}; --mid:${C.mid}; --dark:${C.dark}; --deep:${C.deep}; --deepest:${C.deepest};
          --ink:${C.ink}; --inkMuted:${C.inkMuted};
          background: var(--bg);
          min-height: 100%;
          font-family: 'Sora', Georgia, serif;
          color: var(--ink);
        }
        .dei-dashboard * { box-sizing: border-box; }
        .topbar {
          display:flex; align-items:center; justify-content:space-between;
          padding: 16px 36px; background: var(--white);
          border-bottom: 1px solid var(--pale2);
          position: sticky; top:0; z-index:10;
        }
        .brand { display:flex; align-items:center; gap:10px; }
        .brand-text { display:flex; flex-direction:column; line-height:1.1; }
        .brand-title { font-family:'Fraunces', Georgia, serif; font-weight:600; font-size:16px; color:var(--deepest); letter-spacing:.01em; }
        .brand-sub { font-size:10.5px; color:var(--inkMuted); text-transform:uppercase; letter-spacing:.08em; }
        .nav { display:flex; gap:4px; flex-wrap:wrap; }
        .nav-btn {
          display:flex; align-items:center; gap:6px;
          padding:8px 14px; border-radius:999px; border:1px solid transparent;
          background:transparent; color:var(--inkMuted); font-size:12.5px; font-weight:500;
          cursor:pointer; transition: all .15s ease; font-family:'Sora', sans-serif;
        }
        .nav-btn:hover { background: var(--pale); color: var(--deepest); }
        .nav-btn.active { background: var(--deepest); color: var(--white); }

        .page { padding: 32px 36px 56px; max-width:1280px; margin:0 auto; animation: fadeIn .35s ease both; }
        @keyframes fadeIn { from { opacity:0; transform:translateY(6px);} to {opacity:1; transform:translateY(0);} }
        .page-header { margin-bottom:24px; }
        .page-title { font-family:'Fraunces', Georgia, serif; font-weight:600; font-size:26px; color:var(--deepest); margin:0 0 4px; }
        .page-sub { font-size:12.5px; color:var(--inkMuted); margin:0; text-transform:uppercase; letter-spacing:.05em; }
        .page-footer { font-size:11px; color:var(--inkMuted); font-style:italic; margin:22px 0 0; border-top:1px solid var(--pale2); padding-top:12px; }

        .kpi-grid { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:24px; }
        .kpi-grid-3 { grid-template-columns:repeat(3,1fr); }
        .kpi-grid-2 { grid-template-columns:repeat(2,1fr); }
        .kpi-card {
          background: linear-gradient(160deg, var(--white) 55%, var(--pale) 100%);
          border:1px solid var(--pale2); border-radius:16px; padding:16px 18px;
          display:flex; flex-direction:column; gap:6px;
        }
        .kpi-label { font-size:10.5px; text-transform:uppercase; letter-spacing:.06em; color:var(--inkMuted); }
        .kpi-value { font-family:'Fraunces', Georgia, serif; font-weight:600; font-size:26px; color:var(--deepest); line-height:1.1; }
        .kpi-foot { display:flex; align-items:center; justify-content:space-between; gap:8px; }
        .kpi-sub { font-size:11px; color:var(--inkMuted); }
        .kpi-trend { display:flex; align-items:center; gap:2px; font-size:11px; font-weight:600; color:var(--dark); white-space:nowrap; }

        .chart-grid { display:grid; gap:14px; margin-bottom:14px; }
        .chart-grid.cols-2 { grid-template-columns:1.05fr 1fr; }
        .chart-card { background:var(--white); border:1px solid var(--pale2); border-radius:16px; padding:18px 20px; margin-bottom:14px; }
        .chart-grid .chart-card { margin-bottom:0; }
        .chart-card-head { display:flex; align-items:flex-start; justify-content:space-between; gap:12px; margin-bottom:10px; flex-wrap:wrap; }
        .chart-card-title-row { display:flex; align-items:center; gap:8px; }
        .chart-card-title { font-family:'Fraunces', Georgia, serif; font-weight:600; font-size:14.5px; color:var(--deepest); }
        .chart-card-sub { font-size:11.5px; color:var(--inkMuted); }
        .chart-card-footer { margin-top:10px; }
        .badge-new { background:var(--deepest); color:var(--white); font-size:9.5px; padding:2px 8px; border-radius:999px; text-transform:uppercase; letter-spacing:.04em; }

        .legend-row { display:flex; gap:14px; flex-wrap:wrap; }
        .legend-item { display:flex; align-items:center; gap:6px; font-size:11px; color:var(--inkMuted); }
        .legend-dot { width:8px; height:8px; border-radius:50%; display:inline-block; flex-shrink:0; }
        .donut-legend { display:grid; grid-template-columns:1fr 1fr; gap:5px 14px; }
        .abbrev-caption { font-size:10.5px; color:var(--inkMuted); line-height:1.5; margin:0; }

        .stacked-col { display:flex; flex-direction:column; gap:14px; }
        .callout {
          background: linear-gradient(135deg, var(--deepest), var(--dark));
          color:var(--white); border-radius:16px; padding:16px 18px;
          display:flex; align-items:center; gap:12px;
        }
        .callout strong { font-family:'Fraunces', Georgia, serif; font-size:15px; display:block; margin-bottom:2px; }
        .callout p { margin:0; font-size:12px; opacity:.92; }
        .callout-note { background: var(--pale); color:var(--inkMuted); font-size:11.5px; border-radius:14px; padding:13px 16px; line-height:1.5; }

        .note-banner { background:var(--pale); border:1px solid var(--pale2); border-radius:12px; padding:10px 14px; font-size:11.5px; color:var(--inkMuted); margin-bottom:18px; line-height:1.5; }
        .note-banner strong { color:var(--deepest); }

        .funnel-wrap { display:flex; flex-direction:column; align-items:center; gap:10px; padding:8px 0 4px; }
        .funnel-row { color:#fff; border-radius:12px; padding:13px 18px; text-align:center; display:flex; flex-direction:column; gap:2px; box-shadow:0 2px 10px rgba(92,22,56,.14); }
        .funnel-name { font-size:11.5px; text-transform:uppercase; letter-spacing:.03em; opacity:.92; }
        .funnel-value { font-family:'Fraunces', Georgia, serif; font-weight:600; font-size:18px; line-height:1.3; }
        .funnel-sub { font-size:10.5px; opacity:.88; }

        .rung-wrap { display:flex; flex-direction:column; gap:14px; padding:6px 2px; }
        .rung-row { display:flex; align-items:center; gap:10px; }
        .rung-label { font-size:11.5px; color:var(--inkMuted); width:170px; flex-shrink:0; }
        .rung-track { flex:1; height:14px; background:var(--pale); border-radius:999px; overflow:hidden; }
        .rung-fill { height:100%; border-radius:999px; transition:width .3s ease; }
        .rung-value { font-family:'Fraunces', Georgia, serif; font-weight:600; font-size:14px; color:var(--deepest); width:28px; text-align:right; }
        .rung-caption { font-size:11.5px; color:var(--inkMuted); line-height:1.5; margin:14px 2px 2px; }

        .section-divider { display:flex; align-items:center; justify-content:space-between; gap:10px; margin:28px 0 14px; padding-top:20px; border-top:1px dashed var(--pale2); }
        .section-divider-label { display:flex; align-items:center; gap:7px; font-family:'Fraunces', Georgia, serif; font-weight:600; font-size:16px; color:var(--deepest); }
        .section-divider-tag { font-size:10px; background:var(--pale); color:var(--dark); padding:3px 10px; border-radius:999px; text-transform:uppercase; letter-spacing:.04em; white-space:nowrap; }

        .select-row { display:flex; gap:16px; margin-bottom:10px; }
        .select-field { flex:1; display:flex; flex-direction:column; gap:6px; font-size:11.5px; color:var(--inkMuted); text-transform:uppercase; letter-spacing:.05em; }
        .select-field select {
          font-family:'Sora', sans-serif; font-size:13.5px; color:var(--ink); text-transform:none; letter-spacing:0;
          padding:9px 12px; border-radius:10px; border:1px solid var(--pale2); background:var(--white); cursor:pointer;
        }
        .select-field select:focus { outline:2px solid var(--light); }
        .disclaimer { font-size:11px; color:var(--inkMuted); font-style:italic; margin:0 0 18px; }

        @media (max-width: 880px) {
          .topbar { flex-direction:column; align-items:flex-start; gap:10px; }
          .kpi-grid, .kpi-grid-3, .kpi-grid-2 { grid-template-columns:repeat(2,1fr); }
          .chart-grid.cols-2 { grid-template-columns:1fr; }
          .select-row { flex-direction:column; }
          .section-divider { flex-direction:column; align-items:flex-start; gap:6px; }
          .rung-label { width:120px; }
        }
      `}</style>

      <div className="topbar">
        <div className="brand">
          <BrandMark />
          <div className="brand-text">
            <span className="brand-title">People Analytics · DEI</span>
            <span className="brand-sub">Trajetória feminina · câmpus ao mercado tech</span>
          </div>
        </div>
        <nav className="nav">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={`nav-btn ${page === item.id ? "active" : ""}`}
                onClick={() => setPage(item.id)}
              >
                <Icon size={14} strokeWidth={2} />
                {item.label}
              </button>
            );
          })}
        </nav>
      </div>

      {page === "home" && <HomePage />}
      {page === "base" && <BasePage />}
      {page === "mercado" && <MercadoPage />}
      {page === "funil" && <FunilPage />}
      {page === "irf" && <IrfPage />}
      {page === "simulador" && <SimuladorPage />}
    </div>
  );
}