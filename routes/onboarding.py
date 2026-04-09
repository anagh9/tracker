"""
Onboarding routes for collecting user goals and interests.
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

import database
from services import PersonalizationService
from utils import login_required

onboarding_bp = Blueprint("onboarding", __name__, url_prefix="/onboarding")


@onboarding_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Collect onboarding preferences and persist personalization settings."""
    user_id = session["user_id"]
    user = database.get_user_by_id(user_id)

    if request.method == "POST":
        primary_goal = request.form.get("primary_goal", "").strip()
        experience_level = request.form.get("experience_level", "").strip()

        if not primary_goal or not experience_level:
            flash("Please answer the goal and experience questions before continuing.", "error")
        else:
            try:
                PersonalizationService.save_onboarding(user_id, request.form)
                flash("Your dashboard has been personalized.", "success")
                return redirect(url_for("dashboard.tracker_dashboard"))
            except ValueError as exc:
                flash(str(exc), "error")

    preferences = PersonalizationService.get_user_preferences(user_id)
    onboarding_context = PersonalizationService.get_onboarding_context(preferences)

    return render_template(
        "onboarding.html",
        username=user["username"] if user else "User",
        is_oauth_user=session.get("auth_method") == "google",
        is_editing=preferences.get("onboarding_completed"),
        **onboarding_context,
    )
