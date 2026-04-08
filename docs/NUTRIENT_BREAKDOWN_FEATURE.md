# 🥗 Nutrient Breakdown Feature

## Overview

The Nutrient Breakdown feature uses **OpenAI-powered analysis** to automatically estimate the macronutrient composition (protein, carbohydrates, fats, and fiber) of your daily meals. It displays this information in an interactive chart alongside your calorie tracking.

---

## Features

### 1. **AI-Powered Nutrient Analysis**
- Analyzes all food entries for a selected date
- Uses OpenAI to estimate protein, carbohydrates, fats, and fiber content
- Calculates percentage breakdown based on caloric values:
  - Protein: 4 kcal/gram
  - Carbohydrates: 4 kcal/gram
  - Fats: 9 kcal/gram

### 2. **Interactive Chart**
- **Horizontal Bar Chart**: Shows total grams for each nutrient
- Color-coded nutrients:
  - 🔵 Protein (Blue)
  - 🟢 Carbs (Green)
  - 🟡 Fats (Yellow)
  - 🟣 Fiber (Purple)

### 3. **Detailed Nutrient Breakdown**
- **Total Grams**: Shows exact grams for each macronutrient and fiber
- **Caloric Percentage**: Shows % of total daily calories from each nutrient
- **Analysis Summary**: Brief OpenAI-generated insight about your nutrition

### 4. **Date-Based Analysis**
- Analyzes nutrients for the selected date
- Updates automatically when switching between dates
- Shows loading state while fetching data from OpenAI
- Error handling for API failures

---

## How It Works

### Backend Flow

1. **Request** (`/calorie/nutrient-breakdown`)
   ```
   GET /calorie/nutrient-breakdown?date=YYYY-MM-DD
   ```

2. **Data Preparation**
   - Fetches all calorie entries for the selected date
   - Compiles food items and their calorie counts
   - Prepares prompt with all foods and total calories

3. **OpenAI Analysis**
   - Sends food list to OpenAI with a nutritionist prompt
   - Requests estimation of protein, carbs, fats, and fiber
   - Returns JSON with nutrient values and analysis

4. **Calculation**
   - Converts grams to calories (protein/carbs: ×4, fats: ×9)
   - Calculates percentage of total daily calories
   - Returns formatted response to frontend

### Frontend Flow

1. **Load on Page**
   - `initializeNutrientBreakdown()` runs on page load
   - Fetches nutrient data for current date
   - Shows loading spinner while fetching

2. **Display Chart**
   - Renders horizontal bar chart with Chart.js
   - Each bar represents nutrient in grams
   - Responsive design for mobile/desktop

3. **Show Breakdown**
   - Displays nutrient values in detail card
   - Shows grams and caloric percentage
   - Displays AI-generated analysis

---

## Implementation Details

### New Route: `routes/calorie.py`

```python
@calorie_bp.route("/nutrient-breakdown", methods=["GET"])
@login_required
def nutrient_breakdown():
    # Gets entries for a date
    # Sends to OpenAI for analysis
    # Returns JSON with macronutrients
```

**Response Format:**
```json
{
  "protein": 50,
  "protein_pct": 25,
  "carbs": 200,
  "carbs_pct": 45,
  "fats": 65,
  "fats_pct": 30,
  "fiber": 15,
  "total_calories": 2000,
  "analysis": "Good balance of nutrients. Consider increasing fiber intake.",
  "success": true
}
```

### Template Updates: `templates/calorie/dashboard.html`

**New Chart Container:**
```html
<!-- Nutrient Breakdown Chart -->
<div class="bg-white border border-stone-200 rounded-xl p-6 shadow-sm">
  <p class="text-sm font-semibold text-stone-700 mb-4">🥗 Nutrient Breakdown</p>
  
  <!-- Loading State -->
  <div id="nutrientLoading">Loading...</div>
  
  <!-- Chart -->
  <div id="nutrientChartContainer">
    <canvas id="nutrientChart"></canvas>
  </div>
  
  <!-- Details -->
  <div id="nutrientDetails">
    Protein: 50g (25%)
    Carbs: 200g (45%)
    ...
  </div>
</div>
```

**JavaScript Function:**
```javascript
function initializeNutrientBreakdown() {
  // Fetches nutrient data from backend
  // Initializes Chart.js horizontal bar chart
  // Updates detail cards with values
}
```

---

## Configuration Requirements

### Environment Variables
Ensure your `.env` file contains:
```
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
OPENAI_MODEL=gpt-3.5-turbo  (or gpt-4)
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=500
```

### Config Class
The feature uses `config.py` settings:
```python
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.7))
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", 500))
```

---

## Usage Example

### Scenario: Daily Nutrient Tracking
1. User adds entries throughout the day:
   - Breakfast: Oatmeal with berries (350 kcal)
   - Lunch: Grilled chicken with rice (650 kcal)
   - Dinner: Salmon with vegetables (550 kcal)

