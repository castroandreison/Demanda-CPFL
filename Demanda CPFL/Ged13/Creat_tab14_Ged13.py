import sqlite3
import os

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar tabela 14
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela_14_motores_trifasicos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    potencia_cv TEXT,
    potencia_kw REAL,
    potencia_kva REAL,
    corrente_380 REAL,
    corrente_220 REAL,
    partida_380 REAL,
    partida_220 REAL,
    cos_phi REAL
)
""")

# Dados da tabela GED13
dados = [

("1/4",0.35,0.58,None,1.5,None,None,0.61),
("1/3",0.39,0.65,0.9,1.7,4.1,7.1,0.61),
("1/2",0.58,0.87,1.3,2.3,5.8,9.9,0.66),
("3/4",0.83,1.26,1.9,3.3,9.4,16.3,0.66),
("1",1.05,1.52,2.3,4.0,11.9,20.7,0.69),
("1.5",1.54,2.17,3.3,5.7,19.1,33.1,0.71),
("2",1.95,2.70,4.1,7.1,25.0,44.3,0.72),
("3",2.95,4.04,6.1,10.6,38.0,65.9,0.73),
("4",3.72,5.03,7.6,13.2,43.0,74.4,0.74),
("5",4.51,6.02,9.1,15.8,57.1,98.9,0.75),
("6",5.33,7,None,18.4,None,None,0.75),
("7.5",6.57,8.65,12.7,22.7,90.7,157.1,0.76),
("10",8.89,11.54,17.5,30.3,116.1,201.1,0.77),
("12.5",10.85,14.09,21.3,37.0,156.0,270.5,0.77),
("15",12.82,16.65,25.2,43.7,196.6,340.6,0.77),
("20",17.01,22.10,33.5,58.0,243.7,422.1,0.77),
("25",20.92,25.83,39.1,67.8,275.7,477.6,0.81),
("30",25.03,30.52,46.2,80.1,326.7,566.0,0.82),
("40",33.38,39.74,60.2,104.3,414.0,717.3,0.84),
("50",40.93,48.73,73.8,127.9,528.5,915.5,0.84),
("60",49.42,58.15,88.1,152.6,632.6,1095.7,0.85),
("75",61.44,72.28,109.5,189.7,743.6,1288.0,0.85),
("100",80.55,97.05,None,255,None,None,0.83),
("125",96.23,114.56,None,301,None,None,0.84),
("150",106.25,128.02,None,370,None,None,0.83),
("175",140.13,170.89,None,449,None,None,0.82),
("200",159.08,196.39,None,516,None,None,0.81),
("250 irrigação",196.69,242.82,None,638,None,None,0.81),
("300 irrigação",232.44,286.97,None,754,None,None,0.81)

]

# Inserir dados
cursor.executemany("""
INSERT INTO tabela_14_motores_trifasicos
(potencia_cv,potencia_kw,potencia_kva,corrente_380,corrente_220,partida_380,partida_220,cos_phi)
VALUES (?,?,?,?,?,?,?,?)
""",dados)

conn.commit()

# Contar registros
cursor.execute("SELECT COUNT(*) FROM tabela_14_motores_trifasicos")
total = cursor.fetchone()[0]

print("Tabela 14 criada com sucesso.")
print(f"Registros inseridos: {total}")

conn.close()

# Confirmação
if os.path.exists(nome_banco):
    print(f"\nBanco '{nome_banco}' pronto para uso.")
else:
    print("Erro ao criar banco.")