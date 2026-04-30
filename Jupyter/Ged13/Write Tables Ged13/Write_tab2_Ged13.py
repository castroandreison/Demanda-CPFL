import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar Tabela 2
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    area_min REAL,
    area_max REAL,
    tomadas_100w INTEGER,
    subtotal_I INTEGER,
    tomadas_600w INTEGER,
    subtotal_II INTEGER,
    total_W INTEGER
)
""")

# Dados da Tabela 2
dados = [
(0,8,1,100,1,600,700),
(8,15,3,300,1,600,900),
(15,20,4,400,2,1200,1600),
(20,30,5,500,2,1200,1700),
(30,50,6,600,3,1800,2400),
(50,70,7,700,3,1800,2500),
(70,90,8,800,3,1800,2600),
(90,110,9,900,3,1800,2700),
(110,140,10,1000,3,1800,2800),
(140,170,11,1100,3,1800,2900),
(170,200,12,1200,3,1800,3000),
(200,220,13,1300,3,1800,3100),
(220,250,14,1400,3,1800,3200)
]

# Inserir dados
cursor.executemany("""
INSERT INTO tabela2
(area_min, area_max, tomadas_100w, subtotal_I, tomadas_600w, subtotal_II, total_W)
VALUES (?,?,?,?,?,?,?)
""", dados)

# Salvar
conn.commit()
conn.close()

print("Tabela 2 criada e preenchida com sucesso.")