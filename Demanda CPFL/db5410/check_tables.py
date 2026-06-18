import sqlite3
conn = sqlite3.connect(r'C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\db5410\nbr5410.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for r in cur.fetchall():
    cur.execute(f"SELECT COUNT(*) FROM [{r[0]}]")
    c = cur.fetchone()[0]
    print(f"{r[0]}: {c} linhas")
conn.close()
