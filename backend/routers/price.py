import os
from pathlib import Path
import joblib
import pandas as pd
from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["price"])

BASE_DIR = Path(__file__).resolve().parent.parent
model_path = BASE_DIR / "models" / "price_model.joblib"
data_path = BASE_DIR / "data" / "listings.csv"

model = joblib.load(model_path if model_path.exists() else "models/price_model.joblib")
listings = pd.read_csv(data_path if data_path.exists() else "data/listings.csv")


class PriceRequest(BaseModel):
    town: str
    type: str
    bedrooms: int = Field(ge=0, le=15)
    area_sqft: int = Field(ge=0, le=50000)
    perches: float = Field(ge=0, le=500)


@router.get("/towns")
def get_towns():
    return sorted(listings["town"].unique().tolist())


@router.post("/predict")
def predict(req: PriceRequest):
    row = pd.DataFrame([req.model_dump()])[["town", "type", "bedrooms", "area_sqft", "perches"]]
    price = float(model.predict(row)[0])
    return {
        "estimated_price_lkr": round(price, -4),
        "note": "Approximate estimate from a prototype model trained on simulated data.",
    }
