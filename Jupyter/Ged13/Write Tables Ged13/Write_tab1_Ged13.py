import sqlite3

# =================================================
# BANCO
# =================================================
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# =================================================
# TABELA 1A - MONOFÁSICOS
# =================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela1a_monofasico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT,
    carga_min_kw REAL,
    carga_max_kw REAL,
    cobre_mm2 TEXT,
    aluminio_mm2 TEXT,
    eletroduto TEXT,
    disjuntor TEXT,
    aterramento_condutor TEXT,
    aterramento_eletroduto TEXT,
    limite_motor TEXT,
    poste TEXT,
    caixa TEXT
)
""")

cursor.execute("DELETE FROM tabela1a_monofasico")

dados_1a = [
("A1",0,6,"6 mm²","10 mm²","32 mm","32 A","6 mm²","20 mm","1 cv","Poste padrão","Tipo II"),
("A2",6,12,"16 mm²","16 mm²","32 mm","63 A","10 mm²","20 mm","2 cv","Poste padrão","Tipo II"),
("A3",0,10,"6 mm²","10 mm²","32 mm","32 A","6 mm²","20 mm","3 cv","Poste padrão","Tipo E"),
("A4",10,15,"16 mm²","16 mm²","32 mm","63 A","10 mm²","20 mm","5 cv","Poste padrão","Tipo E")
]

cursor.executemany("""
INSERT INTO tabela1a_monofasico
(categoria,carga_min_kw,carga_max_kw,cobre_mm2,aluminio_mm2,eletroduto,disjuntor,
aterramento_condutor,aterramento_eletroduto,limite_motor,poste,caixa)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
""", dados_1a)

# =================================================
# TABELA 1B - BIFÁSICOS
# =================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela1b_bifasico (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT,
    carga_min_kw REAL,
    carga_max_kw REAL,
    cobre_mm2 TEXT,
    aluminio_mm2 TEXT,
    eletroduto TEXT,
    disjuntor TEXT,
    aterramento_condutor TEXT,
    aterramento_eletroduto TEXT,
    motor_fn TEXT,
    motor_ff TEXT,
    poste TEXT,
    caixa TEXT
)
""")

cursor.execute("DELETE FROM tabela1b_bifasico")

dados_1b = [
("B1",12,18,"16 mm²","16 mm²","32 mm","63 A","10 mm²","20 mm","2 cv","3 cv","Poste padrão","Tipo II"),
("B2",18,25,"25 mm²","25 mm²","40 mm","80 A","10 mm²","20 mm","2 cv","5 cv","Poste padrão","Tipo II"),
("B3",15,25,"16 mm²","16 mm²","32 mm","63 A","10 mm²","20 mm","5 cv","10 cv","Poste padrão","Tipo E")
]

cursor.executemany("""
INSERT INTO tabela1b_bifasico
(categoria,carga_min_kw,carga_max_kw,cobre_mm2,aluminio_mm2,eletroduto,disjuntor,
aterramento_condutor,aterramento_eletroduto,motor_fn,motor_ff,poste,caixa)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
""", dados_1b)

# =================================================
# TABELA 1C - TRIFÁSICOS 127/220V
# =================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela1c_trifasico_127_220 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT,
    demanda_min_kva REAL,
    demanda_max_kva REAL,
    cobre_mm2 TEXT,
    aluminio_mm2 TEXT,
    eletroduto TEXT,
    disjuntor TEXT,
    aterramento_condutor TEXT,
    aterramento_eletroduto TEXT,
    motor_fn TEXT,
    motor_ff TEXT,
    motor_fff TEXT,
    poste TEXT,
    caixa TEXT
)
""")

cursor.execute("DELETE FROM tabela1c_trifasico_127_220")

dados_1c_127 = [

("C1",0,23,"16 mm²","25 mm²","40 mm","63 A","10 mm²","20 mm","2 cv","3 cv","15 cv","90 daN","Tipo III"),
("C2",23,30,"25 mm²","25 mm²","40 mm","80 A","10 mm²","20 mm","2 cv","5 cv","20 cv","90 daN","Tipo III"),
("C3",30,38,"35 mm²","35 mm²","40 mm","100 A","10 mm²","20 mm","3 cv","7,5 cv","25 cv","90 daN","Tipo III"),
("C4",38,47,"50 mm²","50 mm²","50 mm","125 A","16 mm²","20 mm","5 cv","7,5 cv","30 cv","200 daN","Tipo III"),
("C5",47,57,"70 mm²","70 mm²","60 mm","150 A","25 mm²","20 mm","7,5 cv","10 cv","40 cv","200 daN","Tipo III"),
("C6",57,76,"95 mm²","95 mm²","60 mm","200 A","35 mm²","20 mm","7,5 cv","15 cv","50 cv","300 daN","Tipo III")

]

cursor.executemany("""
INSERT INTO tabela1c_trifasico_127_220
(categoria,demanda_min_kva,demanda_max_kva,cobre_mm2,aluminio_mm2,eletroduto,
disjuntor,aterramento_condutor,aterramento_eletroduto,
motor_fn,motor_ff,motor_fff,poste,caixa)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", dados_1c_127)

