import logging
import os
import sys
from pathlib import Path


LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "app.log"


def _check_venv() -> bool:
    """Überprüfe, ob die App in einem venv läuft."""
    return hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    )


def setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    logger = logging.getLogger(__name__)

    if _check_venv():
        logger.info("Läuft in virtualenv: %s", sys.prefix)
    else:
        logger.warning(
            "App läuft NICHT in einem virtualenv. "
            "Umgebungsvariablen könnten nicht korrekt gesetzt sein. "
            "Bitte starten Sie die App mit: .venv/Scripts/activate.bat (Windows) "
            "oder source .venv/bin/activate (Unix)"
        )

    logger.info("Python Interpreter: %s", sys.executable)
    logger.info("PATH: %s", os.environ.get("PATH", "<nicht gesetzt>"))
