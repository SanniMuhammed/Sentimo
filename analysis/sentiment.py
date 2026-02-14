"""VADER sentiment analysis with crypto-specific lexicon."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Crypto-specific lexicon additions
CRYPTO_LEXICON = {
    "hodl": 2.0, "hodling": 2.0, "hodled": 1.5,
    "moon": 2.5, "mooning": 3.0, "moonshot": 2.5,
    "bullish": 2.5, "bull": 1.5, "bulls": 1.5,
    "pump": 1.5, "pumping": 2.0, "pumped": 1.5,
    "lambo": 2.0, "wagmi": 2.5, "gm": 1.0,
    "diamond hands": 2.5, "diamond": 1.0,
    "accumulate": 1.5, "accumulating": 1.5,
    "breakout": 2.0, "ath": 2.5, "rally": 2.0,
    "undervalued": 1.5, "gem": 2.0, "alpha": 1.5,
    "adoption": 1.5, "institutional": 1.0,
    "bearish": -2.5, "bear": -1.5, "bears": -1.5,
    "dump": -2.0, "dumping": -2.5, "dumped": -2.0,
    "rug": -3.5, "rugpull": -3.5, "rug pull": -3.5, "rugged": -3.5,
    "scam": -3.0, "ponzi": -3.0, "fraud": -3.0,
    "fud": -2.0, "fear": -1.5,
    "crash": -3.0, "crashing": -3.0, "crashed": -2.5,
    "rekt": -3.0, "rekted": -3.0, "wrecked": -2.5,
    "paper hands": -2.0, "ngmi": -2.5,
    "sell": -1.0, "selling": -1.5, "sold": -1.0,
    "overvalued": -1.5, "bubble": -2.0,
    "hack": -3.0, "hacked": -3.0, "exploit": -2.5,
    "liquidated": -2.5, "liquidation": -2.0,
    "sec": -0.5, "regulation": -0.5, "lawsuit": -1.5,
    "ban": -2.0, "banned": -2.0,
    "dip": -0.5, "correction": -1.0,
    "whale": 0.5, "whales": 0.5,
    "defi": 0.5, "nft": 0.3, "web3": 0.5,
    "staking": 1.0, "yield": 0.5, "airdrop": 1.5,
}

_analyzer = None

def get_analyzer():
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
        _analyzer.lexicon.update(CRYPTO_LEXICON)
    return _analyzer


def analyze(text: str) -> dict:
    """Return sentiment dict with compound, pos, neg, neu, label."""
    if not text or not text.strip():
        return {"compound": 0.0, "pos": 0.0, "neg": 0.0, "neu": 1.0, "label": "neutral"}
    scores = get_analyzer().polarity_scores(text)
    compound = scores["compound"]
    label = "bullish" if compound >= 0.15 else ("bearish" if compound <= -0.15 else "neutral")
    return {"compound": compound, "pos": scores["pos"], "neg": scores["neg"], "neu": scores["neu"], "label": label}


def analyze_batch(texts: list) -> list:
    return [analyze(t) for t in texts]


def fear_greed_index(sentiments: list) -> dict:
    """Compute a 0-100 Fear & Greed index from a list of compound scores."""
    if not sentiments:
        return {"score": 50, "label": "Neutral"}
    avg = sum(sentiments) / len(sentiments)
    score = int(max(0, min(100, (avg + 1) * 50)))
    if score <= 20:
        label = "Extreme Fear"
    elif score <= 40:
        label = "Fear"
    elif score <= 60:
        label = "Neutral"
    elif score <= 80:
        label = "Greed"
    else:
        label = "Extreme Greed"
    return {"score": score, "label": label}
