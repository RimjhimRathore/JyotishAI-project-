from flask import Flask, render_template, redirect, url_for, request
import os, json
from flask import flash
from dotenv import load_dotenv
from src.generate_kundali import get_output
from src.lushogrid import loshu_grid_from_dob
from config import Config
from database.db import db, login_manager
from database.models import UserDetails, KundaliRecord
from src.astro_engine import calculate_chart
from src.kundli_svg import build_north_chart
# 🔐 Flask-Login imports
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user
)

# 🔐 Password hashing
from werkzeug.security import generate_password_hash, check_password_hash


load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv("FLASK_API_KEY")
app.config.from_object(Config)

# Initialize DB + Login
db.init_app(app)
login_manager.init_app(app)


# 🔑 Load user from session
@login_manager.user_loader
def load_user(user_id):
    return UserDetails.query.get(int(user_id))


# Create tables automatically (SQLite)
with app.app_context():
    db.create_all()


# =========================================================
# 🔐 LOGIN
# =========================================================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        user = UserDetails.query.filter_by(email=email).first()

        # ❌ User not found
        if not user:
            flash("No account found. Please sign up first.", "danger")
            return redirect(url_for("signup"))

        # ❌ Wrong password
        if not check_password_hash(user.password, password):
            flash("Incorrect password", "danger")
            return render_template("login.html")

        # ✅ Success
        login_user(user)
        flash("Login successful!", "success")
        return redirect(url_for("home"))

    return render_template("login.html")



# =========================================================
# 📝 SIGNUP
# =========================================================
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        # 🔴 Check existing email
        existing_user = UserDetails.query.filter_by(email=email).first()

        if existing_user:
            flash("Email already registered. Please login.", "warning")
            return redirect(url_for("login"))

        # ✅ Create new user
        hashed_password = generate_password_hash(password)

        new_user = UserDetails(
            username=name,
            email=email,
            password=hashed_password
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash("Account created successfully!", "success")

        return redirect(url_for("home"))

    return render_template("signup.html")

# =========================================================
# 🔓 LOGOUT
# =========================================================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# =========================================================
# 🏠 HOME (Protected)
# =========================================================
@app.route("/home")
@login_required
def home():
    return render_template("home.html", name=current_user.username)


# =========================================================
# 🔮 KUNDALI FORM
# =========================================================
@app.route("/kundali", methods=["GET", "POST"])
@login_required
def kundali():
    if request.method == "POST":

        dob = request.form.get("dob")
        time = request.form.get("time")
        place = request.form.get("place")

        return redirect(
            url_for("show_kundali", dob=dob, time=time, place=place)
        )

    return render_template("home.html")


def parse_ai_json(text):
    text = (text or "").strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found")
    return json.loads(text[start:end + 1])



def render_kundali(dob, time, place, chart, kundali):
    grid, driver, conductor = loshu_grid_from_dob(dob)
    return render_template(
        "show_kundali.html",
        dob=dob, time=time, place=place,
        chart=chart, kundali=kundali,
        chart_svg=build_north_chart(chart),
        grid=grid, driver=driver, conductor=conductor,
        show_grid=any(grid.values()),
        user_name=current_user.username,
    )


# =========================================================
# 🔮 SHOW KUNDALI
# =========================================================



@app.route("/show_kundali")
@login_required
def show_kundali():
    dob = request.args.get("dob")
    time = request.args.get("time")
    place = (request.args.get("place") or "").strip()

    existing = KundaliRecord.query.filter_by(
        user_id=current_user.id, dob=dob, time=time, place=place
    ).first()
    if existing:
        return render_kundali(dob, time, place,
                              json.loads(existing.chart_json),
                              json.loads(existing.reading_json))

    try:
        chart = calculate_chart(dob, time, place)
    except Exception as e:
        print("CHART ERROR:", e)
        flash("Could not calculate the chart. Please check the birth place.", "danger")
        return redirect(url_for("home"))

    result = get_output(chart)
    try:
        kundali = parse_ai_json(result)
        db.session.add(KundaliRecord(
            user_id=current_user.id, dob=dob, time=time, place=place,
            chart_json=json.dumps(chart), reading_json=json.dumps(kundali),
        ))
        db.session.commit()
    except Exception as e:
        print("JSON ERROR:", e)
        print("RAW RESPONSE:", result)
        kundali = {"Error": "Invalid response from AI"}

    return render_kundali(dob, time, place, chart, kundali)


@app.route("/history")
@login_required
def history():
    records = (KundaliRecord.query
               .filter_by(user_id=current_user.id)
               .order_by(KundaliRecord.created_at.desc())
               .all())
    return render_template("history.html", records=records)


@app.route("/history/<int:record_id>")
@login_required
def view_history(record_id):
    # filtering by user_id means nobody can open another user's report by guessing an ID
    rec = KundaliRecord.query.filter_by(
        id=record_id, user_id=current_user.id).first_or_404()
    return render_kundali(rec.dob, rec.time, rec.place,
                          json.loads(rec.chart_json),
                          json.loads(rec.reading_json))
# =========================================================
# OTHER ROUTES
# =========================================================

@app.route("/login/google")
def google_login():
    return render_template("google_login.html")


@app.route("/login/otp")
def otp_login():
    return render_template("otp_login.html")


@app.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")


# =========================================================

if __name__ == "__main__":
    app.run(debug=True)
