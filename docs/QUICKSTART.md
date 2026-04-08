# 🚀 Quick Start Guide - Tracker App

## Installation & Setup

### 1. Install Dependencies
```bash
cd /home/anaghk/Public/github/tracker
pip install -r requirements.txt
```

### 2. Environment Configuration
Ensure `.env` file has:
```
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback
OPENAI_API_KEY=your-openai-api-key
```

### 3. Run the Application
```bash
python3 app.py
```

Application will be available at: **http://localhost:5000**

---

## User Workflow

### First Time Setup

1. **Navigate to Login Page**
   - Go to: `http://localhost:5000/auth/login`
   
2. **Choose Authentication Method**
   - **Option A**: Google OAuth (Recommended)
     - Click "Google" button
     - Authorize with Google account
     - Account auto-created
   
   - **Option B**: Manual Login
     - Enter username and password
     - Will need to exist in database

3. **First Login**
   - Dashboard tracker switcher appears
   - Two options: Calorie Tracker or Vices Tracker

### Using Calorie Tracker

1. **Access**
   - Click "Calorie Tracker" card on dashboard
   - Or go to: `/calorie/`

2. **Add Entry**
   - Today's date: Form available at top
   - Fill:
     - Food Item: "2 eggs and toast"
     - Calories: "300"
   - Click "+ Add" button
   - Entry appears in list below

3. **Use AI Suggestion**
   - Click "✨ AI" button next to calorie field
   - Type food description: "grilled chicken breast 200g"
   - Modal shows suggestion: "grilled chicken breast: 330 kcal"
   - Click "+ Add Entry" to populate form
   - Submit to add to tracker

4. **View History**
   - Use date selector in sidebar
   - Click date to view entries for that day
   - Total calories calculated automatically

5. **Export Data**
   - Click "Export" in sidebar
   - Choose date or export all
   - Excel file downloaded with all entries

### Using Vices Tracker

1. **Access**
   - Click "Vices Tracker" card on dashboard
   - Or go to: `/vices/`

2. **Add Vice Entry**
   - Select Vice Type: Cigarettes, Alcohol, Coffee
   - Enter Quantity: Number count
   - Optional: Add notes
   - Click "+ Log" button

3. **View Summary**
   - Cards show daily summary for each vice
   - Total quantity tracked
   - Number of entries logged

4. **View History**
   - Entries list shows all vices for day
   - Timestamp for each entry
   - Delete entries if needed

---

## Key Features

### 🔐 Authentication
- **Google OAuth 2.0**: Single sign-on with Google
- **Password Login**: Traditional username/password
- **Password Change**: Update password anytime in dashboard

### 📊 Calorie Tracking
- **Daily Entries**: Log food and approximate calories
- **AI Suggestions**: OpenAI powered calorie estimation
- **Visualization**: Pie chart showing food distribution
- **Calculator**: Mifflin-St Jeor formula for daily needs
- **Export**: Excel download of all entries
- **History**: Access past entries by date

### ⚠️ Vices Tracking
- **Multiple Vices**: Cigarettes, Alcohol, Coffee (customizable)
- **Daily Logging**: Track quantity and add notes
- **Summary Stats**: View totals per vice per day
- **Flexible Units**: Counts, milliliters, cups
- **History**: Access all previous entries

### 🎨 User Experience
- **Responsive Design**: Mobile, tablet, desktop
- **Tailwind CSS**: Modern, clean interface
- **Real-time Updates**: Chart updates as data changes
- **Flash Messages**: Confirmation of actions
- **Sidebar Navigation**: Easy access to features

---

## Common Tasks

### Add Your First Entry
```
1. Click "Calorie Tracker" on main dashboard
2. Enter: Food Item = "Breakfast"
3. Enter: Calories = "500"
4. Click "+ Add"
✓ Entry appears in list, total updates
```

### Get AI Food Suggestion
```
1. In calorie tracker form
2. Type in food field: "salmon with vegetables"
3. Click "✨ AI" button
4. Wait for suggestion modal
5. Click "+ Add Entry" if suggestion is correct
6. Submit form
```

