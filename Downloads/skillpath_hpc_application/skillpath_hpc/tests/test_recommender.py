import pytest
from app.data import validate_dataset, CAREER_DATA
from app.recommender import recommend, generate_roadmap, normalize_profile

def profile(career, skills=None, interests=None, hours=5, weeks=12):
    return {"name":"Test Student","career_goal":career,"skills":skills or {},
            "interests":interests or [],"hours_per_week":hours,"timeframe_weeks":weeks}

def test_dataset_has_no_duplicate_career_skill_pairs():
    assert validate_dataset()
    assert len(CAREER_DATA) > 20

def test_different_careers_produce_different_recommendations():
    ai = {r["skill"] for r in recommend(profile("AI/ML Engineer"))}
    web = {r["skill"] for r in recommend(profile("Web Developer"))}
    assert ai != web
    assert "Machine Learning Fundamentals" in ai
    assert "HTML and CSS" in web

def test_mastered_skills_are_not_gaps():
    recs = recommend(profile("Data Analyst", {
        "SQL and Data Storage":"advanced",
        "Spreadsheet Analysis":"advanced",
        "Data Visualization":"advanced",
        "Statistics Basics":"advanced",
        "Communication":"advanced"
    }))
    assert all(r["gap"] > 0 or r["skill"].lower() in [] for r in recs)
    assert "SQL and Data Storage" not in {r["skill"] for r in recs}

def test_beginner_recommendations_explain_missing_prerequisites():
    recs = recommend(profile("AI/ML Engineer"))
    assert recs
    ml = next(r for r in recs if r["skill"] == "Machine Learning Fundamentals")
    assert "Python Programming" in ml["missing_prerequisites"]
    assert ml["score"] >= 0 and ml["score"] <= 100

def test_roadmap_has_time_feasibility_warning_when_over_budget():
    result = generate_roadmap(profile("AI/ML Engineer", hours=1, weeks=1), limit=12)
    assert result["feasible"] is False
    assert result["warning"]

def test_same_input_is_deterministic():
    p = profile("Data Scientist", {"Python Programming":"beginner"}, ["data"])
    assert recommend(p) == recommend(p)

def test_invalid_proficiency_rejected():
    with pytest.raises(ValueError):
        normalize_profile(profile("AI/ML Engineer", {"Python Programming":"expert"}))

def test_invalid_custom_career_rejected():
    with pytest.raises(ValueError):
        recommend(profile("Unlisted Career"))
