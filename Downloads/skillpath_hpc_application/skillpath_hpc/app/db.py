"""SQLite persistence layer."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "skillpath.db"

def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")

def connect():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            career_goal TEXT NOT NULL,
            education_level TEXT NOT NULL DEFAULT 'Undergraduate',
            branch TEXT NOT NULL DEFAULT 'B.Tech CSE-AI',
            semester INTEGER NOT NULL DEFAULT 3,
            interests_json TEXT NOT NULL DEFAULT '[]',
            skills_json TEXT NOT NULL DEFAULT '{}',
            hours_per_week REAL NOT NULL DEFAULT 5,
            timeframe_weeks INTEGER NOT NULL DEFAULT 12,
            learning_format TEXT NOT NULL DEFAULT 'Mixed',
            focus_skills_json TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS roadmap_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            skill TEXT NOT NULL,
            category TEXT NOT NULL,
            rank INTEGER NOT NULL,
            score REAL NOT NULL,
            current_level INTEGER NOT NULL,
            target_level INTEGER NOT NULL,
            gap INTEGER NOT NULL,
            importance INTEGER NOT NULL,
            estimated_hours REAL NOT NULL,
            prerequisites_json TEXT NOT NULL DEFAULT '[]',
            reason TEXT NOT NULL,
            objective TEXT NOT NULL,
            activity TEXT NOT NULL,
            resource_name TEXT NOT NULL,
            resource_url TEXT NOT NULL,
            next_action TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'not_started',
            hours_logged REAL NOT NULL DEFAULT 0,
            notes TEXT NOT NULL DEFAULT '',
            updated_at TEXT NOT NULL,
            UNIQUE(profile_id, skill)
        );
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_roadmap_profile ON roadmap_items(profile_id);
        """)
        conn.commit()

def row_to_profile(row):
    if not row:
        return None
    d = dict(row)
    for field, col in [
        ("interests", "interests_json"), ("skills", "skills_json"),
        ("focus_skills", "focus_skills_json")
    ]:
        d[field] = json.loads(d.pop(col))
    return d

def get_profile(profile_id):
    with connect() as conn:
        row = conn.execute("SELECT * FROM profiles WHERE id=?", (profile_id,)).fetchone()
    return row_to_profile(row)

def save_profile(data):
    stamp = now_iso()
    with connect() as conn:
        profile_id = data.get("id")
        if profile_id:
            exists = conn.execute("SELECT id FROM profiles WHERE id=?", (profile_id,)).fetchone()
            if not exists:
                raise ValueError(f"Profile {profile_id} does not exist.")
            conn.execute("""
                UPDATE profiles SET name=?, career_goal=?, education_level=?, branch=?, semester=?,
                interests_json=?, skills_json=?, hours_per_week=?, timeframe_weeks=?, learning_format=?,
                focus_skills_json=?, updated_at=? WHERE id=?
            """, (
                data["name"], data["career_goal"], data.get("education_level", "Undergraduate"),
                data.get("branch", "B.Tech CSE-AI"), data.get("semester", 3),
                json.dumps(data.get("interests", [])), json.dumps(data.get("skills", {})),
                data.get("hours_per_week", 5), data.get("timeframe_weeks", 12),
                data.get("learning_format", "Mixed"), json.dumps(data.get("focus_skills", [])),
                stamp, profile_id
            ))
        else:
            cur = conn.execute("""
                INSERT INTO profiles(name, career_goal, education_level, branch, semester,
                interests_json, skills_json, hours_per_week, timeframe_weeks, learning_format,
                focus_skills_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["name"], data["career_goal"], data.get("education_level", "Undergraduate"),
                data.get("branch", "B.Tech CSE-AI"), data.get("semester", 3),
                json.dumps(data.get("interests", [])), json.dumps(data.get("skills", {})),
                data.get("hours_per_week", 5), data.get("timeframe_weeks", 12),
                data.get("learning_format", "Mixed"), json.dumps(data.get("focus_skills", [])),
                stamp, stamp
            ))
            profile_id = cur.lastrowid
        conn.commit()
    return get_profile(profile_id)

def save_roadmap(profile_id, roadmap):
    stamp = now_iso()
    with connect() as conn:
        existing = {
            row["skill"].casefold(): dict(row)
            for row in conn.execute("SELECT * FROM roadmap_items WHERE profile_id=?", (profile_id,))
        }
        conn.execute("DELETE FROM roadmap_items WHERE profile_id=?", (profile_id,))
        for rank, item in enumerate(roadmap["items"], 1):
            old = existing.get(item["skill"].casefold(), {})
            conn.execute("""
                INSERT INTO roadmap_items(profile_id, skill, category, rank, score, current_level,
                target_level, gap, importance, estimated_hours, prerequisites_json, reason,
                objective, activity, resource_name, resource_url, next_action, status, hours_logged,
                notes, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile_id, item["skill"], item["category"], rank, item["score"], item["current_level"],
                item["target_level"], item["gap"], item["importance"], item["estimated_hours"],
                json.dumps(item["prerequisites"]), item["reason"], item["objective"], item["activity"],
                item["resource_name"], item["resource_url"], item["next_action"],
                old.get("status", "not_started"), old.get("hours_logged", 0), old.get("notes", ""), stamp
            ))
        conn.execute(
            "INSERT INTO activity_log(profile_id, message, created_at) VALUES (?, ?, ?)",
            (profile_id, f"Roadmap generated with {len(roadmap['items'])} skill items.", stamp)
        )
        conn.commit()

