from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from dotenv import load_dotenv
from datetime import date, datetime
import os
import database
from pytz import timezone
from openpyxl import Workbook
from io import BytesIO
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-secret")

database.init_db()


def login_required(f):
    from functools import wraps

    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


@app.route("/", methods=["GET"])
@login_required
def index():
    user_id = session["user_id"]
    user = database.get_user_by_id(user_id)
    india = timezone("Asia/Kolkata")
    selected_date = request.args.get(
        "date", datetime.now(india).date().isoformat())
    entries = database.get_entries_by_date(user_id, selected_date)
    # Convert Row objects to dictionaries for JSON serialization
    entries = [dict(entry) for entry in entries]
    total = database.get_total_calories(user_id, selected_date)
    all_dates = database.get_all_dates(user_id)
    today = datetime.now(india).date().isoformat()

    # Ensure today is always in the date list for the sidebar
    if today not in all_dates:
        all_dates = [today] + list(all_dates)

    return render_template(
        "dashboard.html",
        entries=entries,
        selected_date=selected_date,
        total=total,
        all_dates=all_dates,
        today=today,
        username=user["username"] if user else "User"
    )


@app.route("/add", methods=["POST"])
@login_required
def add():
    user_id = session["user_id"]
    food_item = request.form.get("food_item", "").strip()
    calories = request.form.get("calories", "").strip()
    entry_date = request.form.get("entry_date", date.today().isoformat())

    if not food_item or not calories:
        flash("Both food item and calories are required.", "error")
        return redirect(url_for("index", date=entry_date))

    try:
        calories = int(calories)
        if calories <= 0:
            raise ValueError
    except ValueError:
        flash("Calories must be a positive number.", "error")
        return redirect(url_for("index", date=entry_date))

    database.add_entry(user_id, entry_date, food_item, calories)
    return redirect(url_for("index", date=entry_date))


@app.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete(entry_id):
    user_id = session["user_id"]
    entry_date = request.form.get("entry_date", date.today().isoformat())
    database.delete_entry(entry_id, user_id)
    return redirect(url_for("index", date=entry_date))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        user = database.get_user_by_username(username)
        
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash(f"Welcome back, {user['username']}!", "success")
            return redirect(url_for("index"))
        
        flash("Invalid username or password.", "error")
    
    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        confirm_password = request.form.get("confirm_password", "").strip()
        
        # Validation
        if not username or not email or not password:
            flash("All fields are required.", "error")
            return redirect(url_for("signup"))
        
        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect(url_for("signup"))
        
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup"))
        
        # Create user
        password_hash = generate_password_hash(password)
        user_id = database.create_user(username, email, password_hash)
        
        if user_id:
            session["user_id"] = user_id
            flash(f"Welcome, {username}! Your account has been created.", "success")
            return redirect(url_for("index"))
        else:
            flash("Username or email already exists.", "error")
            return redirect(url_for("signup"))
    
    return render_template("signup.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/export", methods=["GET"])
@login_required
def export():
    user_id = session["user_id"]
    # Get all dates from database for this user
    all_dates = database.get_all_dates(user_id)

    if not all_dates:
        flash("No data to export.", "error")
        return redirect(url_for("index"))

    # Create a workbook
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet

    from openpyxl.styles import Font, PatternFill

    # Create a sheet for each date
    for export_date in all_dates:
        entries = database.get_entries_by_date(user_id, export_date)
        total = database.get_total_calories(user_id, export_date)

        # Create sheet with date as name
        ws = wb.create_sheet(title=export_date)

        # Add headers
        headers = ["Food Item", "Calories", "Time"]
        ws.append(headers)

        # Style headers
        header_fill = PatternFill(start_color="FF8B5000",
                                  end_color="FF8B5000", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")

        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font

        # Add data rows
        for entry in entries:
            ws.append([
                entry["food_item"],
                entry["calories"],
                entry["created_at"][:16]
            ])

        # Add total row
        ws.append(["Total", total, ""])
        total_fill = PatternFill(start_color="FFFF9E64",
                                 end_color="FFFF9E64", fill_type="solid")
        total_font = Font(bold=True)
        for cell in ws[ws.max_row]:
            cell.fill = total_fill
            cell.font = total_font

        # Adjust column widths
        ws.column_dimensions['A'].width = 25
        ws.column_dimensions['B'].width = 12
        ws.column_dimensions['C'].width = 18

    # Save to BytesIO and send
    excel_file = BytesIO()
    wb.save(excel_file)
    excel_file.seek(0)

    filename = "calories_all_dates.xlsx"
    return send_file(excel_file, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=True)
