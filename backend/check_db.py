import sqlite3

conn = sqlite3.connect('asclepius.db')
cursor = conn.cursor()

print("=" * 60)
print("Database Tables and Row Counts")
print("=" * 60)
print()

tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()

if not tables:
    print("❌ No tables found! Run: python -m db.init_db")
else:
    for (table_name,) in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        print(f"📊 {table_name:15} : {count} rows")
        
        # Show column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        print(f"   Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
        
        # Show first row as example if exists
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            row = cursor.fetchone()
            print(f"   Sample: {str(row[:3])}...")
        print()

print("=" * 60)
print(f"Database location: E:\\Ideathon2026\\backend\\asclepius.db")
print("=" * 60)

conn.close()