### Track a Vice
```
1. Click "Vices Tracker" on main dashboard
2. Select "Cigarettes" from dropdown
3. Enter quantity: "3"
4. Add note: "Morning and after lunch"
5. Click "+ Log"
✓ Entry logged, summary updates
```

### Export Calories
```
1. In Calorie Tracker
2. Click "Export" in sidebar
3. Excel file "calorie_tracker_YYYY-MM-DD.xlsx" downloads
4. Open in Excel/Sheets
5. View all entries with dates and times
```

### Change Password
```
1. Dashboard -> Click settings icon (gear)
2. For Google users: option to set password
3. For password users: current password required
4. Enter new password twice
5. Click "Update Password"
✓ Password changed, session continues
```

---

## Troubleshooting

### Issue: "Database is locked"
**Solution**: Ensure no other instances of the app are running
```bash
# Kill all Python processes
killall python3

# Restart app
python3 app.py
```

### Issue: "OpenAI API Error"
**Solution**: Verify API key in `.env`
```
OPENAI_API_KEY=sk-proj-YOUR_KEY_HERE
```

### Issue: "Google OAuth not working"
**Solution**: Check OAuth credentials in `.env`
```
GOOGLE_CLIENT_ID=...from Google Cloud Console
GOOGLE_CLIENT_SECRET=...from Google Cloud Console
GOOGLE_REDIRECT_URI=http://localhost:5000/auth/google/callback
```

### Issue: "Templates not found"
**Solution**: Ensure templates are in correct structure
```
templates/
├── base.html
├── dashboard.html
├── auth/
│   └── login.html
├── calorie/
│   └── dashboard.html
└── vices/
    └── dashboard.html
```

---

## File Structure Reference

```
/home/anaghk/Public/github/tracker/
├── app.py                      # Flask app factory
├── config.py                   # Configuration settings
├── database.py                 # Database operations
├── utils.py                    # Shared utilities
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── routes/
│   ├── auth.py                # Authentication routes
│   ├── calorie.py             # Calorie tracker routes
│   ├── vices.py               # Vices tracker routes
│   ├── dashboard.py           # Dashboard routes
│   └── __init__.py            # Blueprint registration
├── templates/
│   ├── base.html              # Base template
│   ├── dashboard.html         # Tracker switcher
│   ├── auth/
│   │   └── login.html         # Login page
│   ├── calorie/
│   │   └── dashboard.html     # Calorie tracker UI
│   └── vices/
│       └── dashboard.html     # Vices tracker UI
└── README.md                   # Project documentation
```

---

## Next Steps

1. **Test Current Features**
   - Add calorie entries
   - Use AI suggestion
   - View analytics
   - Track vices

2. **Customize**
   - Edit vice types in database
   - Change colors in Tailwind CSS
   - Modify feature icons/emojis

3. **Extend**
   - Create new tracker (fitness, water, meditation)
   - Add more analytics/reports
   - Integrate more OAuth providers

4. **Deploy**
   - Use Gunicorn for production
   - Set up HTTPS
   - Configure production database (PostgreSQL)

---

## Support & Documentation

- **REFACTORING.md** - Detailed architecture explanation
- **ARCHITECTURE.md** - Visual diagrams and flows
- **REFACTORING_SUMMARY.md** - Complete changelog
- **docs/GOOGLE_OAUTH_SETUP.md** - OAuth configuration

---

## Dashboard Navigation

```
┌─────────────────────────────────────────┐
│         Main Dashboard (/)              │
│                                         │
│  🔥 Calorie Tracker    ⚠️ Vices Tracker │
│     ↓                      ↓            │
│  /calorie/              /vices/         │
└─────────────────────────────────────────┘

Calorie Tracker (/calorie/)
├── Sidebar
│   ├── Dashboard (link to /)
│   ├── History (expand dates)
│   ├── Calculator
│   ├── Export
│   │
│   └── User Menu
│       ├── Change Password
│       └── Logout

Vices Tracker (/vices/)
├── Date Selector
│   └── View different dates
├── Vice Entry Form
│   ├── Vice Type dropdown
│   ├── Quantity input
│   └── Notes field
├── Daily Summary
│   └── Cards per vice type
└── Entries List
    └── Today's logged vices
```

---

Ready to use? Start with `python3 app.py` and navigate to **http://localhost:5000**! 🚀
