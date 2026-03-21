# How to View SQLite Database in VS Code

## Method 1: Using SQLite Viewer Extension (Recommended)

### Step 1: Install Extension
1. Open VS Code Extensions (Ctrl+Shift+X)
2. Search for "SQLite Viewer" by alexcvzz
3. Click Install

### Step 2: Open Database File
1. In VS Code Explorer, navigate to:
   ```
   E:\Ideathon2026\backend\asclepius.db
   ```
2. **Right-click** on `asclepius.db`
3. Select **"Open Database"**

OR

1. Press **Ctrl+Shift+P**
2. Type "SQLite: Open Database"
3. Browse to: `E:\Ideathon2026\backend\asclepius.db`

### Step 3: View Tables
- You should see tables in the SQLite Explorer panel:
  - `patients`
  - `vitals`
  - `alerts`
  - `protocols`

---

## Method 2: Using SQLite Browser (Standalone App)

### Install DB Browser for SQLite
1. Download from: https://sqlitebrowser.org/dl/
2. Install the application
3. Open DB Browser
4. Click "Open Database"
5. Navigate to: `E:\Ideathon2026\backend\asclepius.db`
6. Click the "Browse Data" tab to see all tables

---

## Method 3: Command Line (Quick Check)

### Using Python
```bash
cd E:\Ideathon2026\backend
python -c "import sqlite3; conn = sqlite3.connect('asclepius.db'); print('Tables:', [t[0] for t in conn.execute(\"SELECT name FROM sqlite_master WHERE type='table'\").fetchall()]); conn.close()"
```

### Using SQLite CLI (if installed)
```bash
cd E:\Ideathon2026\backend
sqlite3 asclepius.db ".tables"
```

---

## Common Issues & Solutions

### Issue: "Unable to open database file"
**Cause:** Extension is trying to open the connection string, not the file

**Solution:**
- Do NOT click on the connection string in `.env`
- Click on the actual `asclepius.db` file in the `backend` folder

### Issue: "Tables not showing"
**Solution:**
```bash
# Reinitialize the database
cd E:\Ideathon2026\backend
del asclepius.db
python -m db.init_db
```

### Issue: "Database is locked"
**Solution:**
- Stop the uvicorn server (Ctrl+C)
- Close any SQLite viewer connections
- Restart the server

---

## Quick Test Script

Create a test to verify database has data:

```python
# E:\Ideathon2026\backend\check_db.py
import sqlite3

conn = sqlite3.connect('asclepius.db')
cursor = conn.cursor()

print("=" * 50)
print("Database Tables and Row Counts")
print("=" * 50)

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

for (table_name,) in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
    print(f"{table_name:15} : {count} rows")
    
    # Show first row as example
    if count > 0:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
        print(f"  Example row: {cursor.fetchone()}")

print("=" * 50)
conn.close()
```

Run it:
```bash
cd E:\Ideathon2026\backend
python check_db.py
```

---

## Database Schema

Your database should have these tables:

### `patients`
- id, name, age, gender, bed_number, diagnosis, allergies, comorbidities, is_post_surgical, is_immunocompromised, risk_level, current_risk_score, created_at, updated_at

### `vitals`
- id, patient_id, heart_rate, systolic_bp, respiratory_rate, temperature, spo2, lactate, risk_score, qsofa_score, sofa_score, source, recorded_at

### `alerts`
- id, patient_id, vital_id, level, risk_score, message, triggered_at, resolved, resolved_at, resolved_by, nurse_notified, nurse_notified_at, doctor_notified, doctor_notified_at

### `protocols`
- id, patient_id, alert_id, risk_score, gemini_recommendation, antibiotic_suggestion, immediate_actions, rationale, status, reviewed_by, reviewed_at, doctor_notes, nurse_notified, nurse_notified_at, generated_at
