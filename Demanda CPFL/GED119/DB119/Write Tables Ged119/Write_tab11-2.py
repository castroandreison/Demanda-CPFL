import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela11_fatores_correcao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forma_agrupamento TEXT,

    c1 REAL,
    c2 REAL,
    c3 REAL,
    c4 REAL,
    c5 REAL,
    c6 REAL,
    c7 REAL,
    c8 REAL,
    c9_11 REAL,
    c12_15 REAL,
    c16_19 REAL,
    c20_mais REAL
)
""")

# Inserir dados
dados = [

("Em feixe: ao ar livre ou sobre superfície; embutidos; em duto fechado",
1.00,0.80,0.70,0.65,0.60,0.57,0.54,0.52,0.50,0.45,0.41,0.38),

("Camada única sobre parede, piso ou em bandeja não perfurada ou prateleira",
1.00,0.85,0.79,0.75,0.73,0.72,0.72,0.71,0.70,None,None,None),

("Camada única no teto",
0.95,0.81,0.72,0.68,0.66,0.64,0.63,0.62,0.61,None,None,None),

("Camada única em bandeja perfurada",
1.00,0.88,0.82,0.77,0.75,0.73,0.73,0.72,0.72,None,None,None),

("Camada única sobre leito, suporte, etc.",
1.00,0.87,0.82,0.80,0.80,0.79,0.79,0.78,0.78,None,None,None)

]

cursor.executemany("""
INSERT INTO tabela11_fatores_correcao
(forma_agrupamento,
c1,c2,c3,c4,c5,c6,c7,c8,
c9_11,c12_15,c16_19,c20_mais)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 11 - Parte 2 inserida com sucesso.")