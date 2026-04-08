"""
Dashboard Routes Blueprint
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import date
import database
from utils import login_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/", methods=["GET"])
@login_required
def tracker_dashboard():
    """Main dashboard with tracker selection"""
    user_id = session["user_id"]
    user = database.get_user_by_id(user_id)
    tracker_type = request.args.get("tracker", "calorie")

    # Available trackers
    available_trackers = [
        {
            "id": "calorie",
            "name": "Calorie Tracker",
            "icon": "🔥",
            "description": "Track your daily calorie intake",
            "url": "/calorie/",
        },
        {
            "id": "vices",
            "name": "Vices Tracker",
            "icon": "⚠️",
            "description": "Monitor your habits and vices",
            "url": "/vices/",
        }
    ]

    return render_template(
        "dashboard.html",
        user=user,
        username=user["username"] if user else "User",
        is_oauth_user=session.get("auth_method") == "google",
        tracker_type=tracker_type,
        available_trackers=available_trackers
    )


@dashboard_bp.route("/switch-tracker", methods=["POST"])
@login_required
def switch_tracker():
    """Switch between different trackers"""
    tracker = request.form.get("tracker", "calorie")
    
    # Redirect to the appropriate tracker
    if tracker == "calorie":
        return redirect(url_for("calorie.index"))
    elif tracker == "vices":
        return redirect(url_for("vices.index"))
    else:
        flash("Unknown tracker type.", "error")
        return redirect(url_for("dashboard.tracker_dashboard"))
