from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta, date
from collections import defaultdict

from models import initialize_database, Session, Habit, Entry

app = Flask(__name__)
initialize_database()

# -------------------------------------------------
# Date Utilities
# -------------------------------------------------

def parse_date(value):
    return datetime.strptime(value, "%Y-%m-%d").date()


def iso(d):
    return d.isoformat()


def week_range(ref):
    start = ref - timedelta(days=ref.weekday())
    return start, start + timedelta(days=6)


def month_range(ref):
    start = ref.replace(day=1)
    if ref.month == 12:
        end = ref.replace(year=ref.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end = ref.replace(month=ref.month + 1, day=1) - timedelta(days=1)
    return start, end


# -------------------------------------------------
# Aggregation Helpers
# -------------------------------------------------

def fetch_week_matrix(days, habits):
    rows = (
        Session.query(
            Entry.habit_id,
            Entry.date,
            Entry.count
        )
        .filter(Entry.date.in_(days))
        .all()
    )

    lookup = {(r.habit_id, r.date): r.count for r in rows}

    result = []
    for h in habits:
        entries = {}
        total = 0

        for d in days:
            val = lookup.get((h.id, d), 0)
            entries[d] = val
            total += val

        result.append({
            "id": h.id,
            "name": h.name,
            "entries": entries,
            "weekly_total": total,
            "weekly_goal": 7
        })

    return result


def fetch_daily_totals(days):
    rows = (
        Session.query(Entry.date, Entry.count)
        .filter(Entry.date.in_(days))
        .all()
    )

    totals = defaultdict(int)
    for d, c in rows:
        totals[d] += c

    return [totals.get(d, 0) for d in days]


# -------------------------------------------------
# UNIQUE ENHANCEMENTS
# -------------------------------------------------

def compute_consistency(days, habit_id):
    rows = (
        Session.query(Entry.date)
        .filter(
            Entry.habit_id == habit_id,
            Entry.date.in_(days),
            Entry.count > 0
        )
        .distinct()
        .all()
    )
    return round(len(rows) / 7, 2)


def calculate_streak(habit_id):
    today_date = date.today()
    streak = 0

    while True:
        d = today_date - timedelta(days=streak)
        entry = (
            Session.query(Entry)
            .filter_by(habit_id=habit_id, date=d.isoformat())
            .first()
        )
        if entry and entry.count > 0:
            streak += 1
        else:
            break

    return streak


# -------------------------------------------------
# Views
# -------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/analytics")
def analytics_page():
    return render_template("analytics.html")


# -------------------------------------------------
# API: Weekly Data + Search
# -------------------------------------------------

@app.route("/api/week", methods=["GET"])
def api_week():
    date_str = request.args.get("date")
    search = request.args.get("search", "").strip()

    base = parse_date(date_str) if date_str else date.today()
    start, end = week_range(base)
    days = [iso(start + timedelta(days=i)) for i in range(7)]

    habit_query = Session.query(Habit)
    if search:
        habit_query = habit_query.filter(Habit.name.ilike(f"%{search}%"))

    habits = habit_query.order_by(Habit.id).all()

    return jsonify({
        "start": iso(start),
        "end": iso(end),
        "days": days,
        "habits": fetch_week_matrix(days, habits),
        "daily_sums": fetch_daily_totals(days)
    })


# -------------------------------------------------
# API: Add Habit
# -------------------------------------------------

@app.route("/api/habit", methods=["POST"])
def api_add_habit():
    name = (request.json or {}).get("name", "").strip()

    if not name:
        return jsonify({"error": "name required"}), 400

    habit = Habit(name=name)
    Session.add(habit)
    Session.commit()

    return jsonify({"id": habit.id, "name": habit.name})


# -------------------------------------------------
# API: Set / Update Entry
# -------------------------------------------------

@app.route("/api/entry", methods=["POST"])
def api_entry():
    payload = request.json or {}

    habit_id = payload.get("habit_id")
    date_str = payload.get("date")
    value = int(payload.get("value", 1))

    if not habit_id or not date_str:
        return jsonify({"error": "habit_id and date required"}), 400

    try:
        parse_date(date_str)
    except Exception:
        return jsonify({"error": "date must be YYYY-MM-DD"}), 400

    entry = (
        Session.query(Entry)
        .filter_by(habit_id=habit_id, date=date_str)
        .first()
    )

    if entry:
        entry.count = value
    else:
        Session.add(
            Entry(habit_id=habit_id, date=date_str, count=value)
        )

    Session.commit()
    return jsonify({"success": True})


# -------------------------------------------------
# API: Delete Habit
# -------------------------------------------------

@app.route("/api/habit/<int:hid>", methods=["DELETE"])
def api_delete_habit(hid):
    habit = Session.query(Habit).get(hid)

    if not habit:
        return jsonify({"error": "not found"}), 404

    Session.query(Entry).filter_by(habit_id=hid).delete()
    Session.delete(habit)
    Session.commit()

    return jsonify({"success": True})


# -------------------------------------------------
# API: Weekly Analytics (High / Low + Enhancements)
# -------------------------------------------------

@app.route("/api/analytics", methods=["GET"])
def api_analytics():
    date_str = request.args.get("date")
    base = parse_date(date_str) if date_str else date.today()

    start, _ = week_range(base)
    days = [iso(start + timedelta(days=i)) for i in range(7)]

    rows = (
        Session.query(Entry.habit_id, Entry.count)
        .filter(Entry.date.in_(days))
        .all()
    )

    totals = defaultdict(int)
    for hid, c in rows:
        totals[hid] += c

    results = []
    for h in Session.query(Habit).all():
        weekly_total = totals.get(h.id, 0)

        results.append({
            "habit_id": h.id,
            "name": h.name,
            "weekly_total": weekly_total,
            "rate": weekly_total / 7.0,
            "consistency": compute_consistency(days, h.id),
            "streak": calculate_streak(h.id)
        })

    ranked = sorted(results, key=lambda x: x["rate"], reverse=True)

    return jsonify({
        "high": ranked[:5],
        "low": ranked[-5:]
    })


# -------------------------------------------------
# API: Monthly Analytics
# -------------------------------------------------

@app.route("/api/monthly", methods=["GET"])
def api_monthly():
    date_str = request.args.get("date")
    base = parse_date(date_str) if date_str else date.today()

    start, end = month_range(base)
    days = [(start + timedelta(days=i)).isoformat()
            for i in range((end - start).days + 1)]

    rows = (
        Session.query(Entry.habit_id, Entry.date, Entry.count)
        .filter(Entry.date.in_(days))
        .all()
    )

    totals = defaultdict(int)
    for hid, _, c in rows:
        totals[hid] += c

    result = []
    for h in Session.query(Habit).all():
        total = totals.get(h.id, 0)
        result.append({
            "habit_id": h.id,
            "name": h.name,
            "monthly_total": total,
            "monthly_rate": round(total / len(days), 2)
        })

    return jsonify(result)


# -------------------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
