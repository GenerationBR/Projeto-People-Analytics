"""
People Analytics & DE&I — A Trajetória Feminina do Câmpus ao Mercado Tech
Pipeline principal de orquestração dos agentes de IA.

Uso:
  python main.py              # pipeline completo
  python main.py etl          # apenas ETL
  python main.py modeling     # apenas Modelagem
  python main.py eda          # apenas EDA
  python main.py stats        # apenas Estatística
  python main.py docs         # apenas Documentação
  python main.py pitch        # apenas Pitch
  python main.py qa           # apenas QA
  python main.py status       # Status do projeto
"""

import json
import logging
import sys
from pathlib import Path
from datetime import datetime

# ─── Logging ──────────────────────────────────────────────────────────────────

Path("logs").mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(f"logs/run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger("main")

# ─── Imports dos agentes ──────────────────────────────────────────────────────

from agents import (
    OrchestratorAgent,
    ETLAgent,
    ModelingAgent,
    EDAAgent,
    StatisticsAgent,
    DocsAgent,
    StorytellerAgent,
    QAAgent,
)

# ─── Configurações do projeto ─────────────────────────────────────────────────

CONFIG = {
    "config_dir":  "config",
    "data_dir":    "data",
    "output_dir":  "outputs",
    "db_path":     "data/analytics.duckdb",
}


def banner():
    print("\n" + "=" * 65)
    print("  People Analytics & DE&I")
    print("  A Trajetória Feminina do Câmpus ao Mercado Tech")
    print("  Sistema de Agentes de IA — Pipeline Completo")
    print("=" * 65 + "\n")


def run_etl(orchestrator: OrchestratorAgent) -> dict:
    logger.info("▶ Iniciando ETL Agent")
    agent = ETLAgent(**{k: CONFIG[k] for k in ["config_dir", "data_dir", "output_dir"]})
    result = agent.run()
    orchestrator.receive_result(result)
    return result.__dict__


def run_modeling(orchestrator: OrchestratorAgent) -> dict:
    logger.info("▶ Iniciando Modeling Agent")
    agent = ModelingAgent(db_path=CONFIG["db_path"], output_dir=CONFIG["output_dir"])
    result = agent.run()
    orchestrator.receive_result(result)
    return result.__dict__


def run_eda(orchestrator: OrchestratorAgent) -> dict:
    logger.info("▶ Iniciando EDA Agent")
    agent = EDAAgent(db_path=CONFIG["db_path"], output_dir=CONFIG["output_dir"])
    result = agent.run()
    orchestrator.receive_result(result)
    return result.__dict__


def run_statistics(orchestrator: OrchestratorAgent) -> dict:
    logger.info("▶ Iniciando Statistics Agent")
    agent = StatisticsAgent(db_path=CONFIG["db_path"], output_dir=CONFIG["output_dir"])
    result = agent.run()
    orchestrator.receive_result(result)
    return result.__dict__


def run_docs(orchestrator: OrchestratorAgent) -> dict:
    logger.info("▶ Iniciando Docs Agent")
    agent = DocsAgent(config_dir=CONFIG["config_dir"], output_dir=CONFIG["output_dir"])
    result = agent.run()
    orchestrator.receive_result(result)
    return result.__dict__


def run_pitch(orchestrator: OrchestratorAgent) -> dict:
    logger.info("▶ Iniciando Storyteller Agent")
    agent = StorytellerAgent(output_dir=CONFIG["output_dir"])
    result = agent.run()
    orchestrator.receive_result(result)
    return result.__dict__


def run_qa(orchestrator: OrchestratorAgent) -> dict:
    logger.info("▶ Iniciando QA Agent")
    agent = QAAgent(output_dir=CONFIG["output_dir"])
    result = agent.run()
    orchestrator.receive_result(result)
    approved = result.payload.get("approved", False)
    if not approved:
        logger.error("❌ QA BLOQUEOU A ENTREGA — ver outputs/relatorio_qa.md")
    else:
        logger.info("✅ QA APROVADO — projeto pronto para entrega")
    return result.__dict__


# ─── Pipeline completo ────────────────────────────────────────────────────────

PIPELINE_STEPS = [
    ("etl",       run_etl,        "T-001"),
    ("modeling",  run_modeling,   "T-002"),
    ("eda",       run_eda,        "T-003"),
    ("stats",     run_statistics, "T-004"),
    ("docs",      run_docs,       "T-005"),
    ("pitch",     run_pitch,      "T-006"),
    ("qa",        run_qa,         "T-007"),
]

OPTIONAL_STEPS: list = []


def run_full_pipeline():
    banner()
    orchestrator = OrchestratorAgent(output_dir=CONFIG["output_dir"])

    logger.info("▶ Orquestrador iniciado — verificando premissas")
    orch_result = orchestrator.run()

    if orch_result.needs_human_approval:
        print("\n" + "⚠" * 30)
        print("AÇÃO NECESSÁRIA: Premissas sensíveis aguardam aprovação humana.")
        print("Revise o arquivo: outputs/plano_execucao.md")
        print("Edite: config/premises.json — defina 'status': 'APROVADO' para cada premissa")
        print("Depois rode novamente: python main.py")
        print("⚠" * 30 + "\n")

    results = {}
    for step_name, step_fn, task_id in PIPELINE_STEPS:
        print(f"\n{'─'*50}")
        print(f"  Etapa: {step_name.upper()} ({task_id})")
        print(f"{'─'*50}")
        try:
            results[step_name] = step_fn(orchestrator)
        except Exception as e:
            logger.error(f"Erro no agente {step_name}: {e}", exc_info=True)
            results[step_name] = {"error": str(e)}

    # Diferenciais opcionais
    print("\n" + "═" * 50)
    print("  Executando diferenciais opcionais...")
    print("═" * 50)
    for step_name, step_fn, task_id in OPTIONAL_STEPS:
        try:
            results[step_name] = step_fn(orchestrator)
        except Exception as e:
            logger.warning(f"Opcional {step_name} falhou: {e}")

    # Salva log final
    log_path = Path(CONFIG["output_dir"]) / "pipeline_run_log.json"
    log_path.write_text(
        json.dumps(
            {"run_at": datetime.now().isoformat(), "results": {k: {"status": v.get("status")} for k, v in results.items()}},
            ensure_ascii=False, indent=2
        ),
        encoding="utf-8"
    )

    print("\n" + "=" * 65)
    print("  PIPELINE CONCLUÍDO")
    print(f"  Log: {log_path}")
    print(f"  QA:  outputs/relatorio_qa.md")
    print("=" * 65 + "\n")

    return orchestrator.status_report()


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "full"

    orchestrator = OrchestratorAgent(output_dir=CONFIG["output_dir"])

    dispatch = {
        "etl":      run_etl,
        "modeling": run_modeling,
        "eda":      run_eda,
        "stats":    run_statistics,
        "docs":     run_docs,
        "pitch":    run_pitch,
        "qa":       run_qa,
        "status":   lambda o: print(o.status_report()),
    }

    if cmd in dispatch:
        dispatch[cmd](orchestrator)
    elif cmd in ("full", "all"):
        run_full_pipeline()
    else:
        print(f"Comando desconhecido: '{cmd}'. Use: {list(dispatch.keys()) + ['full']}")
        sys.exit(1)
