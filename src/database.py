from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from src.config import settings


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


engine = create_engine(settings.database_url, future=True, echo=False)


def initialize_db() -> None:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        Base.metadata.create_all(engine)
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
