import sqlite3

banco = r"C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\GED119\DB\databaseCPFLGed119.db"


conn = sqlite3.connect(banco)
cursor = conn.cursor()

# -------------------------
# TABELA PROJETOS
# -------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS projetos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_cliente TEXT,
    aptos INTEGER,
    area_apto REAL,
    area_adm REAL,
    data TEXT
)
""")

# -------------------------
# TABELA MOTOR (exemplo já usado)
# -------------------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela_motores (
    cv TEXT,
    kva REAL
)
""")

# -------------------------
# DADOS DE TESTE
# -------------------------
cursor.executemany("""
INSERT INTO tabela_motores (cv, kva) VALUES (?,?)
""", [
    ("1", 0.75),
    ("5", 3.7),
    ("10", 7.5),
    ("20", 15.0),
])

conn.commit()
conn.close()

print("Banco de projetos criado com sucesso")