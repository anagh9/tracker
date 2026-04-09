"""
User onboarding and tracker personalization services.
"""

import database
from .calorie_goals import CalorieGoalService


class PersonalizationService:
    """Centralizes onboarding questions and dashboard personalization rules."""

    TRACKER_REGISTRY = {
        "calorie": {
            "id": "calorie",
            "name": "Calorie Tracker",
            "icon": "🔥",
            "description": "Track meals, calorie intake, and nutrition patterns.",
            "url": "/calorie/",
            "color": "orange",
            "supports": {"weight", "nutrition", "energy", "meals"},
        },
        "vices": {
            "id": "vices",
            "name": "Habits Tracker",
            "icon": "📉",
            "description": "Monitor smoking, alcohol, caffeine, and custom habits.",
            "url": "/vices/",
            "color": "blue",
            "supports": {"smoking", "alcohol", "caffeine", "habits", "consistency"},
        },
    }

    GOAL_OPTIONS = [
        {"value": "build_awareness", "label": "Build awareness", "description": "Start by noticing patterns before trying to optimize them."},
        {"value": "reduce_habits", "label": "Reduce unhealthy habits", "description": "Focus on smoking, alcohol, and other habits you want to cut back."},
        {"value": "improve_nutrition", "label": "Improve nutrition", "description": "Stay on top of meals, calories, and food choices."},
        {"value": "create_consistency", "label": "Create consistency", "description": "Build routines and keep your tracking streak going."},
    ]

    EXPERIENCE_OPTIONS = [
        {"value": "just_starting", "label": "Just starting"},
        {"value": "some_experience", "label": "Some experience"},
        {"value": "already_consistent", "label": "Already consistent"},
    ]

    TRACKER_OPTIONS = [
        {"value": "calorie", "label": "Meals and calories", "description": "Keep nutrition front and center."},
        {"value": "vices", "label": "Habits and vices", "description": "Track smoking, alcohol, caffeine, and other behaviors."},
    ]

    FOCUS_OPTIONS = [
        {"value": "smoking", "label": "Smoking"},
        {"value": "alcohol", "label": "Alcohol"},
        {"value": "caffeine", "label": "Caffeine"},
        {"value": "meals", "label": "Meals and calories"},
        {"value": "consistency", "label": "Consistency"},
    ]

    FOCUS_LABELS = {
        "smoking": "Smoking",
        "alcohol": "Alcohol",
        "caffeine": "Caffeine",
        "meals": "Meals",
        "consistency": "Consistency",
    }

    GOAL_LABELS = {option["value"]: option["label"] for option in GOAL_OPTIONS}
    EXPERIENCE_LABELS = {option["value"]: option["label"] for option in EXPERIENCE_OPTIONS}

    @classmethod
    def get_onboarding_context(cls, preferences=None):
        """Return template-friendly onboarding options and selected values."""
        preferences = preferences or {}
        return {
            "goal_options": cls.GOAL_OPTIONS,
            "experience_options": cls.EXPERIENCE_OPTIONS,
            "tracker_options": cls.TRACKER_OPTIONS,
            "focus_options": cls.FOCUS_OPTIONS,
            "selected_trackers": preferences.get("selected_trackers", []),
            "focus_habits": preferences.get("focus_habits", []),
            "primary_goal": preferences.get("primary_goal"),
            "experience_level": preferences.get("experience_level"),
            **CalorieGoalService.get_form_context(database.get_calorie_profile(preferences.get("user_id")) if preferences.get("user_id") else None),
        }

    @staticmethod
    def needs_onboarding(user_id):
        """Check whether a user still needs onboarding."""
        return not database.get_user_preferences(user_id).get("onboarding_completed")

    @classmethod
    def get_user_preferences(cls, user_id):
        """Fetch and normalize saved preferences."""
        preferences = database.get_user_preferences(user_id)
        preferences["primary_goal_label"] = cls.GOAL_LABELS.get(preferences.get("primary_goal"), "Personalized plan")
        preferences["experience_level_label"] = cls.EXPERIENCE_LABELS.get(preferences.get("experience_level"), "Getting started")
        preferences["focus_labels"] = [cls.FOCUS_LABELS.get(item, item.title()) for item in preferences.get("focus_habits", [])]
        return preferences

    @classmethod
    def save_onboarding(cls, user_id, form):
        """Persist onboarding answers and derive dashboard priorities."""
        selected_trackers = form.getlist("selected_trackers")
        focus_habits = form.getlist("focus_habits")
        primary_goal = form.get("primary_goal", "").strip()
        experience_level = form.get("experience_level", "").strip()

        if not selected_trackers:
            selected_trackers = ["calorie", "vices"]

        if "smoking" in focus_habits or "alcohol" in focus_habits or "caffeine" in focus_habits:
            if "vices" not in selected_trackers:
                selected_trackers.append("vices")

        if "meals" in focus_habits or primary_goal == "improve_nutrition":
            if "calorie" not in selected_trackers:
                selected_trackers.append("calorie")

        priority_trackers = cls._prioritize_trackers(selected_trackers, focus_habits, primary_goal)
        dashboard_preferences = {
            "priority_trackers": priority_trackers,
            "focus_summary": cls._build_focus_summary(focus_habits, primary_goal),
        }

        if "calorie" in selected_trackers:
            CalorieGoalService.save_profile_from_form(user_id, form)

        database.save_user_preferences(
            user_id=user_id,
            primary_goal=primary_goal or None,
            experience_level=experience_level or None,
            selected_trackers=selected_trackers,
            focus_habits=focus_habits,
            dashboard_preferences=dashboard_preferences,
            onboarding_completed=True,
        )

    @classmethod
    def build_dashboard_context(cls, user_id, tracker_data, today_stats):
        """Build personalized dashboard cards, ordering, and messaging."""
        preferences = cls.get_user_preferences(user_id)
        prioritized_ids = preferences.get("dashboard_preferences", {}).get("priority_trackers") or []
        selected_trackers = preferences.get("selected_trackers") or list(cls.TRACKER_REGISTRY.keys())

        tracker_ids = []
        for tracker_id in prioritized_ids + selected_trackers + list(cls.TRACKER_REGISTRY.keys()):
            if tracker_id in cls.TRACKER_REGISTRY and tracker_id not in tracker_ids:
                tracker_ids.append(tracker_id)

        personalized_trackers = []
        personalized_stats = []
        stats_by_id = {stat["id"]: stat for stat in today_stats}

        for index, tracker_id in enumerate(tracker_ids, start=1):
            base_tracker = dict(cls.TRACKER_REGISTRY[tracker_id])
            tracker_snapshot = tracker_data.get(tracker_id, {})
            base_tracker.update(tracker_snapshot)
            base_tracker["is_priority"] = tracker_id in prioritized_ids[:2]
            base_tracker["priority_rank"] = prioritized_ids.index(tracker_id) + 1 if tracker_id in prioritized_ids else None
            base_tracker["highlight_reason"] = cls._build_highlight_reason(tracker_id, preferences)
            personalized_trackers.append(base_tracker)

            if tracker_id in stats_by_id:
                stat = dict(stats_by_id[tracker_id])
                stat["is_priority"] = base_tracker["is_priority"]
                stat["priority_rank"] = base_tracker["priority_rank"]
                stat["highlight_reason"] = base_tracker["highlight_reason"]
                personalized_stats.append(stat)

        profile = {
            "goal_label": preferences["primary_goal_label"],
            "experience_level_label": preferences["experience_level_label"],
            "focus_labels": preferences["focus_labels"],
            "focus_summary": preferences.get("dashboard_preferences", {}).get("focus_summary")
            or "Your dashboard is arranged around the habits and trackers you care about most.",
        }

        return {
            "available_trackers": personalized_trackers,
            "today_stats": personalized_stats,
            "preferences": preferences,
            "profile": profile,
        }

    @classmethod
    def _prioritize_trackers(cls, selected_trackers, focus_habits, primary_goal):
        scores = {tracker_id: 0 for tracker_id in cls.TRACKER_REGISTRY}

        for tracker_id in selected_trackers:
            scores[tracker_id] += 20

        if primary_goal == "improve_nutrition":
            scores["calorie"] += 40
        if primary_goal == "reduce_habits":
            scores["vices"] += 40
        if primary_goal == "create_consistency":
            scores["calorie"] += 10
            scores["vices"] += 10

        for focus in focus_habits:
            if focus in {"smoking", "alcohol", "caffeine"}:
                scores["vices"] += 25
            if focus == "meals":
                scores["calorie"] += 25
            if focus == "consistency":
                scores["calorie"] += 10
                scores["vices"] += 10

        return sorted(scores, key=lambda tracker_id: (-scores[tracker_id], tracker_id))

    @classmethod
    def _build_focus_summary(cls, focus_habits, primary_goal):
        if not focus_habits and not primary_goal:
            return "Start with the trackers you selected and refine them as your routine evolves."

        focus_labels = [cls.FOCUS_LABELS.get(item, item.title()) for item in focus_habits]
        if focus_labels:
            if len(focus_labels) == 1:
                focus_text = focus_labels[0]
            else:
                focus_text = ", ".join(focus_labels[:-1]) + f" and {focus_labels[-1]}"
            return f"Your dashboard is tuned for {focus_text.lower()} so the most relevant tracker stays within reach."

        return f"Your dashboard is tuned around your goal to {cls.GOAL_LABELS.get(primary_goal, 'stay consistent').lower()}."

    @classmethod
    def _build_highlight_reason(cls, tracker_id, preferences):
        focus_habits = set(preferences.get("focus_habits", []))
        primary_goal = preferences.get("primary_goal")

        if tracker_id == "vices":
            if "smoking" in focus_habits:
                return "Highlighted for smoking tracking"
            if "alcohol" in focus_habits:
                return "Highlighted for alcohol tracking"
            if "caffeine" in focus_habits:
                return "Highlighted for caffeine tracking"
            if primary_goal == "reduce_habits":
                return "Supports your habit reduction goal"

        if tracker_id == "calorie":
            if "meals" in focus_habits:
                return "Highlighted for meal tracking"
            if primary_goal == "improve_nutrition":
                return "Supports your nutrition goal"

        if tracker_id in (preferences.get("dashboard_preferences", {}).get("priority_trackers") or [])[:2]:
            return "Prioritized based on your onboarding choices"

        return "Available as part of your routine"
