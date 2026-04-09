"""
Dashboard Routes Blueprint - Unified Scalable Dashboard
Aggregates data from all trackers and provides gamification/insights
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from datetime import date
import database
from utils import login_required
from services import (
    GamificationEngine,
    StreakTracker,
    SmartInsights,
    BehaviorAnalysis,
    PersonalizationService,
    CalorieGoalService,
)

dashboard_bp = Blueprint('dashboard', __name__)


def _aggregate_tracker_data(user_id: int, selected_date: str) -> dict:
    """
    Aggregate data from all available trackers for the dashboard
    Designed to easily accommodate new trackers
    """
    tracker_data = {}

    # Calorie tracker data
    try:
        calorie_profile = CalorieGoalService.get_profile(user_id)
        calorie_entries = list(database.get_entries_by_date(user_id, selected_date))
        calorie_total = database.get_total_calories(user_id, selected_date)
        
        # Handle both integer and dict return types
        total_cals = calorie_total if isinstance(calorie_total, int) else (calorie_total.get("total", 0) if calorie_total else 0)
        
        target_calories = calorie_profile["target_calories"] if calorie_profile else 2000
        tracker_data["calorie"] = {
            "tracked": len(calorie_entries) > 0,
            "total": total_cals,
            "target": target_calories,
            "adherence": min(100, int((total_cals / target_calories * 100) if total_cals else 0)),
            "entries_count": len(calorie_entries),
            "icon": "🔥",
            "name": "Calorie Tracker",
            "url": "/calorie/",
            "goal_type": calorie_profile["goal_type"] if calorie_profile else None,
            "goal_label": calorie_profile["goal_label"] if calorie_profile else "Maintenance",
            "remaining": max(0, target_calories - total_cals),
        }
    except Exception as e:
        tracker_data["calorie"] = {"tracked": False, "total": 0, "error": str(e)}

    # Vices/Habits tracker data
    try:
        vice_entries = database.get_vices_by_date(user_id, selected_date)
        vice_summary = database.get_vice_summary(user_id, selected_date)
        avoided_count = len([v for v in vice_entries if v])  # Count tracked entries
        
        tracker_data["vices"] = {
            "tracked": len(vice_entries) > 0,
            "entries_count": len(vice_entries),
            "avoided_count": avoided_count,
            "total_tracked": len(vice_summary) if vice_summary else 0,
            "icon": "📉",
            "name": "Habits Tracker",
            "url": "/vices/",
        }
    except Exception as e:
        tracker_data["vices"] = {"tracked": False, "entries_count": 0, "error": str(e)}

    return tracker_data


def _get_today_tracker_stats(user_id: int) -> list:
    """
    Get today's stats for each tracker for display cards
    """
    selected_date = date.today().isoformat()
    tracker_stats = []

    # Calorie stats
    try:
        calorie_profile = CalorieGoalService.get_profile(user_id)
        calorie_entries = list(database.get_entries_by_date(user_id, selected_date))
        calorie_total = database.get_total_calories(user_id, selected_date)
        
        # Handle both integer and dict return types
        total_cals = calorie_total if isinstance(calorie_total, int) else (calorie_total.get("total", 0) if calorie_total else 0)
        
        target_calories = calorie_profile["target_calories"] if calorie_profile else 2000
        tracker_stats.append({
            "id": "calorie",
            "name": "Calories",
            "icon": "🔥",
            "value": total_cals,
            "unit": "kcal",
            "target": target_calories,
            "percentage": min(100, int((total_cals / target_calories * 100) if total_cals else 0)),
            "color": "orange",
            "url": "/calorie/",
        })
    except:
        pass

    # Vices stats
    try:
        vice_entries = database.get_vices_by_date(user_id, selected_date)
        tracker_stats.append({
            "id": "vices",
            "name": "Habits Logged",
            "icon": "📊",
            "value": len(vice_entries),
            "unit": "entries",
            "target": 3,
            "percentage": min(100, int((len(vice_entries) / 3 * 100))),
            "color": "blue",
            "url": "/vices/",
        })
    except:
        pass

    return tracker_stats


@dashboard_bp.route("/", methods=["GET"])
@login_required
def tracker_dashboard():
    """Main unified dashboard with gamification and insights"""
    user_id = session["user_id"]
    if PersonalizationService.needs_onboarding(user_id):
        return redirect(url_for("onboarding.index"))

    user = database.get_user_by_id(user_id)
    selected_date = date.today().isoformat()

    # Aggregate tracker data
    tracker_data = _aggregate_tracker_data(user_id, selected_date)
    
    # Initialize streak data (mock for now, extensible)
    tracker_data["streak"] = 5  # Mock streak data

    # Calculate gamification score
    daily_score = GamificationEngine.calculate_daily_score(tracker_data)

    # Get streaks and achievements
    streaks = StreakTracker.get_user_streaks(user_id)
    achievements = StreakTracker.get_achievements(user_id)

    # Generate smart insights
    daily_insights = SmartInsights.generate_daily_insights(user_id, tracker_data)
    behavior_summary = BehaviorAnalysis.get_behavior_summary(user_id)
    weekly_overview = BehaviorAnalysis.get_weekly_overview(user_id)
    comparison = BehaviorAnalysis.get_comparison(user_id)

    # Get today's tracker stats
    dashboard_context = PersonalizationService.build_dashboard_context(
        user_id=user_id,
        tracker_data=tracker_data,
        today_stats=_get_today_tracker_stats(user_id),
    )

    return render_template(
        "dashboard.html",
        user=user,
        username=user["username"] if user else "User",
        is_oauth_user=session.get("auth_method") == "google",
        available_trackers=dashboard_context["available_trackers"],
        today_stats=dashboard_context["today_stats"],
        onboarding_profile=dashboard_context["profile"],
        preferences=dashboard_context["preferences"],
        daily_score=daily_score,
        streaks=streaks,
        achievements=achievements,
        daily_insights=daily_insights,
        behavior_summary=behavior_summary,
        weekly_overview=weekly_overview,
        comparison=comparison,
        selected_date=selected_date,
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
