"""CoinGecko market data collector."""
import os, sys, logging, time
from datetime import datetime, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from storage.db import get_conn, insert_market

logger = logging.getLogger(__name__)


def collect():
    """Fetch market data from CoinGecko free API."""
    try:
        import requests
    except ImportError:
        logger.error("requests not installed")
        return 0

    conn = get_conn()
    count = 0
    ids_str = ",".join(config.COINGECKO_IDS)
    url = f"{config.COINGECKO_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ids_str,
        "order": "market_cap_desc",
        "per_page": len(config.COINGECKO_IDS),
        "page": 1,
        "sparkline": "false",
        "price_change_percentage": "24h",
    }

    try:
        resp = requests.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        now_iso = datetime.now(timezone.utc).isoformat()
        for coin in data:
            insert_market(conn, {
                "coin_id": coin["id"],
                "symbol": coin["symbol"],
                "name": coin["name"],
                "price_usd": coin.get("current_price", 0),
                "market_cap": coin.get("market_cap", 0),
                "volume_24h": coin.get("total_volume", 0),
                "price_change_24h": coin.get("price_change_percentage_24h", 0),
                "collected_at": now_iso,
            })
            count += 1
    except Exception as e:
        logger.error(f"CoinGecko error: {e}")

    conn.commit()
    conn.close()
    logger.info(f"Collected market data for {count} coins")
    return count


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    collect()
