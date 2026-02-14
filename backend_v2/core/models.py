from dataclasses import dataclass, field
from typing import Dict
import time


@dataclass
class Entity:
    name: str
    entity_type: str = "unknown"
    first_seen: float = field(default_factory=time.time)
    mention_count: int = 0

    baseline_sentiment: float = 0.0
    current_sentiment: float = 0.0
    sentiment_velocity: float = 0.0

    volume_spike: float = 0.0

    risk_score: float = 0.0
    momentum_score: float = 0.0

    state: str = "STABLE"  # BEARISH_ESCALATION | BULLISH_IGNITION | STABLE
