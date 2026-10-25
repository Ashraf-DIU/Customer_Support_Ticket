"""Small transparent lexicon sentiment scorer (no model download, runs on a free tier)."""
import re
from typing import Tuple

NEGATIVE = {
    "angry", "terrible", "awful", "worst", "unacceptable", "frustrated", "frustrating", "disappointed",
    "useless", "broken", "failed", "fail", "ridiculous", "horrible", "annoyed", "annoying", "error",
    "problem", "issue", "crash", "crashes", "lost", "stolen", "wrong", "bad", "poor", "slow", "waste",
    "stuck", "unable", "cannot", "can't", "doesn't", "didn't", "won't", "damaged", "defective", "refund",
    "cancel", "unresponsive", "overcharged", "charged", "nobody", "never", "urgent", "worse", "complaint",
}
POSITIVE = {
    "thanks", "thank", "great", "love", "excellent", "happy", "awesome", "perfect", "helpful",
    "appreciate", "good", "amazing", "pleased", "wonderful", "fantastic", "satisfied",
}
PHRASES_NEG = ("not working", "no response", "still waiting", "no one", "stopped working", "fed up")


def score_sentiment(text: str) -> Tuple[str, float]:
    low = text.lower()
    words = re.findall(r"[a-z']+", low)
    neg = sum(w in NEGATIVE for w in words) + 2 * sum(p in low for p in PHRASES_NEG)
    pos = sum(w in POSITIVE for w in words)
    score = (pos - neg) / (pos + neg + 2)
    label = "Negative" if score < -0.15 else "Positive" if score > 0.15 else "Neutral"
    return label, round(score, 3)
