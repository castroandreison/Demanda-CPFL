import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS TABELA_2 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_aparelhos TEXT,
    chuveiro_torneira_ferro INTEGER,
    maquinas_lavar_louca INTEGER,
    aquec_central_acumulacao INTEGER,
    aquec_central_passagem INTEGER,
    fogao_microondas INTEGER,
    secadora_sauna_xerox_hidro INTEGER
)
""")

dados = [

("01",100,100,100,100,100,100),
("02",68,72,71,60,100,56),
("03",56,62,64,48,100,47),
("04",48,57,60,40,100,39),
("05",43,54,57,37,80,35),
("06",39,52,54,35,70,25),
("07",36,50,53,33,62,25),
("08",33,49,51,32,60,25),
("09",31,48,50,31,54,25),
("10 a 11",30,46,50,30,50,25),
("12 a 15",29,44,50,28,46,20),
("16 a 20",28,42,47,26,40,20),
("21 a 25",27,40,46,26,36,18),
("26 a 35",26,38,45,25,32,18),
("36 a 40",26,36,45,25,26,15),
("41 a 45",25,35,45,24,25,15),
("46 a 55",25,34,45,24,25,15),
("56 a 65",24,33,45,24,25,15),
("66 a 75",24,32,45,24,25,15),
("76 a 80",24,31,45,23,25,15),
("81 a 90",23,31,45,23,25,15),
("91 a 100",23,30,45,23,25,15),
("101 a 120",22,29,45,23,25,15),
("121 a 150",22,29,45,23,25,15),
("151 a 200",21,28,45,23,25,15),
("201 a 250",21,27,45,23,25,15),
("251 a 350",20,26,45,23,25,15),
("351 a 450",20,25,45,23,25,15),
("451 a 800",20,24,45,23,25,15),
("801 a 1000",20,23,45,23,25,15)

]

cursor.executemany("""
INSERT INTO TABELA_2 (
numero_aparelhos,
chuveiro_torneira_ferro,
maquinas_lavar_louca,
aquec_central_acumulacao,
aquec_central_passagem,
fogao_microondas,
secadora_sauna_xerox_hidro
)
VALUES (?,?,?,?,?,?,?)
""", dados)

conn.commit()

cursor.execute("SELECT COUNT(*) FROM TABELA_2")
print("Registros inseridos:", cursor.fetchone()[0])

conn.close()

print("TABELA 2 criada e preenchida.")