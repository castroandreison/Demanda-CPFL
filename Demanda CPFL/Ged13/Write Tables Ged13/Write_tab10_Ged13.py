import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela_10 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    posicao_motor TEXT UNIQUE,
    fator_demanda REAL
)
""")

# Dados da tabela GED-13
dados = [
    ("1_maior", 1.00),
    ("2_maior", 0.90),
    ("3_4_5_maior", 0.80),
    ("demais", 0.70)
]

# Inserir dados sem duplicar
cursor.executemany("""
INSERT OR IGNORE INTO tabela_10 (posicao_motor, fator_demanda)
VALUES (?, ?)
""", dados)

conn.commit()
conn.close()

print("Tabela 10 criada e preenchida com sucesso.")