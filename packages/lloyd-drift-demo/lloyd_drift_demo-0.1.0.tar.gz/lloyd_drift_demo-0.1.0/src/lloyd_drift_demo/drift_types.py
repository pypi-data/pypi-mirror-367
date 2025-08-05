from dataclasses import dataclass, field
from typing import Optional, List, Tuple

@dataclass
class DriftResult:
    drift_detected: bool
    label: str
    rationale: str
    drift_score: float
    phrase: Optional[str] = None
    polarity: Optional[float] = 0.0
    tone_badge: Optional[str] = None
    tier: Optional[str] = None
    drift: Optional[float] = None  # If you're accessing `.drift` elsewhere

@dataclass
class DriftMemory:
    history: List[Tuple[str, float]] = field(default_factory=list)

    def add(self, text: str, score: float):
        self.history.append((text, score))
        if len(self.history) > 5:
            self.history.pop(0)

    def get_recent(self, n: int = 5) -> List[Tuple[str, float]]:
        return self.history[-n:]