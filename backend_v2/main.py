from fastapi import FastAPI
from core.sentiment_engine import SentimentEngine
from pydantic import BaseModel

app = FastAPI()
engine = SentimentEngine()

class TextRequest(BaseModel):
    text: str

@app.get("/")
def root():
    return {"message": "Sentimo API is running 🚀"}

@app.post("/analyze")
def analyze(request: TextRequest):
    return engine.analyze_text(request.text)
