import sqlite3

banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"

conn = sqlite3.connect(banco)
cursor = conn.cursor()

# VER QUAL TABELA EXISTE (debug)
cursor.execute("PRAGMA table_info(TABELA_10)")
print(cursor.fetchall())

# FORÇAR RESET TOTAL
cursor.execute("DROP TABLE IF EXISTS TABELA_10")

cursor.execute("""
CREATE TABLE TABELA_10 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    demanda_min REAL,
    demanda_max REAL,
    transformador_kva REAL
)
""")

dados = [
(0,33,30),
(34,49,45),
(50,82,75),
(83,124,112.5),
(125,165,150),
(166,250,225),
(251,308,300)
]

cursor.executemany("""
INSERT INTO TABELA_10 (demanda_min, demanda_max, transformador_kva)
VALUES (?,?,?)
""", dados)

conn.commit()
conn.close()

print("TABELA 10 RESETADA COM SUCESSO")