def get_roadmap(profile_id):
    with connect() as conn:
        rows = conn.execute("SELECT * FROM roadmap_items WHERE profile_id=? ORDER BY rank", (profile_id,)).fetchall()
    out = []
    for row in rows:
        item = dict(row)
        item["prerequisites"] = json.loads(item.pop("prerequisites_json"))
        out.append(item)
    return out

def update_roadmap_item(item_id, patch):
    allowed = {"status", "hours_logged", "notes", "current_level"}
    if set(patch) - allowed:
        raise ValueError("Unsupported progress field.")
    with connect() as conn:
        row = conn.execute("SELECT * FROM roadmap_items WHERE id=?", (item_id,)).fetchone()
        if not row:
            return None
        item = dict(row)
        new_status = patch.get("status", item["status"])
        if new_status not in ("not_started", "in_progress", "completed"):
            raise ValueError("Status must be not_started, in_progress, or completed.")
        hours = float(patch.get("hours_logged", item["hours_logged"]))
        if hours < 0 or hours > 100000:
            raise ValueError("Logged hours must be between 0 and 100000.")
        level = int(patch.get("current_level", item["current_level"]))
        if level not in (0, 1, 2, 3):
            raise ValueError("Proficiency must be 0, 1, 2, or 3.")
        if new_status == "completed" and "current_level" not in patch:
            level = int(item["target_level"])
        gap = max(0, int(item["target_level"]) - level)
        notes = str(patch.get("notes", item["notes"]))[:2000]
        stamp = now_iso()
        conn.execute("""
            UPDATE roadmap_items SET status=?, hours_logged=?, notes=?, current_level=?, gap=?, updated_at=?
            WHERE id=?
        """, (new_status, hours, notes, level, gap, stamp, item_id))
        # Keep the saved learner skill inventory aligned with progress so future roadmap regeneration
        # does not forget proficiency updates or completed skills.
        profile_row = conn.execute("SELECT skills_json FROM profiles WHERE id=?", (item["profile_id"],)).fetchone()
        if profile_row and ("current_level" in patch or new_status == "completed"):
            skills = json.loads(profile_row["skills_json"])
            skills[item["skill"]] = level
            conn.execute("UPDATE profiles SET skills_json=?, updated_at=? WHERE id=?",
                         (json.dumps(skills), stamp, item["profile_id"]))
        conn.execute("INSERT INTO activity_log(profile_id, message, created_at) VALUES (?, ?, ?)",
                     (item["profile_id"], f"Updated {item['skill']}: {new_status}.", stamp))
        conn.commit()
        return conn.execute("SELECT * FROM roadmap_items WHERE id=?", (item_id,)).fetchone()

def get_activity(profile_id, limit=8):
    with connect() as conn:
        rows = conn.execute(
            "SELECT message, created_at FROM activity_log WHERE profile_id=? ORDER BY id DESC LIMIT ?",
            (profile_id, limit)
        ).fetchall()
    return [dict(r) for r in rows]

def get_dashboard(profile_id):
    profile = get_profile(profile_id)
    if not profile:
        return None
    items = get_roadmap(profile_id)
    total = len(items)
    completed = sum(i["status"] == "completed" for i in items)
    high = sum(i["importance"] >= 5 and i["gap"] > 0 for i in items)
    return {
        "profile": profile, "career_goal": profile["career_goal"], "total_gaps": sum(i["gap"] > 0 for i in items),
        "high_priority": high, "recommended_hours": sum(i["estimated_hours"] for i in items),
        "hours_logged": round(sum(i["hours_logged"] for i in items), 1), "total_items": total,
        "completed_items": completed, "pending_items": total - completed,
        "completion_percent": round(100 * completed / total) if total else 0,
        "items": items, "activity": get_activity(profile_id)
    }
