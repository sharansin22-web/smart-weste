import pandas as pd
import joblib
import xgboost as xgb
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split

# Load dataset (Excel version)
df = pd.read_csv("dataset.csv.csv")


# Drop rows with missing target
df.dropna(subset=["Attack Type"], inplace=True)

# Split features & target
X = df.drop("Attack Type", axis=1)
y = df["Attack Type"]

# Encode target
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Train test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42
)

# Train model
model = xgb.XGBClassifier(
    tree_method="hist",
    n_estimators=100,
    max_depth=8
)

model.fit(X_train, y_train)

# Save model & encoder
joblib.dump(model, "model.pkl")
joblib.dump(le, "label_encoder.pkl")

print("✅ Model and Encoder saved successfully!")
