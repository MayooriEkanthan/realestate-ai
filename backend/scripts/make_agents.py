import os
from pathlib import Path
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

BASE_DIR = Path(__file__).resolve().parent.parent
data_dir = BASE_DIR / "data"
os.makedirs(data_dir, exist_ok=True)

agents_data = [
    {"id": 1, "name": "Kasun Perera", "town": "Colombo", "specialty": "Apartment", "phone": "0771234567", "email": "kasun.perera@example.com"},
    {"id": 2, "name": "Nimal Fernando", "town": "Colombo", "specialty": "House", "phone": "0772345678", "email": "nimal.fernando@example.com"},
    {"id": 3, "name": "Dilani Wickramasinghe", "town": "Colombo", "specialty": "Land", "phone": "0773456789", "email": "dilani.w@example.com"},
    {"id": 4, "name": "Rohan De Silva", "town": "Kandy", "specialty": "House", "phone": "0774567890", "email": "rohan.desilva@example.com"},
    {"id": 5, "name": "Priya Jayawardena", "town": "Kandy", "specialty": "Apartment", "phone": "0775678901", "email": "priya.j@example.com"},
    {"id": 6, "name": "Sunil Silva", "town": "Galle", "specialty": "House", "phone": "0776789012", "email": "sunil.silva@example.com"},
    {"id": 7, "name": "Anura Bandara", "town": "Galle", "specialty": "Land", "phone": "0777890123", "email": "anura.b@example.com"},
    {"id": 8, "name": "Tharushi Senanayake", "town": "Negombo", "specialty": "House", "phone": "0778901234", "email": "tharushi.s@example.com"},
    {"id": 9, "name": "Mohamed Rizwan", "town": "Negombo", "specialty": "Apartment", "phone": "0779012345", "email": "m.rizwan@example.com"},
    {"id": 10, "name": "Suresh Kumar", "town": "Jaffna", "specialty": "House", "phone": "0711234567", "email": "suresh.kumar@example.com"},
    {"id": 11, "name": "Kavinda Rathnayake", "town": "Kurunegala", "specialty": "Land", "phone": "0712345678", "email": "kavinda.r@example.com"},
    {"id": 12, "name": "Chamari Atapattu", "town": "Matara", "specialty": "House", "phone": "0713456789", "email": "chamari.a@example.com"},
    {"id": 13, "name": "Dinesh Gunawardena", "town": "Kataragama", "specialty": "Land", "phone": "0714567890", "email": "dinesh.g@example.com"},
]

agents_df = pd.DataFrame(agents_data)
agents_csv_path = data_dir / "agents.csv"
agents_df.to_csv(agents_csv_path, index=False)
print(f"Created {agents_csv_path} with {len(agents_df)} agents")

# Link listings to agents
listings_csv_path = data_dir / "listings.csv"
if not listings_csv_path.exists():
    raise FileNotFoundError(f"Cannot find {listings_csv_path}. Please run make_data.py first.")

listings_df = pd.read_csv(listings_csv_path)

agent_ids = []
for _, row in listings_df.iterrows():
    matching = agents_df[agents_df["town"] == row["town"]]
    if not matching.empty:
        chosen_id = int(rng.choice(matching["id"].values))
    else:
        chosen_id = int(rng.choice(agents_df["id"].values))
    agent_ids.append(chosen_id)

listings_df["agent_id"] = agent_ids
listings_df.to_csv(listings_csv_path, index=False)
print(f"Updated {listings_csv_path} with agent_id column ({len(listings_df)} rows)")
print(listings_df[["id", "town", "type", "price_lkr", "agent_id"]].head())
