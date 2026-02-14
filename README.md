<div align="center">

# 🛡️ CRYPTO SENTINEL

### Real-Time Crypto Market Sentiment Intelligence Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-lightgrey.svg)](https://flask.palletsprojects.com)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF.svg)](https://github.com/features/actions)

*Track narratives. Detect anomalies. Stay ahead of the market.*

</div>

---

## 🔮 What Is This?

Sentimo is an open-source intelligence platform that monitors the crypto conversation across Reddit, news outlets, and market data — then distills it into actionable insights through sentiment analysis, entity tracking, narrative clustering, and anomaly detection.

**Zero cost to run. No API keys required for demo mode.**

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🎯 **Fear & Greed Index** | Real-time bull/bear meter computed from aggregate sentiment |
| 📊 **Sentiment Timeline** | Hourly sentiment tracking with interactive charts |
| 🏆 **Entity Leaderboard** | Which coins, people, and protocols are being discussed most |
| 🫧 **Narrative Radar** | Visual bubble map of trending themes sized by volume |
| ⚡ **Anomaly Alerts** | Automatic detection of unusual sentiment shifts and volume spikes |
| 📈 **Market Correlation** | CoinGecko price data alongside sentiment signals |
| 🔍 **Smart NER** | Crypto-aware entity extraction (coins, people, protocols, exchanges) |
| 🧠 **VADER + Crypto Lexicon** | Sentiment analysis tuned for crypto language (HODL, FUD, moon, rug...) |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CRYPTO SENTINEL                       │
├──────────────┬──────────────┬──────────────┬────────────┤
│  COLLECTORS  │   ANALYSIS   │   STORAGE    │    API     │
├──────────────┼──────────────┼──────────────┼────────────┤
│ Reddit       │ Sentiment    │              │            │
│ (PRAW)       │ (VADER +     │   SQLite     │  Flask     │
│              │  crypto      │   Database   │  REST API  │
│ News RSS     │  lexicon)    │              │            │
│ (feedparser) │              │  ┌────────┐  │ /sentiment │
│              │ Entity NER   │  │ posts  │  │ /entities  │
│ CoinGecko    │ (coins,      │  │ scores │  │ /trends    │
│ (free API)   │  people,     │  │ entities│  │ /narratives│
│              │  protocols)  │  │ market │  │ /anomalies │
│              │              │  │ narr.  │  │ /market    │
│              │ Trends &     │  │ anomaly│  │ /sources   │
│              │ Anomalies    │  └────────┘  │            │
│              │ (z-scores)   │              │            │
│              │              │              │            │
│              │ Narratives   │              │            │
│              │ (clustering) │              │            │
├──────────────┴──────────────┴──────────────┴────────────┤
│                    FRONTEND                              │
│  ┌─────────┐ ┌──────────┐ ┌────────────┐ ┌───────────┐ │
│  │Fear &   │ │Sentiment │ │Entity      │ │Narrative  │ │
│  │Greed    │ │Timeline  │ │Leaderboard │ │Radar      │ │
│  │Gauge    │ │Chart     │ │            │ │(Bubbles)  │ │
│  └─────────┘ └──────────┘ └────────────┘ └───────────┘ │
│  ┌─────────────────┐ ┌──────────────────────────────┐   │
│  │Anomaly Alerts   │ │Market Overview               │   │
│  └─────────────────┘ └──────────────────────────────┘   │
│           HTML + Tailwind CSS + Chart.js                 │
└─────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/sentimo.git
cd sentimo
pip install -r requirements.txt
```

### 2. Run (Demo Mode — No API Keys Needed)

```bash
python run.py
```

Open `http://localhost:5000` — the dashboard loads instantly with realistic mock data.

### 3. Run with Live Data

```bash
# Set up Reddit API credentials (free at https://www.reddit.com/prefs/apps)
export REDDIT_CLIENT_ID="your_client_id"
export REDDIT_CLIENT_SECRET="your_client_secret"
export USE_MOCK_DATA="0"

# Collect live data
python run.py collect

# Start the dashboard
python run.py
```

### 4. Static Dashboard (GitHub Pages)

The frontend works as a standalone static site with embedded mock data:

