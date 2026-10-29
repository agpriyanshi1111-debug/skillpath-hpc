from __future__ import annotations
import json
import os
import platform
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from . import db
from .data import CAREERS, get_career_data, validate_dataset
from .recommender import recommend, generate_roadmap, normalize_profile

def startup():
    db.init_db()
    validate_dataset()
    seed_demo()

@asynccontextmanager
async def lifespan(app: FastAPI):
    startup()
    yield

app = FastAPI(
    title="SkillPath API",
    description="Explainable personalized skill development recommendation system for HPC PBL.",
    version="1.0.0",
    lifespan=lifespan,
)
STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class ProfileInput(BaseModel):
    id: int | None = None
    name: str = Field(default="Demo Student", min_length=1, max_length=80)
    career_goal: str = Field(min_length=1, max_length=100)
    education_level: str = Field(default="Undergraduate", max_length=80)
    branch: str = Field(default="B.Tech CSE-AI", max_length=100)
    semester: int = Field(default=3, ge=1, le=12)
    interests: list[str] = Field(default_factory=list, max_length=20)
    skills: dict[str, Any] = Field(default_factory=dict)
    hours_per_week: float = Field(default=5, ge=1, le=80)
    timeframe_weeks: int = Field(default=12, ge=1, le=260)
    learning_format: str = Field(default="Mixed", max_length=40)
    focus_skills: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("name", "career_goal")
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError("This field cannot be blank.")
        return value.strip()

class RecommendationRequest(BaseModel):
    profile: ProfileInput
    limit: int = Field(default=12, ge=1, le=50)

class RoadmapRequest(BaseModel):
    profile: ProfileInput
    limit: int = Field(default=12, ge=1, le=50)


QUIZ_QUESTIONS = [
    {"id": "q1", "question": "Which Python type stores an ordered, mutable sequence?", "options": ["tuple", "list", "set", "str"], "answer": 1, "explanation": "A list is ordered and mutable."},
    {"id": "q2", "question": "What does a function return when it reaches the end without a return statement?", "options": ["0", "False", "None", "An error every time"], "answer": 2, "explanation": "Python functions return None by default."},
    {"id": "q3", "question": "Which construct is commonly used to handle an exception?", "options": ["if/else", "for/in", "try/except", "def/class"], "answer": 2, "explanation": "try/except handles exceptions."},
    {"id": "q4", "question": "What is the average lookup complexity of a dictionary key?", "options": ["O(1)", "O(n)", "O(n²)", "Always O(log n)"], "answer": 0, "explanation": "Dictionary lookup is average O(1), with worst-case caveats."},
    {"id": "q5", "question": "Why split data into training and test sets in machine learning?", "options": ["To make every model accurate", "To estimate performance on unseen data", "To remove all missing values", "To guarantee causation"], "answer": 1, "explanation": "A held-out test set helps estimate generalization."},
]

class QuizSubmission(BaseModel):
    answers: dict[str, int] = Field(default_factory=dict)

class ProgressPatch(BaseModel):
    status: str | None = None
    hours_logged: float | None = Field(default=None, ge=0, le=100000)
    notes: str | None = Field(default=None, max_length=2000)
    current_level: int | None = Field(default=None, ge=0, le=3)

def seed_demo():
    with db.connect() as conn:
        row = conn.execute("SELECT id FROM profiles ORDER BY id LIMIT 1").fetchone()
    if row:
        return
    demo = {
        "name": "Demo Student", "career_goal": "AI/ML Engineer", "education_level": "Undergraduate",
        "branch": "B.Tech CSE-AI", "semester": 3, "interests": ["python", "ai", "data"],
        "skills": {"Python Programming": "beginner", "SQL and Data Storage": "beginner"},
        "hours_per_week": 6, "timeframe_weeks": 16, "learning_format": "Mixed", "focus_skills": []
    }
    profile = db.save_profile(demo)
    roadmap = generate_roadmap(profile, limit=12)
    db.save_roadmap(profile["id"], roadmap)

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "project": "SkillPath", "database": "SQLite", "dataset_rows": len(__import__("app.data", fromlist=["CAREER_DATA"]).CAREER_DATA)}

@app.get("/api/careers")
def careers():
    return {"careers": CAREERS}

@app.get("/api/skills")
def skills(career: str):
    rows = get_career_data(career)
    if not rows:
        raise HTTPException(404, "Career not found in the starter knowledge base.")
    return {"career": career, "skills": rows}

@app.get("/api/quiz")
def get_quiz():
    return {"title": "Python and ML foundations check", "notice": "Indicative self-check only; this is not a formal assessment or certification.",
            "questions": [{k: q[k] for k in ("id", "question", "options")} for q in QUIZ_QUESTIONS]}

