# CalTrack - Calorie Tracker

A modern, responsive web application for tracking daily calorie intake with user authentication, data visualization, and export functionality.

## ✨ Features

### Core Functionality
- 🔐 **Google Sign-In** - Secure authentication with Google OAuth
- 📊 **Dashboard** - Track daily calorie intake with interactive visualizations
- 📈 **Pie Chart Visualization** - See food distribution by calories
- 🧮 **Calorie Calculator** - Calculate daily calorie needs (Mifflin-St Jeor formula)
- 📅 **History** - Browse and select entries from any date
- 💾 **Export** - Download all entries as Excel file
- 📱 **Responsive Design** - Works seamlessly on mobile, tablet, and desktop
- 🎨 **Modern UI** - Clean, minimalist design with smooth animations

### User Management
- Google OAuth 2.0 integration with automatic account creation
- One-click sign-in with Google account
- User-isolated data (each user sees only their entries)
- Automatic username generation from email
- User profile in sidebar

## 📁 Project Structure

```
tracker/
├── app.py                      # Flask application & routes
├── database.py                 # SQLite database management
├── requirements.txt            # Python dependencies
├── calories.db                 # SQLite database
├── README.md                   # This file
│
├── assets/                     # Static assets
│   └── [images]
│
├── scripts/                    # Utility scripts
│   ├── __init__.py
│   ├── load_data.py           # Sample data loader
│   ├── migrate_add_user_id.py              # Migration script (auto)
│   ├── migrate_add_user_id_manual.py       # Migration script (manual)
│   └── MIGRATION.md           # Migration documentation
│
└── templates/                  # HTML templates
    ├── base.html              # Base template with Chart.js
    ├── dashboard.html         # Main dashboard
    ├── login.html             # Login page
    └── signup.html            # Signup page
```

## 🚀 Quick Start

### 1. Prerequisites
Before running CalTrack, you need Google OAuth credentials:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google+ API
4. Create OAuth 2.0 credentials (Web application)
5. Add redirect URI: `http://localhost:5000/auth/google/callback`
6. Copy your Client ID and Client Secret

For detailed instructions, see [GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md)

### 2. Clone & Setup
```bash
git clone <repository-url>
cd tracker
pip install -r requirements.txt
```

### 3. Configure Google OAuth
Create/update `.env` file:
```env
GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='your-client-secret'
GOOGLE_REDIRECT_URI='http://localhost:5000/auth/google/callback'
SECRET_KEY='your-secret-key'
```

### 4. Run the Application
```bash
python app.py
```

Visit `http://127.0.0.1:5000` in your browser.

### 5. Sign In
- Click "Sign in with Google"
- Use your Google account
- Your CalTrack account is created automatically
- Start tracking your calories!

## 🔧 Installation Details

### Prerequisites
- Python 3.7+
- pip

### Install Dependencies
```bash
pip install -r requirements.txt
```

**Required packages:**
- Flask 3.0.3 - Web framework
- python-dotenv 1.0.1 - Environment variables
- pytz - Timezone support
- openpyxl - Excel export
- Werkzeug 3.0.1 - Utilities for password hashing
- google-auth-oauthlib 1.2.0 - Google OAuth integration
- google-auth-httplib2 0.2.0 - Google auth HTTP support
- requests 2.31.0 - HTTP requests
- Chart.js 4.4.0 - Data visualization (CDN)

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Entries Table
```sql
CREATE TABLE entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    entry_date TEXT NOT NULL,
    food_item TEXT NOT NULL,
    calories INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
)
```

## 🔄 Database Migration

If you're upgrading from a version without user authentication:

### Automatic Migration (Recommended)
```bash
python scripts/migrate_add_user_id.py
```

### Manual Migration (Choose specific user)
```bash
python scripts/migrate_add_user_id_manual.py
```

See [scripts/MIGRATION.md](scripts/MIGRATION.md) for detailed migration instructions.

## 🎯 Usage Guide

### Dashboard

1. **Daily Overview**
   - See total calories consumed
   - View pie chart of food distribution
   - Check average calories per item

2. **Add Entry**
   - Type food name
   - Enter calories
   - Click "Add" button

3. **History**
   - Click "History" in sidebar
   - Select any past date
   - View entries for that day

4. **Calorie Calculator**
   - Click "Calculator" in sidebar
   - Enter age, height, weight, activity level
   - Get daily calorie recommendations

5. **Export Data**
   - Click "Export" to download Excel file
   - Contains all entries with totals

### Sidebar Navigation

- 🏠 **Dashboard** - Main tracking view
- 🕐 **History** - Browse past entries
- 🧮 **Calculator** - Calculate daily needs
- 📥 **Export** - Download data
- 👤 **User Profile** - Your account info
- 🚪 **Logout** - Sign out

## 🔐 Security Features

- **Google OAuth 2.0** - Secure authentication via Google
- **Session Management** - Secure session-based authentication
- **User Isolation** - Users only see their own data
- **Unique Constraints** - Prevent duplicate usernames/emails
- **Foreign Keys** - Referential integrity for data consistency
- **No Password Storage** - No passwords stored locally (OAuth handles auth)
- **HTTPS Ready** - Production-ready for HTTPS deployment

## 📱 Responsive Design

Works perfectly on:
- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 🖥️  Desktops (1024px+)

Features:
- Mobile hamburger menu
- Adaptive grid layouts
- Touch-friendly buttons
- Responsive typography

## 🎨 Technology Stack

**Frontend:**
- HTML5
- Tailwind CSS (CDN)
- Chart.js (pie charts)
- Vanilla JavaScript

**Backend:**
- Flask 3.0.3
- SQLite3
- Python 3.7+

**Tools:**
- Flask-Style routing
- Jinja2 templating

## 📋 Environment Variables

Create `.env` file in project root:

```env
# Google OAuth Configuration
GOOGLE_CLIENT_ID='your-client-id.apps.googleusercontent.com'
GOOGLE_CLIENT_SECRET='your-client-secret-here'
GOOGLE_REDIRECT_URI='http://localhost:5000/auth/google/callback'

# Flask Configuration
SECRET_KEY='your-secret-key-here'
```

Get your Google OAuth credentials from [Google Cloud Console](https://console.cloud.google.com/).
See [GOOGLE_OAUTH_SETUP.md](GOOGLE_OAUTH_SETUP.md) for detailed setup instructions.

## 🐛 Troubleshooting

### Common Issues

**Issue: "Row object is not JSON serializable"**
- ✓ Fixed in app.py - entries are converted to dictionaries

**Issue: "Cannot delete entries"**
- Ensure you're on today's date
- Check user_id matches your account

**Issue: Pie chart not showing**
- Make sure there are entries for the day
- Check browser console for JavaScript errors

**Issue: Export file empty**
- Ensure you have entries in your account
- Try adding an entry first

### Debug Mode

Enable Flask debug mode:
```bash
export FLASK_ENV=development
python app.py
```

## 📈 Features Roadmap

Future enhancements:
- [ ] Weight tracking integration
- [ ] Nutrition breakdown (protein, carbs, fats)
- [ ] Goal setting & progress tracking
- [ ] Mobile app
- [ ] Social sharing
- [ ] API for external tools

## 📄 License

MIT License - Free to use and modify.

## 👤 Author

Created with ❤️ for calorie tracking enthusiasts.

---

**Version:** 1.1.0  
**Last Updated:** April 8, 2026  
**Status:** Active Development