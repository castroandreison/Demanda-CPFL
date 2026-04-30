import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela18_limitacao_motores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_fornecimento TEXT,
    carga_min_kw REAL,
    carga_max_kw REAL,
    demanda_min_kva REAL,
    demanda_max_kva REAL,
    motor_fn_cv REAL,
    motor_ff_cv REAL,
    motor_fffn_cv REAL
)
""")

# Dados da tabela
dados = [

# MONOFÁSICO
("Monofasico",0,6,None,None,1,None,None),
("Monofasico",6,12,None,None,2,None,None),

# BIFÁSICO
("Bifasico",12,18,None,None,None,2,3),
("Bifasico",18,25,None,None,2,5,None),

# TRIFÁSICO
("Trifasico",25,75,None,23,2,3,15),
("Trifasico",None,None,23,30,2,5,20),
("Trifasico",None,None,30,38,3,7.5,25),
("Trifasico",None,None,38,47,5,7.5,30),
("Trifasico",None,None,47,57,7.5,10,40),
("Trifasico",None,None,57,76,7.5,15,50)

]

cursor.executemany("""
INSERT INTO tabela18_limitacao_motores
(tipo_fornecimento,carga_min_kw,carga_max_kw,
demanda_min_kva,demanda_max_kva,
motor_fn_cv,motor_ff_cv,motor_fffn_cv)
VALUES (?,?,?,?,?,?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 18 inserida com sucesso.")