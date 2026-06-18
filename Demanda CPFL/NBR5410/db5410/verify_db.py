import sqlite3
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_db = os.path.join(_dir, 'nbr5410.db')
conn = sqlite3.connect(_db)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for t in cur.fetchall():
    name = t[0]
    cur.execute(f"SELECT COUNT(*) FROM [{name}]")
    cnt = cur.fetchone()[0]
    print(f"{name}: {cnt} rows")
conn.close()
