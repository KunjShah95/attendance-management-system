import sqlite3

conn = sqlite3.connect("attendance.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:", cur.fetchall())
try:
    cur.execute("SELECT id,name,date,time FROM attendance LIMIT 50")
    rows = cur.fetchall()
    print("Rows sample (up to 50):")
    for r in rows:
        print(r)
except Exception as e:
    print("Error reading attendance:", e)
conn.close()
