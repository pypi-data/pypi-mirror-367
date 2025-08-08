import sys
from pathlib import Path
import streamlit as st
import pandas as pd
from textblob import TextBlob
import csv
from datetime import datetime
import os

# === Path Setup ===
APP_DIR = Path(__file__).resolve().parent
REPO_ROOT = APP_DIR.parents[4]  # go up to the repo root
SRC_PATH = REPO_ROOT / "src"

# Inject src/ into sys.path so 'lloyd_drift_demo' is importable
sys.path.insert(0, str(SRC_PATH))

# === Import Drift Logic ===
from lloyd_drift_demo.engine.drift_engine import analyze_drift
import lloyd_drift_demo.engine.drift_engine as dbg
print("🔥 Using drift_engine from:", dbg.__file__)

# === Log File ===
OUTPUTS_PATH = APP_DIR.parent / "outputs"
OUTPUTS_PATH.mkdir(parents=True, exist_ok=True)
LOG_FILE = OUTPUTS_PATH / "drift_log.csv"

def compute_slope(history):
    if len(history) < 2:
        return 0.0
    scores = [entry[1] for entry in history]
    indices = list(range(len(scores)))
    n = len(scores)
    x_avg = sum(indices) / n
    y_avg = sum(scores) / n
    numerator = sum((x - x_avg) * (y - y_avg) for x, y in zip(indices, scores))
    denominator = sum((x - x_avg) ** 2 for x in indices)
    return numerator / denominator if denominator else 0.0

def save_drift_log(row):
    log_fields = [
        "timestamp", "baseline", "incoming", "label", "drift_score",
        "tier", "tone_badge", "rationale", "phrase", "polarity"
    ]
    row = {
        "timestamp": datetime.now().isoformat(),
        "baseline": st.session_state.baseline_input,
        "incoming": row.get("phrase", ""),
        **row
    }
    write_header = not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=log_fields)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def get_sentiment_polarity(text: str) -> float:
    return float(getattr(TextBlob(text).sentiment, "polarity", 0.0))

# === UI ===
st.set_page_config(page_title="L.L.O.Y.D. Tone Drift", layout="centered")
st.title("🎛️ L.L.O.Y.D. Tone Drift Analyzer")
st.caption("L.L.O.Y.D. emulates unconscious filtering in language and symbol recognition. The logic can apply to multimodal input.")

# === Baseline Selection ===
st.markdown("#### 🧭 Set the Baseline (Context)")
st.info(
    "🧠 Like in human conversation, tone is measured contextually.\n"
    "Drift Memory tracks tone trajectory to help humanize response. Demo coming soon!"
)
BASELINE_OPTIONS = {
    "Neutral (default)": "Okay.",
    "Friendly": "Thanks again for your help!",
    "Irritated": "Why wasn’t this done earlier?",
    "Warm": "I really appreciate this.",
    "Dismissive": "Whatever. Just do what you want.",
    "Empty/Flat": "Fine.",
    "Polite but tired": "I'm doing fine."
}
labels_with_phrases = [f"{label} → \"{phrase}\"" for label, phrase in BASELINE_OPTIONS.items()]
selection = st.selectbox("Choose baseline tone (and phrase):", labels_with_phrases)
selected_phrase = selection.split("→", 1)[1].strip().strip('"')
st.session_state.baseline_input = selected_phrase

# === Input and Buttons ===
user_input = st.text_area("Enter the new phrase to analyze:", key="incoming_input")

col1, col2 = st.columns([3, 1])
analyze_clicked = col1.button("🔍 Analyze", key="analyze_button")
clear_clicked = col2.button("🧹 Clear Drift Log", key="clear_log_button")

# === Clear Drift Log ===
if clear_clicked:
    if LOG_FILE.exists():
        LOG_FILE.unlink()
        st.success("✅ Drift log has been cleared.")

# === Load drift history and compute slope ===
history_rows = []
if LOG_FILE.exists():
    try:
        df = pd.read_csv(LOG_FILE)
        recent = df.tail(5)
        history_rows = list(zip(recent["incoming"], recent["drift_score"]))
    except Exception as e:
        print("[ERROR] Couldn't load history for slope:", e)

slope = compute_slope(history_rows + [(user_input, get_sentiment_polarity(user_input))])

# === Analyze Input ===
if analyze_clicked:
    if not user_input.strip():
        st.warning("Please enter a phrase to analyze.")
    else:
        print(f"[UI DEBUG] Baseline: '{st.session_state.baseline_input}'")
        print(f"[UI DEBUG] Incoming: '{user_input}'")

        polarity = get_sentiment_polarity(user_input)
        result = analyze_drift(
            st.session_state.baseline_input,
            user_input,
        )

        st.subheader("📊 Drift Analysis")
        st.markdown(f"**Override Label:** `{result.label}`")
        st.markdown(f"**Drift Score:** `{result.drift_score}`")
        st.markdown(f"**Tier:** `{result.tier}`")
        st.markdown(f"**Tone Badge:** `{result.tone_badge}`")
        st.markdown(f"**Rationale:** {result.rationale}")
        st.markdown(f"**Drift Arc Slope:** `{round(slope, 3)}`")

        log_row = {
            "phrase": user_input,
            "label": result.label,
            "drift_score": result.drift_score,
            "tier": result.tier,
            "tone_badge": result.tone_badge,
            "rationale": result.rationale,
            "polarity": polarity
        }
        save_drift_log(log_row)

# === Display Log at Bottom ===
st.markdown("---")
if LOG_FILE.exists():
    try:
        df = pd.read_csv(LOG_FILE)
        if not df.empty:
            st.markdown("### 📜 Drift Log Preview")
            st.dataframe(df[::-1], use_container_width=True)
    except Exception as e:
        st.error("⚠️ Could not read the drift log.")
        print("[ERROR] Log load failed:", e)