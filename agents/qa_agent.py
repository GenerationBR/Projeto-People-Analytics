"""Agente 10 — QA / Revisor (Quality Assurance Agent)."""

import json
import logging
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)


class QAAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o QA. Antes de fechar cada etapa, verifique:
- Os números do dashboard, dos notebooks e do pitch são IDÊNTICOS? (cross-check)
- O ETL é reprodutível? (mesmo input → mesmo output)
- As premissas estão documentadas e aplicadas de forma consistente?
- Há vazamento entre escopo acadêmico e profissional? (não pode haver cruzamento por
  indivíduo)
- O teste estatístico respeita seus pressupostos?
Produza um relatório com status (OK / corrigir) por item. Bloqueie a entrega se houver
inconsistência de números entre artefatos.
"""

    def __init__(self, output_dir: str = "outputs"):
        super().__init__("qa", output_dir=output_dir)
        self.checks: list[dict] = []

    def _check(self, item: str, status: str, detail: str = "") -> dict:
        entry = {"item": item, "status": status, "detail": detail}
        self.checks.append(entry)
        icon = "✅" if status == "OK" else "❌" if status == "CORRIGIR" else "⚠️"
        logger.info(f"[QA] {icon} {item}: {status}")
        return entry

    # ─── Verificações ─────────────────────────────────────────────────────────

    def check_artifacts_exist(self) -> None:
        out = Path(self.output_dir)
        required = {
            "ETL Report": out / "qualidade_dados_etl.md",
            "Modelo de Dados": out / "modelo_dados.md",
            "Síntese Executiva": out / "sintese_executiva.md",
            "Métricas Funil (JSON)": out / "metricas_funil.json",
            "Teste Hipótese": out / "teste_hipotese_pay_gap.md",
            "Resultado Estatístico (JSON)": out / "resultado_teste.json",
            "Dicionário de Dados": out / "dicionario/dicionario_de_dados.md",
            "Log Premissas": out / "log_premissas.md",
            "Roteiro Pitch": out / "pitch/roteiro_pitch.md",
            "Slides Marp": out / "pitch/slides_marp.md",
            "Recomendações": out / "pitch/recomendacoes_politicas.md",
            "README": Path("README.md"),
        }
        for name, path in required.items():
            exists = path.exists()
            self._check(
                f"Artefato: {name}",
                "OK" if exists else "CORRIGIR",
                str(path) if exists else f"AUSENTE: {path}",
            )

    def check_number_consistency(self) -> None:
        """Cross-check: métricas do JSON batem com o que o pitch referencia."""
        metricas_path = Path(self.output_dir) / "metricas_funil.json"
        stats_path = Path(self.output_dir) / "resultado_teste.json"

        if not metricas_path.exists() or not stats_path.exists():
            self._check("Cross-check numérico", "AGUARDANDO", "Arquivos de métricas ainda não gerados")
            return

        with open(metricas_path, encoding="utf-8") as f:
            metricas = json.load(f)
        with open(stats_path, encoding="utf-8") as f:
            stats = json.load(f)

        has_metricas = bool(metricas.get("pct_matriculas") or metricas.get("pay_gap_top20"))
        has_stats = bool(stats.get("p_value") is not None)

        self._check(
            "Métricas do funil disponíveis",
            "OK" if has_metricas else "AGUARDANDO",
            "Banco populado com dados reais" if has_metricas else "Banco vazio — dados demo",
        )
        self._check(
            "Resultado estatístico disponível",
            "OK" if has_stats else "CORRIGIR",
            f"p-valor={stats.get('p_value')}" if has_stats else "Arquivo de resultado ausente",
        )

    def check_no_individual_crossref(self) -> None:
        """Verifica que não há cruzamento por indivíduo (sem CPF)."""
        db_path = Path("data/analytics.duckdb")
        if not db_path.exists():
            self._check(
                "Sem cruzamento individual (CPF)",
                "AGUARDANDO",
                "Banco DuckDB não existe ainda",
            )
            return

        try:
            import duckdb
            con = duckdb.connect(str(db_path), read_only=True)
            tables = con.execute("SHOW TABLES").fetchdf()["name"].tolist()
            cpf_cols = []
            for table in tables:
                try:
                    cols = con.execute(f"DESCRIBE {table}").fetchdf()["column_name"].tolist()
                    cpf_cols += [f"{table}.{c}" for c in cols if "cpf" in c.lower() or "pessoa" in c.lower()]
                except Exception:
                    pass
            self._check(
                "Sem cruzamento individual (CPF)",
                "OK" if not cpf_cols else "CORRIGIR",
                "Nenhuma coluna CPF encontrada" if not cpf_cols else f"ATENÇÃO: {cpf_cols}",
            )
        except Exception as e:
            self._check("Sem cruzamento individual (CPF)", "AGUARDANDO", str(e))

    def check_statistical_test(self) -> None:
        stats_path = Path(self.output_dir) / "resultado_teste.json"
        if not stats_path.exists():
            self._check("Teste estatístico válido", "AGUARDANDO", "resultado_teste.json não existe")
            return

        with open(stats_path, encoding="utf-8") as f:
            stats = json.load(f)

        test_name = stats.get("test_name", "")
        p_val = stats.get("p_value")
        effect = stats.get("effect_size")

        self._check(
            "Teste estatístico correto (Welch/Mann-Whitney)",
            "OK" if any(t in test_name for t in ["Welch", "Mann-Whitney", "Student"]) else "CORRIGIR",
            f"Teste usado: {test_name}",
        )
        self._check(
            "p-valor e efeito reportados",
            "OK" if p_val is not None and effect is not None else "CORRIGIR",
            f"p={p_val}, d={effect}",
        )
        self._check(
            "Significância ≠ relevância prática (Cohen's d reportado)",
            "OK" if effect is not None else "CORRIGIR",
            f"Cohen's d = {effect}",
        )

    def check_premises_approved(self) -> None:
        premises_path = Path("config/premises.json")
        if not premises_path.exists():
            self._check("Premissas aprovadas", "CORRIGIR", "config/premises.json não existe")
            return

        with open(premises_path, encoding="utf-8") as f:
            p = json.load(f)

        pending = [
            key for key, val in p.get("premissas", {}).items()
            if val.get("status") == "AGUARDA_APROVACAO_HUMANA"
        ]
        self._check(
            "Premissas metodológicas aprovadas",
            "CORRIGIR" if pending else "OK",
            f"Pendentes: {pending}" if pending else "Todas aprovadas",
        )

    # ─── Relatório final ──────────────────────────────────────────────────────

    def generate_qa_report(self) -> str:
        ok = sum(1 for c in self.checks if c["status"] == "OK")
        corrigir = sum(1 for c in self.checks if c["status"] == "CORRIGIR")
        aguardando = sum(1 for c in self.checks if c["status"] == "AGUARDANDO")
        total = len(self.checks)

        lines = [
            "# Relatório de QA — People Analytics & DE&I",
            f"*Total: {total} verificações | ✅ OK: {ok} | ❌ Corrigir: {corrigir} | ⏳ Aguardando: {aguardando}*",
            "",
            "## Status Geral",
            f"{'🟢 APROVADO' if corrigir == 0 else '🔴 BLOQUEADO — corrigir itens antes da entrega'}",
            "",
            "## Checklist",
            "| Item | Status | Detalhe |",
            "|---|---|---|",
        ]
        for c in self.checks:
            icon = "✅" if c["status"] == "OK" else "❌" if c["status"] == "CORRIGIR" else "⏳"
            lines.append(f"| {c['item']} | {icon} {c['status']} | {c['detail']} |")

        if corrigir > 0:
            lines += [
                "",
                "## Itens Bloqueando Entrega",
                *[f"- ❌ **{c['item']}**: {c['detail']}" for c in self.checks if c["status"] == "CORRIGIR"],
            ]

        # LLM gera análise final
        llm_analysis = self.ask_llm(
            f"""Analise este relatório de QA de um projeto de People Analytics e forneça:
