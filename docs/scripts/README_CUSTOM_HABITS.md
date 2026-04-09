# Add Custom Habits Script

Script to quickly populate the database with 20+ sample custom habits for testing the Habits Tracker feature.

## Features

- **26 Predefined Habits**: Exercise, Health, Learning, Creative, Productivity, Personal Care
- **User Selection**: Choose which user to add habits for
- **Duplicate Detection**: Skips habits that already exist for the user
- **Emoji Icons**: Each habit has a relevant emoji
- **Progress Tracking**: Shows real-time feedback as habits are added

## Usage

### Basic Usage

```bash
python3 scripts/add_custom_habits.py
```

### Interactive Prompts

1. The script will list all available users
2. Select a user by number or enter their ID
3. Script will add 20+ custom habits to that user
4. Review the summary of added habits

## Sample Output

```
Available Users:
  1. anagh (ID: 1)
  2. anagh.129 (ID: 2)

Select user number (or enter ID): 1
✓ Selected: anagh (ID: 1)

============================================================
Adding 26 Custom Habits for User ID: 1
============================================================

✓ Added: 💪 Gym Workout (minutes)
✓ Added: 🧘 Yoga (minutes)
✓ Added: 🚶 Walking (steps)
... (more habits)

============================================================
Summary:
  ✓ Added: 23 habits
  ⚠ Skipped/Failed: 3
============================================================
```

## Included Habits

### Exercise & Health (5)
- 🏃 Running - miles
- 💪 Gym Workout - minutes
- 🧘 Yoga - minutes
- 🚶 Walking - steps
- 🏊 Swimming - laps

### Mindfulness & Health (5)
- 🧠 Meditation - minutes
- 😴 Sleep - hours
- 💧 Water Intake - glasses
- 🤸 Stretching - minutes

### Learning & Development (5)
- 📚 Reading - pages
- 🎓 Learning - minutes
- 💻 Coding - minutes
- 🗣️ Language Practice - minutes
- 📝 Journaling - entries

### Creative & Personal (4)
- 🎨 Drawing - minutes
- 🎵 Music Practice - minutes
- ✍️ Writing - words
- 📷 Photography - photos

### Productivity & Organization (4)
- ✅ Task Completion - tasks
- 👥 Meetings - count
- ☎️ Calls - minutes
- 🚀 Project Work - hours

### Personal Care & Habits (3)
- 🚿 Cold Shower - count
- 💆 Skincare - minutes
- 🍳 Cooking - meals
- 🧹 Cleaning - minutes

## What Happens Next?

After running the script:

1. Log into the Tracker app
2. Navigate to **Habits Tracker**
3. View your new habits in the **"Your Habits"** section (left sidebar)
4. Click **"Log Habit"** to start tracking any of these habits
5. Habits appear in the dropdown when logging entries

## Notes

- Habits are stored in the `user_habits` table
- Each habit is unique per user (can't have duplicates per user)
- If you run the script twice for the same user, it will skip existing habits
- To add habits for multiple users, run the script multiple times and select different users

## Editing or Deleting Habits

You can manage habits in the app:

1. Go to Habits Tracker → Sidebar
2. Hover over a habit in **"Your Habits"** section
3. Click **✕** to delete it
4. Or click **"New Habit"** to create custom ones
