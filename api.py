from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from nltk.sentiment import SentimentIntensityAnalyzer
from loguru import logger
import nltk

nltk.download('vader_lexicon')

app = FastAPI()
sia = SentimentIntensityAnalyzer()

class Texte(BaseModel):
    texte: str

@app.get("/")
def root():
    return {"message": "API d'analyse de sentiment"}

@app.post("/analyse_sentiment/")
async def analyse_sentiment(texte_object: Texte):
    logger.info(f"Analyse du texte: {texte_object.texte}")
    try:
        sentiment = sia.polarity_scores(texte_object.texte)
        logger.info(f"Résultats: {sentiment}")
        return {
            "neg": sentiment["neg"],
            "neu": sentiment["neu"],
            "pos": sentiment["pos"],
            "compound": sentiment["compound"],
        }
    except Exception as e:
        logger.error(f"Erreur: {e}")
        raise HTTPException(status_code=500, detail=str(e))