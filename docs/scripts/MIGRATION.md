# Database Migration Scripts

These scripts help migrate your CalTrack database to add `user_id` to entries that were created before the user authentication system was implemented.

## Overview

When the user authentication feature was added, all entries needed to be associated with a user via `user_id`. This directory contains scripts to safely migrate legacy entries.

## Scripts

### 1. `migrate_add_user_id.py` (Automatic)

Automatically creates a "legacy_admin" user and assigns all orphaned entries to it.

**Use this when:**
- You want automatic migration with minimal interaction
- You have a single user or want all legacy entries in one place
- You prefer set-and-forget approach

**Usage:**
```bash
python scripts/migrate_add_user_id.py
```

**What it does:**
1. ✓ Checks database status
2. ✓ Creates a "legacy_admin" user (if not exists)
3. ✓ Assigns all entries without user_id to that user
4. ✓ Verifies migration success

**Example output:**
```
============================================================
CalTrack Migration: Add user_id to Previous Entries
============================================================

1. Checking database status...
  - Total users: 2
  - Total entries: 150
  - Entries needing migration: 150

2. Creating/verifying legacy user...
✓ Created legacy user with ID: 1

3. Migrating entries...
Migrating 150 entries...
✓ Successfully migrated 150 entries

4. Verifying migration...
✓ Migration verification PASSED!

Entry Distribution:
  - legacy_admin: 150 entries
  - john_doe: 0 entries
```

### 2. `migrate_add_user_id_manual.py` (Interactive)

Interactively lets you choose which existing user should own the legacy entries.

**Use this when:**
- You want to assign entries to a specific existing user
- You have multiple users and want selective assignment
- You need more control over the process

**Usage:**
```bash
python scripts/migrate_add_user_id_manual.py
```

**What it does:**
1. ✓ Checks for orphaned entries
2. ✓ Lists all available users
3. ✓ Prompts you to select a user
4. ✓ Confirms before proceeding
5. ✓ Assigns entries and verifies

**Example interaction:**
```
============================================================
CalTrack Migration: Assign Legacy Entries to User
============================================================

Found 150 entries without user_id

Available users:
  [1] john_doe (john@example.com)
  [2] jane_smith (jane@example.com)

------------------------------------------------------------
Enter user ID to assign 150 entries to: 1

Assigning 150 entries to user: john_doe (john@example.com)
Continue? (y/n): y

Migrating entries...
✓ Successfully assigned 150 entries!
✓ Migration verified: all entries now have user_id

============================================================
Migration completed successfully!
============================================================
```

## Step-by-Step Migration Guide

### Before You Start

1. **Backup your database** (IMPORTANT!)
   ```bash
   cp calories.db calories.db.backup
   ```

2. **Check your current situation**
   - How many users do you have?
   - Should legacy entries belong to one user or multiple users?

### Option A: Automatic Migration (Recommended for most)

```bash
python scripts/migrate_add_user_id.py
```

This creates a special "legacy_admin" user to own all previous entries.

### Option B: Selective Migration (For existing users)

```bash
python scripts/migrate_add_user_id_manual.py
```

Choose which existing user should own the entries.

### After Migration

1. **Verify entries are accessible**
   - Log in as the user who owns the entries
   - Check that all your food items are visible

2. **Optional: Transfer entries between users**
   - Use SQLite directly if you need to reassign entries to different users:
   ```sql
   UPDATE entries SET user_id = 2 WHERE user_id = 1;
   ```

## Troubleshooting

### "UserWarning: Row object is not serializable"
- This was a previous issue, now fixed in app.py
- The scripts handle this automatically

### "FOREIGN KEY constraint failed"
- The entries table has a FOREIGN KEY constraint
- Ensure the user_id you're assigning exists in the users table
- Use the interactive script to select from available users

### "Entry count doesn't match"
- Check if entries were already partially migrated
- The scripts skip entries that already have a valid user_id

### Need to reverse the migration?

1. Restore from backup:
   ```bash
   cp calories.db.backup calories.db
   ```

2. Or manually fix entries:
   ```sql
   UPDATE entries SET user_id = NULL WHERE user_id = 1;
   DELETE FROM users WHERE username = 'legacy_admin';
   ```

## Database Schema (After Migration)

```
users table:
- id (INTEGER PRIMARY KEY)
- username (TEXT UNIQUE)
- email (TEXT UNIQUE)
- password_hash (TEXT)
- created_at (TIMESTAMP)

entries table:
- id (INTEGER PRIMARY KEY)
- user_id (INTEGER NOT NULL) ← MIGRATED
- entry_date (TEXT)
- food_item (TEXT)
- calories (INTEGER)
- created_at (TIMESTAMP)
```

## Technical Details

### What happens during migration?

1. **Check** - Identify entries with `user_id IS NULL` or `user_id = 0`
2. **Create** - Create a legacy user (only in automatic script)
3. **Update** - Set `user_id` for all orphaned entries
4. **Verify** - Confirm no entries remain orphaned

### Performance

- For 1,000 entries: < 1 second
- For 10,000 entries: < 5 seconds
- Operation is atomic (all-or-nothing)

## Need Help?

If something goes wrong:

1. Check the backup: `ls -la calories.db.backup`
2. Restore from backup: `cp calories.db.backup calories.db`
3. Try the manual script for more control
4. Or manually run: `python scripts/load_data.py` to reload sample data

---

**Last Updated:** April 8, 2026
**For:** CalTrack v1.0 with User Authentication
