import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS capacidade_interrupcao_transformador (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transformador_kva REAL,
    capacidade_interrupcao_ka REAL,
    z_percent REAL
)
""")

# Dados da tabela
dados = [
(15, 1.3, 3.23),
(30, 2.5, 3.23),
(45, 4.0, 3.23),
(75, 7.0, 3.23),
(112.5, 10.0, 3.23),
(150, 12.5, 3.23),
(225, 15.0, 4.16),
(250, 16.0, 4.16),
(300, 20.0, 4.16),
(500, 32.0, 4.16),
(750, 48.0, 4.16),
(1000, 65.0, 4.16)
]

cursor.executemany("""
INSERT INTO capacidade_interrupcao_transformador
(transformador_kva, capacidade_interrupcao_ka, z_percent)
VALUES (?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela de capacidade de interrupção inserida com sucesso.")