from __future__ import annotations

from dataclasses import dataclass
import json
import requests

try:
    from backend.src.config import settings
except ModuleNotFoundError:
    from config import settings


@dataclass
class RootCauseFinding:
    title: str
    subtitle: str
    summary: str
    suspected_issue: str
    prediction: str
    workaround: str
    evidence: list[str]
    confidence: float
    source: str


class AIAgent:
    def _clean_json_text(self, text: str) -> str:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        return cleaned.strip()

    def _build_fallback_details(self, anomaly: dict, metrics: list[dict]) -> RootCauseFinding:
        region = anomaly.get("region", "Unknown")
        pop = anomaly.get("pop", "Unknown")
        latency = float(anomaly.get("latency_ms", 0))
        packet_loss = float(anomaly.get("packet_loss_pct", 0))
        severity = anomaly.get("severity", "unknown")

        healthy_samples = [m for m in metrics if m.get("region") == region and m.get("status") == "healthy"]
        if healthy_samples:
            baseline = sum(float(m.get("latency_ms", 0)) for m in healthy_samples) / len(healthy_samples)
        else:
            baseline = 100.0

        increase_pct = ((latency - baseline) / baseline * 100.0) if baseline > 0 else 0.0
        prediction = (
            f"If no intervention occurs, {region} may continue to exceed 200 ms latency and 3% packet loss "
            "during the next 30-60 minutes, likely triggering repeated customer-impact alerts."
        )
        workaround = (
            "Immediately reroute traffic away from the affected POP where possible, "
            "reduce non-critical load, verify upstream transit health, and run link/interface checks "
            "for congestion or errors on the POP edge."
        )

        evidence = [
            f"Current latency at {region}/{pop}: {latency:.2f} ms.",
            f"Current packet loss: {packet_loss:.2f}%.",
            f"Estimated latency increase over baseline ({baseline:.2f} ms): {increase_pct:.1f}%.",
            f"Anomaly severity reported by detector: {severity}.",
        ]

        return RootCauseFinding(
            title=f"{region} POP Performance Degradation",
            subtitle=f"POP {pop} shows elevated latency and packet loss",
            summary=(
                f"{region} ({pop}) is experiencing a significant performance regression with "
                f"latency at {latency:.2f} ms and packet loss at {packet_loss:.2f}%. "
                f"This points to a likely transit or saturation issue requiring immediate mitigation."
            ),
            suspected_issue="Transit degradation or POP saturation affecting regional traffic.",
            prediction=prediction,
            workaround=workaround,
            evidence=evidence,
            confidence=0.68,
            source="fallback-rule-based",
        )

    def _fallback_analysis(self, anomaly: dict, metrics: list[dict]) -> RootCauseFinding:
        return self._build_fallback_details(anomaly, metrics)

    def analyze(self, anomaly: dict, metrics: list[dict]) -> RootCauseFinding:
        api_key = settings.openai_api_key
        if not api_key:
            return self._fallback_analysis(anomaly, metrics)

        prompt = (
            "You are a network operations AI agent. "
            "Return ONLY valid JSON with these keys: "
            "title, subtitle, summary, suspected_issue, prediction, workaround, evidence, confidence. "
            "Constraints: summary 60-120 words, prediction time-bound and precise, "
            "workaround should be actionable in 3-5 steps in a single paragraph, "
            "evidence must be an array of 3-6 short bullet strings, confidence between 0 and 1. "
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
                    "response_format": {"type": "json_object"},
                    "temperature": 0.2,
                },
                timeout=30,
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"].strip()
            payload = json.loads(self._clean_json_text(content))

            confidence = float(payload.get("confidence", 0.7))
            confidence = max(0.0, min(confidence, 1.0))

            return RootCauseFinding(
                title=payload.get("title", "AI Root-Cause Analysis"),
                subtitle=payload.get("subtitle", "Network anomaly assessment"),
                summary=payload.get("summary", content),
                suspected_issue=payload.get("suspected_issue", "AI-detected network reliability issue."),
                prediction=payload.get("prediction", "Prediction not provided by model."),
                workaround=payload.get("workaround", "Workaround not provided by model."),
                evidence=payload.get("evidence", ["No structured evidence provided."]),
                confidence=confidence,
                source=f"openai:{settings.openai_model}",
            )
        except Exception:
            return RootCauseFinding(
                title="OpenAI Analysis Unavailable",
                subtitle="Model response failed validation or API call failed",
                summary=(
                    "OpenAI analysis could not be generated for this anomaly due to a runtime/API issue. "
                    "No fallback analysis was used because OpenAI-only mode is enabled when an API key is present."
                ),
                suspected_issue="Unable to determine due to OpenAI response failure.",
                prediction="Prediction unavailable until OpenAI request succeeds.",
                workaround=(
                    "Verify OPENAI_API_KEY, outbound network access, and model availability; "
                    "then rerun the pipeline to generate a fresh OpenAI analysis."
                ),
                evidence=["OpenAI request or response parsing failed."],
                confidence=0.0,
                source="openai-error",
            )
