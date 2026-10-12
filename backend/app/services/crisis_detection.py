
import re
from typing import Any

# Initial prototype only. These patterns are not a validated
# clinical assessment and must not be the sole crisis safeguard.
CRISIS_PATTERNS = {
    "self_harm_or_suicide": [
        r"\bkill myself\b",
        r"\bend my life\b",
        r"\bwant to die\b",
        r"\bdon't want to live\b",
        r"\bdo not want to live\b",
        r"\bsuicid(?:e|al)\b",
        r"\bhurt myself\b",
        r"\bself[- ]harm\b",
        r"\bcan't keep myself safe\b",
        r"\bcannot keep myself safe\b",
        r"\btake all (?:the )?pills\b",
        r"\boverdose\b",
    ],
    "immediate_danger": [
        r"\bsomeone is going to hurt me\b",
        r"\bi am in immediate danger\b",
        r"\b(?:someone|they) (?:is|are) threatening to kill me\b",
    ],
}


def assess_crisis(message: str) -> dict[str, Any]:
    """Return a screening signal for downstream safety handling."""
    normalized = message.lower()
    matched_reasons: list[str] = []

    for reason, patterns in CRISIS_PATTERNS.items():
        if any(re.search(pattern, normalized) for pattern in patterns):
            matched_reasons.append(reason)

    flagged = bool(matched_reasons)

    return {
        "flagged": flagged,
        "risk_tier": "high" if flagged else "none",
        "reasons": matched_reasons,
        "needs_human_review": flagged,
        "method": "prototype_rules_v1",
    }
