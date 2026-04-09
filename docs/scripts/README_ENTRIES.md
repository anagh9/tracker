# Manual Entry Addition Scripts

This directory contains two scripts for manually adding entries to the CalTrack database:

1. **`add_entry_manual.py`** - Interactive, single-entry addition
2. **`add_entries_bulk.py`** - Batch import from CSV file

## Quick Start

### Manual Single Entry

```bash
python3 scripts/add_entry_manual.py
```

**Features:**
- Interactive prompts for user_id, date, food item, and calories
- Real-time validation of inputs
- Shows user entry count before and after
- Confirmation summary before saving
- Option to add multiple entries in one session

**Example Session:**
```
Available Users:
  [1] anagh (anagh9931@gmail.com) - 311 entries

Enter user ID: 1
Enter date (YYYY-MM-DD) (default: today - 2026-04-08): 
Enter food item: Grilled Chicken with Rice
Enter calories: 520

Entry Summary
User:       anagh
Date:       2026-04-08
Food:       Grilled Chicken with Rice
Calories:   520

Save this entry? (y/n): y
✓ Entry added successfully (ID: 312)
✓ anagh now has 312 total entries
```

### Bulk Import from CSV

```bash
python3 scripts/add_entries_bulk.py entries.csv
```

**Features:**
- Import multiple entries at once
- Validates all entries before inserting
- Shows detailed error reporting
- Supports any valid date format (YYYY-MM-DD)

#### CSV Format

Create a CSV file with the following columns:

```csv
user_id,date,food_item,calories
1,2026-04-08,Breakfast - Eggs Toast,350
1,2026-04-08,Lunch - Chicken Salad,450
1,2026-04-08,Snack - Apple,80
1,2026-04-09,Breakfast - Oatmeal,300
```

**Column Details:**
- `user_id`: Integer, must be an existing user ID (visible in manual script)
- `date`: YYYY-MM-DD format
- `food_item`: Text description (max 100 characters)
- `calories`: Positive integer only

#### Create Sample CSV

If you don't have a CSV file, the script can create a sample:

```bash
python3 scripts/add_entries_bulk.py
```

Then select "y" to create `sample_entries.csv`. Edit it with your data and run the import.

#### Bulk Import Example

```bash
python3 scripts/add_entries_bulk.py sample_entries.csv
```

**Output:**
```
======================================================================
CalTrack - Bulk Entry Addition
======================================================================
Reading: sample_entries.csv

✓ Row 2: Added entry 312 for user anagh (350 cal)
✓ Row 3: Added entry 313 for user anagh (450 cal)
✓ Row 4: Added entry 314 for user anagh (80 cal)
✓ Row 5: Added entry 315 for user anagh (300 cal)

======================================================================
Summary
======================================================================
Total entries processed: 6
Successfully added:     4
Failed:                 2

Errors:
  - Row 6: User ID 2 does not exist
  - Row 7: User ID 2 does not exist
======================================================================
```

## Validation Rules

### Manual Entry (`add_entry_manual.py`)

- **User ID**: Must exist in the database (shown in list)
- **Date**: Format YYYY-MM-DD (defaults to today)
- **Food Item**: 1-100 characters required
- **Calories**: Positive integer required

### Bulk Import (`add_entries_bulk.py`)

- **user_id**: Integer, must match existing user
- **date**: YYYY-MM-DD format
- **food_item**: 1-100 characters, cannot be empty
- **calories**: Positive integer required

Entries with validation errors are skipped but processing continues.

## Finding User IDs

To see available users and their IDs:

1. Run the manual script and check the "Available Users" list
2. Or check the database directly:
   ```bash
   sqlite3 calories.db "SELECT id, username, email FROM users;"
   ```

## Tips

- **Test first**: Use the manual script to test one entry before bulk importing
- **Backup**: Always backup `calories.db` before bulk operations:
  ```bash
  cp calories.db calories.db.backup
  ```
- **Validate your CSV**: Check for:
  - Correct column headers
  - No extra spaces in user_id
  - Dates in YYYY-MM-DD format
  - Positive calorie numbers
- **Error review**: Check error messages to fix and retry entries
- **Track IDs**: New entry IDs are shown in the output for reference

## Troubleshooting

### "User ID does not exist"

Make sure you're using a valid user ID:
- Run `add_entry_manual.py` to see the list of valid user IDs
- Valid user IDs are numbers (1, 2, 3, etc.)

### "Invalid date format"

Dates must be in YYYY-MM-DD format:
- ✓ Correct: `2026-04-08`
- ✗ Incorrect: `04-08-2026` or `April 8, 2026`

### "Invalid calorie value"

Calories must be a positive integer:
- ✓ Correct: `250`, `350`, `1000`
- ✗ Incorrect: `250.5`, `-100`, `zero`, `Many`

### CSV not found

Make sure the file path is correct:
```bash
# Both work:
python3 scripts/add_entries_bulk.py sample_entries.csv
python3 scripts/add_entries_bulk.py /home/user/entries.csv
```

## Data Consistency

All entries added by these scripts:
- Automatically include `created_at` timestamp (current time)
- Are associated with the specified user via `user_id`
- Will appear immediately in the dashboard for that user
- Can be deleted via the web interface or manually

## Database Schema

The scripts interact with two tables:

**users table:**
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**entries table:**
```sql
CREATE TABLE entries (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    entry_date TEXT NOT NULL,
    food_item TEXT NOT NULL,
    calories INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
);
```

## Advanced Usage

### Adding entries for a specific date range

Use a CSV with multiple dates:

```bash
# entries_april.csv
user_id,date,food_item,calories
1,2026-04-01,Breakfast,300
1,2026-04-01,Lunch,500
1,2026-04-01,Dinner,600
1,2026-04-02,Breakfast,320
...

python3 scripts/add_entries_bulk.py entries_april.csv
```

### Bulk import for multiple users

CSV supports multiple users:

```bash
# entries_multi_user.csv
user_id,date,food_item,calories
1,2026-04-08,Breakfast,350
1,2026-04-08,Lunch,450
2,2026-04-08,Breakfast,280
2,2026-04-08,Lunch,420

python3 scripts/add_entries_bulk.py entries_multi_user.csv
```

## File Outputs

Both scripts work with the main database:
- **Database**: `calories.db` (SQLite3)
- **Sample CSV**: `sample_entries.csv` (auto-created)

No additional files are created or modified.
