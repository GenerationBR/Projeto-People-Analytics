"""Classe base para todos os agentes — encapsula chamadas ao LLM Anthropic."""

import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import anthropic

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    from_agent: str
    to_agent: str
    task_id: str
    status: str  # "pending" | "done" | "error" | "needs_human_approval"
    artifacts: list[dict] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    open_questions: list[str] = field(default_factory=list)
    needs_human_approval: bool = False
    payload: dict = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_json(self) -> str:
        return json.dumps(self.__dict__, ensure_ascii=False, indent=2)


class BaseAgent(ABC):
    """
    Agente base com chamada ao LLM e protocolo de handoff padronizado.
    Subclasses implementam `run()` com lógica específica.
    """

    SYSTEM_PROMPT: str = ""

    def __init__(
        self,
        name: str,
        model: str = "claude-sonnet-4-6",
        output_dir: str = "outputs",
    ):
        self.name = name
        self.model = model
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else None
        self.log: list[dict] = []

    # ─── LLM ──────────────────────────────────────────────────────────────────

    def ask_llm(self, user_message: str, max_tokens: int = 4096) -> str:
        """Envia mensagem ao LLM e retorna a resposta em texto."""
        if not self.client:
            logger.warning(f"[{self.name}] ANTHROPIC_API_KEY não definida — resposta simulada.")
            return f"[SIMULADO] Agente {self.name} processaria: {user_message[:100]}..."

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=self.SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text

    # ─── Protocolo de handoff ─────────────────────────────────────────────────

    def build_message(
        self,
        to_agent: str,
        task_id: str,
        status: str,
        artifacts: list[dict] | None = None,
        assumptions: list[str] | None = None,
        open_questions: list[str] | None = None,
        needs_human_approval: bool = False,
        payload: dict | None = None,
    ) -> AgentMessage:
        return AgentMessage(
            from_agent=self.name,
            to_agent=to_agent,
            task_id=task_id,
            status=status,
            artifacts=artifacts or [],
            assumptions=assumptions or [],
            open_questions=open_questions or [],
            needs_human_approval=needs_human_approval,
            payload=payload or {},
        )

    def save_output(self, filename: str, content: str) -> Path:
        path = self.output_dir / filename
        path.write_text(content, encoding="utf-8")
        logger.info(f"[{self.name}] Salvo: {path}")
        return path

    def log_action(self, action: str, detail: Any = None) -> None:
        entry = {"agent": self.name, "timestamp": datetime.now().isoformat(), "action": action}
        if detail:
            entry["detail"] = str(detail)
        self.log.append(entry)
        logger.info(f"[{self.name}] {action}")

    # ─── Interface pública ────────────────────────────────────────────────────

    @abstractmethod
    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        """Executa a lógica do agente e retorna mensagem de handoff."""
        ...
