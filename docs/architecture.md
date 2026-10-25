# Architecture

```
Browser (Next.js on Vercel)
   |  HTTPS, NEXT_PUBLIC_API_URL
   v
FastAPI (Render) ──> PostgreSQL (tickets, predictions, status)
   |
   ├─ services/prediction.py   TF-IDF pipelines (category, priority, topic) loaded from backend/artifacts
   ├─ services/sentiment.py    lexicon sentiment scorer
   ├─ services/routing.py      urgency escalation + department routing rules
   └─ services/reply.py        template reply, or LLM draft when LLM_API_KEY is set
```

## Ticket flow
1. `POST /api/tickets` validates input, cleans text, runs the three pipelines.
2. Rules may raise (never lower) priority when the customer states explicit urgency. The reason is stored.
3. Predictions under `CONFIDENCE_THRESHOLD` set `needs_review`.
4. A reply draft is generated. An agent reviews it. Nothing is sent automatically.

## Training
`ml/train.py` (also run by `notebooks/02_train_and_export.ipynb`): grouped 70/15/15 split so identical texts never
cross splits, model selection on validation, a single test evaluation, and a random-guessing baseline reported
next to every score in `metrics.json`.
