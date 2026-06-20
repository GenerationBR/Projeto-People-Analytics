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
const CARGOS = ["Estagiário", "Júnior", "Pleno", "Sênior", "Gerente", "Especialista", "Diretor", "CTO/CIO"];
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

/* A Base — INEP */
const inepIngressantes = [
  { ano: "2019", total: 248000, pctFem: 18.2 },
  { ano: "2020", total: 256000, pctFem: 18.6 },
  { ano: "2021", total: 264000, pctFem: 19.1 },
  { ano: "2022", total: 271000, pctFem: 19.7 },
  { ano: "2023", total: 279000, pctFem: 20.3 },
  { ano: "2024", total: 286000, pctFem: 20.8 },
];
const mulheresIngressantes2024 = Math.round(286000 * 0.208);
const mulheresConcluintes2024 = Math.round(167000 * 0.191);

const distribuicaoCurso = [
  { name: "Sistemas de Informação", value: 28.7 },
  { name: "Ciência da Computação", value: 23.4 },
  { name: "Análise e Desenv. de Sistemas", value: 18.9 },
  { name: "Engenharia de Software", value: 12.5 },
  { name: "Ciência de Dados", value: 8.7 },
  { name: "Outros", value: 7.8 },
];
const donutColors = [C.deepest, C.deep, C.dark, C.mid, C.light, C.pale2];

const evasaoPorCurso = [
  { curso: "SI", cursoFull: "Sistemas de Informação", mulheres: 24.8, homens: 19.6 },
  { curso: "CC", cursoFull: "Ciência da Computação", mulheres: 23.1, homens: 18.9 },
  { curso: "ADS", cursoFull: "Análise e Desenvolvimento de Sistemas", mulheres: 20.7, homens: 17.8 },
  { curso: "ES", cursoFull: "Engenharia de Software", mulheres: 19.4, homens: 16.5 },
  { curso: "CD", cursoFull: "Ciência de Dados", mulheres: 16.9, homens: 15.2 },
];

const rankingInstituicoes = [
  { nome: "UFSCAR", pct: 46.2 }, { nome: "UNIFEI", pct: 43.8 },
  { nome: "UFRGS", pct: 42.1 }, { nome: "UNICAMP", pct: 41.7 },
  { nome: "UTFPR", pct: 41.3 },
];

/* O Mercado — State of Data Brasil 2021 (Data Hackers), n = 2.645 */
const representacaoFuncaoDados = [
  { funcao: "Business Analyst", pct: 33.4 },
  { funcao: "Analista de Dados", pct: 32.1 },
  { funcao: "Analista de BI", pct: 29.7 },
  { funcao: "Data Product Manager", pct: 27.2 },
  { funcao: "Cientista de Dados", pct: 23.6 },
  { funcao: "Analytics Engineer", pct: 18.9 },
  { funcao: "Engenheiro de Dados", pct: 15.8 },
  { funcao: "DBA", pct: 14.7 },
  { funcao: "Arquiteto de Dados", pct: 11.5 },
];

const nivelGeneroDados = [
  { nivel: "Estágio", mulheres: 9.4, homens: 6.1 },
  { nivel: "Júnior", mulheres: 27.8, homens: 21.6 },
  { nivel: "Pleno", mulheres: 37.9, homens: 34.8 },
  { nivel: "Sênior", mulheres: 24.9, homens: 37.5 },
];

const faixaSalarialDados = [
  { faixa: "Até R$4k", mulheres: 13.8, homens: 8.6 },
  { faixa: "R$4–8k", mulheres: 31.5, homens: 23.9 },
  { faixa: "R$8–12k", mulheres: 27.6, homens: 27.1 },
  { faixa: "R$12–16k", mulheres: 14.2, homens: 19.4 },
  { faixa: "R$16–20k", mulheres: 7.1, homens: 11.8 },
  { faixa: "Acima de R$20k", mulheres: 5.8, homens: 9.2 },
];

const brokenRung = [
  { label: "Homens promovidos a gestão", value: 100 },
  { label: "Mulheres promovidas a gestão", value: 87 },
];

const gapComparativoSalarial = [
  { escopo: "Dados (Brasil)", pct: 23.5, fonte: "datahackers" },
  { escopo: "TIC geral (Brasil)", pct: 27.0, fonte: "global" },
];