```bash
# Just open the HTML file directly
open frontend/index.html
```

Or deploy to GitHub Pages — no server needed.

## 📁 Project Structure

```
sentimo/
├── run.py                    # Main entry point
├── config.py                 # Centralized configuration
├── requirements.txt          # Python dependencies
├── collectors/
│   ├── reddit_collector.py   # Reddit scraper (PRAW)
│   ├── news_collector.py     # RSS feed collector
│   └── market_collector.py   # CoinGecko market data
├── analysis/
│   ├── sentiment.py          # VADER + crypto lexicon
│   ├── entities.py           # Crypto NER engine
│   ├── trends.py             # Trend detection & anomalies
│   └── narratives.py         # Narrative clustering
├── storage/
│   └── db.py                 # SQLite database layer
├── api/
│   └── routes.py             # Flask REST API
├── frontend/
│   └── index.html            # Dashboard (Tailwind + Chart.js)
├── .github/workflows/
│   └── collect.yml           # Auto-collect every 6 hours
├── LICENSE
└── README.md
```

## 🧠 Crypto Sentiment Lexicon

The VADER sentiment analyzer is augmented with crypto-native terms:

| Bullish 🟢 | Bearish 🔴 | Neutral/Context |
|------------|------------|-----------------|
| HODL (+2.0) | FUD (-2.0) | whale (+0.5) |
| moon (+2.5) | rug (-3.5) | defi (+0.5) |
| bullish (+2.5) | scam (-3.0) | nft (+0.3) |
| diamond hands (+2.5) | rekt (-3.0) | web3 (+0.5) |
| WAGMI (+2.5) | crash (-3.0) | staking (+1.0) |
| pump (+1.5) | dump (-2.0) | airdrop (+1.5) |
| ATH (+2.5) | bearish (-2.5) | dip (-0.5) |

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/sentiment?hours=24` | GET | Overall sentiment stats + timeline |
| `/api/entities?hours=24&type=coin` | GET | Entity mention leaderboard |
| `/api/trends?hours=24` | GET | Trending entities with z-scores |
| `/api/narratives?hours=72` | GET | Narrative clusters |
| `/api/anomalies` | GET | Recent anomaly alerts |
| `/api/market` | GET | Latest market data |
| `/api/sources?hours=24` | GET | Top data sources |

## ⚙️ Configuration

All settings in `config.py`:

| Setting | Default | Description |
|---------|---------|-------------|
| `USE_MOCK_DATA` | `True` | Use mock data (set `0` for live) |
| `REDDIT_POST_LIMIT` | `50` | Posts per subreddit per collection |
| `ANOMALY_Z_THRESHOLD` | `2.0` | Z-score threshold for anomaly detection |
| `TREND_WINDOW_HOURS` | `24` | Rolling window for trend analysis |
| `API_PORT` | `5000` | Flask server port |

## 🤖 Automated Collection (GitHub Actions)

The included workflow runs every 6 hours for free:

1. Add Reddit API secrets to your repo (`Settings → Secrets`):
   - `REDDIT_CLIENT_ID`
   - `REDDIT_CLIENT_SECRET`
2. The workflow collects data and commits results automatically

## 📊 Data Sources

| Source | Type | Cost | Notes |
|--------|------|------|-------|
| Reddit (PRAW) | Social | Free | r/cryptocurrency, r/bitcoin, r/altcoin, r/memecoins |
| CoinDesk RSS | News | Free | Major crypto news |
| CoinTelegraph RSS | News | Free | Industry coverage |
| Decrypt RSS | News | Free | Web3 focused |
| The Block RSS | News | Free | Institutional focus |
| CoinGecko API | Market | Free | Price, volume, market cap |

## 🛠️ Tech Stack

- **Backend:** Python 3.11, Flask, SQLite
- **NLP:** VADER Sentiment Analysis + custom crypto lexicon
- **Frontend:** Vanilla HTML/JS, Tailwind CSS, Chart.js
- **CI/CD:** GitHub Actions
- **Cost:** $0

## 📄 License

MIT — use it, fork it, build on it.

---

<div align="center">

**Built with ☕ and conviction**

*Not financial advice. DYOR.*

</div>
