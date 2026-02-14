"""VADER sentiment analysis with expanded crypto lexicon + emotion detection."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Expanded crypto-specific lexicon (100+ terms)
CRYPTO_LEXICON = {
    # Strong Bullish
    "hodl": 2.0, "hodling": 2.0, "hodled": 1.5, "hodler": 1.5,
    "moon": 2.5, "mooning": 3.0, "moonshot": 2.5, "moonboy": 1.0,
    "bullish": 2.5, "bull": 1.5, "bulls": 1.5, "bullrun": 3.0,
    "pump": 1.5, "pumping": 2.0, "pumped": 1.5, "pamp": 1.5,
    "lambo": 2.0, "wagmi": 2.5, "gm": 1.0, "gmi": 2.0,
    "diamond hands": 2.5, "diamond": 1.0, "diamondhands": 2.5,
    "accumulate": 1.5, "accumulating": 1.5, "accumulation": 1.5,
    "breakout": 2.0, "ath": 2.5, "rally": 2.0, "rallying": 2.0,
    "undervalued": 1.5, "gem": 2.0, "alpha": 1.5, "gigabrain": 2.0,
    "adoption": 1.5, "institutional": 1.0, "mainstream": 1.0,
    "bullmarket": 3.0, "supercycle": 2.5, "parabolic": 2.5,
    "outperform": 1.5, "outperforming": 2.0, "skyrocket": 3.0,
    "soaring": 2.5, "surge": 2.0, "surging": 2.5, "explode": 2.0,
    "exploding": 2.5, "takeoff": 2.0, "liftoff": 2.5,
    "bullcase": 2.0, "upside": 1.5, "uptrend": 1.5,
    "strong buy": 2.5, "buy the dip": 1.5, "btfd": 1.5,
    "massive": 1.0, "huge": 1.0, "incredible": 2.0,
    "based": 1.5, "chad": 1.5, "gigachad": 2.0,
    "flippening": 1.5, "altseason": 2.0, "altszn": 2.0,
    # Moderate Positive
    "staking": 1.0, "yield": 0.5, "airdrop": 1.5, "airdrops": 1.5,
    "whale": 0.5, "whales": 0.5, "defi": 0.5, "nft": 0.3,
    "web3": 0.5, "decentralized": 0.5, "dao": 0.3,
    "tvl": 0.5, "liquidity": 0.3, "farming": 0.5,
    "governance": 0.3, "upgrade": 1.0, "mainnet": 1.0,
    "partnership": 1.0, "integration": 0.8, "listing": 1.0,
    "halving": 1.0, "halvening": 1.0, "deflationary": 0.8,
    "layer2": 0.5, "l2": 0.5, "rollup": 0.5, "zk": 0.5,
    "interoperability": 0.5, "scalability": 0.5,
    # Strong Bearish
    "bearish": -2.5, "bear": -1.5, "bears": -1.5, "bearmarket": -3.0,
    "dump": -2.0, "dumping": -2.5, "dumped": -2.0, "damp": -1.5,
    "rug": -3.5, "rugpull": -3.5, "rug pull": -3.5, "rugged": -3.5,
    "scam": -3.0, "ponzi": -3.0, "fraud": -3.0, "fraudulent": -3.0,
    "fud": -2.0, "fear": -1.5, "panic": -2.5, "panicking": -2.5,
    "crash": -3.0, "crashing": -3.0, "crashed": -2.5, "plunge": -3.0,
    "rekt": -3.0, "rekted": -3.0, "wrecked": -2.5, "destroyed": -2.5,
    "paper hands": -2.0, "paperhands": -2.0, "ngmi": -2.5,
    "sell": -1.0, "selling": -1.5, "sold": -1.0, "selloff": -2.0,
    "overvalued": -1.5, "bubble": -2.0, "overleveraged": -2.0,
    "hack": -3.0, "hacked": -3.0, "exploit": -2.5, "exploited": -2.5,
    "liquidated": -2.5, "liquidation": -2.0,
    "sec": -0.5, "regulation": -0.5, "lawsuit": -1.5,
    "ban": -2.0, "banned": -2.0, "crackdown": -2.0,
    "dip": -0.5, "correction": -1.0, "pullback": -0.8,
    "dead": -2.5, "dying": -2.0, "worthless": -3.0, "shitcoin": -2.0,
    "bankruptcy": -3.0, "bankrupt": -3.0, "insolvent": -3.0,
    "withdraw": -1.0, "frozen": -2.0,
    "depegged": -2.5, "depeg": -2.5,
    "bagholder": -1.5, "bagholding": -1.5, "underwater": -1.5,
    "capitulation": -2.5, "bloodbath": -3.0, "massacre": -3.0,
    "ponzinomics": -3.0, "vaporware": -2.5,
}

# Emotion keyword clusters
EMOTION_KEYWORDS = {
    "fear": {"fear", "scared", "afraid", "worried", "panic", "panicking", "nervous",
             "crash", "plunge", "bloodbath", "capitulation", "liquidation", "fud", "bearish"},
    "hype": {"moon", "mooning", "moonshot", "pump", "pumping", "lambo", "wagmi",
             "rocket", "explode", "skyrocket", "parabolic", "massive", "huge", "insane",
             "bullrun", "supercycle", "altseason", "gem"},
    "doubt": {"doubt", "skeptical", "uncertain", "unsure", "questionable", "suspicious",
              "overvalued", "bubble", "ponzi", "scam", "shitcoin", "vaporware", "concerned"},
    "confidence": {"confident", "conviction", "strong", "solid", "fundamentals", "undervalued",
                   "accumulate", "hodl", "institutional", "adoption", "bullcase", "based", "chad"},
    "fomo": {"fomo", "regret", "too late", "left behind", "all in", "yolo", "ape", "aped", "apeing"},
    "panic": {"panic", "panicking", "crash", "bloodbath", "bankrupt", "insolvent",
              "frozen", "hack", "exploit", "rug"},
}

# Context categories
CONTEXT_KEYWORDS = {
    "regulation": {"sec", "regulation", "regulatory", "compliance", "lawsuit", "legal",
                   "gensler", "enforcement", "ban", "crackdown", "mica", "cftc"},
    "token_utility": {"staking", "governance", "defi", "tvl", "yield", "farming",
                      "mainnet", "upgrade", "scalability", "interoperability", "l2"},
    "scam_risk": {"scam", "ponzi", "rug", "rugpull", "fraud", "hack", "exploit",
                  "vaporware", "shitcoin", "honeypot"},
}

_analyzer = None


def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
        _analyzer.lexicon.update(CRYPTO_LEXICON)
    return _analyzer


def detect_emotions(text: str) -> dict:
    if not text:
        return {e: 0.0 for e in EMOTION_KEYWORDS}
    words = set(text.lower().split())
    results = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        hits = len(words & keywords)
        results[emotion] = round(min(1.0, hits / max(len(keywords) * 0.15, 1)), 4)
    return results


def detect_context(text: str) -> str:
    if not text:
        return "general"
    words = set(text.lower().split())
    scores = {}
    for ctx, keywords in CONTEXT_KEYWORDS.items():
        scores[ctx] = len(words & keywords)
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def sentiment_intensity(compound: float) -> str:
    ac = abs(compound)
    if ac >= 0.6: return "strong"
    elif ac >= 0.3: return "moderate"
    elif ac >= 0.15: return "weak"
    return "neutral"


def analyze(text: str) -> dict:
    if not text or not text.strip():
        return {"compound": 0.0, "pos": 0.0, "neg": 0.0, "neu": 1.0, "label": "neutral",
                "emotions": {e: 0.0 for e in EMOTION_KEYWORDS},
                "context": "general", "intensity": "neutral"}
    scores = get_analyzer().polarity_scores(text)
    compound = scores["compound"]
    label = "bullish" if compound >= 0.15 else ("bearish" if compound <= -0.15 else "neutral")
    return {
        "compound": compound, "pos": scores["pos"], "neg": scores["neg"], "neu": scores["neu"],
        "label": label, "emotions": detect_emotions(text),
        "context": detect_context(text), "intensity": sentiment_intensity(compound),
    }


def analyze_batch(texts: list) -> list:
    return [analyze(t) for t in texts]


def fear_greed_index(sentiments: list) -> dict:
    if not sentiments:
        return {"score": 50, "label": "Neutral"}
    avg = sum(sentiments) / len(sentiments)
    score = int(max(0, min(100, (avg + 1) * 50)))
    if score <= 20: label = "Extreme Fear"
    elif score <= 40: label = "Fear"
    elif score <= 60: label = "Neutral"
    elif score <= 80: label = "Greed"
    else: label = "Extreme Greed"
    return {"score": score, "label": label}