/* Vagas afirmativas — dado cedido pela Generation (webscraping LinkedIn) · período completo do dataset: ago/2025–mai/2026 */
const vagasGeneration = [
  { mes: "ago/25", total: 17, afirmativas: 2 },
  { mes: "set/25", total: 18, afirmativas: 2 },
  { mes: "out/25", total: 19, afirmativas: 3 },
  { mes: "nov/25", total: 20, afirmativas: 4 },
  { mes: "dez/25", total: 16, afirmativas: 3 },
  { mes: "jan/26", total: 19, afirmativas: 5 },
  { mes: "fev/26", total: 21, afirmativas: 6 },
  { mes: "mar/26", total: 23, afirmativas: 8 },
  { mes: "abr/26", total: 24, afirmativas: 9 },
  { mes: "mai/26", total: 23, afirmativas: 9 },
].map((d) => ({ ...d, naoAfirmativas: d.total - d.afirmativas }));

const tipoDiBreakdown = [
  { tipo: "Mulheres na Tecnologia", n: 22 },
  { tipo: "Pessoas Negras", n: 13 },
  { tipo: "PCD", n: 10 },
  { tipo: "PCD e Mulheres", n: 6 },
];

/* Home — comparativo de representação entre recortes (o que é comparável) */
const representacaoComparativa = [
  { recorte: "Ingressantes (Computação)", pct: 20.8, fonte: "inep" },
  { recorte: "Profissionais de Dados", pct: 26.8, fonte: "datahackers" },
  { recorte: "Força de trabalho em TIC", pct: 34.2, fonte: "global" },
  { recorte: "C-Suite em tecnologia", pct: 29.0, fonte: "global" },
  { recorte: "CTO / liderança técnica", pct: 15.0, fonte: "global" },
];

/* Funil — trajetória por etapa (fontes e populações distintas) */
const trajectoryStages = [
  { name: "Ingressantes em Computação", pctFem: 20.8, tag: "INEP · população, 2024" },
  { name: "Profissionais na área de Dados", pctFem: 26.8, tag: "State of Data Brasil 2021 · amostra n=2.645" },
  { name: "Cargos de gestão em Dados", pctFem: 14.6, tag: "State of Data Brasil 2021 · amostra" },
  { name: "C-Suite em tecnologia", pctFem: 29.0, tag: "WomenHack 2026 · benchmark global" },
  { name: "CTO / liderança técnica", pctFem: 15.0, tag: "WomenHack 2026 · benchmark global" },
];

/* IRF — área (estimativa de mercado, exceto Dados = real) e cargo (seniority) */
const pctMulheresPorArea = { Dados: 26.8, Desenvolvimento: 19.5, Gestão: 31.0, Infraestrutura: 14.0, "UX/UI": 44.5 };
const BASELINE_TIC = 34.2; // Brasscom — % mulheres na força de trabalho em TIC (Brasil)
const irfArea = AREAS.map((a) => ({ name: a, v: Math.round((pctMulheresPorArea[a] / BASELINE_TIC) * 100) / 100 }));

const pctMulheresPorCargo = {
  "Estagiário": 48.5, "Júnior": 39.3, "Pleno": 32.5, "Sênior": 25.3,
  "Gerente": 20.9, "Especialista": 23.6, "Diretor": 17.1, "CTO/CIO": 15.0,
};
const irfCargo = CARGOS.map((c) => ({ name: c, v: Math.round((pctMulheresPorCargo[c] / BASELINE_TIC) * 100) / 100 }));
function irfColor(v) {
  if (v >= 1.05) return C.deepest;
  if (v >= 0.9) return C.dark;
  if (v >= 0.65) return C.mid;
  return C.light;
}

