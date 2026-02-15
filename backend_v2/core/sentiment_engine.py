from textblob import TextBlob
from datetime import datetime

class SentimentEngine:
    def analyze_text(self, text: str) -> dict:
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity

        if polarity > 0.1:
            label = "BULLISH"
        elif polarity < -0.1:
            label = "BEARISH"
        else:
            label = "NEUTRAL"

        return {
            "text": text,
            "label": label,
            "polarity": round(polarity, 3),
            "confidence": round(abs(polarity), 3),
            "timestamp": datetime.utcnow().isoformat()
        }

    def aggregate_sentiment(self, texts: list) -> dict:
        results = [self.analyze_text(t) for t in texts]

        if not results:
            return {"error": "No texts provided"}

        avg_score = sum(r["polarity"] for r in results) / len(results)

        if avg_score > 0.1:
            overall = "BULLISH"
        elif avg_score < -0.1:
            overall = "BEARISH"
        else:
            overall = "NEUTRAL"

        return {
            "overall_sentiment": overall,
            "average_score": round(avg_score, 3),
            "total_samples": len(results),
            "details": results
        }
