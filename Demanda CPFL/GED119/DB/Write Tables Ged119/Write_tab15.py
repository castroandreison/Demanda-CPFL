import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela15_ramal_subterraneo_mt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tensao_kv INTEGER,
    tipo_cabo TEXT,
    corrente_A REAL,
    potencia_MVA REAL
)
""")

# Dados da tabela
dados = [

(15, "35mm² Al", 97, 2.3),
(15, "35mm² Cu", 125, 3.0),
(15, "70mm² Al", 142, 3.4),
(15, "70mm² Cu", 160, 3.8),

(25, "50mm² Al", 106, 4.2),
(25, "50mm² Cu", 135, 5.4)

]

cursor.executemany("""
INSERT INTO tabela15_ramal_subterraneo_mt
(tensao_kv, tipo_cabo, corrente_A, potencia_MVA)
VALUES (?,?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 15 inserida com sucesso.")