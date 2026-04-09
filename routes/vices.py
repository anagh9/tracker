"""
Vices Tracker Routes Blueprint
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import date
from pytz import timezone
import database
from utils import login_required, get_timezone, get_today_iso
from config import Config

vices_bp = Blueprint('vices', __name__)

@vices_bp.route("/", methods=["GET"])
@login_required
def index():
    """Vices tracker dashboard"""
    user_id = session["user_id"]
    user = database.get_user_by_id(user_id)
    tz = get_timezone()
    selected_date = request.args.get("date", date.today().isoformat())
    vice_entries = database.get_vices_by_date(user_id, selected_date)
    vice_summary = database.get_vice_summary(user_id, selected_date)
    vice_types = database.get_all_vice_types()
    user_habits = database.get_user_habits(user_id)
    all_dates = database.get_vice_dates(user_id)
    today = date.today().isoformat()

    if today not in all_dates:
        all_dates = [today] + list(all_dates)

    return render_template(
        "vices/dashboard.html",
        vice_entries=vice_entries,
        vice_summary=vice_summary,
        vice_types=vice_types,
        user_habits=user_habits,
        selected_date=selected_date,
        all_dates=all_dates,
        today=today,
        username=user["username"] if user else "User",
        is_oauth_user=session.get("auth_method") == "google",
        tracker_type="vices"
    )


@vices_bp.route("/add", methods=["POST"])
@login_required
def add():
    """Add a vice entry"""
    user_id = session["user_id"]
    vice_type_id = request.form.get("vice_type_id", "").strip()
    quantity = request.form.get("quantity", "").strip()
    entry_date = request.form.get("entry_date", date.today().isoformat())
    notes = request.form.get("notes", "").strip()

    if not vice_type_id or not quantity:
        flash("Habit type and quantity are required.", "error")
        return redirect(url_for("vices.index", date=entry_date))

    try:
        vice_type_id = int(vice_type_id)
        quantity = float(quantity)
        
        if quantity <= 0:
            raise ValueError
            
        # Check if it's a system vice type
        vice_type = database.get_vice_type_by_id(vice_type_id)
        if vice_type:
            database.add_vice_entry(user_id, vice_type_id=vice_type_id, quantity=quantity, entry_date=entry_date, notes=notes)
            flash(f"Added {quantity} {vice_type['unit']} of {vice_type['name']}", "success")
        else:
            # Check if it's a custom user habit
            habit = database.get_user_habit_by_id(vice_type_id, user_id)
            if habit:
                database.add_vice_entry(user_id, habit_id=vice_type_id, quantity=quantity, entry_date=entry_date, notes=notes)
                flash(f"Added {quantity} {habit['unit']} of {habit['name']}", "success")
            else:
                flash("Invalid habit type.", "error")
                return redirect(url_for("vices.index", date=entry_date))
            
    except ValueError:
        flash("Quantity must be a positive number.", "error")
        return redirect(url_for("vices.index", date=entry_date))

    return redirect(url_for("vices.index", date=entry_date))


@vices_bp.route("/delete/<int:entry_id>", methods=["POST"])
@login_required
def delete(entry_id):
    """Delete a vice entry"""
    user_id = session["user_id"]
    entry_date = request.form.get("entry_date", date.today().isoformat())
    database.delete_vice_entry(entry_id, user_id)
    flash("Vice entry deleted successfully.", "success")
    return redirect(url_for("vices.index", date=entry_date))


@vices_bp.route("/habit/create", methods=["POST"])
@login_required
def create_habit():
    """Create a new custom habit"""
    user_id = session["user_id"]
    name = request.form.get("habit_name", "").strip()
    unit = request.form.get("habit_unit", "").strip()
    icon = request.form.get("habit_icon", "📌").strip()
    description = request.form.get("habit_description", "").strip()
    color = request.form.get("habit_color", "purple").strip()

    if not name or not unit:
        flash("Habit name and unit are required.", "error")
        return redirect(url_for("vices.index"))

    try:
        habit_id = database.create_user_habit(user_id, name, unit, icon, description, color)
        flash(f"Habit '{name}' created successfully!", "success")
    except Exception as e:
        flash(f"Error creating habit: {str(e)}", "error")
    
    return redirect(url_for("vices.index"))


@vices_bp.route("/habit/<int:habit_id>/delete", methods=["POST"])
@login_required
def delete_habit(habit_id):
    """Delete a custom habit"""
    user_id = session["user_id"]
    
    try:
        database.delete_user_habit(habit_id, user_id)
        flash("Habit deleted successfully.", "success")
    except Exception as e:
        flash(f"Error deleting habit: {str(e)}", "error")
    
    return redirect(url_for("vices.index"))


@vices_bp.route("/types", methods=["GET"])
@login_required
def get_types():
    """Get all vice types as JSON"""
    vice_types = database.get_all_vice_types()
    return jsonify(vice_types)


@vices_bp.route("/stats/<path:date_range>", methods=["GET"])
@login_required
def stats(date_range):
    """Get vice statistics for a date range"""
    user_id = session["user_id"]
    # TODO: Implement statistics/analytics
    # This can include weekly/monthly summaries, trends, etc.
    return jsonify({"message": "Statistics endpoint - to be implemented"})
