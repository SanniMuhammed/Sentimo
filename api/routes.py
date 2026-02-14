"""Flask REST API routes."""
import os, sys, json
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from storage.db import get_conn, init_db, seed_mock_data
from analysis.sentiment import fear_greed_index
from analysis.trends import compute_entity_trends, detect_anomalies
from analysis.narratives import cluster_narratives, extract_trending_keywords

app = Flask(__name__, static_folder=config.FRONTEND_DIR)
CORS(app)


def _ensure_data():
    init_db()
    if config.USE_MOCK_DATA:
        seed_mock_data()


@app.before_request
def before():
    _ensure_data()


# ── API Endpoints ──────────────────────────────────────────────────────

@app.route("/api/sentiment")
def api_sentiment():
    """Overall sentiment stats."""
    hours = int(request.args.get("hours", 24))
    conn = get_conn()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = conn.execute("""
        SELECT s.compound, s.label, p.created_at
        FROM sentiment_scores s
        JOIN posts p ON s.post_id = p.id
        WHERE p.created_at >= ?
        ORDER BY p.created_at
    """, (cutoff,)).fetchall()
    conn.close()

    compounds = [r["compound"] for r in rows]
    fg = fear_greed_index(compounds)
    labels = {"bullish": 0, "bearish": 0, "neutral": 0}
    for r in rows:
        labels[r["label"]] = labels.get(r["label"], 0) + 1
    total = len(rows) or 1

    # Time series (hourly buckets)
    buckets = {}
    for r in rows:
        ts = r["created_at"][:13]  # YYYY-MM-DDTHH
        if ts not in buckets:
            buckets[ts] = []
        buckets[ts].append(r["compound"])
    timeline = [{"time": k, "avg_sentiment": round(sum(v)/len(v), 4), "count": len(v)}
                for k, v in sorted(buckets.items())]

    return jsonify({
        "fear_greed": fg,
        "distribution": labels,
        "total_posts": len(rows),
        "avg_compound": round(sum(compounds)/total, 4) if compounds else 0,
        "timeline": timeline,
    })


@app.route("/api/trends")
def api_trends():
    hours = int(request.args.get("hours", 24))
    trends = compute_entity_trends(hours)
    keywords = extract_trending_keywords(hours)
    return jsonify({"trends": trends[:30], "keywords": keywords})


@app.route("/api/entities")
def api_entities():
    hours = int(request.args.get("hours", 24))
    entity_type = request.args.get("type")
    conn = get_conn()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    query = """
        SELECT e.entity, e.entity_type, COUNT(*) as mentions, AVG(s.compound) as avg_sentiment
        FROM entities e
        JOIN posts p ON e.post_id = p.id
        LEFT JOIN sentiment_scores s ON s.post_id = p.id
        WHERE p.created_at >= ?
    """
    params = [cutoff]
    if entity_type:
        query += " AND e.entity_type = ?"
        params.append(entity_type)
    query += " GROUP BY e.entity, e.entity_type ORDER BY mentions DESC LIMIT 50"
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([{
        "entity": r["entity"], "type": r["entity_type"],
        "mentions": r["mentions"], "avg_sentiment": round(r["avg_sentiment"] or 0, 4)
    } for r in rows])


@app.route("/api/narratives")
def api_narratives():
    hours = int(request.args.get("hours", 72))
    narratives = cluster_narratives(hours)
    return jsonify(narratives)


@app.route("/api/anomalies")
def api_anomalies():
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM anomalies ORDER BY detected_at DESC LIMIT 20
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/market")
def api_market():
    conn = get_conn()
    rows = conn.execute("""
        SELECT * FROM market_data
        WHERE collected_at = (SELECT MAX(collected_at) FROM market_data)
        ORDER BY market_cap DESC
    """).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/sources")
def api_sources():
    hours = int(request.args.get("hours", 24))
    conn = get_conn()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    rows = conn.execute("""
        SELECT source, COALESCE(subreddit, author) as name, COUNT(*) as count
        FROM posts WHERE created_at >= ?
        GROUP BY source, name ORDER BY count DESC LIMIT 20
    """, (cutoff,)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


# ── Frontend serving ───────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(config.FRONTEND_DIR, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(config.FRONTEND_DIR, path)


if __name__ == "__main__":
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.API_DEBUG)
