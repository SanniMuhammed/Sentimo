from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

# ---- In-Memory Entity Store ---- #

entities: Dict[str, dict] = {
    "Binance": {
        "current_sentiment": -1,
        "velocity": 0,
        "momentum_score": -0.4,
        "risk_score": 0,
        "state": "STABLE"
    }
}


# ---- Risk Engine ---- #

def calculate_risk(sentiment: float, momentum: float) -> float:
    base_risk = abs(sentiment) * 0.6
    momentum_impact = abs(momentum) * 0.4
    return round(base_risk + momentum_impact, 2)


def determine_state(risk: float) -> str:
    if risk < 0.4:
        return "STABLE"
    elif risk < 0.7:
        return "WARNING"
    else:
        return "CRITICAL"


# ---- API Routes ---- #

@app.get("/entity/{name}")
def get_entity(name: str):
    entity = entities.get(name)

    if not entity:
        return {"error": "Entity not found"}

    # Recalculate risk dynamically
    risk = calculate_risk(
        entity["current_sentiment"],
        entity["momentum_score"]
    )

    state = determine_state(risk)

    entity["risk_score"] = risk
    entity["state"] = state

    return {
            "entity": name,
            **entity
        }

# ---- Update Model ---- #

class UpdateRequest(BaseModel):
    name: str
    sentiment: float
    momentum: float


# ---- Update Endpoint ---- #

@app.post("/entity/update")
def update_entity(data: UpdateRequest):

    # Create entity if it doesn't exist
    if data.name not in entities:
        entities[data.name] = {
            "current_sentiment": 0,
            "velocity": 0,
            "momentum_score": 0,
            "risk_score": 0,
            "state": "STABLE"
        }

    entity = entities[data.name]

    def calculate_risk(sentiment, momentum, velocity=0):
        base_risk = (0.5 * abs(sentiment)) + (0.3 * abs(momentum))
        velocity_boost = 0.2 * abs(velocity)
    
        return round(base_risk + velocity_boost, 2)
        risk = calculate_risk(data.sentiment, data.momentum, velocity)# Calculate velocity
    previous_sentiment = entity["current_sentiment"]
    velocity = data.sentiment - previous_sentiment
    
    entity["velocity"] = velocity
    entity["current_sentiment"] = data.sentiment
    entity["momentum_score"] = data.momentum
    entity["current_sentiment"] = data.sentiment
    entity["momentum_score"] = data.momentum

    # Recalculate risk
    risk = calculate_risk(data.sentiment, data.momentum)
    state = determine_state(risk)

    entity["risk_score"] = risk
    entity["state"] = state

    return {
        "entity": data.name,
        **entity
    }
