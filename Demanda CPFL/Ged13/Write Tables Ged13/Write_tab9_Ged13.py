# Caminho do banco
import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar a tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela_9 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_aparelhos TEXT,
    fator_demanda REAL
)
""")

# Inserir dados
dados = [
    ("1 a 10", 1.00),
    ("11 a 20", 0.90),
    ("21 a 30", 0.82),
    ("31 a 40", 0.80),
    ("41 a 50", 0.77),
    ("51 a 75", 0.75),
    ("76 a 100", 0.75),
    ("Acima de 100", 0.75)
]

cursor.executemany("""
INSERT INTO tabela_9 (numero_aparelhos, fator_demanda)
VALUES (?, ?)
""", dados)

# Salvar
conn.commit()
conn.close()

print("Tabela 9 criada e dados inseridos com sucesso.")