# Tracker App - Modular Refactoring Documentation

## Overview
The Calorie & Vices Tracker application has been refactored from a monolithic structure into a modular, scalable blueprint-based architecture following Flask best practices.

## Architecture Changes

### Before Refactoring
```
app.py                  # All routes, logic, and configuration
database.py             # Database functions
templates/
  ├── dashboard.html   # Single dashboard for calorie tracking
  ├── login.html
  ├── base.html
  └── ...
```

### After Refactoring
```
app.py                  # Minimal entry point using app factory pattern
config.py               # Configuration management
utils.py                # Shared utilities and decorators
database.py             # Expanded with vices tracker tables
routes/
  ├── __init__.py      # Blueprint registration
  ├── auth.py          # Authentication (login, signup, OAuth, password)
  ├── calorie.py       # Calorie tracker endpoints
  ├── vices.py         # Vices tracker endpoints
  ├── dashboard.py     # Dashboard with tracker switching
  └── ...
templates/
  ├── base.html        # Base template
  ├── dashboard.html   # Tracker switcher (main entry point)
  ├── auth/
  │   └── login.html
  ├── calorie/
  │   └── dashboard.html  # Calorie tracker interface
  └── vices/
      └── dashboard.html  # Vices tracker interface
```

## Key Components

### 1. Configuration Module (`config.py`)
- Centralized configuration management
- Environment-based settings (Development, Production, Testing)
- All OAuth and OpenAI settings in one place

### 2. Utilities Module (`utils.py`)
- `login_required()` decorator for route protection
- `get_timezone()` function for timezone handling
- `get_today()` and `get_today_iso()` for date operations

### 3. Blueprint Structure (`routes/`)

#### Auth Blueprint (`routes/auth.py`)
Routes:
- `/auth/login` - User login (POST/GET)
- `/auth/logout` - Logout (GET)
- `/auth/google` - Google OAuth initiation (GET)
- `/auth/google/callback` - OAuth callback (GET)
- `/auth/change-password` - Password change (POST)

#### Calorie Blueprint (`routes/calorie.py`)
Routes:
- `/calorie/` - Dashboard (GET)
- `/calorie/add` - Add entry (POST)
- `/calorie/delete/<id>` - Delete entry (POST)
- `/calorie/export` - Export to Excel (GET)
- `/calorie/suggest-food` - AI food suggestion (POST)

#### Vices Blueprint (`routes/vices.py`)
Routes:
- `/vices/` - Dashboard (GET)
- `/vices/add` - Add vice entry (POST)
- `/vices/delete/<id>` - Delete entry (POST)
- `/vices/types` - Get vice types (GET)
- `/vices/stats/<date_range>` - Statistics (GET)

#### Dashboard Blueprint (`routes/dashboard.py`)
Routes:
- `/` - Main dashboard with tracker switcher (GET)

### 4. Database Schema Enhancements

**New Tables for Vices Tracking:**

```sql
vice_types (
  id, name, unit, description, icon
)

vices (
  id, user_id, vice_type_id, quantity, 
  entry_date, notes, created_at
)
```

**Default Vice Types:**
- Cigarettes (count)
- Alcohol (ml)
- Coffee (count)

### 5. Template Structure

**Main Entry Point:** `/` - Tracker switcher dashboard
- Shows both Calorie and Vices trackers
- Users choose which one to view
- Features overview section

**Calorie Tracker:** `/calorie/` - Full-featured calorie tracking
- Daily entry management
- AI-powered food suggestions
- Pie chart analytics
- Export functionality
- Password change modal

**Vices Tracker:** `/vices/` - Habit monitoring
- Track multiple vice types
- View summaries for each vice
- Daily logging and history
- Notes field for additional context

## Benefits of This Architecture

✅ **Modularity**: Each feature is isolated in its own blueprint
✅ **Scalability**: Easy to add new trackers (fitness, water intake, etc.)
✅ **Maintainability**: Clear code organization and separation of concerns
✅ **Reusability**: Shared utilities and decorators across blueprints
✅ **Configuration**: Centralized settings management
✅ **Testing**: Blueprint isolation enables easier unit testing
✅ **Extensibility**: New routes and templates can be added without affecting existing code

## Database Functions for Vices

### Vice Type Functions
- `get_all_vice_types()` - List all available vice types
- `get_vice_type_by_id(id)` - Get vice type by ID
- `get_vice_type_by_name(name)` - Get vice type by name

### Vice Entry Functions
- `add_vice_entry(user_id, type_id, quantity, date, notes)` - Log a vice
- `get_vices_by_date(user_id, date)` - Get entries for a date
- `delete_vice_entry(entry_id, user_id)` - Remove an entry
- `get_vice_dates(user_id)` - Get all dates with entries
- `get_vice_summary(user_id, date)` - Get summary stats for a date

## Migration Guide

### For Existing Users
1. No data loss - all existing calorie data is preserved
2. Old routes still work via blueprints (with prefixes)
3. Dashboard is now a tracker switcher - click to access calorie tracker

### URL Changes
| Old Route | New Route |
|-----------|-----------|
| `/` | `/calorie/` (for calorie tracker) |
| `/add` | `/calorie/add` |
| `/delete/<id>` | `/calorie/delete/<id>` |
| `/export` | `/calorie/export` |
| `/logout` | `/auth/logout` |
| `/change-password` | `/auth/change-password` |
| `/suggest-food` | `/calorie/suggest-food` |

## Running the Application

```bash
# Install dependencies (if not already done)
pip install -r requirements.txt

# Run the application
python3 app.py

# Application starts at http://localhost:5000
# Main entry point: Dashboard for tracker selection
```

## Future Enhancements

The modular architecture enables easy addition of:
- Fitness tracker (workouts, steps, calories burned)
- Water intake tracker
- Sleep tracker
- Meditation/mindfulness tracker
- Vehicle mileage tracker
- Expense tracker

Simply create a new blueprint following the existing pattern and register it in `routes/__init__.py`.

## Files Modified/Created

**Created:**
- `config.py` - Configuration management
- `utils.py` - Shared utilities
- `routes/__init__.py` - Blueprint registration
- `routes/auth.py` - Authentication blueprint
- `routes/calorie.py` - Calorie tracker blueprint
- `routes/vices.py` - Vices tracker blueprint
- `routes/dashboard.py` - Dashboard blueprint
- `templates/auth/login.html` - Auth login template
- `templates/calorie/dashboard.html` - Calorie tracker template
- `templates/vices/dashboard.html` - Vices tracker template

**Modified:**
- `app.py` - Simplified to app factory pattern
- `database.py` - Added vices tracker tables and functions
- `templates/dashboard.html` - New tracker switcher dashboard

**Unchanged:**
- `requirements.txt` - All dependencies
- `.env` - Environment variables
- `templates/base.html` - Base template
- All user data and calorie entries

