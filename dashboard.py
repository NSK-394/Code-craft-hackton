import streamlit as st
import pandas as pd
import subprocess
import os

st.set_page_config(page_title="API Abuse Detection", layout="wide")

st.title("🚨 API Abuse & Bot Detection Dashboard")

st.write("Behavior Fingerprinting + Risk Scoring + Anomaly Detection")

bot_percent = st.slider(
    "Bot Traffic Percentage",
    min_value=5,
    max_value=90,
    value=30,
    step=5)
if st.button("▶ Run Detection Pipeline"):
    st.write("Running full pipeline...")
    subprocess.run([
    "python",
    "coder1.py",
    str(bot_percent)
])
    subprocess.run(["python", "coder2.py"])
    subprocess.run(["python", "coder3.py"])

    st.success("Pipeline completed")


if os.path.exists("api_behavior_features.csv"):
    df = pd.read_csv("api_behavior_features.csv")

    st.subheader("📊 Behavior Fingerprints Table")
    st.dataframe(df)
    
  

    st.subheader("⚠️ High Risk API Keys")

    risky = df[df["risk_score"] >= 6]

    st.dataframe(risky)

   

    st.subheader("📈 Decision Distribution")

    counts = df["decision"].value_counts()
    st.bar_chart(counts)

else:
    st.info("Run pipeline first to generate data")
