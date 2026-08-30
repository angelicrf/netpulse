from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.agent import AIAgent
from src.database import fetch_latest_metrics, initialize_db, insert_metrics
from src.monitoring import detect_anomaly, generate_metrics


def main() -> None:
    initialize_db()
    metrics = generate_metrics()
    insert_metrics(metrics)

    anomaly = detect_anomaly(metrics)
    if anomaly is None:
        print("No anomaly detected.")
        return

    print("Anomaly detected:")
    print(anomaly)

    agent = AIAgent()
    finding = agent.analyze(anomaly, metrics)
    print("\nRoot-cause analysis:")
    print(finding.summary)
    print(f"Suspected issue: {finding.suspected_issue}")
    for item in finding.evidence:
        print(f"- {item}")

    print("\nRecent metrics:")
    for row in fetch_latest_metrics(limit=5):
        print(row)


if __name__ == "__main__":
    main()
