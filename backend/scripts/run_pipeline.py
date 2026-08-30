from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from backend.src.agent import AIAgent
from backend.src.database import (
    fetch_latest_metrics,
    fetch_latest_root_cause_analyses,
    initialize_db,
    insert_metrics,
    insert_root_cause_analysis,
)
from backend.src.config import settings
from backend.src.monitoring import detect_anomaly, generate_metrics


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
    print(f"OpenAI API key loaded: {'yes' if bool(settings.openai_api_key) else 'no'}")
    model_used = settings.openai_model if settings.openai_api_key else "fallback"
    insert_root_cause_analysis(anomaly, finding, model_used)

    print("\nRoot-cause analysis:")
    print(f"Title: {finding.title}")
    print(f"Subtitle: {finding.subtitle}")
    print(finding.summary)
    print(f"Suspected issue: {finding.suspected_issue}")
    print(f"Prediction: {finding.prediction}")
    print(f"Workaround: {finding.workaround}")
    print(f"Confidence: {finding.confidence:.2f}")
    print(f"Source: {finding.source}")
    for item in finding.evidence:
        print(f"- {item}")

    print("\nRecent root-cause analyses:")
    for row in fetch_latest_root_cause_analyses(limit=5):
        print(row)

    print("\nRecent metrics:")
    for row in fetch_latest_metrics(limit=5):
        print(row)


if __name__ == "__main__":
    main()
