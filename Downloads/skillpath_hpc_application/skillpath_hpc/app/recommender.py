"""Deterministic, explainable rule-based recommendation engine."""
from __future__ import annotations
from collections import defaultdict
from .data import CAREER_DATA, get_career_data

LEVELS = {"beginner": 1, "intermediate": 2, "advanced": 3}
LEVEL_NAMES = {0: "Not assessed", 1: "Beginner", 2: "Intermediate", 3: "Advanced"}

def level_value(value):
    if value is None or value == "":
        return 0
    if isinstance(value, int):
        if value not in (0, 1, 2, 3):
            raise ValueError("Proficiency must be 0, 1, 2, or 3.")
        return value
    if isinstance(value, str):
        value = value.strip().lower()
        if value in ("not assessed", "none", "not started", "no experience"):
            return 0
        if value in LEVELS:
            return LEVELS[value]
        if value.isdigit() and int(value) in (0, 1, 2, 3):
            return int(value)
    raise ValueError("Proficiency must be Beginner, Intermediate, Advanced, or a level from 0 to 3.")

def normalize_profile(profile: dict) -> dict:
    p = dict(profile)
    p["career_goal"] = str(p.get("career_goal") or "").strip()
    if not p["career_goal"]:
        raise ValueError("Please select a career goal.")
    p["skills"] = p.get("skills") or {}
    if not isinstance(p["skills"], dict):
        raise ValueError("Skills must be an object mapping skill names to proficiency.")
    p["skills"] = {str(k).strip(): level_value(v) for k, v in p["skills"].items() if str(k).strip()}
    p["interests"] = [str(x).strip().lower() for x in (p.get("interests") or []) if str(x).strip()]
    p["hours_per_week"] = float(p.get("hours_per_week", 5) or 5)
    p["timeframe_weeks"] = int(p.get("timeframe_weeks", 12) or 12)
    p["focus_skills"] = [str(x).strip().lower() for x in (p.get("focus_skills") or []) if str(x).strip()]
    if not 1 <= p["hours_per_week"] <= 80:
        raise ValueError("Weekly learning time must be between 1 and 80 hours.")
    if not 1 <= p["timeframe_weeks"] <= 260:
        raise ValueError("Timeframe must be between 1 and 260 weeks.")
    return p

def _all_skills_for_career(career: str):
    rows = get_career_data(career)
    if not rows:
        # Allow a custom career goal by falling back to related interests only when no mapped path exists.
        raise ValueError(f"No career-skill mapping exists for '{career}'. Choose a listed career or use one of the supported career names.")
    return rows

