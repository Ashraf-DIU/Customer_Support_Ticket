import json
import logging
from typing import Dict, List, Optional, Tuple

import joblib
import sklearn

from ..config import settings
from .preprocessing import build_text
from .routing import escalate_priority, route_department
from .sentiment import score_sentiment

log = logging.getLogger("supportiq.prediction")

ARTIFACTS = {
    "category": "category_pipeline.joblib",
    "priority": "priority_pipeline.joblib",
    "topic": "topic_pipeline.joblib",
}

# Used only when trained artifacts are missing, so the UI still works during development.
FALLBACK_CATEGORY = [
    ("Refund request", ("refund", "money back", "reimburse")),
    ("Cancellation request", ("cancel", "unsubscribe", "close my account")),
    ("Billing inquiry", ("charge", "invoice", "payment", "billing", "bill")),
    ("Technical issue", ("error", "crash", "not working", "bug", "broken", "connect", "won't", "install")),
]


class PredictionService:
    def __init__(self) -> None:
        self.pipes: Dict[str, object] = {}
        self.metrics: dict = {}

    def load(self) -> None:
        d = settings.model_dir
        for task, fname in ARTIFACTS.items():
            path = d / fname
            if path.exists():
                try:
                    self.pipes[task] = joblib.load(path)  # only load artifacts you trained yourself
                except Exception as exc:  # noqa: BLE001
                    log.error("Could not load %s: %s", path, exc)
        mpath = d / "metrics.json"
        if mpath.exists():
            self.metrics = json.loads(mpath.read_text())
            trained = self.metrics.get("sklearn_version")
            if trained and trained != sklearn.__version__:
                log.warning("Artifacts trained with scikit-learn %s, running %s", trained, sklearn.__version__)
        log.info("Loaded models: %s", list(self.pipes) or "none (using rule fallback)")

    @property
    def ready(self) -> bool:
        return all(t in self.pipes for t in ARTIFACTS)

    @property
    def version(self) -> str:
        return self.metrics.get("version", "trained") if self.ready else "rules-fallback"

    def _top(self, task: str, text: str, k: int = 3) -> Optional[List[Tuple[str, float]]]:
        pipe = self.pipes.get(task)
        if pipe is None:
            return None
        proba = pipe.predict_proba([text])[0]
        ranked = sorted(zip(pipe.classes_, proba), key=lambda x: -x[1])[:k]
        return [(str(label), float(p)) for label, p in ranked]

    def predict(self, subject: str, message: str) -> dict:
        text = build_text(subject, message)
        raw = f"{subject}. {message}"

        cat = self._top("category", text)
        if cat is None:
            label = next((c for c, kws in FALLBACK_CATEGORY if any(k in text for k in kws)), "Product inquiry")
            cat = [(label, 0.0)]
        pri = self._top("priority", text, 1) or [("Medium", 0.0)]
        top = self._top("topic", text, 1) or [("General inquiry", 0.0)]

        priority, reason = escalate_priority(pri[0][0], raw)
        sentiment, sscore = score_sentiment(raw)
        department = route_department(cat[0][0], top[0][0])
        low_conf = (not self.ready) or cat[0][1] < settings.confidence_threshold \
            or (pri[0][1] < settings.confidence_threshold and reason == "Model prediction")

        return {
            "category": cat[0][0],
            "category_confidence": round(cat[0][1], 4),
            "category_alternatives": [{"label": l, "confidence": round(p, 4)} for l, p in cat],
            "priority": priority,
            "priority_confidence": round(pri[0][1], 4),
            "priority_reason": reason,
            "topic": top[0][0],
            "topic_confidence": round(top[0][1], 4),
            "sentiment": sentiment,
            "sentiment_score": sscore,
            "department": department,
            "needs_review": bool(low_conf),
            "model_version": self.version,
        }


predictor = PredictionService()
