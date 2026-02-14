"""Database layer - SQLite models and helpers."""
import sqlite3
import json
import os
from datetime import datetime, timedelta, timezone
import random

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import config


def get_conn():
    os.makedirs(os.path.dirname(config.DB_PATH), exist_ok=True)
    conn = sqlite3.connect(config.DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS posts (
        id TEXT PRIMARY KEY,
        source TEXT NOT NULL,
        subreddit TEXT,
        title TEXT,
        body TEXT,
        author TEXT,
        url TEXT,
        score INTEGER DEFAULT 0,
        num_comments INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        collected_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS sentiment_scores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id TEXT NOT NULL,
        compound REAL,
        positive REAL,
        negative REAL,
        neutral REAL,
        label TEXT,
        scored_at TEXT NOT NULL,
        FOREIGN KEY (post_id) REFERENCES posts(id)
    );
    CREATE TABLE IF NOT EXISTS entities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id TEXT NOT NULL,
        entity TEXT NOT NULL,
        entity_type TEXT,
        FOREIGN KEY (post_id) REFERENCES posts(id)
    );
    CREATE TABLE IF NOT EXISTS narratives (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        label TEXT NOT NULL,
        keywords TEXT,
        post_ids TEXT,
        volume INTEGER DEFAULT 0,
        avg_sentiment REAL DEFAULT 0,
        detected_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS anomalies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity TEXT,
        metric TEXT,
        z_score REAL,
        description TEXT,
        detected_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS market_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        coin_id TEXT NOT NULL,
        symbol TEXT,
        name TEXT,
        price_usd REAL,
        market_cap REAL,
        volume_24h REAL,
        price_change_24h REAL,
        collected_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_at);
    CREATE INDEX IF NOT EXISTS idx_sentiment_post ON sentiment_scores(post_id);
    CREATE INDEX IF NOT EXISTS idx_entities_entity ON entities(entity);
    CREATE INDEX IF NOT EXISTS idx_market_coin ON market_data(coin_id, collected_at);
    """)
    conn.commit()
    conn.close()


def insert_post(conn, p):
    try:
        conn.execute(
            "INSERT OR IGNORE INTO posts (id,source,subreddit,title,body,author,url,score,num_comments,created_at,collected_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (p["id"],p["source"],p.get("subreddit"),p.get("title",""),p.get("body",""),p.get("author",""),p.get("url",""),p.get("score",0),p.get("num_comments",0),p["created_at"],p["collected_at"]))
    except sqlite3.IntegrityError:
        pass


def insert_sentiment(conn, post_id, s):
    conn.execute(
        "INSERT INTO sentiment_scores (post_id,compound,positive,negative,neutral,label,scored_at) VALUES (?,?,?,?,?,?,?)",
        (post_id, s["compound"], s["pos"], s["neg"], s["neu"], s["label"], datetime.now(timezone.utc).isoformat()))


def insert_entity(conn, post_id, entity, entity_type):
    conn.execute("INSERT INTO entities (post_id,entity,entity_type) VALUES (?,?,?)", (post_id, entity, entity_type))


def insert_narrative(conn, label, keywords, post_ids, volume, avg_sentiment):
    conn.execute(
        "INSERT INTO narratives (label,keywords,post_ids,volume,avg_sentiment,detected_at) VALUES (?,?,?,?,?,?)",
        (label, json.dumps(keywords), json.dumps(post_ids), volume, avg_sentiment, datetime.now(timezone.utc).isoformat()))


def insert_anomaly(conn, entity, metric, z_score, description):
    conn.execute(
        "INSERT INTO anomalies (entity,metric,z_score,description,detected_at) VALUES (?,?,?,?,?)",
        (entity, metric, z_score, description, datetime.now(timezone.utc).isoformat()))


def insert_market(conn, d):
    conn.execute(
        "INSERT INTO market_data (coin_id,symbol,name,price_usd,market_cap,volume_24h,price_change_24h,collected_at) VALUES (?,?,?,?,?,?,?,?)",
        (d["coin_id"],d["symbol"],d["name"],d["price_usd"],d["market_cap"],d["volume_24h"],d["price_change_24h"],d["collected_at"]))


def seed_mock_data():
    """Generate realistic mock data so dashboard works without API keys."""
    conn = get_conn()
    init_db()
    if conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0] > 0:
        conn.close()
        return
    now = datetime.now(timezone.utc)
    random.seed(42)

    coins = ["Bitcoin","Ethereum","Solana","Dogecoin","Cardano","XRP","Polkadot","Avalanche","Chainlink","Polygon"]
    symbols = ["BTC","ETH","SOL","DOGE","ADA","XRP","DOT","AVAX","LINK","MATIC"]
    coin_ids = ["bitcoin","ethereum","solana","dogecoin","cardano","ripple","polkadot","avalanche-2","chainlink","polygon"]
    prices = [67234.5,3456.78,178.23,0.165,0.62,0.58,7.82,38.45,18.92,0.89]
    subs = ["cryptocurrency","bitcoin","altcoin","memecoins"]
    news_src = ["CoinDesk","CoinTelegraph","Decrypt","The Block"]
    people = ["Vitalik Buterin","CZ","Brian Armstrong","Gary Gensler","Michael Saylor","Elon Musk","Larry Fink"]
    protocols = ["Uniswap","Aave","Lido","Compound","MakerDAO","Raydium","Jupiter","Arbitrum","Optimism","Base"]

    bull = ["{c} breaks resistance - new ATH incoming?","Why {c} could 10x this cycle","{c} institutional adoption accelerating","Just loaded up on {c}. Here's my thesis.","{c} fundamentals never been stronger","Massive {c} whale accumulation spotted","{c} network hits record TVL"]
    bear = ["{c} looking weak - correction ahead?","Sold all my {c}. Here's why.","SEC targeting {c} - what this means","{c} congestion getting worse","Why I'm bearish on {c} short term"]
    neut = ["{c} technical analysis this week","Understanding {c}'s latest upgrade","{c} daily discussion thread","What's happening with {c} development?"]

    post_list = []
    for i in range(300):
        hrs = random.uniform(0, 72)
        ts = now - timedelta(hours=hrs)
        ci = random.randint(0, len(coins)-1)
        src = random.choice(["reddit","news"])
        roll = random.random()
        if roll < 0.45:
            title = random.choice(bull).format(c=coins[ci])
            compound = random.uniform(0.15, 0.9)
        elif roll < 0.75:
            title = random.choice(neut).format(c=coins[ci])
            compound = random.uniform(-0.15, 0.15)
        else:
            title = random.choice(bear).format(c=coins[ci])
            compound = random.uniform(-0.9, -0.15)

        pid = f"mock_{i:04d}"
        sub = random.choice(subs) if src == "reddit" else None
        author = f"user_{random.randint(1000,9999)}" if src == "reddit" else random.choice(news_src)
        insert_post(conn, {"id":pid,"source":src,"subreddit":sub,"title":title,"body":f"Discussion about {coins[ci]}.","author":author,"url":f"https://example.com/{pid}","score":random.randint(1,5000),"num_comments":random.randint(0,500),"created_at":ts.isoformat(),"collected_at":ts.isoformat()})

        pos = max(0, (compound+1)/2*0.6 + random.uniform(-0.05,0.05))
        neg = max(0, 0.6-pos+random.uniform(-0.05,0.05))
        neu = max(0, 1.0-pos-neg)
        label = "bullish" if compound>0.15 else ("bearish" if compound<-0.15 else "neutral")
        conn.execute("INSERT INTO sentiment_scores (post_id,compound,positive,negative,neutral,label,scored_at) VALUES (?,?,?,?,?,?,?)",
            (pid, round(compound,4), round(pos,4), round(neg,4), round(neu,4), label, ts.isoformat()))
        insert_entity(conn, pid, coins[ci], "coin")
        insert_entity(conn, pid, symbols[ci], "coin")
        if random.random() < 0.3:
            insert_entity(conn, pid, random.choice(people), "person")
        if random.random() < 0.25:
            insert_entity(conn, pid, random.choice(protocols), "protocol")
        post_list.append(pid)

    narr = [("Bitcoin ETF Momentum",["bitcoin","etf","blackrock","institutional"]),("Ethereum Layer 2 Scaling",["ethereum","layer2","rollup","optimism"]),("Solana DeFi Summer",["solana","defi","raydium","jupiter"]),("Meme Coin Mania",["doge","shib","pepe","meme","moon"]),("Regulation Fears",["sec","regulation","lawsuit","compliance"]),("DePIN Revolution",["depin","helium","render","infrastructure"]),("AI + Crypto Convergence",["ai","gpu","compute","render"]),("Stablecoin Wars",["usdt","usdc","stablecoin","tether"])]
    for lbl, kw in narr:
        related = random.sample(post_list, k=random.randint(5,25))
        insert_narrative(conn, lbl, kw, related, len(related), round(random.uniform(-0.3,0.6),3))

    for ent, met, z, desc in [("Bitcoin","volume_spike",3.2,"BTC mentions surged 340% in last 4 hours"),("Solana","sentiment_shift",2.8,"SOL sentiment flipped bearish to strongly bullish"),("Dogecoin","volume_spike",2.5,"DOGE discussion spiked after Elon Musk tweet"),("Ethereum","sentiment_shift",-2.1,"ETH sentiment dropped on gas fee concerns"),("XRP","volume_spike",3.9,"XRP mentions exploded after SEC ruling news")]:
        conn.execute("INSERT INTO anomalies (entity,metric,z_score,description,detected_at) VALUES (?,?,?,?,?)",
            (ent, met, z, desc, (now-timedelta(hours=random.uniform(0,12))).isoformat()))

    for snap in range(12):
        st = now - timedelta(hours=snap*6)
        for j, cid in enumerate(coin_ids):
            drift = 1 + random.uniform(-0.05,0.05)
            insert_market(conn, {"coin_id":cid,"symbol":symbols[j].lower(),"name":coins[j],"price_usd":round(prices[j]*drift,2),"market_cap":round(prices[j]*drift*random.uniform(1e7,1e10)),"volume_24h":round(random.uniform(1e8,5e10)),"price_change_24h":round(random.uniform(-8,12),2),"collected_at":st.isoformat()})

    conn.commit()
    conn.close()
