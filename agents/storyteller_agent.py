"""Agente 7 — Storyteller (Executive Pitch Agent)."""

import json
import logging
from pathlib import Path

from .base_agent import AgentMessage, BaseAgent

logger = logging.getLogger(__name__)


class StorytellerAgent(BaseAgent):
    SYSTEM_PROMPT = """
Você é o Storyteller executivo. Público: RH e diretoria — pouco tempo, foco em decisão.

Construa o pitch como uma jornada (o FUNIL): comece pela promessa (entrada feminina nas
universidades), mostre os vazamentos (evasão, queda na empregabilidade, sub-representação
na liderança) e termine no pay gap, com a evidência estatística do teste T.

REFERÊNCIAS A USAR NO PITCH:
- Brasscom: base da análise salarial — gap médio de ~27% entre gêneros detectado nos dados
- State of Data Brazil: fonte dos cargos e senioridade analisados
- McKinsey (Women in the Workplace): fundamento do gargalo de liderança — dificuldade
  progressivamente maior para mulheres alcançarem Diretoria e CTO; excelente ponto de
  destaque no slide de sub-representação na liderança

Para cada slide: 1 ideia central, 1 número de impacto, 1 visual. Inclua um slide técnico
explicando como a equipe lidou com arquivos pesados (INEP) e como a base de mercado foi
construída (simulação baseada em Brasscom + State of Data + McKinsey). Feche com
recomendações ACIONÁVEIS de políticas de contratação. Tom: profissional, baseado em
evidências, sem sensacionalismo.
"""

    def __init__(self, output_dir: str = "outputs"):
        super().__init__("pitch", output_dir=output_dir)

    def _load_metrics(self) -> dict:
        path = Path(self.output_dir) / "metricas_funil.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _load_stats(self) -> dict:
        path = Path(self.output_dir) / "resultado_teste.json"
        if path.exists():
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def generate_pitch_script(self, metricas: dict, stats: dict) -> str:
        return self.ask_llm(
            f"""Crie o roteiro completo de uma apresentação executiva de 10-12 slides sobre
"A Trajetória Feminina do Câmpus ao Mercado Tech" para RH e diretoria de uma empresa de tecnologia.

Métricas do funil (use [X%] se vazio):
{json.dumps(metricas, ensure_ascii=False, indent=2)[:2000]}

Resultado estatístico:
{json.dumps(stats, ensure_ascii=False, indent=2)[:1000]}

ESTRUTURA OBRIGATÓRIA:

Slide 1 — CAPA: Título, subtítulo, data
Slide 2 — O PROBLEMA: Por que isso importa para o negócio? (1 dado macro impactante)
Slide 3 — A PROMESSA: Entrada feminina nas universidades tech (% matrículas)
Slide 4 — 1º VAZAMENTO: Taxa de evasão feminina vs masculina
Slide 5 — 2º VAZAMENTO: Queda na empregabilidade em tech
Slide 6 — 3º VAZAMENTO: Sub-representação em cargos de liderança
Slide 7 — O DESTINO: Gender Pay Gap (resultado do Teste T com p-valor e Cohen's d)
Slide 8 — TÉCNICO: Como tratamos arquivos pesados (INEP) e outliers salariais
Slide 9 — ONDE INTERVIR: Análise do maior gargalo do funil
Slide 10 — RECOMENDAÇÕES: 3 políticas acionáveis de contratação e retenção
Slide 11 — METODOLOGIA: Fontes, premissas e limitações (INEP; base de mercado simulada com Brasscom + State of Data Brazil + McKinsey; gap de 27% intencional para análise)
Slide 12 — PRÓXIMOS PASSOS: Data App, expansão da análise

Para cada slide: título, ideia central (1 frase), dado de impacto, descrição do visual sugerido.
Tom: profissional, empático, baseado em evidências. Sem sensacionalismo."""
        )

    def generate_slide_deck_md(self, script: str) -> str:
        return self.ask_llm(
            f"""A partir do roteiro abaixo, gere um deck de slides em Markdown usando formato Marp
(compatível com VS Code extension Marp for VS Code e marp-cli).

Roteiro:
{script[:4000]}

Use:
- `---` para separar slides
- Títulos H1 (#) para o título do slide
- Bullet points concisos (máx 3 por slide)
- Indicação de visual: `> [Visual: descrição]`
- Paleta de cores: azul (#1E3A5F), rosa (#E91E8C), branco (#FFFFFF), cinza (#F5F5F5)

Frontmatter Marp:
```yaml
---
marp: true
theme: default
paginate: true
backgroundColor: '#FFFFFF'
color: '#1E3A5F'
---
```"""
        )

    def generate_policy_recommendations(self, metricas: dict, stats: dict) -> str:
        return self.ask_llm(
            f"""Com base nos dados de People Analytics sobre trajetória feminina na tecnologia,
gere 5 recomendações de políticas acionáveis para RH e diretoria.

Contexto:
{json.dumps({"metricas_funil": metricas, "pay_gap_stats": stats}, ensure_ascii=False, indent=2)[:2000]}

Para cada recomendação:
- Nome da política
- Problema que resolve (etapa do funil)
- Ação concreta (o que fazer nos próximos 90 dias)
- Métrica de sucesso (como medir em 12 meses)
- Custo estimado: baixo/médio/alto

Exemplos de áreas: recrutamento ativo, programas de bolsa/mentoria, cultura inclusiva,
transparência salarial, trilha de liderança. Baseie-se nos dados — não generealize."""
        )

    def run(self, incoming: AgentMessage | None = None) -> AgentMessage:
        self.log_action("Storyteller Agent iniciado")

        metricas = self._load_metrics()
        stats = self._load_stats()

        script = self.generate_pitch_script(metricas, stats)
        script_path = self.save_output("pitch/roteiro_pitch.md", script)

        deck = self.generate_slide_deck_md(script)
        deck_path = self.save_output("pitch/slides_marp.md", deck)

        policies = self.generate_policy_recommendations(metricas, stats)
        policies_path = self.save_output("pitch/recomendacoes_politicas.md", policies)

        return self.build_message(
            to_agent="qa",
            task_id="T-007",
            status="done",
            artifacts=[
                {"type": "script", "path": str(script_path)},
                {"type": "slides_marp", "path": str(deck_path)},
                {"type": "policies", "path": str(policies_path)},
            ],
            assumptions=[
                "Slides gerados em formato Marp (Markdown) — renderizar com marp-cli ou VS Code",
                "Todos os números no pitch têm origem rastreável nos arquivos outputs/",
                "Recomendações baseadas nos dados — não genéricas",
            ],
            open_questions=[
                "Validar que todos os números citados nos slides correspondem ao banco analítico",
                "Confirmar com QA que métricas do pitch == métricas do dashboard",
            ],
        )