def recommend(profile: dict, limit: int = 12) -> list[dict]:
    p = normalize_profile(profile)
    rows = _all_skills_for_career(p["career_goal"])
    current = {name.casefold(): lvl for name, lvl in p["skills"].items()}
    skill_lookup = {r["skill"].casefold(): r for r in rows}
    focus = set(p["focus_skills"])
    interests = set(p["interests"])
    results = []
    total_hours_available = p["hours_per_week"] * p["timeframe_weeks"]

    # Include direct career skills and known prerequisite skills missing from the profile.
    candidate_rows = {r["skill"].casefold(): r for r in rows}
    pending = list(rows)
    while pending:
        row = pending.pop()
        for prereq in row["prerequisites"]:
            key = prereq.casefold()
            if key not in candidate_rows:
                matching = next((x for x in CAREER_DATA if x["skill"].casefold() == key), None)
                if matching:
                    candidate_rows[key] = matching
                    pending.append(matching)

    for row in candidate_rows.values():
        skill_key = row["skill"].casefold()
        cur = current.get(skill_key, 0)
        target = row["target_level"]
        gap = max(0, target - cur)
        is_focus = skill_key in focus
        if gap == 0 and not is_focus:
            continue

        missing_prereqs = [
            prereq for prereq in row["prerequisites"]
            if current.get(prereq.casefold(), 0) < 1
        ]
        gap_score = gap / target if target else 0
        importance_score = row["importance"] / 5
        combined_tags = " ".join([row["skill"].lower(), row["category"].lower()] + row.get("tags", []))
        interest_score = 1.0 if any(i in combined_tags or combined_tags in i for i in interests) else 0.5
        prerequisite_score = 1.0 if not missing_prereqs else 0.65
        time_feasibility = min(1.0, total_hours_available / max(row["estimated_hours"], 1))
        score = round(100 * (
            0.40 * gap_score + 0.25 * importance_score + 0.15 * interest_score
            + 0.10 * prerequisite_score + 0.10 * time_feasibility
        ), 2)
        if gap == 0 and is_focus:
            score = min(100.0, score * 0.65)
        if missing_prereqs:
            reason = f"{row['skill']} is relevant to {p['career_goal']}; first build prerequisite(s): {', '.join(missing_prereqs)}."
        elif cur == 0:
            reason = f"{row['skill']} is a missing skill mapped to {p['career_goal']} and has importance {row['importance']}/5."
        elif gap > 0:
            reason = f"Your {LEVEL_NAMES[cur].lower()} level is below the suggested {LEVEL_NAMES[target].lower()} target for {p['career_goal']}."
        else:
            reason = "You marked this skill as a focus area; use it for practice and portfolio depth."
        if total_hours_available < row["estimated_hours"]:
            reason += f" Estimated {row['estimated_hours']} hours may exceed your {total_hours_available:g}-hour total timeframe."
        results.append({
            "career": p["career_goal"], "skill": row["skill"], "category": row["category"],
            "current_level": cur, "current_level_name": LEVEL_NAMES[cur],
            "target_level": target, "target_level_name": LEVEL_NAMES[target],
            "gap": gap, "gap_label": "High" if gap >= 2 else ("Moderate" if gap == 1 else "Focus"),
            "importance": row["importance"], "priority": "High" if row["importance"] >= 5 and gap >= 1 else ("Medium" if gap else "Practice"),
            "score": score, "estimated_hours": row["estimated_hours"],
            "prerequisites": row["prerequisites"], "missing_prerequisites": missing_prereqs,
            "reason": reason, "objective": row["objective"], "activity": row["activity"],
            "resource_name": row["resource_name"], "resource_url": row["resource_url"],
            "next_action": f"Start with {missing_prereqs[0]}" if missing_prereqs else f"Study {row['skill']} and complete the suggested activity",
            "tags": row.get("tags", [])
        })
    results.sort(key=lambda r: (-r["score"], -r["importance"], r["skill"].casefold()))
    for idx, item in enumerate(results, 1):
        item["rank"] = idx
    return results[:max(1, min(int(limit), 50))]

def generate_roadmap(profile: dict, limit: int = 12) -> dict:
    p = normalize_profile(profile)
    recs = recommend(p, limit=limit)
    by_skill = {r["skill"].casefold(): r for r in recs}
    # Order by prerequisite readiness with a stable topological pass; cycles fall back to score ordering.
    remaining = list(recs)
    ordered = []
    completed_names = {name.casefold() for name, lvl in p["skills"].items() if lvl >= 1}
    while remaining:
        ready = [
            r for r in remaining
            if all(pr.casefold() in completed_names or pr.casefold() not in by_skill for pr in r["prerequisites"])
        ]
        if not ready:
            ready = [remaining[0]]
        ready.sort(key=lambda r: (-r["score"], r["skill"].casefold()))
        item = ready[0]
        ordered.append(item)
        completed_names.add(item["skill"].casefold())
        remaining.remove(item)

    total_hours = sum(r["estimated_hours"] for r in ordered)
    available = p["hours_per_week"] * p["timeframe_weeks"]
    feasible = total_hours <= available
    milestones = []
    if ordered:
        chunks = [
            ("Foundation building", [r for r in ordered if r["category"] in ("Programming", "Mathematics", "Systems", "Networking")]),
            ("Core skills", [r for r in ordered if r["category"] not in ("Programming", "Mathematics", "Systems", "Networking", "Soft skill")]),
            ("Communication and practice", [r for r in ordered if r["category"] == "Soft skill"]),
        ]
        for title, items in chunks:
            if items:
                milestones.append({"title": title, "skills": [x["skill"] for x in items]})
    return {
        "career_goal": p["career_goal"], "items": ordered, "total_hours": total_hours,
        "available_hours": available, "feasible": feasible,
        "warning": None if feasible else f"This roadmap estimates {total_hours} hours, but your timeframe provides {available:g} hours. Extend the timeframe or increase weekly study time.",
        "suggested_weeks": max(1, (total_hours + p["hours_per_week"] - 1) // p["hours_per_week"]),
        "milestones": milestones
    }
