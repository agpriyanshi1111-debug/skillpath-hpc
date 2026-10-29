import os
from pathlib import Path
import tempfile

# Point the DB to a temporary path before importing app.main/db connection logic.
import app.db as db
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
db.DB_PATH = Path(_tmp.name)

from fastapi.testclient import TestClient
from app.main import app, startup

client = TestClient(app)

def setup_module():
    # Start with a clean test DB; startup initializes schema and demo profile.
    if db.DB_PATH.exists():
        db.DB_PATH.unlink()
    startup()

def teardown_module():
    try:
        db.DB_PATH.unlink(missing_ok=True)
    except Exception:
        pass

def test_health_and_careers():
    assert client.get("/api/health").status_code == 200
    data = client.get("/api/careers").json()
    assert "AI/ML Engineer" in data["careers"]

def test_demo_profile_dashboard_and_roadmap_persist():
    profile = client.get("/api/profile/1")
    assert profile.status_code == 200
    dashboard = client.get("/api/dashboard/1")
    assert dashboard.status_code == 200
    assert dashboard.json()["total_items"] > 0
    item = dashboard.json()["items"][0]
    patched = client.patch(f"/api/roadmap/items/{item['id']}", json={"status":"in_progress","hours_logged":1.5,"notes":"test note"})
    assert patched.status_code == 200
    again = client.get("/api/roadmap/1").json()["items"]
    found = next(x for x in again if x["id"] == item["id"])
    assert found["status"] == "in_progress"
    assert found["hours_logged"] == 1.5
    assert found["notes"] == "test note"

def test_recommendation_endpoint_and_invalid_input():
    response = client.post("/api/recommendations", json={"profile":{"career_goal":"Web Developer","skills":{}}, "limit":10})
    assert response.status_code == 200
    assert any(x["skill"] == "HTML and CSS" for x in response.json()["recommendations"])
    bad = client.post("/api/recommendations", json={"profile":{"career_goal":"Not Supported"}, "limit":10})
    assert bad.status_code == 422

def test_quiz_returns_questions_and_scores_answers():
    quiz = client.get("/api/quiz")
    assert quiz.status_code == 200
    questions = quiz.json()["questions"]
    assert len(questions) == 5
    result = client.post("/api/quiz", json={"answers": {"q1": 1, "q2": 2, "q3": 2, "q4": 0, "q5": 1}})
    assert result.status_code == 200
    assert result.json()["correct"] == 5
    assert result.json()["suggested_python_level"] == 3
    assert "not a formal" in result.json()["notice"]

def test_completed_skill_updates_gap_and_profile_inventory():
    dashboard = client.get("/api/dashboard/1").json()
    item = next(i for i in dashboard["items"] if i["gap"] > 0)
    response = client.patch(f"/api/roadmap/items/{item['id']}", json={"status": "completed"})
    assert response.status_code == 200
    assert response.json()["current_level"] == response.json()["target_level"]
    assert response.json()["gap"] == 0
    saved = client.get("/api/profile/1").json()
    assert saved["skills"][item["skill"]] == item["target_level"]
