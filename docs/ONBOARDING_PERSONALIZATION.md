# Onboarding Personalization

This project now includes a lightweight onboarding flow that asks users about:

- their primary tracking goal
- their current experience level
- the trackers they want active
- the habits or interests that deserve extra attention
- their calorie goal and body metrics when they enable the calorie tracker

## Architecture

- `routes/onboarding.py` owns the HTTP flow for onboarding
- `services/personalization.py` owns preference parsing, tracker prioritization, and dashboard personalization
- `database.py` persists user preferences in `user_preferences`
- `templates/onboarding.html` renders the onboarding questions
- `templates/dashboard.html` renders the personalized dashboard experience

## Personalization behavior

- Users who select smoking, alcohol, or caffeine automatically get the habits tracker prioritized.
- Users focused on meals or nutrition automatically get the calorie tracker prioritized.
- Users who enable the calorie tracker are asked for fat loss, maintenance, or muscle gain details plus activity/body stats.
- The calorie profile is converted into BMR, TDEE, and a saved daily calorie target that is reused across the dashboard and calorie tracker.
- Dashboard cards and quick access sections are ordered from the saved priority list.
- The personalization layer is registry-based, so new trackers can be added by extending `TRACKER_REGISTRY` and its matching rules.
