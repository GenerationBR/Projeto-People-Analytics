"""Agente 0 — Orquestrador (Project Manager Agent)."""

import json
import logging
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)


class OrchestratorAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o Orquestrador de um projeto de People Analytics & DE&I sobre a trajetória
feminina na tecnologia. Sua função é coordenar uma equipe de agentes especialistas.

Responsabilidades:
1. Quebrar o projeto em tarefas com dependências claras (ETL → Modelagem → Análise →
   Estatística → BI → Documentação → Pitch).
2. Delegar cada tarefa ao agente correto, definindo entradas, formato de saída e
   critério de aceite.
3. Antes de qualquer decisão metodológica sensível (o que conta como "Tech", o que é
   "liderança", como tratar gênero/outliers), apresentar a proposta a um humano para
   aprovação. NUNCA decidir sozinho premissas que afetam interpretação de DE&I.
4. Consolidar entregáveis e acionar o agente de QA antes de fechar cada etapa.

Regras: nunca invente dados; se um agente reportar dados ausentes ou ambíguos, registre
como risco e proponha alternativas. Mantenha um log de premissas versionado.
"""

    # Fases e ordem de dependências
    PIPELINE = [
        ("T-001", "etl",        "Extrair e tratar INEP e base de mercado tech brasil (Brasscom+StateOfData+McKinsey)"),
        ("T-002", "modeling",   "Modelar banco analítico (esquema estrela)"),
        ("T-003", "eda",        "Análise exploratória e funil feminino"),
        ("T-004", "statistics", "Teste de hipótese — Gender Pay Gap"),
        ("T-005", "docs",       "Dicionário de dados e README"),
        ("T-006", "pitch",      "Montar pitch executivo"),
        ("T-007", "qa",         "Validar consistência de todos os entregáveis"),
    ]

    OPTIONAL = [
        ("T-008", "scraping", "Web scraping LinkedIn — vagas com menção a D&I"),
    ]

    def __init__(self, output_dir: str = "outputs"):
        super().__init__("orchestrator", output_dir=output_dir)
        self.premises_log: list[dict] = []
        self.completed_tasks: list[str] = []
        self.risks: list[str] = []

    # ─── Premissas sensíveis ───────────────────────────────────────────────────

    def request_human_approval(self, topic: str, proposal: str) -> dict:
        """
        Registra premissa sensível que precisa de aprovação humana.
        Em produção, dispara notificação para o revisor.
        """
        entry = {
            "topic": topic,
            "proposal": proposal,
            "status": "AGUARDA_APROVACAO",
        }
        self.premises_log.append(entry)
        self.log_action(f"Premissa pendente de aprovação: {topic}")
        logger.warning(
            f"\n{'='*60}\n"
            f"[HUMAN-IN-THE-LOOP] Premissa sensível requer aprovação:\n"
            f"  Tópico: {topic}\n"
            f"  Proposta: {proposal}\n"
            f"{'='*60}"
        )
        return entry

    def approve_premise(self, topic: str, approved_by: str) -> None:
        for entry in self.premises_log:
            if entry["topic"] == topic:
                entry["status"] = "APROVADO"
                entry["aprovado_por"] = approved_by
                self.log_action(f"Premissa aprovada: {topic} por {approved_by}")

    # ─── Delegação ────────────────────────────────────────────────────────────

    def delegate(self, task_id: str, to_agent: str, description: str, context: dict | None = None) -> AgentMessage:
        msg = self.build_message(
            to_agent=to_agent,
            task_id=task_id,
            status="pending",
            payload={"description": description, "context": context or {}},
        )
        self.log_action(f"Delegando {task_id} → {to_agent}: {description}")
        return msg

    def receive_result(self, msg: AgentMessage) -> None:
        if msg.status == "done":
            self.completed_tasks.append(msg.task_id)
            self.log_action(f"Tarefa concluída: {msg.task_id} de {msg.from_agent}")
        elif msg.status == "error":
            self.risks.append(f"{msg.task_id}: {msg.payload.get('error', 'Erro desconhecido')}")
            logger.error(f"[{msg.from_agent}] Erro em {msg.task_id}: {msg.payload}")
        if msg.open_questions:
            for q in msg.open_questions:
                self.request_human_approval(f"{msg.task_id} — questão aberta", q)

    # ─── Relatório de status ──────────────────────────────────────────────────

    def status_report(self) -> str:
        total = len(self.PIPELINE) + len(self.OPTIONAL)
        done = len(self.completed_tasks)
        pending_premises = [p for p in self.premises_log if p["status"] == "AGUARDA_APROVACAO"]

        report = self.ask_llm(
            f"""Gere um relatório de status do projeto no seguinte formato:

Contexto:
- Tarefas total: {total} (obrigatórias: {len(self.PIPELINE)}, opcionais: {len(self.OPTIONAL)})
- Tarefas concluídas: {done} — {self.completed_tasks}
- Riscos identificados: {self.risks}
- Premissas aguardando aprovação humana: {[p['topic'] for p in pending_premises]}
- Log de ações: {self.log[-10:]}

Forneça:
1. % de conclusão
2. Próximos passos prioritários
3. Riscos que precisam de atenção imediata
4. Premissas bloqueando progresso (se houver)

Tom: objetivo e direto para um gerente de projeto."""
        )
        return report

    # ─── run() ────────────────────────────────────────────────────────────────

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("Orquestrador iniciado")

        # Premissas iniciais que precisam de aprovação humana
        self.request_human_approval(
            "Definição de 'Tech'",
            "Incluir: Ciência da Computação, Eng. de Computação, Sistemas de Informação, ADS, Eng. de Software, "
            "Redes, Banco de Dados, Ciência de Dados, IA, Segurança, Eng. Elétrica, Eletrônica, Telecom, "
            "Controle e Automação. Excluir: Civil, Química, Ambiental. Ver course_mapping.json."
        )
        self.request_human_approval(
            "Definição de 'Liderança'",
            "Considerar liderança: cargos Sênior, Staff, Lead, Manager, Gerente, Diretor, VP, C-Level. "
            "Ver campo 'lideranca' em premises.json."
        )
        self.request_human_approval(
            "Tratamento de outliers salariais",
            "Método proposto: Winsorization no percentil 99 (valores acima do p99 são substituídos por p99). "
            "Alternativa: remoção por IQR. Requer aprovação antes de rodar ETL."
        )
        self.request_human_approval(
            "Categorias de gênero",
            "INEP usa categorias binárias (Masculino/Feminino). "
            "Proposta: manter as categorias da fonte para fidelidade, registrar limitação na documentação."
        )

        # Gera o plano de execução
        plano = self.ask_llm(
            "Crie um plano de execução detalhado com dependências para o projeto de People Analytics "
            "sobre trajetória feminina na tecnologia. Pipeline: ETL → Modelagem → EDA → Estatística → "
            "BI → Docs → Pitch → QA. Inclua critérios de aceite para cada entregável."
        )

        plan_path = self.save_output("plano_execucao.md", plano)

        return self.build_message(
            to_agent="etl",
            task_id="T-001",
            status="pending",
            artifacts=[{"type": "plan", "path": str(plan_path)}],
            assumptions=[
                "Premissas sensíveis registradas e aguardam aprovação humana",
                "Ver config/premises.json e config/course_mapping.json",
            ],
            open_questions=[
                "Confirmar definição de 'Tech' (course_mapping.json)",
                "Confirmar definição de 'liderança'",
                "Confirmar método de outliers salariais",
            ],
            needs_human_approval=True,
            payload={"pipeline": self.PIPELINE, "optional": self.OPTIONAL},
        )
