import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela11_cabos_bt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    secao_mm2 REAL,
    diametro_externo_mm REAL,
    
    A REAL,
    B REAL,
    C REAL,
    D REAL,
    E REAL,
    F REAL,

    B_pvc REAL,
    C_pvc REAL,
    D_pvc REAL,
    E_pvc REAL,
    F_pvc REAL
)
""")

# Dados da tabela
dados = [
(16, 6.90, 26,34,37,30,40,30,26,29,26,32,25),
(25, 8.50, 34,45,45,38,54,40,34,37,32,43,33),
(35, 9.50, 42,55,56,46,67,48,42,45,39,54,41),
(50,11.50, 51,67,68,55,82,58,51,55,46.4,66,49),
(70,13.00, 65,85,87,68,106,72,65,70,58,86,61),
(95,15.00, 79,103,106,80,130,88,79,85,68,105,74),
(120,16.50,91,119,123,91,151,102,91,99,77,122,85),
(150,18.50,105,140,141,103,176,115,105,112,88,141,97),
(185,20.50,120,159,162,116,202,132,120,130,98,162,111),
(240,23.50,141,187,191,134,240,155,141,154,113,192,130)
]

cursor.executemany("""
INSERT INTO tabela11_cabos_bt
(secao_mm2, diametro_externo_mm,
A,B,C,D,E,F,
B_pvc,C_pvc,D_pvc,E_pvc,F_pvc)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 11 inserida com sucesso no banco.")