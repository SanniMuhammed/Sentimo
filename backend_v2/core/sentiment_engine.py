import re


class SentimentEngine:
    def __init__(self):
        self.positive_keywords = [
            "bullish", "pump", "breakout", "accumulate",
            "partnership", "approval", "growth", "surge",
            "strong", "buy", "moon"
        ]

        self.negative_keywords = [
            "fud", "scam", "hack", "collapse",
            "withdrawal", "ban", "lawsuit", "dump",
            "sell", "fear", "crash", "liquidation"
        ]

    def score(self, text: str) -> float:
        text = text.lower()

        pos_count = sum(1 for word in self.positive_keywords if re.search(rf"\b{word}\b", text))
        neg_count = sum(1 for word in self.negative_keywords if re.search(rf"\b{word}\b", text))

        total = pos_count + neg_count

        if total == 0:
            return 0.0

        return (pos_count - neg_count) / total
