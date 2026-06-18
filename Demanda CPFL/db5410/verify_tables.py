import sqlite3, os
_dir = os.path.dirname(os.path.abspath(__file__))
_db = os.path.join(_dir, 'nbr5410.db')
conn = sqlite3.connect(_db)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'tabela4%' ORDER BY name")
tables = cur.fetchall()
for t in tables:
    name = t[0]
    cur.execute(f"SELECT COUNT(*) FROM [{name}]")
    cnt = cur.fetchone()[0]
    print(f"{name}: {cnt} linhas")
    cur.execute(f"SELECT * FROM [{name}] LIMIT 2")
    cols = [d[0] for d in cur.description]
    print(f"  Colunas: {', '.join(cols)}")
    for row in cur.fetchall():
        print(f"  {row}")
conn.close()
