"""Agente 8 — Web Scraping LinkedIn (diferencial / opcional)."""

import logging
import time
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)

# Termos de D&I auditáveis — lista transparente e editável
DI_TERMS = [
    "diversidade", "inclusão", "equidade", "diversity", "inclusion", "equity",
    "DEI", "D&I", "igualdade de gênero", "gender equality", "mulheres em tech",
    "women in tech", "programa de diversidade", "vaga afirmativa",
    "pessoas negras", "LGBTQIA", "PCD", "pessoa com deficiência",
]


class ScrapingAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o agente de coleta complementar de vagas tech. Objetivo: quantificar quantas vagas
mencionam iniciativas de diversidade (D&I) na descrição.

Antes de qualquer coleta:
- Verifique a viabilidade legal/ética. Prefira APIs oficiais e dados públicos. Respeite
  robots.txt, rate limits e a LGPD. Não colete dados pessoais identificáveis.
- Sinalize riscos ao Orquestrador e aguarde aprovação humana.
Na análise, use NLP para classificar menções a diversidade (lista de termos auditável) e
reporte a proporção de vagas com D&I por cargo/região. Documente vieses de amostragem.
"""

    def __init__(self, output_dir: str = "outputs"):
        super().__init__("scraping", output_dir=output_dir)

    # ─── Verificação ética ─────────────────────────────────────────────────────

    def assess_legal_risk(self) -> str:
        return self.ask_llm(
            """Avalie os riscos legais e éticos de realizar web scraping no LinkedIn para
coletar vagas de tecnologia, especificamente:
1. Violação dos Termos de Uso do LinkedIn (hiQ Labs v. LinkedIn precedente)
2. Conformidade com a LGPD (dados pessoais identificáveis x dados públicos)
3. Alternativas legais: LinkedIn Job Search API, Glassdoor API, Indeed API, vagas.com.br, InfoJobs
4. O que pode ser coletado sem violar ToS

Conclua com uma recomendação clara: usar API oficial ou scraping controlado, com justificativa."""
        )

    # ─── Análise de D&I nas descrições ────────────────────────────────────────

    def classify_di_mentions(self, descricoes: list[str]) -> dict:
        """
        Classifica menções a D&I nas descrições de vaga.
        Retorna contagens e proporção.
        """
        total = len(descricoes)
        com_di = 0
        matches_por_termo: dict[str, int] = {t: 0 for t in DI_TERMS}

        for desc in descricoes:
            desc_lower = desc.lower()
            menciona_di = False
            for termo in DI_TERMS:
                if termo.lower() in desc_lower:
                    matches_por_termo[termo] += 1
                    menciona_di = True
            if menciona_di:
                com_di += 1

        return {
            "total_vagas": total,
            "vagas_com_di": com_di,
            "pct_com_di": round(com_di / total * 100, 2) if total > 0 else 0,
            "matches_por_termo": {k: v for k, v in matches_por_termo.items() if v > 0},
            "termos_auditaveis": DI_TERMS,
            "bias_amostragem": [
                "Vagas coletadas refletem a plataforma usada, não o mercado total",
                "Menção a D&I ≠ efetiva política de D&I — é sinalização",
                "Período de coleta pode influenciar resultados (ex: datas próximas ao Dia da Mulher)",
            ],
        }

    def generate_collection_script(self) -> str:
        """Gera um script de coleta via API oficial (alternativa ao scraping)."""
        return self.ask_llm(
            f"""Gere um script Python para coletar vagas de tecnologia de fontes OFICIAIS
(sem violar ToS), identificar menções a D&I e produzir dataset analítico.

Fontes preferidas (em ordem):
1. API Vagas.com.br ou InfoJobs (nacionais)
2. Glassdoor Jobs API (se disponível)
3. RSS feeds públicos de empresas tech
4. Dados públicos do CAGED/MTE sobre vagas formais

Termos D&I a detectar: {DI_TERMS[:10]}...

O script deve:
- Respeitar rate limits (sleep entre requests)
- NÃO coletar dados pessoais identificáveis (nome, CPF, email)
- Salvar em Parquet: campos = titulo_vaga, empresa, cargo, regiao, data_publicacao, menciona_di, termos_detectados
- Gerar relatório: total vagas, % com D&I, top termos, por cargo e região
- Incluir docstring com aviso legal

Use requests + BeautifulSoup (apenas se página pública) ou SDK oficial da plataforma."""
        )

    # ─── run() ────────────────────────────────────────────────────────────────

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("Scraping Agent iniciado — verificação ética primeiro")

        # Sempre avalia risco legal antes de qualquer coleta
        risk_report = self.assess_legal_risk()
        risk_path = self.save_output("scraping_avaliacao_legal.md", risk_report)

        # Gera script de coleta via fontes oficiais
        script = self.generate_collection_script()
        script_path = self.save_output("scraping_coleta_vagas.py", script)

        # Demonstração com dados fictícios (sem scraping real)
        demo_descricoes = [
            "Buscamos profissionais para compor equipe diversa e inclusiva. Valorizamos DEI.",
            "Desenvolvedor Python Sênior. Requisitos: 5 anos Python, AWS.",
            "Programa de diversidade: vaga afirmativa para mulheres em tecnologia.",
            "Analista de Dados — igualdade de oportunidades, pessoas com deficiência bem-vindas.",
            "Engenheiro de Software — não há menção específica a diversidade.",
        ] * 20  # Simula 100 vagas

        di_analysis = self.classify_di_mentions(demo_descricoes)
        analysis_path = self.save_output(
            "scraping_analise_di_demo.json",
            __import__("json").dumps(di_analysis, ensure_ascii=False, indent=2)
        )

        return self.build_message(
            to_agent="orchestrator",
            task_id="T-009",
            status="needs_human_approval",
            artifacts=[
                {"type": "legal_report", "path": str(risk_path)},
                {"type": "collection_script", "path": str(script_path)},
                {"type": "demo_analysis", "path": str(analysis_path)},
            ],
            assumptions=[
                "Scraping direto do LinkedIn NÃO executado — risco legal avaliado primeiro",
                "Lista de termos D&I é auditável e editável em scraping_agent.py:DI_TERMS",
                "Análise demonstrativa usa dados fictícios — substituir por coleta real aprovada",
            ],
            open_questions=[
                "Aprovação humana necessária para qualquer coleta — ver scraping_avaliacao_legal.md",
                "Qual API/fonte oficial a equipe tem acesso ou orçamento para contratar?",
            ],
            needs_human_approval=True,
        )
