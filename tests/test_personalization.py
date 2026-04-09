import os
import tempfile
import unittest

import database
from services.personalization import PersonalizationService


class FakeForm:
    def __init__(self, values):
        self.values = values

    def get(self, key, default=None):
        value = self.values.get(key, default)
        if isinstance(value, list):
            return value[0] if value else default
        return value

    def getlist(self, key):
        value = self.values.get(key, [])
        if isinstance(value, list):
            return value
        return [value]


class PersonalizationServiceTest(unittest.TestCase):
    def setUp(self):
        self.original_db_name = database.DB_NAME
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        database.DB_NAME = self.db_path
        database.init_db()
        self.user_id = database.create_user("tester", "tester@example.com", "hash")

    def tearDown(self):
        database.DB_NAME = self.original_db_name
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_smoking_focus_prioritizes_habits_tracker(self):
        form = FakeForm({
            "primary_goal": "reduce_habits",
            "experience_level": "just_starting",
            "selected_trackers": ["vices"],
            "focus_habits": ["smoking"],
        })

        PersonalizationService.save_onboarding(self.user_id, form)
        preferences = database.get_user_preferences(self.user_id)

        self.assertTrue(preferences["onboarding_completed"])
        self.assertIn("vices", preferences["selected_trackers"])
        self.assertEqual("vices", preferences["dashboard_preferences"]["priority_trackers"][0])

    def test_dashboard_context_marks_priority_cards(self):
        database.save_user_preferences(
            user_id=self.user_id,
            primary_goal="improve_nutrition",
            experience_level="some_experience",
            selected_trackers=["calorie", "vices"],
            focus_habits=["meals"],
            dashboard_preferences={
                "priority_trackers": ["calorie", "vices"],
                "focus_summary": "Your dashboard is tuned for meals.",
            },
            onboarding_completed=True,
        )

        context = PersonalizationService.build_dashboard_context(
            user_id=self.user_id,
            tracker_data={
                "calorie": {"tracked": True},
                "vices": {"tracked": False},
            },
            today_stats=[
                {"id": "calorie", "name": "Calories", "color": "orange"},
                {"id": "vices", "name": "Habits Logged", "color": "blue"},
            ],
        )

        self.assertEqual("calorie", context["available_trackers"][0]["id"])
        self.assertTrue(context["available_trackers"][0]["is_priority"])
        self.assertEqual("Highlighted for meal tracking", context["available_trackers"][0]["highlight_reason"])
        self.assertEqual("Improve nutrition", context["profile"]["goal_label"])


if __name__ == "__main__":
    unittest.main()
