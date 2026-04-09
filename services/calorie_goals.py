"""
Calorie goal calculation and persistence service.
"""

import database


class CalorieGoalService:
    """Calculates and stores daily calorie targets."""

    GOAL_OPTIONS = [
        {"value": "fat_loss", "label": "Fat loss", "description": "Create a sustainable calorie deficit."},
        {"value": "maintenance", "label": "Maintenance", "description": "Keep your current weight steady."},
        {"value": "muscle_gain", "label": "Muscle gain", "description": "Support gradual lean mass gain."},
    ]

    SEX_OPTIONS = [
        {"value": "male", "label": "Male"},
        {"value": "female", "label": "Female"},
    ]

    ACTIVITY_LEVELS = [
        {"value": "sedentary", "label": "Sedentary", "description": "Little or no exercise", "multiplier": 1.2},
        {"value": "lightly_active", "label": "Lightly active", "description": "Exercise 1-3 days per week", "multiplier": 1.375},
        {"value": "moderately_active", "label": "Moderately active", "description": "Exercise 3-5 days per week", "multiplier": 1.55},
        {"value": "very_active", "label": "Very active", "description": "Exercise 6-7 days per week", "multiplier": 1.725},
        {"value": "extremely_active", "label": "Extremely active", "description": "Highly physical routine", "multiplier": 1.9},
    ]

    GOAL_ADJUSTMENTS = {
        "fat_loss": -450,
        "maintenance": 0,
        "muscle_gain": 300,
    }

    GOAL_LABELS = {option["value"]: option["label"] for option in GOAL_OPTIONS}
    ACTIVITY_LABELS = {option["value"]: option["label"] for option in ACTIVITY_LEVELS}
    ACTIVITY_MULTIPLIERS = {option["value"]: option["multiplier"] for option in ACTIVITY_LEVELS}

    @classmethod
    def get_form_context(cls, profile=None):
        """Return template-friendly calorie setup options."""
        profile = profile or {}
        return {
            "calorie_goal_options": cls.GOAL_OPTIONS,
            "calorie_sex_options": cls.SEX_OPTIONS,
            "calorie_activity_options": cls.ACTIVITY_LEVELS,
            "calorie_profile": profile,
        }

    @classmethod
    def save_profile_from_form(cls, user_id, form):
        """Validate, calculate, and persist calorie targets."""
        profile_input = {
            "goal_type": form.get("calorie_goal_type", "").strip(),
            "sex": form.get("calorie_sex", "").strip(),
            "age": form.get("calorie_age", "").strip(),
            "height_cm": form.get("calorie_height_cm", "").strip(),
            "weight_kg": form.get("calorie_weight_kg", "").strip(),
            "activity_level": form.get("calorie_activity_level", "").strip(),
        }
        validated = cls.validate_profile_input(profile_input)
        calculated = cls.calculate_targets(validated)
        database.save_calorie_profile(user_id=user_id, **calculated)
        return calculated

    @classmethod
    def validate_profile_input(cls, profile_input):
        """Validate calorie profile fields and normalize types."""
        required_fields = {
            "goal_type": "calorie goal",
            "sex": "sex",
            "age": "age",
            "height_cm": "height",
            "weight_kg": "weight",
            "activity_level": "activity level",
        }

        for field, label in required_fields.items():
            if not profile_input.get(field):
                raise ValueError(f"Please provide your {label} for the calorie calculator.")

        goal_type = profile_input["goal_type"]
        if goal_type not in cls.GOAL_LABELS:
            raise ValueError("Please choose a valid calorie goal.")

        sex = profile_input["sex"]
        if sex not in {"male", "female"}:
            raise ValueError("Please choose a valid sex for calorie calculations.")

        activity_level = profile_input["activity_level"]
        if activity_level not in cls.ACTIVITY_MULTIPLIERS:
            raise ValueError("Please choose a valid activity level.")

        try:
            age = int(profile_input["age"])
            height_cm = float(profile_input["height_cm"])
            weight_kg = float(profile_input["weight_kg"])
        except ValueError as exc:
            raise ValueError("Age, height, and weight must be valid numbers.") from exc

        if age < 18 or age > 100:
            raise ValueError("Age must be between 18 and 100.")
        if height_cm < 120 or height_cm > 250:
            raise ValueError("Height must be between 120 cm and 250 cm.")
        if weight_kg < 30 or weight_kg > 300:
            raise ValueError("Weight must be between 30 kg and 300 kg.")

        return {
            "goal_type": goal_type,
            "sex": sex,
            "age": age,
            "height_cm": height_cm,
            "weight_kg": weight_kg,
            "activity_level": activity_level,
        }

    @classmethod
    def calculate_targets(cls, profile):
        """Calculate BMR, TDEE, and goal-adjusted calorie target."""
        if profile["sex"] == "male":
            bmr = (10 * profile["weight_kg"]) + (6.25 * profile["height_cm"]) - (5 * profile["age"]) + 5
        else:
            bmr = (10 * profile["weight_kg"]) + (6.25 * profile["height_cm"]) - (5 * profile["age"]) - 161

        activity_multiplier = cls.ACTIVITY_MULTIPLIERS[profile["activity_level"]]
        tdee = round(bmr * activity_multiplier)
        target_calories = round(tdee + cls.GOAL_ADJUSTMENTS[profile["goal_type"]])

        return {
            "goal_type": profile["goal_type"],
            "sex": profile["sex"],
            "age": profile["age"],
            "height_cm": profile["height_cm"],
            "weight_kg": profile["weight_kg"],
            "activity_level": profile["activity_level"],
            "activity_multiplier": activity_multiplier,
            "bmr": round(bmr),
            "tdee": tdee,
            "target_calories": max(1200, target_calories),
        }

    @classmethod
    def get_profile(cls, user_id):
        """Get saved calorie profile enriched with labels and helpers."""
        profile = database.get_calorie_profile(user_id)
        if not profile:
            return None

        profile["goal_label"] = cls.GOAL_LABELS.get(profile["goal_type"], "Maintenance")
        profile["activity_label"] = cls.ACTIVITY_LABELS.get(profile["activity_level"], "Active")
        profile["delta_from_tdee"] = profile["target_calories"] - profile["tdee"]
        if profile["delta_from_tdee"] < 0:
            profile["goal_summary"] = f"{abs(profile['delta_from_tdee'])} kcal deficit from maintenance"
        elif profile["delta_from_tdee"] > 0:
            profile["goal_summary"] = f"{profile['delta_from_tdee']} kcal surplus from maintenance"
        else:
            profile["goal_summary"] = "At maintenance calories"
        return profile

    @classmethod
    def get_target_for_user(cls, user_id, default=2000):
        """Get the user's calorie target or a sensible default."""
        profile = cls.get_profile(user_id)
        return profile["target_calories"] if profile else default