@app.post("/api/quiz")
def submit_quiz(payload: QuizSubmission):
    known = {q["id"] for q in QUIZ_QUESTIONS}
    if set(payload.answers) - known:
        raise HTTPException(422, "Submission contains an unknown question ID.")
    if any(not isinstance(v, int) or v < 0 or v > 3 for v in payload.answers.values()):
        raise HTTPException(422, "Each answer must be an option index from 0 to 3.")
    answered = len(payload.answers)
    correct = sum(payload.answers.get(q["id"]) == q["answer"] for q in QUIZ_QUESTIONS)
    pct = round(100 * correct / len(QUIZ_QUESTIONS))
    suggested_level = 1 if pct < 40 else 2 if pct < 80 else 3
    explanations = [{"question_id": q["id"], "correct": payload.answers.get(q["id"]) == q["answer"],
                    "correct_answer": q["options"][q["answer"]], "explanation": q["explanation"]} for q in QUIZ_QUESTIONS]
    return {"answered": answered, "total": len(QUIZ_QUESTIONS), "correct": correct, "score_percent": pct,
            "suggested_python_level": suggested_level, "level_label": {1: "Beginner", 2: "Intermediate", 3: "Advanced"}[suggested_level],
            "explanations": explanations, "notice": "Indicative self-check only; not a formal assessment or certification."}

@app.get("/api/profile/{profile_id}")
def read_profile(profile_id: int):
    profile = db.get_profile(profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found.")
    return profile

@app.post("/api/profile")
def create_or_update_profile(payload: ProfileInput):
    try:
        profile = normalize_profile(payload.model_dump())
        saved = db.save_profile({**payload.model_dump(), **profile})
        return saved
    except ValueError as exc:
        raise HTTPException(422, str(exc))

@app.post("/api/recommendations")
def get_recommendations(payload: RecommendationRequest):
    try:
        return {"recommendations": recommend(payload.profile.model_dump(), payload.limit)}
    except ValueError as exc:
        raise HTTPException(422, str(exc))

@app.post("/api/roadmap/generate")
def create_roadmap(payload: RoadmapRequest):
    try:
        normalized = normalize_profile(payload.profile.model_dump())
        profile = db.save_profile({**payload.profile.model_dump(), **normalized})
        roadmap = generate_roadmap(normalized, payload.limit)
        db.save_roadmap(profile["id"], roadmap)
        return {"profile": profile, "roadmap": roadmap, "items": db.get_roadmap(profile["id"])}
    except ValueError as exc:
        raise HTTPException(422, str(exc))

@app.get("/api/roadmap/{profile_id}")
def read_roadmap(profile_id: int):
    profile = db.get_profile(profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found.")
    return {"profile_id": profile_id, "items": db.get_roadmap(profile_id)}

@app.patch("/api/roadmap/items/{item_id}")
def patch_progress(item_id: int, payload: ProgressPatch):
    patch = {k: v for k, v in payload.model_dump().items() if v is not None}
    try:
        row = db.update_roadmap_item(item_id, patch)
    except ValueError as exc:
        raise HTTPException(422, str(exc))
    if not row:
        raise HTTPException(404, "Roadmap item not found.")
    result = dict(row)
    result["prerequisites"] = json.loads(result.pop("prerequisites_json"))
    return result

@app.get("/api/dashboard/{profile_id}")
def dashboard(profile_id: int):
    result = db.get_dashboard(profile_id)
    if not result:
        raise HTTPException(404, "Profile not found.")
    return result

def _benchmark_one(profile):
    # Small deterministic CPU task approximating independent recommendation work.
    return len(recommend(profile, limit=12))

@app.post("/api/benchmark/run")
def run_benchmark(payload: dict | None = None):
    payload = payload or {}
    profile_count = int(payload.get("profiles", 100))
    repeats = int(payload.get("repeats", 3))
    if not 1 <= profile_count <= 20000 or not 1 <= repeats <= 10:
        raise HTTPException(422, "profiles must be 1..20000 and repeats must be 1..10.")
    base = {
        "career_goal": "AI/ML Engineer", "skills": {"Python Programming": "beginner"},
        "interests": ["python", "ai"], "hours_per_week": 5, "timeframe_weeks": 12
    }
    profiles = [dict(base, interests=["python", "ai", "data"] if i % 2 == 0 else ["math", "statistics"]) for i in range(profile_count)]
    sequential_times, threaded_times = [], []
    for _ in range(repeats):
        start = time.perf_counter()
        seq = [_benchmark_one(p) for p in profiles]
        sequential_times.append(time.perf_counter() - start)
        start = time.perf_counter()
        with ThreadPoolExecutor(max_workers=min(8, os.cpu_count() or 2)) as pool:
            threaded = list(pool.map(_benchmark_one, profiles))
        threaded_times.append(time.perf_counter() - start)
        if seq != threaded:
            raise HTTPException(500, "Benchmark correctness check failed.")
    seq_avg = sum(sequential_times) / repeats
    thr_avg = sum(threaded_times) / repeats
    return {
        "profiles": profile_count, "repeats": repeats,
        "environment": {"python": platform.python_version(), "os": platform.platform(), "cpu_count": os.cpu_count()},
        "sequential_seconds": round(seq_avg, 6), "threaded_seconds": round(thr_avg, 6),
        "sequential_profiles_per_second": round(profile_count / seq_avg, 2) if seq_avg else None,
        "threaded_profiles_per_second": round(profile_count / thr_avg, 2) if thr_avg else None,
        "threaded_speedup": round(seq_avg / thr_avg, 3) if thr_avg else None,
        "note": "Measured on this running machine. Threading may be slower for CPU-bound work; this is not a cluster-scale benchmark."
    }
