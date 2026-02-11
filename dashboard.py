import streamlit as st
import pandas as pd
import subprocess
import os
import matplotlib.pyplot as plt
from score_store import score_history

st.set_page_config(page_title="API Abuse Detection", layout="wide")

st.title("🚨 API Abuse & Bot Detection Dashboard")
st.write("Behavior Fingerprinting + Risk Scoring + Anomaly Detection")

# -----------------------------
# BOT RATIO CONTROL
# -----------------------------
bot_percent = st.slider(
    "Bot Traffic Percentage",
    min_value=5,
    max_value=90,
    value=30,
    step=5
)

# -----------------------------
# RUN PIPELINE
# -----------------------------
if st.button("▶ Run Detection Pipeline"):
    st.info("Running pipeline stages...")
    subprocess.run(["python", "coder1.py", str(bot_percent)])
    subprocess.run(["python", "coder2.py"])
    subprocess.run(["python", "coder3.py"])
    st.success("Pipeline completed")

# -----------------------------
# LOAD FEATURES
# -----------------------------
if os.path.exists("api_behavior_features.csv"):

    df = pd.read_csv("api_behavior_features.csv")

    # ===== Summary Metrics =====
    st.subheader("📌 System Summary")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total API Keys", len(df))
    c2.metric("Blocked", (df["decision"] == "BLOCK").sum())
    c3.metric("Monitor", (df["decision"] == "MONITOR").sum())
    c4.metric("Allowed", (df["decision"] == "ALLOW").sum())

    # ===== Table =====
    st.subheader("📊 Behavior Fingerprints Table")
    st.dataframe(df)

    # ===== Risky Keys =====
    st.subheader("⚠️ High Risk API Keys")
    st.dataframe(df[df["risk_score"] >= 6])

    # ===== Decision Charts =====
    st.subheader("📈 Decision Distribution")
    counts = df["decision"].value_counts()
    st.bar_chart(counts)

    st.subheader("🥧 Decision Breakdown (Pie)")
    fig, ax = plt.subplots()
    ax.pie(counts.values, labels=counts.index, autopct="%1.1f%%")
    st.pyplot(fig)

    # ===== Anomaly Score Line =====
    if "anomaly_score" in df.columns:
        st.subheader("🧪 Anomaly Score Distribution")
        st.line_chart(df["anomaly_score"])

    # ===== Saved coder3 graphs =====
    st.subheader("🧠 Isolation Forest Visuals")

    if os.path.exists("anomaly_scatter.png"):
        st.image("anomaly_scatter.png", caption="Anomaly Scatter")

    if os.path.exists("anomaly_bar.png"):
        st.image("anomaly_bar.png", caption="Anomaly Bar")

    # ===== Explainability Panel =====
    st.subheader("🔍 Inspect API Key")

    selected_key = st.selectbox(
        "Select API Key",
        df["api_key"].unique()
    )

    if selected_key:
        row = df[df["api_key"] == selected_key].iloc[0]

        explain_cols = [
        "requests_per_min",
        "fail_ratio",
        "unique_ip_count",
        "endpoint_variety",
        "risk_score",
        "decision"
    ]


        explain_data = {c: row[c] for c in explain_cols if c in df.columns}
        st.json(explain_data)

        # ===== Score History Trend =====
        if selected_key in score_history:
            st.subheader("📉 Anomaly Score Trend")
            st.line_chart(list(score_history[selected_key]))

else:
    st.info("Run pipeline first to generate behavior features")

# -----------------------------
# STEP 6 EXPERIMENT RESULTS
# -----------------------------
if os.path.exists("ratio_results.csv"):

    exp_df = pd.read_csv("ratio_results.csv")

    st.subheader("🎯 Detection vs Bot Ratio Experiments")
    st.line_chart(exp_df.set_index("ratio"))
