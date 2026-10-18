import json
import os
import sqlite3
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def run_tests():
    print("=" * 60)
    print("RUNNING WORKFLOW VERIFICATION TESTS")
    print("=" * 60)

    # 0. Test /api/predict
    print("\n--- 0. Testing /api/predict ---")
    predict_payload = {
        "town": "Colombo",
        "type": "Apartment",
        "bedrooms": 3,
        "area_sqft": 1500,
        "perches": 0.0
    }
    r = client.post("/api/predict", json=predict_payload)
    print(f"POST /api/predict Status: {r.status_code}")
    print(json.dumps(r.json(), indent=2))
    assert r.status_code == 200
    assert "estimated_price_lkr" in r.json()

    # 1. GET /api/listings/1
    print("\n--- 1. Testing GET /api/listings/1 ---")
    r = client.get("/api/listings/1")
    print(f"GET /api/listings/1 Status: {r.status_code}")
    data = r.json()
    print("Listing ID:", data.get("listing", {}).get("id"))
    print("Town:", data.get("listing", {}).get("town"))
    print("Type:", data.get("listing", {}).get("type"))
    print("Price LKR:", data.get("listing", {}).get("price_lkr"))
    print("Agent:", data.get("agent"))
    print("Fee Terms:", data.get("fee_terms"))
    print("Price Check:", data.get("price_check"))
    print("Safety Notice:", data.get("safety_notice"))
    assert r.status_code == 200
    assert data.get("listing") is not None
    assert data.get("agent") is not None
    assert data.get("fee_terms") is not None
    assert data.get("price_check") is not None

    # 2. POST /api/inquiries
    print("\n--- 2. Testing POST /api/inquiries ---")
    inq_payload = {
        "listing_id": 1,
        "buyer_name": "Test Buyer",
        "buyer_phone": "0771234567",
        "buyer_email": "",
        "message": "Is this still available?",
        "consent": True
    }
    r = client.post("/api/inquiries", json=inq_payload)
    print(f"POST /api/inquiries Status: {r.status_code}")
    inq_res = r.json()
    print(json.dumps(inq_res, indent=2))
    assert r.status_code == 200
    reference = inq_res["reference"]
    initial_commission = inq_res["snapshot"]["commission_pct"]
    print(f"Created Inquiry Reference: {reference} with commission {initial_commission}%")

    # 3. POST /api/listings/1/fee-terms (Over cap test -> 400, then valid -> version 2)
    print("\n--- 3. Testing Fee Terms Cap and Versioning ---")
    over_cap_payload = {
        "commission_pct": 5.0,
        "payer": "buyer",
        "due_when": "Only after the sale agreement is signed",
        "covers": "Viewings, negotiation and paperwork guidance",
        "other_fees": "None"
    }
    r_over = client.post("/api/listings/1/fee-terms", json=over_cap_payload)
    print(f"POST /api/listings/1/fee-terms (5%) Status: {r_over.status_code} (Expected 400)")
    print(r_over.json())
    assert r_over.status_code == 400

    valid_payload = {
        "commission_pct": 2.0,
        "payer": "buyer",
        "due_when": "Only after the sale agreement is signed and both parties confirm on the platform",
        "covers": "Viewings, negotiation and paperwork guidance",
        "other_fees": "None"
    }
    r_valid = client.post("/api/listings/1/fee-terms", json=valid_payload)
    print(f"POST /api/listings/1/fee-terms (2%) Status: {r_valid.status_code}")
    print(json.dumps(r_valid.json(), indent=2))
    assert r_valid.status_code == 200
    assert r_valid.json()["version"] >= 2

    # 4. GET /api/inquiries/{reference} (Fee Lock Test)
    print("\n--- 4. Testing Fee Lock: GET /api/inquiries/{reference} ---")
    r_inq = client.get(f"/api/inquiries/{reference}")
    print(f"GET /api/inquiries/{reference} Status: {r_inq.status_code}")
    inq_details = r_inq.json()
    print("Snapshot Terms in Inquiry:")
    print(json.dumps(inq_details["fee_terms_at_that_time"], indent=2))
    assert inq_details["fee_terms_at_that_time"]["commission_pct"] == initial_commission
    print("Snapshot commission verified:", inq_details["fee_terms_at_that_time"]["commission_pct"])

    # 5. POST /api/deals
    print("\n--- 5. Testing POST /api/deals ---")
    deal_payload = {
        "reference": reference,
        "agreed_price_lkr": 30000000.0,
        "use_agent": True
    }
    r_deal = client.post("/api/deals", json=deal_payload)
    print(f"POST /api/deals Status: {r_deal.status_code}")
    deal_data = r_deal.json()
    print(json.dumps(deal_data, indent=2))
    assert r_deal.status_code == 200
    deal_id = deal_data["deal"]["id"]
    assert deal_data["deal"]["state"] == "DEAL_PROPOSED"

    # 6. POST /api/deals/{deal_id}/confirm
    print("\n--- 6. Testing Deal Confirmation (Buyer then Seller) ---")
    r_buyer = client.post(f"/api/deals/{deal_id}/confirm", json={"role": "buyer"})
    print("Buyer confirm state:", r_buyer.json()["deal"]["state"], "| Buyer confirmed:", r_buyer.json()["deal"]["buyer_confirmed"])
    assert r_buyer.json()["deal"]["state"] == "DEAL_PROPOSED"

    r_seller = client.post(f"/api/deals/{deal_id}/confirm", json={"role": "seller"})
    print("Seller confirm state:", r_seller.json()["deal"]["state"], "| Seller confirmed:", r_seller.json()["deal"]["seller_confirmed"])
    assert r_seller.json()["deal"]["state"] == "BOTH_CONFIRMED"

    # 7. POST /api/deals/{deal_id}/pay-demo
    print("\n--- 7. Testing Simulated Payment: POST /api/deals/{deal_id}/pay-demo ---")
    r_pay = client.post(f"/api/deals/{deal_id}/pay-demo")
    print(f"pay-demo Status: {r_pay.status_code}")
    pay_data = r_pay.json()
    print("Deal state:", pay_data["deal"]["state"])
    print("Ledger entries:")
    for entry in pay_data["ledger"]:
        print(f"  {entry['entry_type']}: LKR {entry['amount_lkr']:,.2f} from {entry['payer']} to {entry['payee']} [{entry['status']}]")
    assert pay_data["deal"]["state"] == "DISPUTE_WINDOW"
    assert len(pay_data["ledger"]) >= 1

    # 8. POST /api/deals/{deal_id}/release-demo
    print("\n--- 8. Testing Release Funds: POST /api/deals/{deal_id}/release-demo ---")
    r_rel = client.post(f"/api/deals/{deal_id}/release-demo")
    print(f"release-demo Status: {r_rel.status_code}")
    rel_data = r_rel.json()
    print("Deal state:", rel_data["deal"]["state"])
    print("Ledger entries:")
    for entry in rel_data["ledger"]:
        print(f"  {entry['entry_type']}: LKR {entry['amount_lkr']:,.2f} from {entry['payer']} to {entry['payee']} [{entry['status']}]")
    assert rel_data["deal"]["state"] == "CLOSED"

    # 9. Try pay-demo again (enforced state order test -> 409)
    print("\n--- 9. Testing Invalid Transition: pay-demo on CLOSED deal ---")
    r_pay_again = client.post(f"/api/deals/{deal_id}/pay-demo")
    print(f"pay-demo again Status: {r_pay_again.status_code} (Expected 409)")
    print(r_pay_again.json())
    assert r_pay_again.status_code == 409

    # 10. Tamper test: direct SQLite edit test
    print("\n--- 10. Tamper Test: Direct SQLite UPDATE and DELETE on locked table ---")
    con = sqlite3.connect("data/app.db")
    update_failed = False
    try:
        con.execute("UPDATE fee_terms SET commission_pct = 5.0 WHERE id = 1")
    except sqlite3.DatabaseError as e:
        update_failed = True
        print("UPDATE blocked as expected:", e)
    assert update_failed, "Direct UPDATE on locked table fee_terms should have failed!"

    delete_failed = False
    try:
        con.execute("DELETE FROM fee_terms WHERE id = 1")
    except sqlite3.DatabaseError as e:
        delete_failed = True
        print("DELETE blocked as expected:", e)
    assert delete_failed, "Direct DELETE on locked table fee_terms should have failed!"
    con.close()

    print("\n" + "=" * 60)
    print("ALL 10 TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
