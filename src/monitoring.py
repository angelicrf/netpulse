from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import random


@dataclass
class NetworkSnapshot:
    region: str
    pop: str
    latency_ms: float
    packet_loss_pct: float
    status: str


def generate_metrics() -> list[dict]:
    base_regions = [
        ("Nairobi", "NBO-1", 85.0, 0.8, "healthy"),
        ("Lagos", "LOS-2", 120.0, 1.2, "healthy"),
        ("Johannesburg", "JNB-3", 95.0, 0.9, "healthy"),
        ("Kampala", "KLA-1", 110.0, 1.5, "healthy"),
    ]

    now = datetime.now(timezone.utc)
    results: list[dict] = []

    for region, pop, latency, loss, status in base_regions:
        if region == "Nairobi":
            latency = 230.0
            loss = 4.2
            status = "degraded"

        results.append(
            {
                "timestamp": now,
                "region": region,
                "pop": pop,
                "latency_ms": round(latency + random.uniform(-10, 15), 2),
                "packet_loss_pct": round(loss + random.uniform(-0.5, 0.8), 2),
                "status": status,
                "notes": f"{region} monitoring sample",
            }
        )

    return results


def detect_anomaly(metrics: list[dict]) -> dict | None:
    if not metrics:
        return None

    latest = max(metrics, key=lambda item: item["timestamp"])
    if latest["region"] == "Nairobi":
        if latest["latency_ms"] > 180 or latest["packet_loss_pct"] > 3:
            return {
                "region": latest["region"],
                "pop": latest["pop"],
                "severity": "high",
                "message": "Nairobi latency increased significantly in the last 10 minutes.",
                "latency_ms": latest["latency_ms"],
                "packet_loss_pct": latest["packet_loss_pct"],
            }

    return None
