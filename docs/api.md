# API

Interactive docs: `/docs` on the running backend.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/health` | Health, DB and model status |
| POST | `/api/predict` | Triage without saving. Body: `{subject, message}` |
| GET | `/api/model-info` | Version and evaluation metrics |
| POST | `/api/tickets` | Triage and save a ticket |
| GET | `/api/tickets` | List. Params: `q, status, priority, category, department, needs_review, open_only, sort, limit, offset` |
| GET | `/api/tickets/{id}` | Ticket details |
| PATCH | `/api/tickets/{id}` | Update `status, priority, department, suggested_reply` |
| DELETE | `/api/tickets/{id}` | Delete |
| POST | `/api/tickets/{id}/suggest-reply` | Regenerate the reply draft |
| GET | `/api/analytics` | Counts and 14-day trend |
| POST | `/api/demo/seed` | Load 8 sample tickets (disable with `ALLOW_DEMO_SEED=false`) |
