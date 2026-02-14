"""Narrative clustering - group related discussions into themes."""
import os, sys, re
from collections import defaultdict, Counter
from datetime import datetime, timedelta, timezone
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config
from storage.db import get_conn

# Pre-defined narrative patterns (keyword-based clustering for MVP)
NARRATIVE_TEMPLATES = {
    "Bitcoin ETF & Institutional": {"bitcoin", "btc", "etf", "blackrock", "institutional", "grayscale", "fidelity", "spot"},
    "Ethereum Upgrades & L2": {"ethereum", "eth", "layer2", "l2", "rollup", "optimism", "arbitrum", "dencun", "eip", "blob"},
    "Solana Ecosystem": {"solana", "sol", "raydium", "jupiter", "marinade", "jito", "blinks"},
    "Meme Coin Season": {"doge", "shib", "pepe", "meme", "memecoin", "bonk", "wif", "moon"},
    "DeFi Renaissance": {"defi", "tvl", "yield", "lending", "dex", "amm", "liquidity"},
    "Regulation & Legal": {"sec", "regulation", "lawsuit", "gensler", "compliance", "ban", "legal"},
    "AI & Crypto": {"ai", "artificial intelligence", "gpu", "compute", "render", "fetch", "singularity"},
    "DePIN & Real World": {"depin", "rwa", "real world", "tokenization", "helium", "infrastructure"},
    "NFT & Gaming": {"nft", "gaming", "metaverse", "play to earn", "opensea", "blur"},
    "Stablecoins": {"usdt", "usdc", "stablecoin", "tether", "circle", "dai", "depeg"},
}

STOP_WORDS = {"the","a","an","is","are","was","were","be","been","being","have","has","had",
    "do","does","did","will","would","could","should","may","might","shall","can",
    "i","you","he","she","it","we","they","me","him","her","us","them","my","your",
    "his","its","our","their","this","that","these","those","what","which","who",
    "in","on","at","to","for","with","from","by","about","into","through","of","and",
    "or","but","not","no","so","if","then","than","just","very","really","much",
    "more","most","also","too","here","there","now","how","why","when","where","all",
    "any","some","get","got","like","know","think","want","go","going","up","out"}


def cluster_narratives(hours=None):
    """Assign posts to narrative clusters based on keyword matching."""
    hours = hours or config.TREND_WINDOW_HOURS
    conn = get_conn()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    posts = conn.execute("""
        SELECT p.id, p.title, p.body, s.compound
        FROM posts p
        LEFT JOIN sentiment_scores s ON s.post_id = p.id
        WHERE p.created_at >= ?
    """, (cutoff,)).fetchall()
    conn.close()

    clusters = defaultdict(lambda: {"post_ids": [], "sentiments": [], "keyword_hits": Counter()})

    for p in posts:
        text = f"{p['title']} {p['body']}".lower()
        words = set(re.findall(r'[a-z0-9]+', text))
        for narr_name, keywords in NARRATIVE_TEMPLATES.items():
            hits = words & keywords
            if len(hits) >= 1:
                clusters[narr_name]["post_ids"].append(p["id"])
                if p["compound"] is not None:
                    clusters[narr_name]["sentiments"].append(p["compound"])
                for h in hits:
                    clusters[narr_name]["keyword_hits"][h] += 1

    results = []
    for name, data in clusters.items():
        vol = len(data["post_ids"])
        if vol < config.NARRATIVE_MIN_CLUSTER_SIZE:
            continue
        avg_s = sum(data["sentiments"]) / len(data["sentiments"]) if data["sentiments"] else 0
        top_kw = [k for k, _ in data["keyword_hits"].most_common(5)]
        results.append({
            "label": name,
            "keywords": top_kw,
            "volume": vol,
            "avg_sentiment": round(avg_s, 4),
            "post_ids": data["post_ids"][:20],
        })

    results.sort(key=lambda x: x["volume"], reverse=True)
    return results


def extract_trending_keywords(hours=None, top_n=20):
    """Extract most frequent meaningful words from recent posts."""
    hours = hours or config.TREND_WINDOW_HOURS
    conn = get_conn()
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    posts = conn.execute("SELECT title, body FROM posts WHERE created_at >= ?", (cutoff,)).fetchall()
    conn.close()

    counter = Counter()
    for p in posts:
        words = re.findall(r'[a-z][a-z0-9]{2,}', f"{p['title']} {p['body']}".lower())
        for w in words:
            if w not in STOP_WORDS:
                counter[w] += 1
    return counter.most_common(top_n)
