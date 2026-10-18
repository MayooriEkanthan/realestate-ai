import json
import os
from pathlib import Path
import secrets
from typing import Literal

import joblib
import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import COMMISSION_CAP_PCT, HIGH_RATIO, SUSPICIOUS_LOW_RATIO
from services.database import create_fee_terms, get_con, latest_terms, now

router = APIRouter(prefix="/api", tags=["marketplace"])

BASE_DIR = Path(__file__).resolve().parent.parent

_model = None


def price_model():
    global _model
    if _model is None:
        model_path = BASE_DIR / "models" / "price_model.joblib"
        _model = joblib.load(model_path if model_path.exists() else "models/price_model.joblib")
    return _model


def rec(df):
    """DataFrame to a list of plain dicts that FastAPI can always serialise."""
    return json.loads(df.to_json(orient="records"))


def listings_df():
    data_path = BASE_DIR / "data" / "listings.csv"
    return pd.read_csv(data_path if data_path.exists() else "data/listings.csv")


def agents_df():
    data_path = BASE_DIR / "data" / "agents.csv"
    return pd.read_csv(data_path if data_path.exists() else "data/agents.csv")


def price_check(listing: dict):
    """Compare the listed price with the AI estimate to spot suspicious prices."""
    try:
        cols = ["town", "type", "bedrooms", "area_sqft", "perches"]
        est = float(price_model().predict(pd.DataFrame([{c: listing[c] for c in cols}]))[0])
        ratio = listing["price_lkr"] / est if est > 0 else None
        flag = "OK"
        if ratio is not None and ratio < SUSPICIOUS_LOW_RATIO:
            flag = "SUSPICIOUSLY_LOW"
        elif ratio is not None and ratio > HIGH_RATIO:
            flag = "HIGH"
        return {"estimated_price_lkr": round(est, -4),
                "ratio": round(ratio, 2) if ratio else None, "flag": flag}
    except Exception:
        return None


# ---------- Browse ----------
@router.get("/listings")
def list_listings(town: str | None = None, type: str | None = None,
                  min_bedrooms: int = 0, max_price: float | None = None, limit: int = 30):
    df = listings_df()
    if town:
        df = df[df.town == town]
    if type:
        df = df[df.type == type]
    df = df[df.bedrooms >= min_bedrooms]
    if max_price:
        df = df[df.price_lkr <= max_price]
    return rec(df.head(limit))


@router.get("/listings/{listing_id}")
def get_listing(listing_id: int):
    df = listings_df()
    row = df[df.id == listing_id]
    if row.empty:
        raise HTTPException(404, "Listing not found")
    listing = rec(row)[0]
    a = agents_df()
    agent_row = a[a.id == listing["agent_id"]]
    with get_con() as con:
        terms = latest_terms(con, listing_id)
    return {
        "listing": listing,
        "agent": rec(agent_row)[0] if not agent_row.empty else None,
        "fee_terms": dict(terms) if terms else None,
        "price_check": price_check(listing),
        "safety_notice": ("Never pay money to an individual before verifying the property "
                          "and signing a lawyer-reviewed agreement."),
    }


@router.get("/agents")
def list_agents(town: str | None = None, specialty: str | None = None):
    df = agents_df()
    if town:
        df = df[df.town == town]
    if specialty:
        df = df[df.specialty == specialty]
    return rec(df)


@router.get("/agents/{agent_id}")
def get_agent(agent_id: int):
    a = agents_df()
    row = a[a.id == agent_id]
    if row.empty:
        raise HTTPException(404, "Agent not found")
    mine = listings_df()
    return {"agent": rec(row)[0], "listings": rec(mine[mine.agent_id == agent_id].head(20))}


# ---------- Fee terms (locked, versioned) ----------
class FeeTermsIn(BaseModel):
    commission_pct: float = Field(ge=0)
    payer: Literal["buyer", "seller", "split"]
    due_when: str = Field(min_length=5, max_length=300)
    covers: str = Field(min_length=3, max_length=300)
    other_fees: str = Field(default="None", max_length=300)


