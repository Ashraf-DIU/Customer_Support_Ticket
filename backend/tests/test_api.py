import os

os.environ["DATABASE_URL"] = "sqlite:///./test_supportiq.db"

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402
from app.services.routing import escalate_priority, route_department  # noqa: E402
from app.services.sentiment import score_sentiment  # noqa: E402


def test_health_and_ticket_flow():
    with TestClient(app) as c:
        assert c.get("/api/health").json()["status"] == "ok"
        r = c.post("/api/tickets", json={"subject": "Payment deducted", "message": "My payment was deducted but my order was cancelled. Urgent!"})
        assert r.status_code == 201
        t = r.json()
        assert t["priority"] in ("High", "Critical") and t["suggested_reply"]
        assert c.patch(f"/api/tickets/{t['id']}", json={"status": "Resolved"}).json()["status"] == "Resolved"
        assert c.get("/api/tickets?q=payment").json()["total"] >= 1
        assert c.get("/api/analytics").json()["total"] >= 1
        assert c.delete(f"/api/tickets/{t['id']}").status_code == 204


def test_validation():
    with TestClient(app) as c:
        assert c.post("/api/predict", json={"message": "short"}).status_code == 422


def test_rules():
    assert escalate_priority("Low", "this is URGENT")[0] == "High"
    assert escalate_priority("Critical", "urgent")[0] == "Critical"
    assert route_department("Technical issue", "Payment issue") == "Billing Support"
    assert score_sentiment("terrible, nothing works and nobody replies")[0] == "Negative"
