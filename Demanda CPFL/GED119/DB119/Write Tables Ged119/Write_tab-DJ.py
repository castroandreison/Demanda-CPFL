import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS disjuntores_termomagneticos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    corrente_nominal_A INTEGER
)
""")

# Correntes padronizadas
dados = [
(100,),
(125,),
(150,),
(160,),
(175,),
(200,),
(225,),
(250,),
(300,),
(350,),
(400,),
(450,),
(500,),
(600,)
]

# Inserir dados
cursor.executemany("""
INSERT INTO disjuntores_termomagneticos (corrente_nominal_A)
VALUES (?)
""", dados)

conn.commit()
conn.close()

print("Correntes de disjuntores inseridas com sucesso.")