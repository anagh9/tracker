# Quick Start Guide - Dashboard Features

## For Developers: Adding a New Tracker

### Step 1: Extend Data Aggregation (routes/dashboard.py)

```python
def _aggregate_tracker_data(user_id: int, selected_date: str) -> dict:
    # Add this block
    try:
        workout_data = database.get_workouts_by_date(user_id, selected_date)
        total_minutes = sum(w['duration'] for w in workout_data)
        tracker_data["workout"] = {
            "tracked": len(workout_data) > 0,
            "total": total_minutes,
            "entries_count": len(workout_data),
            "icon": "🏃",
            "name": "Workout Tracker",
            "url": "/workout/",
        }
    except Exception as e:
        tracker_data["workout"] = {"tracked": False, "error": str(e)}
```

### Step 2: Add to Stats Display

```python
def _get_today_tracker_stats(user_id: int) -> list:
    # Add this block
    try:
        workout_data = database.get_workouts_by_date(user_id, selected_date)
        total_minutes = sum(w['duration'] for w in workout_data)
        tracker_stats.append({
            "id": "workout",
            "name": "Workout Time",
            "icon": "🏃",
            "value": total_minutes,
            "unit": "minutes",
            "target": 30,
            "percentage": min(100, int((total_minutes / 30 * 100))),
            "color": "green",
            "url": "/workout/",
        })
    except:
        pass
```

### Step 3: Add to Available Trackers

```python
available_trackers = [
    # ... existing ...
    {
        "id": "workout",
        "name": "Workout Tracker",
        "icon": "🏃",
        "description": "Track your exercises and stay fit.",
        "url": "/workout/",
        "color": "green",
    }
]
```

### Step 4: Update Gamification Scoring

```python
# In gamification.py, update calculate_daily_score()

# Add to the tracker_data dictionary
if "workout" in tracker_data and tracker_data["workout"]:
    workout_score = GamificationEngine._score_workout(tracker_data["workout"])
    breakdown["workout"] = workout_score
    score += workout_score

# Add the scoring method to GamificationEngine class
@staticmethod
def _score_workout(workout_data: dict) -> int:
    """Score workout tracking (max 20 points)"""
    if not workout_data:
        return 0
    
    score = 0
    
    # 10 points for logging
    if workout_data.get("tracked"):
        score += 10
    
    # Up to 10 points for duration
    duration = workout_data.get("total", 0)
    if duration >= 30:  # Target is 30 minutes
        score += 10
    elif duration > 0:
        score += int((duration / 30) * 10)
    
    return min(score, 20)
```

### Step 5: Create Database Functions

```python
# In database.py, add:

def get_workouts_by_date(user_id: int, date_str: str) -> list:
    """Get all workout entries for a user on a specific date"""
    conn = get_connection()
    cursor = conn.execute(
        "SELECT * FROM workouts WHERE user_id = ? AND workout_date = ? ORDER BY created_at DESC",
        (user_id, date_str)
    )
    workouts = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return workouts
```

### Step 6: Create Tracker Blueprint

Create `routes/workout.py`:

```python
from flask import Blueprint, render_template, session
from utils import login_required
import database

workout_bp = Blueprint('workout', __name__, url_prefix='/workout')

@workout_bp.route('/', methods=['GET'])
@login_required
def index():
    user_id = session['user_id']
    # Your workout dashboard logic
    return render_template('workout/dashboard.html', ...)
```

### Step 7: Register Blueprint

In `routes/__init__.py`:

```python
from .workout import workout_bp

def register_blueprints(app):
    # ... existing ...
    app.register_blueprint(workout_bp)
```

---

## For AI Integration: Adding OpenAI Insights

### 1. Update Environment

```bash
# Add to requirements.txt
openai>=0.27.0

# Set environment variable
export OPENAI_API_KEY=your_key_here
```

### 2. Implement AI Insights

```python
# In insights.py, replace mock methods with real API calls

from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@staticmethod
def _get_primary_insight(tracker_data: dict) -> dict:
    """Get AI-generated primary insight"""
    
    # Prepare context about user activity
    context = f"""
    User tracking data today:
    - Calories: {tracker_data.get('calorie', {}).get('total')} kcal
    - Habits logged: {tracker_data.get('vices', {}).get('entries_count')} entries
    - Streak: {tracker_data.get('streak')} days
    
    Generate ONE primary insight about their discipline and behavior.
    Return as JSON: {{"title": "...", "description": "...", "icon": "..."}}
    """
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a wellness coach"},
            {"role": "user", "content": context}
        ]
    )
    
    # Parse and return the AI response
    import json
    result = json.loads(response.choices[0].message.content)
    return result
```

