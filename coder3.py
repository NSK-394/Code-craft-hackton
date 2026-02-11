import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("api_behavior_features.csv")

print("Features loaded:", len(df))

model_cols = [
    "requests_per_min",
    "unique_ip_count",
    "endpoint_variety",
    "fail_ratio",
    "risk_score"
]

X = df[model_cols]


scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

model = IsolationForest(
    contamination=0.25,   
    random_state=42
)

model.fit(X_scaled)

df["anomaly_flag"] = model.predict(X_scaled)
df["anomaly_score"] = model.decision_function(X_scaled)

print("Anomaly detection complete")

plt.figure()

normal = df[df.anomaly_flag == 1]
anomaly = df[df.anomaly_flag == -1]

plt.scatter(
    normal["requests_per_min"],
    normal["unique_ip_count"],
    label="Normal"
)

plt.scatter(
    anomaly["requests_per_min"],
    anomaly["unique_ip_count"],
    label="Anomaly"
)

plt.xlabel("Requests per Minute")
plt.ylabel("Unique IP Count")
plt.title("Behavior Anomaly Detection")
plt.legend()
plt.show()

plt.figure()
plt.hist(df["anomaly_score"], bins=20)
plt.title("Anomaly Score Distribution")
plt.xlabel("Score")
plt.ylabel("Count")
plt.show()

df.to_csv("api_behavior_with_anomaly.csv", index=False)

print("\nAnomaly counts:")
print(df["anomaly_flag"].value_counts())
