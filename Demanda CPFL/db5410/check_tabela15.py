import sqlite3
conn = sqlite3.connect(r'C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\GED119\DB119\databaseCPFLGed119.db')
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%tabela15%'")
for t in cur.fetchall():
    print(f"=== {t[0]} ===")
    cur.execute(f"PRAGMA table_info([{t[0]}])")
    for col in cur.fetchall():
        print(f"  {col}")
    cur.execute(f"SELECT * FROM [{t[0]}]")
    for row in cur.fetchall():
        print(f"  {row}")
conn.close()
