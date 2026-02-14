from core.models import Entity


class NarrativeEngine:
    def update_entity(self, entity: Entity, new_sentiment: float):

        # Calculate velocity
        entity.sentiment_velocity = new_sentiment - entity.current_sentiment

        # Update sentiment
        entity.current_sentiment = new_sentiment

        # Update baseline gradually
        entity.baseline_sentiment = (
            entity.baseline_sentiment * 0.9 + new_sentiment * 0.1
        )

        # Simple volume spike logic
        entity.volume_spike = entity.mention_count / 10

        # Risk & momentum scoring
        entity.risk_score = abs(entity.sentiment_velocity) * entity.volume_spike
        entity.momentum_score = entity.current_sentiment * entity.volume_spike

        # Determine state
        if entity.sentiment_velocity < -0.3:
            entity.state = "BEARISH_ESCALATION"

        elif entity.sentiment_velocity > 0.3:
            entity.state = "BULLISH_IGNITION"

        else:
            entity.state = "STABLE"

        return entity
