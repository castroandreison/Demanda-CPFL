import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()


# criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS TABELA_5 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    potencia_cv_hp TEXT,
    potencia_kw REAL,
    potencia_kva REAL,
    corrente_plena_127v REAL,
    corrente_plena_220v REAL,
    corrente_partida_127v REAL,
    corrente_partida_220v REAL,
    fator_potencia REAL
)
""")

# limpar dados antigos (opcional)
cursor.execute("DELETE FROM TABELA_5")

dados = [

("1/4",0.42,0.66,5.9,3.0,27,14,0.63),
("1/3",0.51,0.77,7.1,3.5,31,16,0.66),
("1/2",0.79,1.18,11.6,5.4,47,24,0.67),
("3/4",0.90,1.34,12.2,6.1,63,33,0.67),
("1",1.14,1.56,14.2,7.1,68,35,0.73),
("1 1/2",1.67,2.35,21.4,10.7,96,48,0.71),
("2",2.17,2.97,27.0,13.5,132,68,0.73),
("3",3.22,4.07,37.0,18.5,220,110,0.79),
("5",5.11,6.16,None,28.0,None,145,0.83),
("7 1/2",7.07,8.84,None,40.2,None,210,0.80),
("10",9.31,11.64,None,52.9,None,260,0.80),
("12 1/2",11.58,14.94,None,67.9,None,330,0.78),
("15",13.72,16.94,None,77.0,None,408,0.81)

]

cursor.executemany("""
INSERT INTO TABELA_5 (
potencia_cv_hp,
potencia_kw,
potencia_kva,
corrente_plena_127v,
corrente_plena_220v,
corrente_partida_127v,
corrente_partida_220v,
fator_potencia
)
VALUES (?,?,?,?,?,?,?,?)
""", dados)

conn.commit()

cursor.execute("SELECT COUNT(*) FROM TABELA_5")
print("Registros inseridos:", cursor.fetchone()[0])

conn.close()

print("TABELA 5 criada e preenchida com sucesso.")