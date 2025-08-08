import re
import json
import logging
import difflib
import inspect
import emoji 
from pathlib import Path
from datetime import datetime
from textblob import TextBlob
from typing import Optional, Dict, List, Union
from collections import deque
# In engine/drift_engine.py:
# src/lloyd_drift_demo/engine/drift_engine.py
from lloyd_drift_demo.drift_types import DriftResult, DriftMemory
from lloyd_drift_demo.override_scores import OVERRIDE_WEIGHTS, OVERRIDE_MESSAGES
from lloyd_drift_demo.engine.shared_utils import get_sentiment_polarity

from .shared_utils import (
    get_polarity_score,
    symbolic_emphasis_score,
    detect_symbolic_override,
    is_mocked_echo,
    is_hedge_override,
    is_emphasis_override,
    is_emoji_override,
    is_negation_amplified,
    is_rhetorical_drift,
    has_sarcasm_hint,
    DRIFT_THRESHOLD,
    is_gray_zone_ambiguous,
)
def polarity(text: str) -> str:
    """Basic polarity classifier — returns 'positive', 'negative', or 'neutral'."""
    lower = text.lower()
    if any(word in lower for word in ["love", "like", "enjoy", "great", "wonderful", "good"]):
        return "positive"
    if any(word in lower for word in ["hate", "dislike", "awful", "bad", "terrible", "worse"]):
        return "negative"
    return "neutral"

def shared_root(text1: str, text2: str) -> bool:
    words1 = normalize(text1).split()
    words2 = normalize(text2).split()
    return bool(words1 and words2 and words1[0] == words2[0])

def is_uppercase_yelling(text: str) -> bool:
    return text.isupper() and len(text) > 3

def has_intensifiers(text: str) -> bool:
    intensifiers = [
        "really", "seriously", "actually", "fine", "very",
        "absolutely", "completely", "totally", "so", "extremely",
        "literally", "freaking", "fucking", "insanely", "incredibly"
    ]
    return "!" in text or "?" in text or any(word in text.lower() for word in intensifiers)

ANTONYM_PAIRS = [
    ("love", "hate"),
    ("like", "dislike"),
    ("happy", "sad"),
    ("good", "bad"),
    ("fine", "terrible"),
    ("calm", "angry"),
    ("right", "wrong"),
    ("yes", "no"),
    ("helpful", "useless"),
    ("clean", "dirty"),
]

def is_antonymic_reversal(baseline: str, incoming: str) -> bool:
    base = normalize(baseline).lower().split()
    inc = normalize(incoming).lower().split()
    for a, b in ANTONYM_PAIRS:
        if (a in base and b in inc) or (b in base and a in inc):
            return True
    return False
def is_reversed(baseline: str, incoming: str) -> bool:
    baseline = baseline.lower()
    incoming = incoming.lower()
    return (
        ("like" in baseline and "don’t like" in incoming)
        or ("love" in baseline and "hate" in incoming)
        or ("yes" in baseline and "no" in incoming)
        or ("i" in baseline and "i" in incoming and "not" in incoming)
    )

# ——————————————————
# Config Loader
# ——————————————————
DEFAULT_CONFIG = {
    "POLARITY_THRESHOLD": 0.15,
    "EMPHASIS_OVERRIDE": 1.0,
    "RARE_TAGS": ["lament", "awe", "reverence", "resignation"]
}

def load_config(path: str = "drift_config.json") -> dict:
    if Path(path).is_file():
        with open(path) as f:
            return json.load(f)
    return DEFAULT_CONFIG

config = load_config()
POLARITY_THRESHOLD = config["POLARITY_THRESHOLD"]
EMPHASIS_OVERRIDE = config["EMPHASIS_OVERRIDE"]
RARE_TAGS = set(config["RARE_TAGS"])
ACRONYM_WHITELIST = {"AI", "LLM", "GPT", "NASA", "CPU", "GPU", "URL", "PDF", "API", "SQL"}

# ——————————————————
# Logging Setup
# ——————————————————
logger = logging.getLogger("DriftUtils")
logger.setLevel(logging.INFO)

