import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela12_barramento_bt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    demanda_min_kva REAL,
    demanda_max_kva REAL,
    barra_mm TEXT,
    barra_polegada TEXT
)
""")

# Dados da tabela
dados = [
(0,60,"25.4 x 6.4","1 x 1/4"),
(61,120,"31.8 x 6.4","1 1/4 x 1/4"),
(121,150,"38.1 x 6.4","1 1/2 x 1/4"),
(151,200,"50.8 x 6.4","2 x 1/4"),
(201,250,"38.1 x 12.7","1 1/2 x 1/2"),
(251,300,"50.8 x 12.7","2 x 1/2"),
(301,350,"63.5 x 12.7","2 1/2 x 1/2"),
(351,450,"88.9 x 12.7","3 x 1/2"),
(451,550,"101.6 x 12.7","4 x 1/2"),
(551,700,"127 x 12.7","5 x 1/2")
]

cursor.executemany("""
INSERT INTO tabela12_barramento_bt
(demanda_min_kva,demanda_max_kva,barra_mm,barra_polegada)
VALUES (?,?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 12 inserida com sucesso.")