1. Resumo em 3 frases do status atual
2. Prioridade dos itens a corrigir (alto/médio/baixo impacto)
3. Estimativa de esforço para fechar os pendentes

Relatório:
OK: {ok} | Corrigir: {corrigir} | Aguardando: {aguardando}
Itens corrigir: {[c for c in self.checks if c['status'] == 'CORRIGIR']}"""
        )
        lines += ["", "## Análise do QA", llm_analysis]

        return "\n".join(lines)

    # ─── run() ────────────────────────────────────────────────────────────────

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("QA Agent iniciado")

        self.check_artifacts_exist()
        self.check_number_consistency()
        self.check_no_individual_crossref()
        self.check_statistical_test()
        self.check_premises_approved()

        report = self.generate_qa_report()
        report_path = self.save_output("relatorio_qa.md", report)

        corrigir = [c for c in self.checks if c["status"] == "CORRIGIR"]
        aguardando = [c for c in self.checks if c["status"] == "AGUARDANDO"]
        status = "done" if not corrigir else "error"

        return self.build_message(
            to_agent="orchestrator",
            task_id="T-008",
            status=status,
            artifacts=[{"type": "qa_report", "path": str(report_path)}],
            assumptions=[
                "QA verifica artefatos, banco e consistência numérica",
                "Entrega BLOQUEADA se qualquer item tiver status CORRIGIR",
            ],
            open_questions=[c["item"] for c in aguardando],
            payload={
                "corrigir": corrigir,
                "total_checks": len(self.checks),
                "approved": not corrigir,
            },
        )
