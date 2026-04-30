import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela14_condutores_medidores_380 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_fornecimento TEXT,
    carga_min_kw REAL,
    carga_max_kw REAL,
    demanda_min_kva REAL,
    demanda_max_kva REAL,
    cabo_mm2 REAL,
    disjuntor_A INTEGER,
    eletroduto TEXT
)
""")

# Dados da Tabela 14
dados = [

# MONOFÁSICO
("Monofasico",0,10,None,None,10,50,"32 mm (1\")"),
("Monofasico",10,15,None,None,16,70,None),

# BIFÁSICO
("Bifasico",15,25,None,None,25,70,"40 mm (1 1/4\")"),

# TRIFÁSICO
("Trifasico",25,75,None,26,10,50,None),
("Trifasico",None,None,26,40,16,60,None),
("Trifasico",None,None,40,46,25,70,None),
("Trifasico",None,None,46,66,35,100,None),
("Trifasico",None,None,66,82,50,125,"50 mm (1 1/2\")")

]

cursor.executemany("""
INSERT INTO tabela14_condutores_medidores_380
(tipo_fornecimento,carga_min_kw,carga_max_kw,
demanda_min_kva,demanda_max_kva,
cabo_mm2,disjuntor_A,eletroduto)
VALUES (?,?,?,?,?,?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 14 inserida com sucesso.")