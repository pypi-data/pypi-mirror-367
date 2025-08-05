import pandas as pd
import matplotlib.pyplot as plt
import json
from datetime import datetime

# === Load session log ===
file_path = "drift_journal.jsonl"

# Parse JSONL entries
with open(file_path, "r") as f:
    records = [json.loads(line) for line in f if line.strip()]

df = pd.DataFrame(records)

# Ensure timestamp is datetime
df["timestamp"] = pd.to_datetime(df["timestamp"])

# === Print basic stats ===
total = len(df)
num_drift = df["drift"].sum()
avg_emphasis = df["emphasis_score"].mean()
avg_drift = df[df["drift"] == True]["rationale"].str.extract(r"Δ=([-0-9.]+)").astype(float).mean()[0]

print("\n📊 Drift Journal Summary")
print(f"Total entries: {total}")
print(f"Drift events: {num_drift} ({num_drift/total:.1%})")
print(f"Average emphasis score: {avg_emphasis:.3f}")
print(f"Average Δ for drift entries: {avg_drift:.2f}")

# === Top rationales (if any) ===
print("\n🧠 Top Rationales:")
print(df["rationale"].dropna().value_counts().head())

# === Drift Score Over Time ===
print("\n📈 Plotting drift score over time...")
df_plot = df.copy()
df_plot["drift_score"] = df_plot["rationale"].str.extract(r"Δ=([-0-9.]+)").astype(float)

plt.figure(figsize=(10, 5))
plt.plot(df_plot["timestamp"], df_plot["drift_score"], marker="o", linestyle="-")
plt.axhline(y=0, color="gray", linestyle="--", linewidth=0.5)
plt.title("Drift Score Over Time")
plt.xlabel("Timestamp")
plt.ylabel("Δ Drift Score")
plt.xticks(rotation=45)
plt.tight_layout()
plt.grid(True)
plt.show()