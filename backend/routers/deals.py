import secrets
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import DISPUTE_WINDOW_DAYS, PLATFORM_FEE_PAYER, PLATFORM_FEE_PCT
from services.database import get_con, now

router = APIRouter(prefix="/api/deals", tags=["deals"])

DEMO_NOTICE = "DEMO ONLY. No real money is moved. Payments are simulated."

# The only allowed moves between states
TRANSITIONS = {
    "DEAL_PROPOSED": {"BOTH_CONFIRMED", "CANCELLED"},
    "BOTH_CONFIRMED": {"DISPUTE_WINDOW", "CANCELLED"},
    "DISPUTE_WINDOW": {"CLOSED", "REFUNDED"},
}


def get_deal(con, deal_id: int):
    deal = con.execute("SELECT * FROM deals WHERE id=?", (deal_id,)).fetchone()
    if deal is None:
        raise HTTPException(404, "Deal not found")
    return deal


def add_event(con, deal_id, from_state, to_state, note=""):
    con.execute("INSERT INTO deal_events (deal_id, from_state, to_state, note, created_at) "
                "VALUES (?,?,?,?,?)", (deal_id, from_state, to_state, note, now()))


def add_ledger(con, deal_id, entry_type, amount, payer, payee):
    con.execute(
        "INSERT INTO ledger (deal_id, entry_type, amount_lkr, payer, payee, status, reference, "
        "created_at) VALUES (?,?,?,?,?,?,?,?)",
        (deal_id, entry_type, amount, payer, payee, "paid_demo",
         "LED-" + secrets.token_hex(3).upper(), now()))


def transition(con, deal, new_state, note=""):
    if new_state not in TRANSITIONS.get(deal["state"], set()):
        raise HTTPException(409, f"Cannot move from {deal['state']} to {new_state}")
    con.execute("UPDATE deals SET state=?, updated_at=? WHERE id=?", (new_state, now(), deal["id"]))
    add_event(con, deal["id"], deal["state"], new_state, note)


def deal_view(con, deal_id):
    deal = get_deal(con, deal_id)
    events = con.execute("SELECT * FROM deal_events WHERE deal_id=? ORDER BY id", (deal_id,)).fetchall()
    ledger = con.execute("SELECT * FROM ledger WHERE deal_id=? ORDER BY id", (deal_id,)).fetchall()
    return {"deal": dict(deal), "events": [dict(e) for e in events],
            "ledger": [dict(x) for x in ledger],
            "dispute_window_days": DISPUTE_WINDOW_DAYS, "notice": DEMO_NOTICE}


class DealIn(BaseModel):
    reference: str
    agreed_price_lkr: float = Field(gt=0)
    use_agent: bool = False


class ConfirmIn(BaseModel):
    role: Literal["buyer", "seller"]


@router.post("")
def propose_deal(d: DealIn):
    with get_con() as con:
        inq = con.execute("SELECT * FROM inquiries WHERE reference=?", (d.reference,)).fetchone()
        if inq is None:
            raise HTTPException(404, "Inquiry reference not found")
        active = con.execute(
            "SELECT id FROM deals WHERE inquiry_id=? AND state NOT IN ('CANCELLED','REFUNDED')",
            (inq["id"],)).fetchone()
        if active:
            raise HTTPException(409, f"This inquiry already has an active deal (id {active['id']})")
        # Fees use the terms the buyer saw at inquiry time, not any newer version
        terms = con.execute("SELECT * FROM fee_terms WHERE id=?", (inq["fee_terms_id"],)).fetchone()
        platform_fee = round(d.agreed_price_lkr * PLATFORM_FEE_PCT / 100, 2)
        agent_fee = round(d.agreed_price_lkr * terms["commission_pct"] / 100, 2) if d.use_agent else 0.0
        cur = con.execute(
            "INSERT INTO deals (inquiry_id, listing_id, agent_id, use_agent, agreed_price_lkr, "
            "commission_pct, platform_fee_lkr, agent_fee_lkr, state, created_at, updated_at) "
            "VALUES (?,?,?,?,?,?,?,?,?,?,?)",
            (inq["id"], inq["listing_id"], inq["agent_id"], int(d.use_agent), d.agreed_price_lkr,
             terms["commission_pct"], platform_fee, agent_fee, "DEAL_PROPOSED", now(), now()))
        add_event(con, cur.lastrowid, None, "DEAL_PROPOSED", "Deal proposed")
        return deal_view(con, cur.lastrowid)


