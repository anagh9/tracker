# Architecture Overview - Visual Guide

## Application Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interaction                          │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
        ╔═════════════════════════════════════╗
        ║   Main Dashboard  (/)               ║
        ║   Tracker Switcher                  ║
        ║   - Calorie Tracker                 ║
        ║   - Vices Tracker                   ║
        └─────────────────┬────────────────────┘
                 ┌────────┴────────┐
                 │                 │
                 ▼                 ▼
        ┌──────────────────┐  ┌──────────────────┐
        │   Calorie        │  │  Vices           │
        │   Blueprint      │  │  Blueprint       │
        │   (/calorie/*)   │  │  (/vices/*)      │
        │                  │  │                  │
        │ • Dashboard      │  │ • Dashboard      │
        │ • Add Entry      │  │ • Add Entry      │
        │ • Delete Entry   │  │ • Delete Entry   │
        │ • Export         │  │ • Summary Stats  │
        │ • AI Suggest     │  │ • Multiple Types │
        └────────┬─────────┘  └────────┬─────────┘
                 │                     │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │  Shared Components   │
                 │                      │
                 │ • Auth Blueprint     │
                 │ • Database Module    │
                 │ • Utils Module       │
                 │ • Config Module      │
                 └──────────────────────┘
```

## Module Dependencies

```
┌──────────────────────────────────────┐
│          Flask App (app.py)           │
│         [App Factory Pattern]         │
└──────────────────┬───────────────────┘
                   │
        ┌──────────┼──────────┐
        │          │          │
        ▼          ▼          ▼
    ┌────────┐ ┌────────┐ ┌───────────┐
    │ config.py│ database.py│routes/   │
    └────────┘ │          │ __init__.py
               │  [Tables]│ └────┬─────┘
               │          │      │
               │ • users  │    ┌─┴───────────────┐
               │ • entries│    │                 │
               │ • vices  │    ▼                 ▼
               │ • types  │  ┌─────┐  ┌──────┐
               │          │  │auth.py  calorie.py
               │ [+20     │  └─────┘  └──────┘
               │  funcs]  │
               └────────┘   [Functions]
                              • Add
                              • Delete
                              • Export
                              • Stats
                              └────────────┐
                                           │
                                        ┌──┴───────┐
                                        │          │
                                        ▼          ▼
                                    ┌────────┐ ┌────────┐
                                    │ utils │ │templates
                                    └────────┘ └────────┘
```

## Component Interaction

### Request Flow
```
1. User Request
         │
         ▼
   ┌──────────────┐
   │ Flask Router │
   └──────┬───────┘
          │
   ┌──────▼──────────────────┐
   │ Blueprint Handler        │
   │ (Route Handler)          │
   ├───────────────────────────┤
   │ ✓ @login_required check   │
   │ ✓ Input validation        │
   │ ✓ Database operation      │
   │ ✓ Response generation     │
   └──────┬───────────────────┘
          │
   ┌──────▼──────────────────┐
   │ Template Rendering       │
   │ (Jinja2 + Tailwind CSS)  │
   └──────┬───────────────────┘
          │
          ▼
   User Receives Response
```

### Data Flow
```
Blueprint Handler
       │
       ├─→ [Query Parameters]
       │
       ├─→ [Form Data] → Validation
       │                    │
       ├─→ [Session Data]   │
       │                    │
       └─→ [User ID] ────────→ Database Functions
                                   │
          ┌────────────────────────┼────────────────────┐
          │                        │                    │
          ▼                        ▼                    ▼
      [SELECT]              [INSERT/UPDATE]        [DELETE]
          │                        │                    │
          └────────────────────────┼────────────────────┘
                                   │
                                   ▼
                          Database Response
                                   │
                                   ▼
                          Format for Template
```

## Technology Stack

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Layer                        │
├─────────────────────────────────────────────────────────┤
│ • HTML5 Templates (Jinja2)                              │
│ • CSS3 with Tailwind (Responsive Design)                │
│ • JavaScript (Vanilla JS + AJAX)                        │
│ • Chart.js (Data Visualization)                         │
│ • OpenPyXL (Excel Export)                              │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                  Application Layer                       │
├─────────────────────────────────────────────────────────┤
│ • Flask 3.0.3 (Web Framework)                          │
│ • Flask Blueprints (Modular Routes)                    │
│ • Werkzeug (Security - Passwords)                      │
│ • OpenAI API (AI Features)                              │
│ • Python Requests (OAuth, HTTP)                        │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                   Data Layer                             │
├─────────────────────────────────────────────────────────┤
│ • SQLite3 (Database)                                    │
│ • Python sqlite3 (Database Driver)                      │
│ • Row Factory (ORM-like interface)                      │
│ • SQL Queries (CRUD Operations)                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                 Authentication Layer                     │
├─────────────────────────────────────────────────────────┤
│ • Google OAuth 2.0 (Third-party Auth)                  │
│ • Session Management (Flask Sessions)                   │
│ • Password Hashing (Werkzeug generate_password_hash)   │
│ • @login_required Decorator (Route Protection)         │
└─────────────────────────────────────────────────────────┘
```

## Blueprint Structure

```
routes/
├── __init__.py
│   └─ register_blueprints(app)
│      ├─ app.register_blueprint(auth_bp)
│      ├─ app.register_blueprint(calorie_bp, url_prefix='/calorie')
│      ├─ app.register_blueprint(vices_bp, url_prefix='/vices')
│      └─ app.register_blueprint(dashboard_bp)
│
├── auth.py (207 lines)
│   ├─ @auth_bp.route("/login", methods=["GET", "POST"])
│   ├─ @auth_bp.route("/logout", methods=["GET"])
│   ├─ @auth_bp.route("/google", methods=["GET"])
│   ├─ @auth_bp.route("/google/callback", methods=["GET"])
│   └─ @auth_bp.route("/change-password", methods=["POST"])
│
├── calorie.py (175 lines)
│   ├─ @calorie_bp.route("/", methods=["GET"])
│   ├─ @calorie_bp.route("/add", methods=["POST"])
│   ├─ @calorie_bp.route("/delete/<id>", methods=["POST"])
│   ├─ @calorie_bp.route("/export", methods=["GET"])
│   └─ @calorie_bp.route("/suggest-food", methods=["POST"])
│
├── vices.py (102 lines)
│   ├─ @vices_bp.route("/", methods=["GET"])
│   ├─ @vices_bp.route("/add", methods=["POST"])
│   ├─ @vices_bp.route("/delete/<id>", methods=["POST"])
│   ├─ @vices_bp.route("/types", methods=["GET"])
│   └─ @vices_bp.route("/stats/<range>", methods=["GET"])
│
└── dashboard.py (50 lines)
    ├─ @dashboard_bp.route("/", methods=["GET"])
    └─ @dashboard_bp.route("/switch-tracker", methods=["POST"])
```

## Configuration Hierarchy

```
config.py
├── Config (Base Configuration)
│   ├── SECRET_KEY
│   ├── DATABASE
│   ├── TIMEZONE
│   ├── GOOGLE_CLIENT_ID
│   ├── GOOGLE_CLIENT_SECRET
│   ├── GOOGLE_REDIRECT_URI
│   ├── OPENAI_API_KEY
│   └── ... [20+ settings]
│
├── DevelopmentConfig (extends Config)
│   ├── DEBUG = True
│   └── TESTING = False
│
├── ProductionConfig (extends Config)
│   ├── DEBUG = False
│   └── TESTING = False
│
└── TestingConfig (extends Config)
    ├── DEBUG = True
    ├── TESTING = True
    └── DATABASE = ":memory:"
```

## Database Relationships

```
users
├── id (PK)
├── username (UQ)
├── email (UQ)
├── password_hash
└── created_at
    │
    ├──→ (1:M) entries
    │       ├── id (PK)
    │       ├── user_id (FK)
    │       ├── food_item
    │       ├── calories
    │       ├── entry_date
    │       └── created_at
    │
    └──→ (1:M) vices
            ├── id (PK)
            ├── user_id (FK)
            ├── vice_type_id (FK) ──→ vice_types
            │                          ├── id (PK)
            │                          ├── name (UQ)
            │                          ├── unit
            │                          ├── description
            │                          └── icon
            ├── quantity
            ├── entry_date
            ├── notes
            └── created_at
```

## Execution Flow Example

### Adding a Calorie Entry

```
1. User Fills Form
   ├─ food_item: "pizza"
   ├─ calories: "320"
   └─ entry_date: "2026-04-08"

2. Form Submission (POST /calorie/add)
   └─ Router matches blueprint route

3. Blueprint Handler (calorie.py)
   ├─ @login_required decorator checks session
   ├─ Validates form input
   ├─ Converts calories to integer
   └─ Calls database.add_entry(user_id, date, food, calories)

4. Database Operation
   ├─ Creates INSERT query
   ├─ Executes SQL
   ├─ Commits transaction
   └─ Returns

5. Response
   ├─ Redirects to /calorie/?date=2026-04-08
   └─ Flash message: "Added pizza (320 kcal)"

6. New Dashboard Render
   ├─ Fetches entries for date
   ├─ Recalculates total: 1050 kcal
   ├─ Updates chart data
   └─ Shows updated list
```

---

End of Architectural Documentation
