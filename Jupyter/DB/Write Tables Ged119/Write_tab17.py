import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela17_fusiveis_expulsao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transformador TEXT,
    fusivel_23_1kv TEXT,
    fusivel_13_8kv TEXT,
    fusivel_11_9kv TEXT
)
""")

# Dados da tabela
dados = [

("30", "1H", "1H", "1H"),
("45", "2H", "2H", "2H"),
("75", "2H", "3H", "5H"),
("112.5", "3H", "5H", "5H"),
("150", "5H", "8K", "8K"),
("225", "6K", "10K", "15K"),
("300", "8K", "15K", "15K"),
("500", "15K", "25K", "25K"),

("2 x 45", "3H", "5H", "5H"),
("3 x 45", "5H", "5H", "6K"),
("2 x 75", "5H", "6K", "8K"),
("3 x 75", "6K", "10K", "15K"),
("2 x 112.5", "6K", "10K", "15K"),
("2 x 150", "8K", "15K", "15K"),
("2 x 225", "12K", "25K", "25K")

]

cursor.executemany("""
INSERT INTO tabela17_fusiveis_expulsao
(transformador,fusivel_23_1kv,fusivel_13_8kv,fusivel_11_9kv)
VALUES (?,?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 17 inserida com sucesso.")