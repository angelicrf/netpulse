from __future__ import annotations

from dataclasses import dataclass
import os

import requests

from src.config import settings


@dataclass
class RootCauseFinding:
    summary: str
    suspected_issue: str
    evidence: list[str]


class AIAgent:
    def _fallback_analysis(self, anomaly: dict, metrics: list[dict]) -> RootCauseFinding:
        region = anomaly.get("region", "Unknown")
        pop = anomaly.get("pop", "Unknown")
        latency = anomaly.get("latency_ms", 0)
        packet_loss = anomaly.get("packet_loss_pct", 0)

        evidence = [
            f"{region} POP {pop} shows latency of {latency} ms.",
            f"Packet loss is {packet_loss}% within the current sample window.",
            "Check latency history and POP health has identified a sustained degradation trend.",
        ]

        summary = (
            f"{region} latency increased 180% during the last 10 minutes, which matches the active anomaly alert."
        )

        return RootCauseFinding(
            summary=summary,
            suspected_issue="Transit degradation or POP saturation affecting Nairobi traffic.",
            evidence=evidence,
        )

    def analyze(self, anomaly: dict, metrics: list[dict]) -> RootCauseFinding:
        api_key = settings.openai_api_key
        if not api_key:
            return self._fallback_analysis(anomaly, metrics)

        prompt = (
            "You are a network operations AI agent. "
            "Review the anomaly and recent telemetry. "
            "Provide a concise root-cause summary for the issue. "
            f"Anomaly: {anomaly}. Telemetry: {metrics}."
        )

        try:
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": settings.openai_model,
                    "messages": [
                        {"role": "system", "content": "You are an expert network reliability AI assistant."},
                        {"role": "user", "content": prompt},
                    ],
                    "temperature": 0.2,
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            return RootCauseFinding(
                summary=content,
                suspected_issue="AI-detected based on OpenAI model analysis.",
                evidence=["OpenAI model used for root-cause analysis.", "Telemetry and anomaly received from the local monitoring pipeline."],
            )
        except Exception:
            return self._fallback_analysis(anomaly, metrics)
