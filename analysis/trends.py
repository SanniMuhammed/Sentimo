"""Trend detection with rolling windows and z-score anomaly detection."""
import os, sys, math
from datetime import datetime, timedelta, timezone
from collections import defaultdict
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from storage.db import get_conn


def compute_entity_trends(hours=None):
    """Compute mention counts per entity in recent window, plus z-scores."""
    hours = hours or config.TREND_WINDOW_HOURS
    conn = get_conn()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = conn.execute("""
        SELECT e.entity, e.entity_type, COUNT(*) as cnt,
               AVG(s.compound) as avg_sent
        FROM entities e
        JOIN posts p ON e.post_id = p.id
        LEFT JOIN sentiment_scores s ON s.post_id = p.id
        WHERE p.created_at >= ?
        GROUP BY e.entity, e.entity_type
        ORDER BY cnt DESC
    """, (cutoff,)).fetchall()
    conn.close()

    if not rows:
        return []
    counts = [r["cnt"] for r in rows]
    mean = sum(counts) / len(counts)
    std = math.sqrt(sum((c - mean)**2 for c in counts) / max(len(counts), 1))

    results = []
    for r in rows:
        z = (r["cnt"] - mean) / std if std > 0 else 0
        results.append({
            "entity": r["entity"],
            "type": r["entity_type"],
            "mentions": r["cnt"],
            "avg_sentiment": round(r["avg_sent"] or 0, 4),
            "z_score": round(z, 2),
            "trending": z > config.ANOMALY_Z_THRESHOLD,
        })
    return results


def detect_anomalies():
    """Detect sentiment shifts and volume spikes."""
    conn = get_conn()
    now = datetime.now(timezone.utc)
    recent = (now - timedelta(hours=6)).isoformat()
    baseline_start = (now - timedelta(hours=48)).isoformat()

    entities_recent = conn.execute("""
        SELECT e.entity, COUNT(*) as cnt, AVG(s.compound) as avg_s
        FROM entities e
        JOIN posts p ON e.post_id = p.id
        LEFT JOIN sentiment_scores s ON s.post_id = p.id
        WHERE p.created_at >= ?
        GROUP BY e.entity
    """, (recent,)).fetchall()

    entities_baseline = conn.execute("""
        SELECT e.entity, COUNT(*) as cnt, AVG(s.compound) as avg_s
        FROM entities e
        JOIN posts p ON e.post_id = p.id
        LEFT JOIN sentiment_scores s ON s.post_id = p.id
        WHERE p.created_at >= ? AND p.created_at < ?
        GROUP BY e.entity
    """, (baseline_start, recent)).fetchall()
    conn.close()

    baseline = {r["entity"]: {"cnt": r["cnt"], "avg_s": r["avg_s"] or 0} for r in entities_baseline}
    anomalies = []
    for r in entities_recent:
        ent = r["entity"]
        if ent not in baseline:
            continue
        b = baseline[ent]
        # Volume spike
        if b["cnt"] > 0:
            ratio = r["cnt"] / (b["cnt"] / 7)  # normalize baseline to 6h window
            if ratio > 3:
                anomalies.append({
                    "entity": ent, "metric": "volume_spike",
                    "z_score": round(ratio, 2),
                    "description": f"{ent} mentions surged {int(ratio*100)}% vs baseline",
                })
        # Sentiment shift
        shift = abs((r["avg_s"] or 0) - b["avg_s"])
        if shift > 0.4:
            direction = "positive" if (r["avg_s"] or 0) > b["avg_s"] else "negative"
            anomalies.append({
                "entity": ent, "metric": "sentiment_shift",
                "z_score": round(shift * 5, 2),
                "description": f"{ent} sentiment shifted {direction} by {shift:.2f}",
            })
    return anomalies
