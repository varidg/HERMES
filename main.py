"""
main.py
-------
MIDAS entry point.

Usage:
    python main.py          # waits for scheduled time
    python main.py --now    # fires all pipelines immediately, then waits
"""

import sys
import time
from orchestrator import Orchestrator
from utils.logger import get_logger

log = get_logger("Main")


def main() -> None:
    run_now = "--now" in sys.argv
    orchestrator = Orchestrator()
    orchestrator.start(run_now=run_now)

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        log.info("MIDAS shutting down. Goodbye.")


if __name__ == "__main__":
    main()