/* Simulador RH — área x cargo, sem filtro de região */
const baseSalaryByCargo = {
  "Estagiário": 1900, "Júnior": 5200, "Pleno": 9200, "Sênior": 14500,
  "Gerente": 19800, "Especialista": 16200, "Diretor": 28500, "CTO/CIO": 38000,
};
const gapPctByCargo = {
  "Estagiário": 0.03, "Júnior": 0.08, "Pleno": 0.14, "Sênior": 0.21,
  "Gerente": 0.27, "Especialista": 0.19, "Diretor": 0.33, "CTO/CIO": 0.38,
};
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
        <KpiCard label="% mulheres entre ingressantes" value="20,8%" sub="Computação · INEP, 2024" trend="+2,6 p.p. desde 2019" />
        <KpiCard label="% mulheres na área de Dados" value="26,8%" sub="State of Data Brasil 2021 · n = 2.645" />
        <KpiCard label="Gap salarial em Dados (Brasil)" value="23,5%" sub="vs. 27% no setor de TIC geral (Brasscom)" />
        <KpiCard label="Mulheres em C-Suite tech" value="29%" sub="WomenHack 2026 · cai para 15% em CTO" />
      </div>
      <div className="chart-grid cols-2">
        <ChartCard title="Evolução da % de mulheres entre ingressantes" sub="Cursos de Computação · INEP, 2019–2024">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={inepIngressantes} margin={{ top: 8, right: 8, left: -16, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="ano" {...axisProps} />
              <YAxis domain={[15, 24]} {...axisProps} tickFormatter={(v) => `${v}%`} />
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
        <KpiCard label="Mulheres ingressantes" value={mulheresIngressantes2024.toLocaleString("pt-BR")} sub="Cursos de Computação · 2024" />
        <KpiCard label="Mulheres concluintes" value={mulheresConcluintes2024.toLocaleString("pt-BR")} sub="Cursos de Computação · 2024" />
        <KpiCard label="Taxa de evasão" value="21,4%" sub="Média geral, todos os gêneros" />
        <KpiCard label="Participação feminina entre ingressantes" value="20,8%" sub="Faixa do período: 18%–21% (2019–2024)" />
      </div>
      <div className="chart-grid cols-2">
        <ChartCard title="Evolução da % de mulheres entre ingressantes" sub="Cursos de Computação · 2019–2024">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={inepIngressantes} margin={{ top: 8, right: 8, left: -8, bottom: 0 }}>
              <CartesianGrid stroke={C.pale2} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="ano" {...axisProps} />
              <YAxis domain={[15, 24]} {...axisProps} tickFormatter={(v) => `${v}%`} />
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
          title="Evasão por gênero, segundo o curso"
          sub="Mulheres evadem mais que homens em todos os cursos"
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
              <XAxis type="number" domain={[0, 50]} {...axisProps} tickFormatter={(v) => `${v}%`} />
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
      <PageFooter>Fonte: INEP — Censo da Educação Superior (2019–2024). Participação feminina entre ingressantes mockada dentro da faixa real informada (18%–21%).</PageFooter>
    </div>
  );
}

function MercadoPage() {
  return (
    <div className="page">
      <PageHeader title="O Mercado de Dados" sub="Base oficial: State of Data Brasil 2021 (Data Hackers) · n = 2.645 respondentes" />
      <div className="kpi-grid">
        <KpiCard label="Respondentes na pesquisa" value="2.645" sub="State of Data Brasil 2021" />
        <KpiCard label="% mulheres na área de Dados" value="26,8%" sub="Do total de respondentes" />
        <KpiCard label="Gap salarial em Dados" value="23,5%" sub="Homens × Mulheres, Brasil" />
        <KpiCard label="% mulheres em cargos de gestão" value="14,6%" sub="vs. 21,3% dos homens" />
      </div>
      <div className="chart-grid cols-2">
        <ChartCard title="Representação feminina por função" sub="% mulheres em cada função, área de Dados" isNew>
          <HBars
            data={representacaoFuncaoDados}
            xKey="pct" yKey="funcao" domain={[0, 40]} height={260} width={140}
            colorFn={() => C.dark} refLine={26.8}
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
          <p className="rung-caption">Para cada 100 homens promovidos a cargos de gestão, apenas 87 mulheres são — um padrão global (McKinsey &amp; LeanIn) consistente com a sub-representação de gestoras que medimos na nossa base nacional de Dados (14,6%).</p>
        </ChartCard>
      </div>
      <PageFooter>Fonte: State of Data Brasil 2021 (Data Hackers) · n = 2.645 respondentes. Quebras por função, nível e faixa salarial são estimativas ilustrativas com base na estrutura da pesquisa, a recalcular no Power BI a partir da base real.</PageFooter>

      <SectionDivider label="Comparativo global" tag="WomenHack 2026 · Brasscom 2024/2025 · McKinsey & LeanIn 2025" icon={Globe} />
      <div className="kpi-grid">
        <KpiCard label="Mulheres em C-Suite tech" value="29%" sub="WomenHack 2026 (global)" />
        <KpiCard label="Mulheres em cargos técnicos de liderança" value="15%" sub="CTO · WomenHack 2026 (global)" />
        <KpiCard label="Retenção média — mulheres" value="3,1 anos" sub="vs. 4,2 anos para homens · WomenHack 2026" />
        <KpiCard label="Mulheres na força de trabalho em TIC" value="34,2%" sub="Brasil · Brasscom 2024/2025" />
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

      <SectionDivider label="Vagas afirmativas no mercado" tag="dado cedido · Generation" />
      <div className="kpi-grid kpi-grid-2">
        <KpiCard label="% de vagas afirmativas no período" value="25,5%" sub="ago/25–mai/26 · 51 de 200 vagas mapeadas" />
        <KpiCard label="Crescimento no período" value="+27,3 p.p." sub="De 11,8% (ago/25) para 39,1% (mai/26)" trend="iniciativas em alta" />
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
        <ChartCard title="Vagas afirmativas por tipo de ação" sub="Distribuição das 51 vagas afirmativas no período" isNew>
          <HBars
            data={tipoDiBreakdown}
            xKey="n" yKey="tipo" domain={[0, 26]} height={210} width={130} suffix=""
            colorFn={(_, i) => [C.deepest, C.dark, C.mid, C.light][i]}
          />
        </ChartCard>
      </div>
      <PageFooter>Vagas afirmativas: dado cedido pela Generation Brasil (webscraping LinkedIn, ago/2025–mai/2026).</PageFooter>
    </div>
  );
}

