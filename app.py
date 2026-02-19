import streamlit as st
import sqlite3
import pandas as pd
import random
from datetime import datetime
import plotly.express as px

# =====================================================
# CONFIG
# =====================================================
st.set_page_config(page_title="Cyber Threat Detection System", layout="wide")

DB_FILE = "alerts.db"
USERS = {"admin": "admin123"}

# =====================================================
# SESSION STATE
# =====================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# =====================================================
# LOGIN PAGE
# =====================================================
def login():

    st.markdown("""
    <style>
    .stApp {
        background: url("https://images.unsplash.com/photo-1550751827-4bd374c3f58b?auto=format&fit=crop&w=1950&q=80");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }

    .login-container {
        background: rgba(0,0,0,0.8);
        padding: 40px;
        border-radius: 15px;
        width: 400px;
        margin: auto;
        margin-top: 120px;
        color: white;
        box-shadow: 0px 0px 25px rgba(0,255,200,0.4);
    }

    h1 {
        text-align: center;
        color: #00ffcc;
    }

    .stButton>button {
        width: 100%;
        background-color: #00ffcc;
        color: black;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1>🔐 Cyber Security Login</h1>", unsafe_allow_html=True)
    st.markdown('<div class="login-container">', unsafe_allow_html=True)

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user in USERS and USERS[user] == pwd:
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid Credentials")

    st.markdown('</div>', unsafe_allow_html=True)


if not st.session_state.logged_in:
    login()
    st.stop()



# =====================================================
# DATABASE SETUP
# =====================================================
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    time TEXT,
    source_ip TEXT,
    attack_type TEXT,
    risk_level TEXT,
    risk_score INTEGER
)
""")
conn.commit()

# =====================================================
# SIDEBAR
# =====================================================
st.sidebar.title("🛡 Cyber Monitor")
page = st.sidebar.radio("Navigation", ["📊 Dashboard", "🚨 Live Detection"])

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

# =====================================================
# ATTACK SIMULATION FUNCTION
# =====================================================
def generate_attack():
    attacks = {
        "DDoS": 90,
        "Brute Force": 75,
        "Malware": 65,
        "Phishing": 50,
        "Normal Traffic": 10
    }

    attack = random.choice(list(attacks.keys()))
    score = attacks[attack]

    if score >= 80:
        level = "Critical"
    elif score >= 60:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"

    ip = f"192.168.{random.randint(0,255)}.{random.randint(1,254)}"

    return attack, score, level, ip

# =====================================================
# LIVE DETECTION PAGE
# =====================================================
if page == "🚨 Live Detection":

    st.title("🚨 Real-Time Cyber Attack Simulation")

    if st.button("Generate Threat"):

        attack, score, level, ip = generate_attack()

        st.subheader("🔍 Detected Threat")
        st.write(f"Source IP: {ip}")
        st.write(f"Attack Type: {attack}")
        st.write(f"Risk Score: {score}")
        st.write(f"Threat Level: {level}")

        cursor.execute("""
        INSERT INTO alerts (time, source_ip, attack_type, risk_level, risk_score)
        VALUES (?, ?, ?, ?, ?)
        """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
              ip, attack, level, score))
        conn.commit()

        if level == "Critical":
            st.error("🚨 CRITICAL ALERT!")
        elif level == "High":
            st.warning("⚠ HIGH RISK DETECTED")
        else:
            st.success("System Stable")

# =====================================================
# DASHBOARD PAGE
# =====================================================
if page == "📊 Dashboard":

    st.title("📊 Cyber Threat Dashboard")

    df = pd.read_sql_query("SELECT * FROM alerts", conn)

    if df.empty:
        st.info("No alerts yet. Generate threats first.")
    else:
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Alerts", len(df))
        col2.metric("Critical Threats", len(df[df["risk_level"] == "Critical"]))
        col3.metric("High Threats", len(df[df["risk_level"] == "High"]))

        st.markdown("---")

        st.subheader("📈 Risk Level Distribution")
        fig1 = px.pie(df, names="risk_level")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("🧠 Attack Type Frequency")
        attack_counts = df["attack_type"].value_counts().reset_index()
        attack_counts.columns = ["attack_type", "count"]
        fig2 = px.bar(attack_counts, x="attack_type", y="count")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("📊 Risk Score Over Time")
        df["time"] = pd.to_datetime(df["time"])
        fig3 = px.line(df, x="time", y="risk_score")
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")
        st.subheader("📋 Alert Logs")
        st.dataframe(df, use_container_width=True)

        if st.button("🗑 Clear Logs"):
            cursor.execute("DELETE FROM alerts")
            conn.commit()
            st.success("Logs Cleared")
            st.rerun()
