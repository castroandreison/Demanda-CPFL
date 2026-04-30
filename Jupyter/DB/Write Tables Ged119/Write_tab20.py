import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela20_dimensionamento_poste (

    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tensao_fornecimento TEXT,
    demanda_min_kva REAL,
    demanda_max_kva REAL,
    tipo_poste TEXT,
    capacidade_dan INTEGER

)
""")

# Dados da tabela

dados = [

# 127/220V
("127/220",0,23,"Poste Concreto",90),
("127/220",23,47,"Poste Concreto",200),
("127/220",47,100,"Poste Concreto",300),
("127/220",100,150,"Poste Concreto ou Moldado",400),
("127/220",150,400,"Poste Concreto ou Moldado",700),

# 220/380V
("220/380",0,40,"Poste Concreto",90),
("220/380",40,100,"Poste Concreto",200),
("220/380",100,150,"Poste Concreto ou Moldado",300),
("220/380",150,400,"Poste Concreto ou Moldado",500)

]

cursor.executemany("""

INSERT INTO tabela20_dimensionamento_poste
(tensao_fornecimento,demanda_min_kva,demanda_max_kva,tipo_poste,capacidade_dan)

VALUES (?,?,?,?,?)

""", dados)

conn.commit()
conn.close()

print("Tabela 20 inserida com sucesso.")