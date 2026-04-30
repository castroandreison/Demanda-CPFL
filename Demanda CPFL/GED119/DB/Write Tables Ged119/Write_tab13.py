import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela13_condutores_medidores (
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

# Dados da tabela
dados = [

# MONOFÁSICO
("Monofasico",0,6,None,None,10,50,None),
("Monofasico",6,12,None,None,16,70,"32 mm (1\")"),

# BIFÁSICO
("Bifasico",12,18,None,None,16,60,None),
("Bifasico",18,25,None,None,25,70,"40 mm (1 1/4\")"),

# TRIFÁSICO
("Trifasico",25,75,None,23,16,60,None),
("Trifasico",None,None,23,30,25,80,None),
("Trifasico",None,None,30,38,35,100,None),
("Trifasico",None,None,38,47,50,125,"50 mm (1 1/2\")"),
("Trifasico",None,None,47,57,70,150,"60 mm (2\")"),
("Trifasico",None,None,57,76,95,200,None)

]

cursor.executemany("""
INSERT INTO tabela13_condutores_medidores
(tipo_fornecimento,carga_min_kw,carga_max_kw,
demanda_min_kva,demanda_max_kva,
cabo_mm2,disjuntor_A,eletroduto)
VALUES (?,?,?,?,?,?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 13 inserida com sucesso.")