2. Nutrient Breakdown is displayed:
   - **Protein**: 120g (24%)
   - **Carbs**: 220g (44%)
   - **Fats**: 65g (32%)
   - **Fiber**: 12g

3. Analysis shows:
   - ✅ Good protein intake for muscle building
   - ⚠️ Consider adding more fiber-rich foods
   - ✅ Fat intake within healthy range

---

## Error Handling

### Scenarios Handled

1. **No Entries for Date**
   ```json
   {
     "protein": 0,
     "carbs": 0,
     "fats": 0,
     "fiber": 0,
     "details": "No entries for this date"
   }
   ```

2. **OpenAI API Key Not Configured**
   ```json
   {
     "error": "OpenAI API key not configured",
     "success": false
   }
   ```

3. **API Response Parsing Error**
   ```json
   {
     "error": "Failed to parse nutrition data",
     "success": false
   }
   ```

4. **Network Error**
   - Shows error message in nutrient chart area
   - Falls back to empty state

### Frontend Error Handling

```javascript
.catch(error => {
  document.getElementById('nutrientError').textContent = 
    'Unable to analyze nutrients';
});
```

---

## Performance Considerations

### API Calls
- **Frequency**: One call per date selection
- **Cost**: ~$0.001 per call (gpt-3.5-turbo)
- **Latency**: 1-3 seconds typically

### Optimization Tips
1. Cache nutrient data per date (future enhancement)
2. Use async/await for better error handling
3. Implement request debouncing for rapid date changes
4. Store nutrient results in database if frequent queries

---

## Integration with Other Features

### Calorie Tracker Dashboard
- Nutrient chart is displayed alongside existing charts
- Updates when date is changed
- Responsive layout adapts to screen size

### Chart Comparison
| Chart | Type | Data | Purpose |
|-------|------|------|---------|
| Food Distribution | Pie | Calories per food | See biggest calorie sources |
| Nutrient Breakdown | Bar | Grams per nutrient | See macronutrient composition |

---

## Future Enhancements

### Planned Features
1. **Nutrient Goals**
   - Set target macronutrient ratios
   - Display progress toward goals
   - Recommendations based on goals

2. **Micronutrient Analysis**
   - Vitamins and minerals
   - Food sources for nutrients
   - Deficiency warnings

3. **Nutrient Database**
   - Store analyzed nutrients in database
   - Enable historical comparisons
   - Generate nutrient trends

4. **Dietary Preferences**
   - Customize analysis for diet type (keto, vegan, etc.)
   - Adjusted macronutrient recommendations
   - Specific nutrient warnings

5. **Export Analysis**
   - Include nutrient breakdown in Excel export
   - Create nutrient reports
   - Share nutrition summaries

---

## Troubleshooting

### Chart Not Showing

**Problem**: Nutrient breakdown chart appears but no data

**Solutions**:
1. Check OpenAI API key in `.env`
2. Verify you have food entries for the date
3. Check browser console for errors
4. Ensure Chart.js is loaded from CDN

### API Error: "Invalid Response Format"

**Problem**: OpenAI returns unexpected format

**Cause**: API response not in expected JSON format

**Solution**:
```python
# Check Config.OPENAI_MODEL is gpt-3.5-turbo or gpt-4
# Verify OPENAI_TEMPERATURE is between 0-1
# Check max_tokens is sufficient (500+)
```

### High API Costs

**Problem**: Too many API calls to nutrient-breakdown

**Solution**:
1. Implement caching (store results by date)
2. Only analyze when user views the date
3. Use batch requests for multiple dates

---

## Code Examples

### Add Custom Nutrient Rules

```python
# In routes/calorie.py, modify OpenAI prompt
system_prompt = """
Analyze nutrition considering keto diet...
Minimize carbs, maximize fats...
"""
```

### Add Nutrient Caching

```python
# Add to database.py
def cache_nutrients(user_id, entry_date, nutrients):
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO nutrient_cache
        (user_id, date, protein, carbs, fats, fiber)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, entry_date, nutrients['protein'], ...))
    conn.commit()
```

### Customize Chart Colors

```javascript
// In template JavaScript
backgroundColor: [
  'rgb(59, 130, 246)',   // Change blue
  'rgb(34, 197, 94)',    // Change green
  'rgb(234, 179, 8)',    // Change yellow
  'rgb(168, 85, 247)'    // Change purple
]
```

---

## Summary

The **Nutrient Breakdown** feature adds AI-powered nutritional analysis to your CalTrack application. It automatically analyzes your daily food intake and provides detailed macronutrient breakdowns with interactive visualizations, helping you track not just calories, but the quality and balance of your nutrition.

✨ **Key Benefit**: Understand not just HOW MUCH you're eating, but WHAT you're eating nutritionally!
