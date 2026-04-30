import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS TABELA_4 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    potencia_cv_hp TEXT,
    potencia_kw REAL,
    potencia_kva REAL,
    corrente_plena_a REAL,
    corrente_partida_a REAL,
    fator_potencia REAL
)
""")

# limpar dados antigos (opcional)
cursor.execute("DELETE FROM TABELA_4")

dados = [

("1/3",0.39,0.65,1.7,7.1,0.61),
("1/2",0.58,0.87,2.3,9.9,0.66),
("3/4",0.83,1.26,3.3,16.3,0.66),
("1",1.05,1.52,4.0,20.7,0.69),
("1 1/2",1.54,2.17,5.7,33.1,0.71),
("2",1.95,2.70,7.1,44.3,0.72),
("3",2.95,4.04,10.6,65.9,0.73),
("4",3.72,5.03,13.2,74.4,0.74),
("5",4.51,6.02,15.8,98.9,0.75),
("7 1/2",6.57,8.65,22.7,157.1,0.76),
("10",8.89,11.54,30.3,201.1,0.77),
("12 1/2",10.85,14.09,37.0,270.5,0.77),
("15",12.82,16.65,43.7,340.6,0.77),
("20",17.01,22.10,58.0,422.1,0.77),
("25",20.92,25.83,67.8,477.6,0.81),
("30",25.03,30.52,80.1,566.0,0.82),
("40",33.38,39.74,104.3,717.3,0.84),
("50",40.93,48.73,127.9,915.5,0.84),
("60",49.42,58.15,152.6,1095.7,0.85),
("75",61.44,72.28,189.7,1288.0,0.85),
("100",81.23,95.56,250.8,1619.0,0.85),
("125",100.67,117.05,307.2,2014.0,0.86),
("150",120.09,141.29,370.8,2521.7,0.85),
("200",161.65,190.18,499.1,3458.0,0.85)

]

cursor.executemany("""
INSERT INTO TABELA_4 (
potencia_cv_hp,
potencia_kw,
potencia_kva,
corrente_plena_a,
corrente_partida_a,
fator_potencia
)
VALUES (?,?,?,?,?,?)
""", dados)

conn.commit()

cursor.execute("SELECT COUNT(*) FROM TABELA_4")
print("Registros inseridos:", cursor.fetchone()[0])

conn.close()

print("TABELA 4 criada e preenchida com sucesso.")