@router.get("/{deal_id}")
def read_deal(deal_id: int):
    with get_con() as con:
        return deal_view(con, deal_id)


# DEMO ONLY: no login, so anyone can confirm for either side.
@router.post("/{deal_id}/confirm")
def confirm(deal_id: int, c: ConfirmIn):
    with get_con() as con:
        deal = get_deal(con, deal_id)
        if deal["state"] != "DEAL_PROPOSED":
            raise HTTPException(409, f"Deal is {deal['state']}, confirmation is closed")
        column = {"buyer": "buyer_confirmed", "seller": "seller_confirmed"}[c.role]
        con.execute(f"UPDATE deals SET {column}=1, updated_at=? WHERE id=?", (now(), deal_id))
        deal = get_deal(con, deal_id)
        add_event(con, deal_id, deal["state"], deal["state"], f"{c.role} confirmed")
        if deal["buyer_confirmed"] and deal["seller_confirmed"]:
            transition(con, deal, "BOTH_CONFIRMED", "Both sides confirmed")
        return deal_view(con, deal_id)


@router.post("/{deal_id}/pay-demo")
def pay_demo(deal_id: int):
    with get_con() as con:
        deal = get_deal(con, deal_id)
        if deal["state"] != "BOTH_CONFIRMED":
            raise HTTPException(409, "Fees can only be paid after BOTH sides confirm the deal")
        add_ledger(con, deal_id, "PLATFORM_FEE", deal["platform_fee_lkr"], PLATFORM_FEE_PAYER, "platform")
        if deal["agent_fee_lkr"] > 0:
            add_ledger(con, deal_id, "AGENT_FEE_HELD", deal["agent_fee_lkr"], "buyer", "platform")
        transition(con, deal, "DISPUTE_WINDOW", "Fees paid (simulated). Dispute window started.")
        return deal_view(con, deal_id)


@router.post("/{deal_id}/release-demo")
def release_demo(deal_id: int):
    """Real version: runs automatically after the dispute window. The demo lets you skip the wait."""
    with get_con() as con:
        deal = get_deal(con, deal_id)
        if deal["state"] != "DISPUTE_WINDOW":
            raise HTTPException(409, "Agent payout is only possible after fees are paid")
        if deal["agent_fee_lkr"] > 0:
            add_ledger(con, deal_id, "AGENT_PAYOUT", deal["agent_fee_lkr"], "platform",
                       f"agent:{deal['agent_id']}")
        transition(con, deal, "CLOSED", "Agent paid out (simulated). Deal closed.")
        return deal_view(con, deal_id)


@router.post("/{deal_id}/cancel")
def cancel(deal_id: int):
    with get_con() as con:
        deal = get_deal(con, deal_id)
        if deal["state"] in ("DEAL_PROPOSED", "BOTH_CONFIRMED"):
            transition(con, deal, "CANCELLED", "Cancelled before any payment")
        elif deal["state"] == "DISPUTE_WINDOW":
            paid = con.execute(
                "SELECT * FROM ledger WHERE deal_id=? AND entry_type IN ('PLATFORM_FEE','AGENT_FEE_HELD')",
                (deal_id,)).fetchall()
            for e in paid:   # reverse every payment: payer and payee swap
                add_ledger(con, deal_id, "REFUND", e["amount_lkr"], e["payee"], e["payer"])
            transition(con, deal, "REFUNDED", "Cancelled in dispute window, fees refunded (simulated)")
        else:
            raise HTTPException(409, f"A {deal['state']} deal cannot be cancelled")
        return deal_view(con, deal_id)
