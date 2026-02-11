import pandas as pd
from features import build_features

features = build_features()
print("Feature table created")

LOG_FILE = "api_logs_simulated.csv"   

df = pd.read_csv(LOG_FILE)
df["timestamp"] = pd.to_datetime(df["timestamp"])

print(" Logs loaded:", len(df))
print("Columns:", list(df.columns))

g = df.groupby("api_key")

features = g.agg(
    total_requests=("api_key", "count"),
    failed_requests=("status", lambda x: (x == "FAIL").sum()),
    unique_ip_count=("ip", "nunique"),
    endpoint_variety=("endpoint", "nunique"),
    first_seen=("timestamp", "min"),
    last_seen=("timestamp", "max")
)

features["active_seconds"] = (
    features["last_seen"] - features["first_seen"]
).dt.total_seconds().clip(lower=1)

features["requests_per_min"] = (
    features["total_requests"] /
    (features["active_seconds"] / 60)
)

features["fail_ratio"] = (
    features["failed_requests"] /
    features["total_requests"]
)

features["hour_of_access"] = features["first_seen"].dt.hour

features.reset_index(inplace=True)

print("Feature table created")

def compute_risk(row):
    score = 0

    if row.requests_per_min > 80:
        score += 3

    if row.fail_ratio > 0.30:
        score += 3

    if row.unique_ip_count > 5:
        score += 4

    if row.endpoint_variety > 6:
        score += 2

    if row.hour_of_access < 5 or row.hour_of_access > 23:
        score += 2

    return score


features["risk_score"] = features.apply(compute_risk, axis=1)

def decide(score):
    if score < 3:
        return "ALLOW"
    elif score <= 5:
        return "MONITOR"
    elif score <= 8:
        return "THROTTLE"
    else:
        return "BLOCK"


features["decision"] = features["risk_score"].apply(decide)

label_map = (
    df.groupby("api_key")["traffic_type"]
      .agg(lambda x: x.mode()[0])
)

features["true_type"] = features["api_key"].map(label_map)

detected_bot = features["decision"].isin(["THROTTLE", "BLOCK"])
actual_bot = features["true_type"] == "BOT"

accuracy = (detected_bot == actual_bot).mean()

features.to_csv("api_behavior_features.csv", index=False)

print("\nRisk scoring completed\n")
print(features.head())

print("\nDecision Counts:")
print(features["decision"].value_counts())

print("\nDemo Detection Accuracy:",
      round(accuracy * 100, 2), "%")
