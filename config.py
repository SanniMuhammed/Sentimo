"""
Sentimo - Centralized Configuration
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "storage", "sentimo.db")
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

# Reddit (PRAW)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "sentimo/0.1")
SUBREDDITS = ["cryptocurrency", "bitcoin", "altcoin", "memecoins"]
REDDIT_POST_LIMIT = 50

# RSS News Feeds
RSS_FEEDS = {
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "CoinTelegraph": "https://cointelegraph.com/rss",
    "Decrypt": "https://decrypt.co/feed",
    "The Block": "https://www.theblock.co/rss.xml",
}

# CoinGecko
COINGECKO_BASE = "https://api.coingecko.com/api/v3"
COINGECKO_IDS = [
    "bitcoin", "ethereum", "solana", "cardano", "dogecoin",
    "ripple", "polkadot", "avalanche-2", "chainlink", "polygon",
]

# Analysis
ANOMALY_Z_THRESHOLD = 2.0
TREND_WINDOW_HOURS = 24
NARRATIVE_MIN_CLUSTER_SIZE = 3

# Flask API
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "5000"))
API_DEBUG = os.getenv("API_DEBUG", "0") == "1"

# Misc
USE_MOCK_DATA = os.getenv("USE_MOCK_DATA", "1") == "1"