@router.get("/listings/{listing_id}/fee-terms")
def fee_terms_history(listing_id: int):
    with get_con() as con:
        rows = con.execute("SELECT * FROM fee_terms WHERE listing_id=? ORDER BY version",
                           (listing_id,)).fetchall()
    return [dict(r) for r in rows]


# DEMO ONLY: no login. A real version must authenticate the listing's agent.
# There is deliberately no edit or delete endpoint: a change is always a NEW version.
@router.post("/listings/{listing_id}/fee-terms")
def new_fee_terms_version(listing_id: int, t: FeeTermsIn):
    if t.commission_pct > COMMISSION_CAP_PCT:
        raise HTTPException(400, f"Commission cannot exceed {COMMISSION_CAP_PCT}% on this platform")
    if listings_df()[lambda d: d.id == listing_id].empty:
        raise HTTPException(404, "Listing not found")
    with get_con() as con:
        terms_id, version = create_fee_terms(
            con, listing_id, t.commission_pct, t.payer, t.due_when, t.covers, t.other_fees)
    return {"fee_terms_id": terms_id, "version": version,
            "note": "Existing inquiries and deals keep the terms they were created under."}


# ---------- Inquiries (with snapshot) ----------
class InquiryIn(BaseModel):
    listing_id: int
    buyer_name: str = Field(min_length=2, max_length=80)
    buyer_phone: str = Field(min_length=7, max_length=20)
    buyer_email: str = Field(default="", max_length=120)
    message: str = Field(min_length=3, max_length=1000)
    consent: bool


@router.post("/inquiries")
def create_inquiry(q: InquiryIn):
    if not q.consent:
        raise HTTPException(400, "Consent is required to contact the agent")
    df = listings_df()
    row = df[df.id == q.listing_id]
    if row.empty:
        raise HTTPException(404, "Listing not found")
    listing = rec(row)[0]
    reference = "INQ-" + secrets.token_hex(3).upper()
    with get_con() as con:
        terms = latest_terms(con, q.listing_id)
        if terms is None:
            raise HTTPException(409, "This listing has no declared fee terms yet")
        con.execute(
            "INSERT INTO inquiries (reference, listing_id, agent_id, buyer_name, buyer_phone, "
            "buyer_email, message, listed_price_lkr, fee_terms_id, terms_hash, consent, created_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (reference, q.listing_id, listing["agent_id"], q.buyer_name, q.buyer_phone,
             q.buyer_email, q.message, listing["price_lkr"], terms["id"], terms["terms_hash"],
             1, now()))
    return {"status": "sent", "reference": reference, "agent_id": listing["agent_id"],
            "snapshot": {"listed_price_lkr": listing["price_lkr"],
                         "commission_pct": terms["commission_pct"],
                         "fee_terms_version": terms["version"]},
            "note": "Keep this reference. It proves the terms you were shown."}


@router.get("/inquiries/{reference}")
def get_inquiry(reference: str):
    with get_con() as con:
        inq = con.execute("SELECT * FROM inquiries WHERE reference=?", (reference,)).fetchone()
        if inq is None:
            raise HTTPException(404, "Inquiry not found")
        terms = con.execute("SELECT * FROM fee_terms WHERE id=?", (inq["fee_terms_id"],)).fetchone()
    return {"inquiry": dict(inq), "fee_terms_at_that_time": dict(terms)}


# DEMO ONLY: no login, so anyone can read this. A real version needs agent authentication.
@router.get("/agents/{agent_id}/inquiries")
def agent_inbox(agent_id: int):
    with get_con() as con:
        rows = con.execute("SELECT * FROM inquiries WHERE agent_id=? ORDER BY id DESC",
                           (agent_id,)).fetchall()
    return [dict(r) for r in rows]
