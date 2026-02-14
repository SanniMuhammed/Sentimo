#!/usr/bin/env python3
"""
Sentimo — Main Entry Point

Usage:
    python run.py              # Start the web dashboard
    python run.py collect      # Run data collection
    python run.py seed         # Seed mock data only
"""
import sys
import logging
import config
from storage.db import init_db, seed_mock_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("sentimo")


def run_collect():
    """Run all data collectors."""
    logger.info("Starting data collection...")
    init_db()
    from collectors.reddit_collector import collect as collect_reddit
    from collectors.news_collector import collect as collect_news
    from collectors.market_collector import collect as collect_market
    from analysis.trends import detect_anomalies
    from analysis.narratives import cluster_narratives
    from storage.db import get_conn, insert_anomaly, insert_narrative

    r = collect_reddit()
    n = collect_news()
    m = collect_market()
    logger.info(f"Collected: {r} reddit, {n} news, {m} market")

    # Run analysis
    anomalies = detect_anomalies()
    conn = get_conn()
    for a in anomalies:
        insert_anomaly(conn, a["entity"], a["metric"], a["z_score"], a["description"])
    conn.commit()

    narratives = cluster_narratives()
    for nr in narratives:
        insert_narrative(conn, nr["label"], nr["keywords"], nr["post_ids"], nr["volume"], nr["avg_sentiment"])
    conn.commit()
    conn.close()
    logger.info(f"Detected {len(anomalies)} anomalies, {len(narratives)} narratives")


def run_server():
    """Start Flask web server."""
    init_db()
    if config.USE_MOCK_DATA:
        seed_mock_data()
        logger.info("Mock data seeded")
    from api.routes import app
    logger.info(f"Starting server on {config.API_HOST}:{config.API_PORT}")
    app.run(host=config.API_HOST, port=config.API_PORT, debug=config.API_DEBUG)


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "serve"
    if cmd == "collect":
        run_collect()
    elif cmd == "seed":
        init_db()
        seed_mock_data()
        logger.info("Mock data seeded successfully")
    elif cmd in ("serve", "server", "run"):
        run_server()
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
