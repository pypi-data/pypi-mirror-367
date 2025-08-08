from lloyd_drift_demo.engine.drift_engine import analyze_drift
from lloyd_drift_demo.drift_types import DriftMemory
from lloyd_drift_demo.engine.shared_utils import symbolic_emphasis_score
from lloyd_drift_demo.drift_types import DriftResult

TEST_CASES = {
    "stable": ("AI", "GPT"),
    "symbolic_override": ("We reflect quietly", "There is a sense of awe and wonder."),
    "emphasis_override": ("Ignore that.", "PLEASE LISTEN!!!"),
    "negative_reversal": ("I love this.", "I hate this!"),
    "hedged_response": ("I'm doing fine.", "Maybe not."),
    "mocked_echo": ("I'm fine.", "I SAID I'M FINE!!!"),
    "sarcasm_hint": ("Great job.", "Great job..."),
    "rhetorical_drift": ("You helped a lot.", "You helped a lot?"),
    "negation_amplified": ("I like it.", "I don’t like it."),
    "emoji_override": ("Sure", "Sure 😂😂"),
    "sign_flip_subtle": ("That was okay.", "That was terrible."),
    "rational_hedge_combo": ("It should work.", "I guess it might not."),
    "high_emotion_flip": ("We’re safe.", "WE ARE NOT SAFE!!! 😡"),
}

def print_drift_result(label, baseline, incoming, result):
    print(f"🔹 [{label}]")
    print(f"Baseline : {baseline}")
    print(f"Incoming : {incoming}")
    print(f"Drift    : {result.drift}")
    print(f"Label    : {result.label}")
    print(f"Δ        : {result.drift_score}")
    print(f"Rationale: {result.rationale}")
    print("-" * 30)
    print(f"Badge    : {result.tone_badge}")

def run_all_tests():
    print("\n🧪 LLOYD Drift Test Cases\n" + "-" * 30)
    for label, (baseline, incoming) in TEST_CASES.items():
        result = analyze_drift(baseline, incoming, memory=DriftMemory())
        print_drift_result(label, baseline, incoming, result)