# =================================================
# TABELA 1C - TRIFÁSICOS 220/380V
# =================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela1c_trifasico_220_380 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categoria TEXT,
    demanda_min_kva REAL,
    demanda_max_kva REAL,
    cobre_mm2 TEXT,
    aluminio_mm2 TEXT,
    eletroduto TEXT,
    disjuntor TEXT,
    aterramento_condutor TEXT,
    aterramento_eletroduto TEXT,
    motor_fn TEXT,
    motor_ff TEXT,
    motor_fff TEXT,
    poste TEXT,
    caixa TEXT
)
""")

cursor.execute("DELETE FROM tabela1c_trifasico_220_380")

dados_1c_220 = [

("C7",0,26,"10 mm²","16 mm²","40 mm","40 A","6 mm²","20 mm","3 cv","5 cv","20 cv","90 daN","Tipo III"),
("C8",26,40,"16 mm²","16 mm²","40 mm","63 A","10 mm²","20 mm","3 cv","5 cv","30 cv","90 daN","Tipo III"),
("C9",40,52,"25 mm²","25 mm²","40 mm","80 A","10 mm²","20 mm","5 cv","10 cv","30 cv","90 daN","Tipo III"),
("C10",52,66,"35 mm²","35 mm²","40 mm","100 A","10 mm²","20 mm","7,5 cv","12 cv","40 cv","200 daN","Tipo H"),
("C11",66,82,"50 mm²","50 mm²","50 mm","125 A","16 mm²","20 mm","7,5 cv","12 cv","50 cv","200 daN","Tipo H")

]

cursor.executemany("""
INSERT INTO tabela1c_trifasico_220_380
(categoria,demanda_min_kva,demanda_max_kva,cobre_mm2,aluminio_mm2,eletroduto,
disjuntor,aterramento_condutor,aterramento_eletroduto,
motor_fn,motor_ff,motor_fff,poste,caixa)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", dados_1c_220)


# =================================================
# TABELA 1D - DOIS CLIENTES
# =================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela1d_dois_clientes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    tensao TEXT,

    cliente1 TEXT,
    cliente2 TEXT,

    ramal TEXT,
    tipo_rede TEXT,
    poste TEXT
)
""")

cursor.execute("DELETE FROM tabela1d_dois_clientes")

dados_1d = [

# -------------------------------
# 127/220V
# -------------------------------
("127/220V","A1","A1","25 mm²","Triplex","90 daN"),
("127/220V","A1","A2","25 mm²","Triplex","90 daN"),
("127/220V","A1","B1","25 mm²","Quadruplex","90 daN"),
("127/220V","A1","C3","50 mm²","Quadruplex","200 daN"),

("127/220V","A2","B1","35 mm²","Quadruplex","90 daN"),
("127/220V","A2","B2","50 mm²","Quadruplex","200 daN"),
("127/220V","A2","C3","70 mm²","Quadruplex","300 daN"),

("127/220V","B2","C1","70 mm²","Quadruplex","300 daN"),
("127/220V","C2","C3","70 mm²","Quadruplex","300 daN"),

# -------------------------------
# 220/380V
# -------------------------------
("220/380V","A3","A3","25 mm²","Triplex","90 daN"),
("220/380V","A3","B3","25 mm²","Quadruplex","90 daN"),
("220/380V","A3","C9","35 mm²","Quadruplex","90 daN"),
("220/380V","A3","C10","50 mm²","Quadruplex","200 daN"),

("220/380V","A4","B3","35 mm²","Quadruplex","90 daN"),
("220/380V","A4","C9","50 mm²","Quadruplex","200 daN"),
("220/380V","A4","C10","70 mm²","Quadruplex","300 daN"),

("220/380V","C9","C10","70 mm²","Quadruplex","300 daN")
]

cursor.executemany("""
INSERT INTO tabela1d_dois_clientes
(tensao,cliente1,cliente2,ramal,tipo_rede,poste)
VALUES (?,?,?,?,?,?)
""", dados_1d)





# =================================================
# FINAL
# =================================================
conn.commit()
conn.close()

print("Tabela 1A, 1B e 1C criadas e preenchidas com sucesso.")