# ——————————————————
# Text Normalization
# ——————————————————
def normalize(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("\u200b", "")
    text = text.replace("\n", " ").replace("\r", " ")
    text = re.sub(r"[^\w\s']", "", text)
    return re.sub(r"\s+", " ", text)

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"([!?])\1+", r"\1", text)
    text = re.sub(r"\b(\w)\s+\1\b", r"\1", text)
    return text.strip()

# ——————————————————
# Symbolic Tag Stub
# ——————————————————
def expand_symbolic_tags(text: str) -> Optional[str]:
    lowered = text.lower()
    for tag in RARE_TAGS:
        if tag in lowered:
            return "symbolic_" + tag
    return None

# ——————————————————
# Token Heatmap Stub
# ——————————————————
def attach_token_heatmap(text: str) -> Dict[str, List[Dict[str, Union[str, float]]]]:
    tokens = text.split()
    return {
        "tokens": [{"word": tok, "score": round(len(tok) / 10, 2)} for tok in tokens]
    }

# ——————————————————
# Tone badge
# ——————————————————
def compute_tone_badge(label: str, is_drift: bool) -> str:
    if label in OVERRIDE_WEIGHTS:
        return f"🛳 override: {label}"
    if label == "reversal":
        return "☯ reversal"
    if label == "positive":
        return "🔵 positive"
    if label == "negative":
        return "🔴 negative"
    if label == "stable_rationale":
        return "🟡 rationale"
    if label == "stable":
        return "🟢 stable"
    return f"⚪ unknown ({label})"

# ——————————————
# Responsiveness
# ——————————————
def compute_responsiveness(baseline: str, incoming: str, label: str) -> str:
    if label == "mocked_echo":
        return "reactive"
    if label in {"emphasis_override", "emoji_emphasis_override"}:
        if any(char.isupper() for char in incoming) and not is_mirrored(baseline, incoming):
            return "proactive"
    return "neutral"

def is_mirrored(baseline: str, incoming: str) -> bool:
    return normalize(incoming).startswith(normalize(baseline)) or \
           difflib.SequenceMatcher(None, normalize(baseline), normalize(incoming)).ratio() > 0.85

def compute_slope(pairs: list[tuple[str, float]]) -> float:
    if len(pairs) < 2:
        return 0.0
    values = [score for _, score in pairs]
    diffs = [b - a for a, b in zip(values, values[1:])]
    return sum(diffs) / len(diffs)

# ——————————————
# Override Conditions
# ——————————————
def is_mocked_echo(baseline: str, incoming: str) -> bool:
    norm_base = normalize(baseline)
    norm_inc = normalize(incoming)

    score_base = compute_emphasis_score(baseline)
    score_inc = compute_emphasis_score(incoming)

    return norm_base == norm_inc and (score_inc - score_base > 0.5)

def has_sarcasm_hint(incoming: str) -> bool:
    return incoming.strip().endswith("...") or "/s" in incoming.lower()

def is_negation_amplified(baseline: str, incoming: str) -> bool:
    negators = r"\b(not|don’t|never|no|nothing|can't|won't|n't)\b"
    return shared_root(baseline, incoming) and bool(re.search(negators, incoming.lower()))

def is_emphasis_override(baseline: str, incoming: str) -> bool:
    return is_uppercase_yelling(incoming) or "!!" in incoming or "???" in incoming

def is_emoji_override(baseline: str, incoming: str) -> bool:
    count = sum(1 for char in incoming if emoji.is_emoji(char))
    return count >= 2

def is_hedge_override(baseline: str, incoming: str) -> bool:
    return any(p in incoming.lower() for p in ["maybe", "perhaps", "kind of", "sort of", "i guess", "i think"])

def is_rhetorical_drift(baseline: str, incoming: str) -> bool:
    return incoming.strip().endswith("?") and shared_root(baseline, incoming)

def is_sign_flip(baseline: str, incoming: str) -> bool:
    base_score = compute_polarity_score(baseline)
    inc_score = compute_polarity_score(incoming)
    return base_score * inc_score < 0 and abs(base_score - inc_score) < 0.3