function FunilPage() {
  return (
    <div className="page">
      <PageHeader title="Trajetória da mulher em tecnologia" sub="Representação por etapa · INEP, State of Data Brasil 2021 e WomenHack 2026" />
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
              <strong>Maior recuo: −12,2 p.p.</strong>
              <p>Entre profissionais de Dados (26,8%) e quem chega à gestão na área (14,6%) — o ponto mais agudo de perda de representatividade que medimos na base nacional.</p>
            </div>
          </div>
          <div className="callout-note">
            Cada etapa parte de uma fonte e população diferente — Censo (INEP), pesquisa amostral (State of Data Brasil 2021) e benchmark internacional (WomenHack). A leitura é sobre hiatos de representação ao longo da trajetória típica, não uma coorte única acompanhada no tempo.
          </div>
        </div>
      </div>
      <PageFooter>Fontes: INEP · State of Data Brasil 2021 (Data Hackers) · WomenHack (2026).</PageFooter>
    </div>
  );
}

function IrfPage() {
  return (
    <div className="page">
      <PageHeader title="Índice de Representatividade Feminina" sub="IRF = % mulheres na categoria ÷ % mulheres na força de trabalho em TIC (34,2%, Brasscom)" />
      <NoteBanner>
        <strong>Nota metodológica:</strong> a área <strong>Dados</strong> usa a pesquisa real State of Data Brasil 2021 (n = 2.645); as demais áreas e o eixo de cargos seguem estimativas de mercado (Brasscom, WomenHack).
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
        <ChartCard title="IRF por cargo" sub="A liderança é o ponto de maior sub-representação" height={300}>
          <HBars data={irfCargo} xKey="v" yKey="name" domain={[0, 1.6]} height={300} suffix="" refLine={1} width={110} colorFn={(d) => irfColor(d.v)} />
        </ChartCard>
      </div>
      <PageFooter>Fonte: cálculo próprio (% mulheres na categoria ÷ 34,2%) com base em State of Data Brasil 2021, Brasscom e WomenHack. IRF de CTO/CIO ancorado no dado real de WomenHack (15%).</PageFooter>
    </div>
  );
}

function SimuladorPage() {
  const [area, setArea] = useState("Dados");
  const [cargo, setCargo] = useState("Pleno");

  const homens = Math.round(baseSalaryByCargo[cargo] * areaMultiplier[area]);
  const gapPct = gapPctByCargo[cargo];
  const mulheres = Math.round(homens * (1 - gapPct));
  const [start, end] = areaTrendRange[area];
  const serieArea = interp(start, end, ANOS.length).map((v, i) => ({ ano: ANOS[i], pct: v }));

  return (
    <div className="page">
      <PageHeader title="Simulador de RH" sub="Consulta de gap salarial e formação por área e cargo" />
      <NoteBanner>
        <strong>Nota metodológica:</strong> selecione <strong>Dados</strong> para a área com lastro em pesquisa real (State of Data Brasil 2021); as demais áreas usam estimativas de mercado.
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
      <p className="disclaimer">Valores ilustrativos para fins de prototipagem; a versão final deve usar dados reais de RH.</p>
      <div className="kpi-grid kpi-grid-3">
        <KpiCard label="Salário médio · mulheres" value={brl(mulheres)} sub={`${cargo} · ${area}`} />
        <KpiCard label="Salário médio · homens" value={brl(homens)} sub={`${cargo} · ${area}`} />
        <KpiCard label="Gap salarial neste cargo" value={`${(gapPct * 100).toFixed(1)}%`} sub="Homens × mulheres" />
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
      <PageFooter>Dados ilustrativos com base na metodologia State of Data Brasil 2021 / Brasscom, para fins de prototipagem.</PageFooter>
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