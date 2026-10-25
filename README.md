# SupportIQ AI

AI-assisted support ticket triage. A customer message comes in; the system predicts its **category**, **priority** and **issue topic**, scores **sentiment**, routes it to a **team**, drafts a **reply** for an agent to review, and stores everything for a dashboard.

- **Frontend:** Next.js 14 (App Router, TypeScript, Recharts), deployed on Vercel
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL, deployed on Render
- **ML:** TF-IDF + Logistic Regression / calibrated LinearSVC (scikit-learn), trained in Google Colab
- **Dataset:** [Customer Support Ticket Dataset](https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset) (Kaggle, `suraj520`)

## Repository layout

```
supportiq-ai/
├── frontend/            Next.js app (queue, tickets, new ticket, ticket detail, analytics)
├── backend/             FastAPI app, tests, artifacts/ (trained models go here)
├── ml/train.py          Training script (also embedded in the Colab notebook)
├── notebooks/           01_eda_and_label_check.ipynb, 02_train_and_export.ipynb
├── data/                Put the Kaggle CSV here (git-ignored)
├── docs/                architecture.md, api.md
└── render.yaml          Optional Render blueprint
```

## Step 1: Train the models in Google Colab

1. Upload `notebooks/01_eda_and_label_check.ipynb` to [Colab](https://colab.research.google.com), then **Runtime > Run all**. It downloads the dataset (or asks you to upload the CSV), explores it, and tests whether labels can be predicted from text.
2. Do the same with `notebooks/02_train_and_export.ipynb`. At the end it downloads `supportiq_artifacts.zip`.
3. Unzip it into `backend/artifacts/`. You should have `category_pipeline.joblib`, `priority_pipeline.joblib`, `topic_pipeline.joblib`, `metrics.json` and a `reports/` folder.

The scikit-learn version in Colab must match `backend/requirements.txt` (pinned to 1.6.1; the notebooks install that version). Only load joblib files you trained yourself, because joblib can execute code when loading.

**About the results.** This Kaggle dataset is synthetic. Its priority and type labels often do not depend on the ticket text, so some scores may sit near random guessing. The notebooks and the Analytics page report each score next to a random baseline so you can say this honestly in your README. Urgency rules in the backend and the "needs review" flag keep routing safe regardless.

## Step 2: Run locally

```bash
# backend
cd backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                   # SQLite is used when DATABASE_URL is empty
uvicorn app.main:app --reload --port 8000              # docs at http://localhost:8000/docs
pytest                                                 # optional

# frontend (new terminal)
cd frontend
cp .env.example .env.local
npm install
npm run dev                                            # http://localhost:3000
```

Without model files the API falls back to keyword rules so the interface still works. On the dashboard choose **Load sample tickets** to see it populated.

## Step 3: Push to GitHub

Check that `.env` files and the CSV are not staged (the root `.gitignore` excludes them), then:

```bash
git init
git add .
git commit -m "SupportIQ AI"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/supportiq-ai.git
git push -u origin main
```

Commit the `.joblib` files in `backend/artifacts/` if they are small (a few MB). Do not commit the dataset.

## Step 4: Deploy the backend on Render

1. In [Render](https://dashboard.render.com), create a **PostgreSQL** database. Copy its **Internal** connection string. (Check Render's current free-tier limits; free databases may expire.)
2. **New > Web Service**, connect the repo, and set:

   | Setting | Value |
   |---|---|
   | Root Directory | `backend` |
   | Runtime | Python |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
   | Health Check Path | `/api/health` |

3. Environment variables:

   | Key | Value |
   |---|---|
   | `PYTHON_VERSION` | `3.11.9` |
   | `DATABASE_URL` | the PostgreSQL connection string |
   | `FRONTEND_URL` | your Vercel URL (set after Step 5; no trailing slash) |
   | `LLM_API_KEY` | optional, enables LLM reply drafts |

4. Open `https://YOUR-API.onrender.com/api/health`. It should report `"models_loaded": true`.

Alternative: use `render.yaml` (New > Blueprint), which creates the database and service together.

## Step 5: Deploy the frontend on Vercel

1. [Vercel](https://vercel.com/new) > import the repo. Set **Root Directory** to `frontend`. Framework is detected as Next.js.
2. Add the environment variable `NEXT_PUBLIC_API_URL` = `https://YOUR-API.onrender.com` (no trailing slash).
3. Deploy. Then return to Render and set `FRONTEND_URL` to the Vercel URL, and let the backend redeploy.

Changing an environment variable on Vercel requires a new deployment to take effect. Never put secrets in `NEXT_PUBLIC_` variables.

## Step 6: Verify

- [ ] Frontend loads and the sidebar shows "API online"
- [ ] Submit a ticket, and category, priority, sentiment and team appear
- [ ] Reload the ticket page; it persists
- [ ] Change status, priority and team; edit and save the reply draft
- [ ] Analytics shows charts and the Model quality table
- [ ] An empty message shows a clear validation error

## Troubleshooting

| Symptom | Fix |
|---|---|
| "Cannot reach the API" | Free Render services sleep when idle; wait about a minute and retry |
| Browser CORS error | `FRONTEND_URL` must exactly match your Vercel origin (scheme, no trailing slash) |
| `models_loaded: false` | The `.joblib` files are missing from `backend/artifacts/` in the deployed commit |
| Pickle / version warning | Train with the same scikit-learn version as `requirements.txt` |
| Tickets disappear after redeploy | You are on SQLite. Set `DATABASE_URL` to PostgreSQL |

## Limitations and next steps

- No authentication: anyone with the URL can create or delete tickets. Add login and per-role permissions before using real customer data, and disable `ALLOW_DEMO_SEED`.
- Sentiment is a transparent lexicon, not a trained model.
- Reply drafts are suggestions only and are never sent automatically.
- Ideas: a pretrained sentiment model, confidence-based auto-escalation, feedback-driven retraining, rate limiting.