def is_hostile_emphasis(baseline: str, incoming: str) -> bool:
    incoming_lower = incoming.lower()
    hostile_terms = [
        "disgusted", "garbage", "trash", "hate", "worthless",
        "awful", "literally", "useless", "ruined", "terrible",
        "fuming", "furious", "crap", "filth", "shit", "junk"
    ]

    # Style 1: Intensified hostile language
    hostile_by_emphasis = (
        compute_polarity_score(incoming) <= -0.5 and
        any(term in incoming_lower for term in hostile_terms) and
        (has_intensifiers(incoming) or "!" in incoming)
    )

    # Style 2: Short hostile evaluation using linking verbs
    linking_verbs = ["is", "are", "you're", "you are", "this is", "that is"]
    short_phrase = len(incoming.split()) <= 6
    is_structural_eval = (
        any(verb in incoming_lower for verb in linking_verbs) and
        any(term in incoming_lower for term in hostile_terms) and
        (short_phrase or "!" in incoming)
    )

    return hostile_by_emphasis or is_structural_eval

# ——————————————
# Drift Analyzer Core
# ——————————————
def compute_emphasis_score(text: str) -> float:
    caps = sum(1 for c in text if c.isupper())
    excl = text.count("!")
    qmark = text.count("?")
    emoji_count = len(re.findall(r"[😂🤣😡😢😍😭❤️]", text))
    return 0.3 * caps + 0.5 * excl + 0.5 * qmark + 0.5 * emoji_count

def compute_polarity_score(text: str) -> float:
    return float(getattr(TextBlob(text).sentiment, "polarity", 0.0) or 0.0)

