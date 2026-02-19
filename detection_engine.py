import pandas as pd
import numpy as np
import joblib
import sqlite3
import time
import datetime
import random

print("🛡 Advanced Detection Engine Starting...")

# ----------------------------
# Load Model
# ----------------------------
model = joblib.load("model.pkl")
le = joblib.load("label_encoder.pkl")

# ----------------------------
# Load Dataset (100 Records)
# ----------------------------
df = pd.read_csv("dataset.csv.csv")
df = df.head(1000)

if "Attack Type" in df.columns:
    X_full = df.drop("Attack Type", axis=1)
else:
    X_full = df.copy()

X_full = X_full.replace([np.inf, -np.inf], np.nan)
X_full = X_full.fillna(X_full.median(numeric_only=True))

# ----------------------------
# Database Setup
# ----------------------------
conn = sqlite3.connect("alerts.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS alerts")

cursor.execute("""
CREATE TABLE alerts (
    time TEXT,
    source_ip TEXT,
    prediction TEXT,
    risk TEXT,
    risk_score INTEGER
)
""")

conn.commit()

# ----------------------------
# Risk Mapping
# ----------------------------
def risk_level(label):
    if label == "BENIGN":
        return "LOW", random.randint(0,20)
    elif "DoS" in label or "DDoS" in label:
        return "CRITICAL", random.randint(80,100)
    elif "PortScan" in label or "Brute" in label:
        return "HIGH", random.randint(60,79)
    else:
        return "MEDIUM", random.randint(30,59)

# ----------------------------
# Detection Loop
# ----------------------------
for i in range(len(X_full)):

    row = X_full.iloc[[i]]
    prediction = model.predict(row)
    label = le.inverse_transform(prediction)[0]

    risk, risk_score = risk_level(label)

    fake_ip = f"192.168.1.{np.random.randint(1,255)}"
    current_time = str(datetime.datetime.now())

    cursor.execute("""
    INSERT INTO alerts (time, source_ip, prediction, risk, risk_score)
    VALUES (?, ?, ?, ?, ?)
    """, (current_time, fake_ip, label, risk, risk_score))

    conn.commit()

    print(f"Packet {i+1}: {label} | Risk: {risk} ({risk_score})")

    time.sleep(0.5)

print("✅ Detection Completed")
conn.close()
