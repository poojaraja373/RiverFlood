from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "river-flood-demo-key-2026")
DB_PATH = Path(__file__).with_name("river_flood.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def normalize_status(level):
    if level is None:
        return "Unknown"
    if level >= 3.0:
        return "Danger"
    if level >= 1.5:
        return "Warning"
    return "Safe"


def compute_trend(previous_level, current_level):
    if previous_level is None or current_level is None:
        return "Unknown"
    diff = current_level - previous_level
    if diff > 0.2:
        return "Rising"
    if diff < -0.2:
        return "Falling"
    return "Stable"


def order_readings(rows):
    urgency = {"Danger": 0, "Warning": 1, "Safe": 2, "Unknown": 3}
    return sorted(
        rows,
        key=lambda row: (
            urgency.get(row["derived_status"], 3),
            row["recorded_at"],
            -row["reading_id"],
        ),
    )


def build_payload(data, conn):
    location = (data.get("location") or "").strip()
    device_id = (data.get("device_id") or "").strip()
    raw_level = data.get("water_level_m")
    status = (data.get("status") or "").strip().capitalize()
    recorded_at = data.get("recorded_at") or datetime.now(timezone.utc).isoformat()

    errors = {}
    if not location:
        errors["location"] = "Location is required"
    if not device_id:
        errors["device_id"] = "Device ID is required"

    if raw_level is None or raw_level == "":
        errors["water_level_m"] = "Water level is required"
    else:
        try:
            level = float(raw_level)
        except (TypeError, ValueError):
            errors["water_level_m"] = "Water level must be a number"
        else:
            if not math.isfinite(level) or level < 0 or level > 12:
                errors["water_level_m"] = "Water level must be between 0 and 12 meters"
            elif status not in {"Safe", "Warning", "Danger", "Unknown"}:
                errors["status"] = "Status must be Safe, Warning, Danger or Unknown"
            else:
                previous = conn.execute(
                    "SELECT water_level_m FROM readings WHERE location = ? ORDER BY reading_id DESC LIMIT 1",
                    (location,),
                ).fetchone()
                previous_level = previous["water_level_m"] if previous else None
                derived_status = normalize_status(level)
                trend = compute_trend(previous_level, level)
                delta = None if previous_level is None else round(level - previous_level, 2)
                return {
                    "location": location,
                    "water_level_m": level,
                    "status": status,
                    "recorded_at": recorded_at,
                    "device_id": device_id,
                    "derived_status": derived_status,
                    "trend": trend,
                    "delta_m": delta,
                }, errors

    return None, errors


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS readings (
            reading_id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            water_level_m REAL,
            status TEXT NOT NULL,
            recorded_at TEXT NOT NULL,
            device_id TEXT NOT NULL,
            derived_status TEXT NOT NULL,
            trend TEXT NOT NULL,
            delta_m REAL
        )
        """
    )
    conn.commit()

    user_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    if user_count == 0:
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            ("operator", "flood2026"),
        )
        conn.commit()

    conn.close()


@app.before_request
def before_request():
    if not DB_PATH.exists():
        init_db()


def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        error = None

        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        else:
            conn = get_db()
            user = conn.execute(
                "SELECT user_id, username FROM users WHERE username = ? AND password = ?",
                (username, password),
            ).fetchone()
            conn.close()

            if user:
                session["user_id"] = user["user_id"]
                session["username"] = user["username"]
                return redirect(url_for("dashboard"))
            else:
                error = "Invalid username or password"

        return render_template("login.html", error=error)

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        confirm_password = (request.form.get("confirm_password") or "").strip()
        error = None

        if not username:
            error = "Username is required"
        elif len(username) < 3:
            error = "Username must be at least 3 characters"
        elif not password:
            error = "Password is required"
        elif len(password) < 6:
            error = "Password must be at least 6 characters"
        elif password != confirm_password:
            error = "Passwords do not match"
        else:
            conn = get_db()
            try:
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, password),
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                error = "Username already exists"
            finally:
                conn.close()

        return render_template("signup.html", error=error)

    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/dashboard")
@login_required
def dashboard():
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM readings ORDER BY reading_id DESC"
    ).fetchall()
    conn.close()
    ordered = order_readings(rows)
    return render_template("dashboard.html", readings=ordered, count=len(ordered), username=session.get("username"))


@app.route("/register", methods=["GET", "POST"])
@login_required
def register():
    if request.method == "POST":
        conn = get_db()
        payload, errors = build_payload(request.form, conn)
        if errors:
            conn.close()
            return render_template("register.html", errors=errors, payload=request.form)

        conn.execute(
            """
            INSERT INTO readings (location, water_level_m, status, recorded_at, device_id, derived_status, trend, delta_m)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload["location"],
                payload["water_level_m"],
                payload["status"],
                payload["recorded_at"],
                payload["device_id"],
                payload["derived_status"],
                payload["trend"],
                payload["delta_m"],
            ),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    return render_template("register.html", errors={}, payload={})


@app.route("/api/readings")
@login_required
def api_readings():
    conn = get_db()
    rows = conn.execute("SELECT * FROM readings ORDER BY reading_id DESC").fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/simulate", methods=["POST"])
@login_required
def simulate_reading():
    data = request.get_json() or {}
    location = (data.get("location") or "North Bank").strip() or "North Bank"
    device_id = (data.get("device_id") or "NODE-01").strip() or "NODE-01"
    level = data.get("water_level_m", 1.2)
    try:
        level = float(level)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "Invalid water level"}), 400

    if not math.isfinite(level) or level < 0 or level > 12:
        return jsonify({"ok": False, "message": "Water level must stay within 0 to 12m"}), 400

    conn = get_db()
    previous_row = conn.execute(
        "SELECT water_level_m FROM readings WHERE location = ? ORDER BY reading_id DESC LIMIT 1",
        (location,),
    ).fetchone()
    previous_level = previous_row["water_level_m"] if previous_row else None

    if previous_level is not None:
        if level - previous_level > 1.8:
            level = previous_level + 0.8
        elif previous_level - level > 1.8:
            level = previous_level - 0.8

    derived_status = normalize_status(level)
    trend = compute_trend(previous_level, level)
    delta = None if previous_level is None else round(level - previous_level, 2)
    conn.execute(
        """
        INSERT INTO readings (location, water_level_m, status, recorded_at, device_id, derived_status, trend, delta_m)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (location, level, derived_status, datetime.now(timezone.utc).isoformat(), device_id, derived_status, trend, delta),
    )
    conn.commit()
    conn.close()
    return jsonify({"ok": True, "message": "Simulated reading stored"})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