### 3. Add Behavior Analysis

```python
@staticmethod
def _generate_insights_list(tracker_data: dict) -> list:
    """Generate AI-powered insights from user behavior"""
    
    # Get historical data
    # Use OpenAI to analyze patterns
    # Return actionable insights
    
    context = """
    Analyze this user's tracking behavior and generate 3 key insights.
    Focus on: consistency, patterns, and areas for improvement.
    """
    
    # Call OpenAI API
    # Format and return results
    pass
```

### 4. Test AI Integration

```python
# Add to tests
def test_ai_insights():
    tracker_data = {"calorie": {...}, "vices": {...}}
    insights = SmartInsights.generate_daily_insights(1, tracker_data)
    
    assert insights['primary_insight']['title']
    assert len(insights['insights_list']) > 0
    assert len(insights['recommendations']) > 0
```

---

## Configuration Reference

### Gamification Thresholds

```python
# gamification.py - Adjust these values

ACHIEVEMENT_LEVELS = {
    1: {"min_score": 0, "title": "Novice", "badge": "🌱"},
    2: {"min_score": 100, "title": "Committed", "badge": "🔥"},
    3: {"min_score": 300, "title": "Dedicated", "badge": "⛓️"},
    4: {"min_score": 500, "title": "Master", "badge": "👑"},
}

# Score weights (total = 100)
# Calorie: 40 points max
# Vices: 30 points max
# Consistency: 20 points max
# Streak: 10 points max
```

### Dashboard Colors

```python
# routes/dashboard.py - Color assignments

color_map = {
    "calorie": "orange",
    "vices": "blue", 
    "workout": "green",
    "meditation": "purple",
    "sleep": "indigo",
}
```

### Tracker Display Order

```python
# routes/dashboard.py

available_trackers = [
    # Order matters for display
    # Primary trackers first
]
```

---

## Testing Checklist

- [ ] New tracker data aggregates correctly
- [ ] Stats card displays proper values
- [ ] Score calculation includes new tracker
- [ ] Template renders without errors
- [ ] Responsive design works on mobile
- [ ] AI integration doesn't break fallback
- [ ] Error handling catches exceptions
- [ ] Database queries are optimized

---

## Performance Tips

1. **Cache Daily Scores**
   ```python
   # Score doesn't change often, cache for 1 hour
   from functools import lru_cache
   
   @lru_cache(maxsize=128)
   def get_cached_score(user_id, date):
       ...
   ```

2. **Lazy Load Insights**
   ```python
   # Load insights via AJAX if needed
   @dashboard_bp.route("/insights/<int:user_id>")
   def get_insights(user_id):
       return jsonify(SmartInsights.generate_daily_insights(...))
   ```

3. **Precompute Weekly Stats**
   ```python
   # Cache weekly stats overnight
   # Regenerate at midnight
   ```

---

## Monitoring & Logging

```python
import logging

logger = logging.getLogger(__name__)

# In routes that aggregate data
logger.info(f"Dashboard loaded for user {user_id}")
logger.error(f"Tracker aggregation failed: {tracker_name}")

# In gamification
logger.debug(f"Score calculation: {breakdown}")
```

---

## Troubleshooting

### Problem: New Tracker Not Showing
- Check database function returns data
- Verify tracker added to available_trackers
- Check template for typos in variable names

### Problem: Score Stays at 0
- Verify tracker_data has "tracked": True
- Check gamification scoring for new tracker
- Ensure database queries return valid data

### Problem: AI Insights Fail
- Check OPENAI_API_KEY environment variable
- Verify API quota not exceeded
- Add fallback to mock data

### Problem: Performance Degrades
- Profile database queries
- Consider caching insights
- Lazy load secondary information

---

## Resources

- [Complete Dashboard Redesign Documentation](./DASHBOARD_REDESIGN.md)
- [Visual Dashboard Structure](./DASHBOARD_VISUAL.md)
- [API Documentation](./API_DOCS.md)
