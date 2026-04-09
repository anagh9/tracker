import os
import tempfile
import unittest

import database
from services.calorie_goals import CalorieGoalService


class FakeForm:
    def __init__(self, values):
        self.values = values

    def get(self, key, default=None):
        return self.values.get(key, default)


class CalorieGoalServiceTest(unittest.TestCase):
    def setUp(self):
        self.original_db_name = database.DB_NAME
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        database.DB_NAME = self.db_path
        database.init_db()
        self.user_id = database.create_user("calorie_user", "calorie@example.com", "hash")

    def tearDown(self):
        database.DB_NAME = self.original_db_name
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_save_profile_from_form_persists_target(self):
        form = FakeForm({
            "calorie_goal_type": "fat_loss",
            "calorie_sex": "male",
            "calorie_age": "30",
            "calorie_height_cm": "180",
            "calorie_weight_kg": "85",
            "calorie_activity_level": "moderately_active",
        })

        profile = CalorieGoalService.save_profile_from_form(self.user_id, form)
        saved = database.get_calorie_profile(self.user_id)

        self.assertEqual("fat_loss", saved["goal_type"])
        self.assertEqual(profile["target_calories"], saved["target_calories"])
        self.assertLess(saved["target_calories"], saved["tdee"])

    def test_validate_profile_input_rejects_missing_fields(self):
        with self.assertRaises(ValueError):
            CalorieGoalService.validate_profile_input({
                "goal_type": "maintenance",
                "sex": "female",
                "age": "",
                "height_cm": "165",
                "weight_kg": "60",
                "activity_level": "lightly_active",
            })


if __name__ == "__main__":
    unittest.main()
