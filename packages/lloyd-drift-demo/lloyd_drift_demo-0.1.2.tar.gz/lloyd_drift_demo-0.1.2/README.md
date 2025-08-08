# L.L.O.Y.D. — Language Layers Over Your Data

A symbolic drift detection and tone deviation engine that listens like a human would — tracking not just sentiment, but **meaning breaks**, **symbolic conflict**, and **emotional escalation**.

---

### 🔗 Try It Now

- 📦 **Install via PyPI:**  
  `pip install lloyd-drift-demo==0.1.0`  
  [→ View on PyPI](https://pypi.org/project/lloyd-drift-demo/)

- 🌐 **Live Demo (Streamlit):**  
  [https://tinyurl.com/Lloyd-demo](https://tinyurl.com/Lloyd-demo)

---

## 🔍 What Is LLOYD?

LLOYD isn’t another sentiment classifier.  
It’s a drift-aware analyzer that tells you when **a conversation turns** — emotionally, symbolically, or relationally.

From sarcastic reversals to performative breakdowns, LLOYD is designed to detect subtle shifts in tone that traditional NLP often misses.

> ✅ *Calibration is limited, but customizable.*  
> LLOYD is lightly tuned, but designed for adaptation to domain-specific tone models.

> ✅ *Work-in-progress with feedback welcome.*  
> This is an active project — contributions, questions, and use-case tests are encouraged.  
> Contact: [putmanmodel@pm.me](mailto:putmanmodel@pm.me)

---

## ✨ What Makes It Different?

### 🧱 How LLOYD Compares: Above the Stack

LLOYD doesn’t just label tone — it listens like a person, tracking symbolic shifts, emotional slope, and layered meaning.

Here’s how it stacks up:

| Tier            | Model Type            | Capabilities                                  | Notes                                                  |
|-----------------|-----------------------|-----------------------------------------------|--------------------------------------------------------|
| 🟩 **LLOYD**     | Symbolic Drift Engine | Emotional drift scoring, override logic, symbolic pattern detection, sarcasm flags, badges | ✅ Built for human-level nuance and meaning tracking   |
| 🟨 Mid-Level     | Sentiment Classifier  | Polarity scoring, intensity detection         | ⚠️ Misses sarcasm, symbolic shifts, escalation cues     |
| 🟥 Legacy        | Keyword Matcher       | Token triggers, emotion word lists            | ❌ Fails on nuance, symbolic inversion, or context      |

> 🟢 *LLOYD hears the difference between “Great job” and “Great job…”*  
> 🔴 *Others just check for “positive” or “negative.”*

> **Please note**: LLOYD is already scaffolded for *Drift Memory* and short-term tone weighting —  
> this table excludes those in-progress features until the official demo drops.

✨ *It’s better — and it’s not even done yet.*

- Symbolic override detection (`"Great job…"`, `"You helped?"`)
- Emphasis escalation tracking (`ALL CAPS`, `!!!`, emoji floods)
- Drift memory modeling to detect emotional pressure buildup
- Mirror match and mocked echo detection
- Output includes rationale, badge label, override label

---

## 🧪 Quick Start

```bash
pip install lloyd-drift-demo==0.1.0
python devtools/run.py
```

Sample output:

```
Badge    : 🛳 override: emphasis_override
🔹 [sarcasm_hint]
Baseline : Great job.
Incoming : Great job...
Drift    : True
Label    : sarcasm_hint
Δ        : 80
Rationale: Trailing or embedded sarcasm marker detected.
```

---

## 🌐 Streamlit GUI

Launch the visual interface:

```bash
streamlit run devtools/sandbox_demo/app/app.py
```

Try this real example:

```
Baseline : Why wasn’t this done earlier?
Incoming : You are garbage.
Drift    : True
Label    : hostile_emphasis
Δ        : 92
Badge    : 🛳 override: hostile_emphasis
Rationale: Intensified hostile language detected — override triggered.
```
```text
Baseline : Why wasn’t this done earlier?
Incoming : I had to take out the garbage.
Drift    : False
Label    : neutral
Δ        : 5
Badge    : none
Rationale: No drift detected — response remains within expected symbolic frame.
```

---

## 📊 Drift Graph — Tone Shift Over Time

![Drift Graph](media/graph.png)

This plot captures real drift data across a conversation, showing:

- Δ tone changes turn by turn  
- Sudden spikes in emotional pressure  
- Contextual difference between neutral and hostile replies  
- Future use of short-term memory to weight recent drift and override impact

---

## 🧠 Coming Soon — Drift Memory + Field Responsiveness Demo

Scaffolding is already in place for a future interactive demo that showcases:

- Short-term memory tracking across turns
- Escalation detection (e.g., passive → sarcastic → hostile)
- Override arbitration with memory decay
- Field responsiveness (proactive vs. reactive tone shifts)

Prototype logic lives in:

```
src/lloyd_drift_demo/engine/drift_memory.py
```

---

## 🛠 Drift Thresholds (Tunable)

Users can modify:

- `DRIFT_THRESHOLD` (default = 0.15)
- Emphasis override sensitivity
- Symbolic override rules

Feedback is welcome for future tuning.

---

## 💡 Tip: Use ChatGPT as a Temporary Code Lab Assistant

You can copy and paste full Python files into ChatGPT to get live analysis, refactors, and debugging help — just like a pair programmer.

✅ Totally legal — as long as it’s your code (or permissively licensed)  
✅ Session-aware — ChatGPT can remember your pasted files for the whole conversation  
✅ No training risk — Your code stays private; nothing is used to train the model

⚠️ Session memory resets when you refresh, log out, or start a new chat  
⚠️ Don’t paste private or proprietary code unless you’re sure it’s safe

---

## 🗂 Project Structure

```
📁 LLOYD_Language_Engine/
├── README.md
├── media/
│   └── graph.png
├── src/
│   └── lloyd_drift_demo/
│       └── engine/
│           └── drift_utils_v2.py
├── demos/
│   └── sandbox_demo/
│       └── app/
│           └── app.py
```

---

## 📦 Requirements

- Python 3.11+
- `pip install -r requirements.txt`

---

## 🤝 Contribute or Collaborate

This is an active research project.  
Feedback, testing, and conceptual contributions welcome.

📬 Contact: [putmanmodel@pm.me](mailto:putmanmodel@pm.me)  
🧵 Twitter/Reddit: [@putmanmodel](https://twitter.com/putmanmodel)

---

## 📚 Credits

- Built on top of the excellent [GoEmotions dataset](https://github.com/google-research/google-research/tree/master/goemotions) from Google Research  
- Special thanks to the community at [r/datasets](https://www.reddit.com/r/datasets) for sharing valuable resources and inspiration  
- And to **Lloyd**, my brother — whom I *"accidentally"* named this project after

---

## 📜 License

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)  
Use, modify, and remix freely — just don’t sell it.

> “Most sentiment systems end with polarity.  
> LLOYD starts with meaning.”