def analyze_drift(baseline: str, incoming: str, memory: Optional[DriftMemory] = None, verbose: bool = False) -> DriftResult:
    base_score = compute_emphasis_score(baseline)
    inc_score = compute_emphasis_score(incoming)
    drift_score = inc_score - base_score

    candidates = []

    if is_reversed(baseline, incoming) and ("I" in incoming or "we" in incoming):
        candidates.append(("reversal", 100, "Polarity reversal detected with strong personal negation."))

    if is_antonymic_reversal(baseline, incoming):
        candidates.append((
        "reversal",
        100,
        "Incoming reverses polarity of baseline with strong antonymic contrast."
    ))

    if is_mocked_echo(baseline, incoming):
        # Optional reassertion signal
        if is_uppercase_yelling(incoming) or has_intensifiers(incoming):
            candidates.append((
                "reasserted_escalation",
                OVERRIDE_WEIGHTS["reasserted_escalation"],
                OVERRIDE_MESSAGES["reasserted_escalation"]
            ))

    # Compute slope (memory-aware or fallback)
        if memory and memory.history:
            recent_history = memory.get_recent()
            incoming_score = get_sentiment_polarity(incoming)
            slope = compute_slope(recent_history + [(incoming, incoming_score)])
        else:
            slope = 0.0

    # Apply gray zone override or fallback to mocked_echo
        if is_gray_zone_ambiguous(baseline, incoming, slope):
            candidates.append((
                "gray_zone_ambiguous",
                85,
                "Ambiguous symbolic collapse phrase with directional slope detected."
            ))
        else:
            candidates.append((
                "mocked_echo",
                OVERRIDE_WEIGHTS["mocked_echo"],
                OVERRIDE_MESSAGES["mocked_echo"]
            ))
    if is_sign_flip(baseline, incoming):
        candidates.append(("sign_flip", OVERRIDE_WEIGHTS["sign_flip"], "Polarity sign-flip detected"))
    if is_rhetorical_drift(baseline, incoming):
        candidates.append(("rhetorical_drift", OVERRIDE_WEIGHTS["rhetorical_drift"], OVERRIDE_MESSAGES["rhetorical_drift"]))
    if has_sarcasm_hint(incoming):
        candidates.append(("sarcasm_hint", OVERRIDE_WEIGHTS["sarcasm_hint"], OVERRIDE_MESSAGES["sarcasm_hint"]))
    if is_emphasis_override(baseline, incoming) and not is_mirrored(baseline, incoming):
        candidates.append(("emphasis_override", OVERRIDE_WEIGHTS["emphasis_override"], OVERRIDE_MESSAGES["emphasis_override"]))
    if is_emoji_override(baseline, incoming):
        candidates.append(("emoji_emphasis_override", OVERRIDE_WEIGHTS["emoji_emphasis_override"], OVERRIDE_MESSAGES["emoji_emphasis_override"]))
    if is_hedge_override(baseline, incoming):
        candidates.append(("stable_rationale", OVERRIDE_WEIGHTS["stable_rationale"], OVERRIDE_MESSAGES["stable_rationale"]))
    if is_negation_amplified(baseline, incoming):
        candidates.append(("negation_amplified", OVERRIDE_WEIGHTS["negation_amplified"], OVERRIDE_MESSAGES["negation_amplified"]))
    if is_hostile_emphasis(baseline, incoming):
        candidates.append(("hostile_emphasis", OVERRIDE_WEIGHTS["hostile_emphasis"], OVERRIDE_MESSAGES["hostile_emphasis"]))


    if candidates:
        if verbose:
            print(f"Override candidates: {[c[0] for c in candidates]}")
            for label_debug, score_debug, rationale_debug in candidates:
                print(f"↳ Candidate: {label_debug} | Score: {score_debug} | Rationale: {rationale_debug}")

    # Select the override with the highest score
        label, score, rationale = max(candidates, key=lambda x: x[1])

    else:
        polarity_changed = polarity(baseline) != polarity(incoming)
        if polarity_changed:
            label = "reversal"
            score = 100.0
            rationale = "Polarity reversal detected with strong antonymic contrast."
        else:
            score = inc_score - base_score
            label = "stable"
            rationale = f"Polarity shift within tolerance (Δ={round(score, 2)})"

    drift = score >= 70
    responsiveness = compute_responsiveness(baseline, incoming, label)

    if memory:
        memory.add(incoming, score)

    return DriftResult(
        drift_detected=True,
        drift=drift,
        label=label,
        rationale=rationale,
        drift_score=round(score, 2),
        tone_badge=compute_tone_badge(label, drift),
        tier = str(int(score) // 10)
    )
    
# ——————————————
# Drift Journal Logger
# ——————————————
def log_drift_result(baseline: str, incoming: str, result: DriftResult, heatmap: dict, path: Optional[str] = None):
    if not path:
        return
    entry = {
        "timestamp": datetime.now().isoformat(),
        "baseline": baseline,
        "incoming": incoming,
        "result": {
            "label": result.label,
            "rationale": result.rationale,
            "drift_score": result.drift_score
        },
        "heatmap": heatmap
    }
# ——————————————————
# Compatibility: analyze_phrase + analyze_chunks for Streamlit
# ——————————————————
def analyze_phrase(phrase: str, simulated_polarity: Optional[float] = None) -> dict:
    polarity_score = simulated_polarity if simulated_polarity is not None else compute_polarity_score(phrase)
    dummy_baseline = "I’m doing fine."  # Placeholder for real conversational context
    memory = DriftMemory()  # Dummy memory for now

    result = analyze_drift(dummy_baseline, phrase, memory=memory)

    # Response polarity direction
    delta = polarity_score - get_polarity_score(dummy_baseline)
    response_polarity = polarity_score - (delta * 0.5)
    response_label = "Neutral"
    if response_polarity > 0.5:
        response_label = "Warm"
    elif response_polarity > 0.2:
        response_label = "Supportive"
    elif response_polarity < -0.5:
        response_label = "Cold"
    elif response_polarity < -0.2:
        response_label = "Guarded"

    return {
        "input": phrase,
        "polarity": round(polarity_score, 3),
        "closest_tone": result.label,
        "drift_score": result.drift_score,
        "status": "Flagged" if result.drift else "Stable",
        "delta": round(delta, 3),
        "response_polarity": round(response_polarity, 3),
        "response_label": response_label
    }

def analyze_chunks(text: str) -> list:
    chunks = re.split(r"(?<=[.!?])\s+|,|\band\b|\bor\b", text)
    results = []
    dummy_baseline = "I’m doing fine."

    for chunk in chunks:
        chunk = chunk.strip()
        if not chunk:
            continue

        polarity_score = compute_polarity_score(chunk)
        result = analyze_drift(dummy_baseline, chunk)
        results.append({
            "chunk": chunk,
            "polarity": round(polarity_score, 3),
            "closest_tone": result.label,
            "drift_score": result.drift_score,
            "status": "Flagged" if result.drift else "Stable"
        })

    return results
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")