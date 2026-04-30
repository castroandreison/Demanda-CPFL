import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela16_barramento_mt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    demanda_min_kva REAL,
    demanda_max_kva REAL,
    
    vergalhao_cobre_mm REAL,
    vergalhao_cobre_kgm REAL,
    
    vergalhao_aluminio_mm REAL,
    vergalhao_aluminio_kgm REAL,
    
    tubo_cobre_ips TEXT,
    tubo_cobre_kgm REAL,
    
    tubo_aluminio_ips TEXT,
    tubo_aluminio_kgm REAL
)
""")

# Dados da tabela
dados = [

(0,1300,5.16,0.187,6.35,0.085,"1/4",0.680,"3/8",0.290),

(1301,1800,6.35,0.281,9.53,0.192,None,None,None,None),

(1801,2500,9.53,0.634,12.70,0.342,"3/8",0.960,"1/2",0.440),

(2501,5000,12.70,1.127,15.87,0.535,None,None,None,None)

]

cursor.executemany("""
INSERT INTO tabela16_barramento_mt
(demanda_min_kva,demanda_max_kva,
vergalhao_cobre_mm,vergalhao_cobre_kgm,
vergalhao_aluminio_mm,vergalhao_aluminio_kgm,
tubo_cobre_ips,tubo_cobre_kgm,
tubo_aluminio_ips,tubo_aluminio_kgm)
VALUES (?,?,?,?,?,?,?,?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 16 inserida com sucesso.")