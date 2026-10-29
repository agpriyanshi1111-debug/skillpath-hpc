# SkillPath — Personalized Skill Development Recommendation System

Academic PBL prototype for HPC (CCSAI0302), Group 42, aligned with SDG 4 — Quality Education.

## What is implemented

- FastAPI backend with validated request models.
- SQLite persistence for learner profiles and roadmap progress.
- Editable seed career/skill knowledge base in `app/data.py`.
- Transparent, deterministic skill-gap recommendation algorithm.
- Prerequisite-aware roadmap ordering.
- Progress updates, learning hours, notes, proficiency updates, and dashboard metrics.
- Browser-based frontend served by the API (no separate Node install required).
- Repeatable sequential-vs-threaded benchmark script.
- Pytest coverage for recommendation behavior and API persistence.

The included career-skill mapping is a hand-authored starter knowledge base for demonstration. It is not an official industry dataset, and target levels are system-defined recommendations rather than universal industry standards. The recommendation engine is rule-based, not a trained ML model.

## Requirements

Python 3.10+ recommended.

## Windows PowerShell setup

```powershell
cd path\to\skillpath_hpc
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

Open:
- App: http://127.0.0.1:8000
- API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/api/health

The SQLite database is created automatically at `skillpath.db` in the project root. Demo data is seeded automatically on first startup.

## Run tests

In a second terminal with the virtual environment activated:

```powershell
python -m pytest -q
```

## Run benchmark

```powershell
python benchmark.py --profiles 100 500 1000 --repeats 5
```

The benchmark writes actual measurements to `benchmark_results.json` and prints the environment and measured times. Results depend on your machine and should be reported only after running it on the target machine. Threaded results are not guaranteed to be faster.

## Main API routes

- `GET /api/health`
- `GET /api/careers`
- `GET /api/skills?career=AI/ML%20Engineer`
- `GET /api/profile/{profile_id}`
- `POST /api/profile`
- `POST /api/recommendations`
- `POST /api/roadmap/generate`
- `GET /api/roadmap/{profile_id}`
- `PATCH /api/roadmap/items/{item_id}`
- `GET /api/dashboard/{profile_id}`
- `POST /api/benchmark/run`

## Recommendation formula

For each career-required skill:

- `gap = max(0, target_level - current_level)`, where Beginner = 1, Intermediate = 2, Advanced = 3, and unknown = 0.
- `gap_score = gap / target_level`.
- `importance_score = importance / 5`.
- `interest_score = 1` when a listed learner interest matches the skill/domain tags, otherwise `0.5`.
- `prerequisite_score = 1` when prerequisites are already met, otherwise `0.65` to keep foundational missing prerequisites visible.
- `time_feasibility = min(1, available_hours_per_week * 4 / estimated_hours)`.

The final score is:
`100 * (0.40*gap_score + 0.25*importance_score + 0.15*interest_score + 0.10*prerequisite_score + 0.10*time_feasibility)`

Skills already at or above target are excluded from the gap recommendations unless marked as a focus skill. Missing prerequisite skills are added as foundational roadmap items where they are known in the career knowledge base. A stable tie-break by skill name makes repeated input deterministic.

## HPC benchmark notes

`benchmark.py` compares sequential and thread-pool processing over synthetic independent profiles. It reports actual wall-clock measurements, throughput, Python version, OS, CPU count, and run parameters. This is a small local experiment, not evidence of cluster-scale performance or speedup. Threads may not improve CPU-bound Python work because of interpreter overhead/GIL; measure before drawing conclusions.

## Project limitations

- Starter knowledge base is manually curated and needs review against current job descriptions and learner/counsellor feedback.
- Proficiency is self-reported unless the optional quiz is expanded; the current prototype does not claim validated assessment.
- No account authentication or multi-user authorization is included. This is intended for local demo use, not public deployment with private learner data.
- External course links are general reputable learning/search pages; availability and content can change.
- No trained machine-learning model is included because the reports do not identify a validated labeled dataset.

## Optional quiz and project information

The profile page includes a five-question Python/ML foundations quiz. Its score suggests a rough Python proficiency level and can be applied to the profile form; it is not a validated assessment or certification. The Project Information page documents the architecture, formula, HPC experiment and limitations.

## API quick check

- `GET /api/quiz` returns quiz questions without answer keys.
- `POST /api/quiz` scores submitted option indices and returns explanations.
- `GET /api/dashboard/{profile_id}` returns database-derived metrics and activity.
- `PATCH /api/roadmap/items/{item_id}` persists status, hours, notes and proficiency. Marking an item complete updates the saved skill inventory to its target level and sets its gap to zero; regenerating the roadmap uses that updated inventory.

## Faculty demonstration script (about 3 minutes)

1. Open the app and point out the demo learner dashboard. Explain that the counts come from the SQLite profile and roadmap, not fixed dashboard numbers.
2. Open **My profile**. Change the learner name, choose **AI/ML Engineer** or **Data Scientist**, select interests, and set proficiency levels. Optionally load the short quiz, answer questions, view explanations, and apply its suggested Python level.
3. Click **Generate my learning path**. Show how the selected career and known skills affect the prioritized gaps, scores, prerequisite notes and learning-resource links.
4. Open **Skill recommendations** and explain the score formula: gap 40%, importance 25%, interest 15%, prerequisite readiness 10%, time feasibility 10%.
5. Open **Learning roadmap**. Mark a skill in progress, log learning hours and add a note, then save. Marking a skill complete updates its proficiency/gap in the database. Return to the dashboard to show the recalculated metrics.
6. Open **HPC benchmark**, run 100 profiles over 3 repeats, and discuss the measured sequential/threaded times. Do not claim a speedup if the measured ratio is below 1; this local thread-pool test is not a cluster-scale experiment.
7. Open **Project information** to summarize the architecture, starter dataset, limitations and future work.

## Evidence and interpretation

`benchmark_results.json` contains a real benchmark run made during development in the current Linux/Python environment. It is an example of measured output, not a prediction for another computer. Run the benchmark on the machine used for your faculty demonstration and report those values separately. The uploaded progress reports document planning and a proposed workflow; this repository is the implemented prototype and its test evidence, not a claim that the earlier reports had already documented completed implementation.

## Explicit scope limitations

- Custom free-text career goals are not currently supported by the recommendation engine; select one of the nine careers in the starter knowledge base so skill mappings and prerequisites are meaningful.
- The current browser interface is a single active learner workspace seeded with a demo learner. The API can create/read multiple profile records, but the interface does not yet provide account login or a profile switcher.
- The knowledge base includes a small curated subset of skills per career. It should be reviewed and expanded with current job-posting evidence and learner/counsellor feedback before real career-advice use.
