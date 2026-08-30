from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from backend.src.config import settings


class Base(DeclarativeBase):
    pass


class NetworkMetric(Base):
    __tablename__ = "network_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    region: Mapped[str] = mapped_column(nullable=False)
    pop: Mapped[str] = mapped_column(nullable=False)
    latency_ms: Mapped[float] = mapped_column(nullable=False)
    packet_loss_pct: Mapped[float] = mapped_column(nullable=False)
    status: Mapped[str] = mapped_column(nullable=False)
    notes: Mapped[str] = mapped_column(nullable=True)


class RootCauseAnalysis(Base):
    __tablename__ = "root_cause_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
    region: Mapped[str] = mapped_column(nullable=False)
    pop: Mapped[str] = mapped_column(nullable=False)
    severity: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False, default="AI Root-Cause Analysis")
    subtitle: Mapped[str] = mapped_column(nullable=False, default="Network anomaly assessment")
    summary: Mapped[str] = mapped_column(nullable=False)
    suspected_issue: Mapped[str] = mapped_column(nullable=False)
    prediction: Mapped[str] = mapped_column(nullable=True)
    workaround: Mapped[str] = mapped_column(nullable=True)
    evidence: Mapped[str] = mapped_column(nullable=True)
    confidence: Mapped[float] = mapped_column(nullable=True)
    source: Mapped[str] = mapped_column(nullable=False, default="fallback-rule-based")
    model: Mapped[str] = mapped_column(nullable=False)


engine = create_engine(settings.database_url, future=True, echo=False)


def initialize_db() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        Base.metadata.create_all(engine)
        with engine.begin() as connection:
            connection.execute(text("ALTER TABLE root_cause_analyses ADD COLUMN IF NOT EXISTS title VARCHAR(200)"))
            connection.execute(text("ALTER TABLE root_cause_analyses ADD COLUMN IF NOT EXISTS subtitle VARCHAR(300)"))
            connection.execute(text("ALTER TABLE root_cause_analyses ADD COLUMN IF NOT EXISTS prediction TEXT"))
            connection.execute(text("ALTER TABLE root_cause_analyses ADD COLUMN IF NOT EXISTS workaround TEXT"))
            connection.execute(text("ALTER TABLE root_cause_analyses ADD COLUMN IF NOT EXISTS confidence DOUBLE PRECISION"))
            connection.execute(text("ALTER TABLE root_cause_analyses ADD COLUMN IF NOT EXISTS source VARCHAR(120)"))
            connection.execute(
                text(
                    """
                    UPDATE root_cause_analyses
                    SET title = COALESCE(title, 'AI Root-Cause Analysis'),
                        subtitle = COALESCE(subtitle, 'Network anomaly assessment'),
                        source = COALESCE(source, model)
                    """
                )
            )
    except OperationalError as exc:
        raise RuntimeError(
            "PostgreSQL is not running or not reachable. "
            "Start PostgreSQL on localhost:5432 or update POSTGRES_HOST/POSTGRES_PORT in the .env file."
        ) from exc


def insert_metrics(metrics: Iterable[dict]) -> None:
    try:
        with Session(engine) as session:
            for metric in metrics:
                session.add(
                    NetworkMetric(
                        timestamp=metric.get("timestamp", datetime.now(timezone.utc)),
                        region=metric["region"],
                        pop=metric["pop"],
                        latency_ms=float(metric["latency_ms"]),
                        packet_loss_pct=float(metric["packet_loss_pct"]),
                        status=metric["status"],
                        notes=metric.get("notes"),
                    )
                )
            session.commit()
    except OperationalError as exc:
        raise RuntimeError(
            "PostgreSQL connection failed while inserting telemetry. "
            "Start PostgreSQL and verify the database user and port settings."
        ) from exc


def fetch_latest_metrics(limit: int = 20):
    try:
        with Session(engine) as session:
            query = text(
                """
                SELECT region, pop, latency_ms, packet_loss_pct, status, timestamp
                FROM network_metrics
                ORDER BY timestamp DESC
                LIMIT :limit
                """
            )
            return session.execute(query, {"limit": limit}).fetchall()
    except OperationalError as exc:
        raise RuntimeError(
            "PostgreSQL connection failed while reading telemetry. "
            "Start PostgreSQL and verify the database settings first."
        ) from exc


def insert_root_cause_analysis(anomaly: dict, finding, model: str) -> None:
    try:
        evidence = finding.evidence if isinstance(finding.evidence, list) else [str(finding.evidence)]
        with Session(engine) as session:
            session.add(
                RootCauseAnalysis(
                    timestamp=datetime.now(timezone.utc),
                    region=anomaly.get("region", "Unknown"),
                    pop=anomaly.get("pop", "Unknown"),
                    severity=anomaly.get("severity", "unknown"),
                    title=getattr(finding, "title", "AI Root-Cause Analysis"),
                    subtitle=getattr(finding, "subtitle", "Network anomaly assessment"),
                    summary=finding.summary,
                    suspected_issue=finding.suspected_issue,
                    prediction=getattr(finding, "prediction", None),
                    workaround=getattr(finding, "workaround", None),
                    evidence="\n".join(evidence),
                    confidence=getattr(finding, "confidence", None),
                    source=getattr(finding, "source", model),
                    model=model,
                )
            )
            session.commit()
    except OperationalError as exc:
        raise RuntimeError(
            "PostgreSQL connection failed while saving root-cause analysis. "
            "Start PostgreSQL and verify the database settings first."
        ) from exc


def fetch_latest_root_cause_analyses(limit: int = 5):
    try:
        with Session(engine) as session:
            query = text(
                """
                SELECT timestamp, region, pop, severity, title, subtitle, summary,
                       suspected_issue, prediction, workaround, confidence, source, model
                FROM root_cause_analyses
                ORDER BY timestamp DESC
                LIMIT :limit
                """
            )
            return session.execute(query, {"limit": limit}).fetchall()
    except OperationalError as exc:
        raise RuntimeError(
            "PostgreSQL connection failed while reading root-cause analyses. "
            "Start PostgreSQL and verify the database settings first."
        ) from exc
