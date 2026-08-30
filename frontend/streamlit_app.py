from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.src.database import engine


def _latest_openai_analysis() -> dict | None:
    query = text(
        """
        SELECT timestamp, region, pop, severity, title, subtitle, summary,
               suspected_issue, prediction, workaround, confidence, source, model
        FROM root_cause_analyses
        WHERE source LIKE 'openai:%'
        ORDER BY timestamp DESC
        LIMIT 1
        """
    )
    with engine.connect() as conn:
        row = conn.execute(query).mappings().first()
        return dict(row) if row else None


def _latest_region_metrics() -> list[dict]:
    query = text(
        """
        WITH ranked AS (
            SELECT timestamp, region, pop, latency_ms, packet_loss_pct, status,
                   ROW_NUMBER() OVER (PARTITION BY region ORDER BY timestamp DESC) AS rn
            FROM network_metrics
        )
        SELECT timestamp, region, pop, latency_ms, packet_loss_pct, status
        FROM ranked
        WHERE rn = 1
        ORDER BY region ASC
        """
    )
    with engine.connect() as conn:
        rows = conn.execute(query).mappings().all()
    return [dict(row) for row in rows]


def _render_text_panel(title: str, body: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div style=\"border:1px solid #d9dee7;border-radius:14px;padding:18px 20px;margin-bottom:12px;background:#fbfdff;\">
            <div style=\"font-size:28px;font-weight:700;line-height:1.15;margin-bottom:4px;\">{title}</div>
            <div style=\"font-size:18px;color:#4b5563;line-height:1.35;margin-bottom:14px;\">{subtitle}</div>
            <div style=\"font-size:22px;line-height:1.6;color:#0f172a;white-space:pre-wrap;\">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="NetPulse AI Analysis", layout="wide")
    st.title("NetPulse AI Narrative")
    st.caption("Dedicated OpenAI analysis viewer outside Grafana")

    latest = _latest_openai_analysis()
    if latest is None:
        st.warning("No OpenAI analysis found yet. Run backend/scripts/run_pipeline.py with a valid OPENAI_API_KEY.")
        return

    top1, top2, top3 = st.columns(3)
    top1.metric("Region", f"{latest['region']} ({latest['pop']})")
    top2.metric("Severity", str(latest["severity"]))
    conf = latest.get("confidence")
    top3.metric("Confidence", f"{float(conf):.2f}" if conf is not None else "n/a")

    st.markdown("### Latest OpenAI Summary")
    _render_text_panel(
        title=str(latest.get("title") or "AI Root-Cause Analysis"),
        subtitle=str(latest.get("subtitle") or ""),
        body=str(latest.get("summary") or "No summary provided."),
    )

    st.markdown("### Predicted Impact")
    _render_text_panel(
        title="Prediction",
        body=str(latest.get("prediction") or "No prediction provided."),
    )

    st.markdown("### Suggested Workaround")
    _render_text_panel(
        title="Workaround",
        body=str(latest.get("workaround") or "No workaround provided."),
    )

    st.markdown("### Supporting Details")
    st.write(f"Suspected issue: {latest.get('suspected_issue')}")
    st.write(f"Source: {latest.get('source')} | Model: {latest.get('model')}")

    region_rows = _latest_region_metrics()
    if not region_rows:
        st.info("No metrics available for charting yet.")
        return

    st.markdown("### Latest Metrics by Region")
    cols = st.columns(len(region_rows))
    for col, row in zip(cols, region_rows):
        with col:
            st.markdown(f"#### {row['region']}")
            st.metric("Latency (ms)", f"{float(row['latency_ms']):.2f}")
            st.metric("Packet Loss (%)", f"{float(row['packet_loss_pct']):.2f}")
            st.caption(f"POP: {row['pop']} | Status: {row['status']}")


if __name__ == "__main__":
    main()
