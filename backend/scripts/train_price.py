import os
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from xgboost import XGBRegressor

df = pd.read_csv("data/listings.csv")

FEATURES = ["town", "type", "bedrooms", "area_sqft", "perches"]
X = df[FEATURES]
y = df["price_lkr"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=1)

pre = ColumnTransformer(
    [("cat", OneHotEncoder(handle_unknown="ignore"), ["town", "type"])],
    remainder="passthrough",
)
model = Pipeline([
    ("pre", pre),
    ("xgb", XGBRegressor(n_estimators=300, max_depth=4, learning_rate=0.08)),
])
model.fit(X_train, y_train)

pred = model.predict(X_test)
print(f"MAE: LKR {mean_absolute_error(y_test, pred):,.0f}")
print(f"R2 : {r2_score(y_test, pred):.3f}")

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/price_model.joblib")
print("Saved models/price_model.joblib")
