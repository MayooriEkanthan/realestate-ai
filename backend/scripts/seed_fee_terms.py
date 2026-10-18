import os
import sys
import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from services.database import init_db, get_con, create_fee_terms, latest_terms

rng = np.random.default_rng(11)
init_db()
listings = pd.read_csv("data/listings.csv")

with get_con() as con:
    added = 0
    for lid in listings["id"]:
        if latest_terms(con, int(lid)) is None:
            create_fee_terms(
                con, int(lid),
                commission_pct=float(rng.choice([1.0, 1.5, 2.0, 2.5])),
                payer="buyer",
                due_when="Only after the sale agreement is signed and both parties confirm on the platform",
                covers="Viewings, negotiation and paperwork guidance",
                other_fees="None",
            )
            added += 1
print(f"Fee terms version 1 created for {added} listings")
