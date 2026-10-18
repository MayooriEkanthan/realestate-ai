import os
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 500

# price multiplier per town (Colombo most expensive)
towns = {
    "Colombo": 3.0, "Kandy": 1.7, "Galle": 1.5, "Negombo": 1.5,
    "Kurunegala": 1.0, "Matara": 1.1, "Kataragama": 0.7, "Jaffna": 0.8,
}
features = ["near school", "with garden", "near main road", "quiet neighbourhood",
            "newly renovated", "near hospital", "with parking", "close to the beach"]

town = rng.choice(list(towns), N)
ptype = rng.choice(["House", "Apartment", "Land"], N, p=[0.5, 0.3, 0.2])

bedrooms = np.where(ptype == "Land", 0, rng.integers(1, 6, N))
area = np.where(ptype == "Land", 0, rng.integers(500, 4000, N))
perches = np.where(ptype == "Apartment", 0, rng.integers(5, 40, N))

mult = np.array([towns[t] for t in town])
price = (area * 9000 + perches * 450000 + bedrooms * 1_200_000) * mult
price = price * rng.normal(1.0, 0.08, N)          # random noise
price = np.maximum(price, 1_500_000).round(-4)

desc = []
for i in range(N):
    extra = ", ".join(rng.choice(features, 2, replace=False))
    if ptype[i] == "Land":
        desc.append(f"{perches[i]} perch land in {town[i]}, {extra}")
    else:
        desc.append(f"{bedrooms[i]} bedroom {ptype[i].lower()} in {town[i]}, {extra}")

df = pd.DataFrame({
    "id": range(1, N + 1), "town": town, "type": ptype, "bedrooms": bedrooms,
    "area_sqft": area, "perches": perches, "price_lkr": price, "description": desc,
})

os.makedirs("data", exist_ok=True)
df.to_csv("data/listings.csv", index=False)
print(df.head())
print("Rows:", len(df), "| Missing values:", int(df.isna().sum().sum()))
