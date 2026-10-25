"""Train SupportIQ models on the Kaggle 'Customer Support Ticket Dataset'.

Usage:
    python ml/train.py --csv data/customer_support_tickets.csv --out backend/artifacts
"""
import argparse
import json
import re
import warnings
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
import sklearn  # noqa: E402
from sklearn.calibration import CalibratedClassifierCV  # noqa: E402
from sklearn.dummy import DummyClassifier  # noqa: E402
from sklearn.feature_extraction.text import TfidfVectorizer  # noqa: E402
from sklearn.linear_model import LogisticRegression  # noqa: E402
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, f1_score  # noqa: E402
from sklearn.model_selection import GroupShuffleSplit  # noqa: E402
from sklearn.pipeline import Pipeline  # noqa: E402
from sklearn.svm import LinearSVC  # noqa: E402

warnings.filterwarnings("ignore")

# task name -> CSV target column
TASKS = {"category": "Ticket Type", "priority": "Ticket Priority", "topic": "Ticket Subject"}
SEED = 42

_PLACEHOLDER = re.compile(r"\{[^}]*\}")
_WS = re.compile(r"\s+")


# --- KEEP IDENTICAL to backend/app/services/preprocessing.py -----------------
def clean_text(text) -> str:
    text = _PLACEHOLDER.sub(" ", str(text))
    return _WS.sub(" ", text).strip().lower()


def build_text(subject, message) -> str:
    return clean_text(f"{subject}. {message}")
# -----------------------------------------------------------------------------


def load_data(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    needed = ["Ticket Subject", "Ticket Description", *TASKS.values()]
    missing = [c for c in needed if c not in df.columns]
    if missing:
        raise SystemExit(f"CSV is missing columns: {missing}. Found: {list(df.columns)}")
    df = df.dropna(subset=needed).copy()
    df["text"] = [build_text(s, d) for s, d in zip(df["Ticket Subject"], df["Ticket Description"])]
    df = df[df["text"].str.len() > 10].drop_duplicates(subset=["text", *TASKS.values()])
    return df.reset_index(drop=True)


def split(df: pd.DataFrame):
    """70/15/15 split. Identical texts always land in the same split (no leakage)."""
    g1 = GroupShuffleSplit(n_splits=1, test_size=0.15, random_state=SEED)
    trainval_idx, test_idx = next(g1.split(df, groups=df["text"]))
    trainval = df.iloc[trainval_idx]
    g2 = GroupShuffleSplit(n_splits=1, test_size=0.1765, random_state=SEED)
    tr, va = next(g2.split(trainval, groups=trainval["text"]))
    return trainval.iloc[tr], trainval.iloc[va], df.iloc[test_idx]


def candidates():
    for ngram in [(1, 1), (1, 2)]:
        for C in (0.5, 2.0, 8.0):
            yield f"logreg(C={C})", ngram, LogisticRegression(C=C, max_iter=2000, class_weight="balanced")
        yield "linear_svc_calibrated", ngram, CalibratedClassifierCV(
            LinearSVC(C=0.5, class_weight="balanced"), cv=3)


def make_pipe(ngram, clf) -> Pipeline:
    return Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=ngram, min_df=2, sublinear_tf=True, strip_accents="unicode")),
        ("clf", clf),
    ])


def train_task(task, column, tr, va, te, out: Path) -> dict:
    ytr, yva, yte = tr[column], va[column], te[column]
    best = (-1.0, None, None, None)
    for name, ngram, clf in candidates():
        pipe = make_pipe(ngram, clf).fit(tr["text"], ytr)
        f1 = f1_score(yva, pipe.predict(va["text"]), average="macro")
        print(f"  [{task}] {name} ngram={ngram}: val macro-F1={f1:.3f}")
        if f1 > best[0]:
            best = (f1, name, ngram, pipe)
    val_f1, name, ngram, pipe = best

    pred = pipe.predict(te["text"])
    test_f1 = f1_score(yte, pred, average="macro")
    acc = accuracy_score(yte, pred)

    base = DummyClassifier(strategy="stratified", random_state=SEED).fit(tr["text"], ytr)
    bpred = base.predict(te["text"])
    base_f1 = f1_score(yte, bpred, average="macro")
    base_acc = accuracy_score(yte, bpred)

    report = classification_report(yte, pred, zero_division=0)
    (out / "reports").mkdir(parents=True, exist_ok=True)
    (out / "reports" / f"{task}_report.txt").write_text(report)
    fig, ax = plt.subplots(figsize=(8, 7))
    ConfusionMatrixDisplay.from_predictions(yte, pred, ax=ax, xticks_rotation=60, colorbar=False)
    ax.set_title(f"{task}: test confusion matrix (macro-F1 {test_f1:.2f})")
    fig.tight_layout()
    fig.savefig(out / "reports" / f"{task}_confusion.png", dpi=130)
    plt.close(fig)

    joblib.dump(pipe, out / f"{task}_pipeline.joblib", compress=3)
    print(f"  [{task}] best={name} {ngram} | test macro-F1={test_f1:.3f} acc={acc:.3f} "
          f"| random baseline F1={base_f1:.3f} acc={base_acc:.3f}")
    return {
        "target_column": column, "classes": [str(c) for c in pipe.classes_],
        "best_model": name, "ngram": list(ngram),
        "val_macro_f1": round(val_f1, 4), "test_macro_f1": round(test_f1, 4), "test_accuracy": round(acc, 4),
        "baseline_macro_f1": round(base_f1, 4), "baseline_accuracy": round(base_acc, 4),
        "above_chance": bool(test_f1 > base_f1 + 0.05),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out", default="artifacts")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    df = load_data(args.csv)
    tr, va, te = split(df)
    print(f"rows={len(df)} train={len(tr)} val={len(va)} test={len(te)}")

    results = {t: train_task(t, col, tr, va, te, out) for t, col in TASKS.items()}
    now = datetime.now(timezone.utc)
    metrics = {
        "version": "tfidf-linear-" + now.strftime("%Y%m%d"),
        "trained_at": now.isoformat(), "sklearn_version": sklearn.__version__,
        "rows": {"total": len(df), "train": len(tr), "val": len(va), "test": len(te)},
        "tasks": results,
    }
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2))
    print("Saved artifacts to", out.resolve())


if __name__ == "__main__":
    main()
