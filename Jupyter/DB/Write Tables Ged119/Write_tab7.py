import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"

conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar TABELA 7
cursor.execute("""
CREATE TABLE IF NOT EXISTS TABELA_7 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_apartamentos TEXT,
    fator_simultaneidade REAL
)
""")

# limpar dados antigos
cursor.execute("DELETE FROM TABELA_7")

dados = [

("02 a 03",0.98),
("04 a 06",0.97),
("07 a 09",0.96),
("10 a 12",0.95),
("13 a 15",0.91),
("16 a 18",0.89),
("19 a 21",0.87),
("22 a 24",0.84),
("25 a 27",0.81),
("28 a 30",0.79),
("31 a 33",0.77),
("34 a 36",0.76),
("37 a 39",0.75),
("40 a 42",0.74),
("43 a 45",0.73),
("46 a 48",0.72),
("49 a 51",0.71),
("52 a 54",0.70),
("55 a 57",0.69),
("58 a 63",0.68),
("64 a 69",0.67),
("70 a 78",0.66),

("79 a 87",0.65),
("88 a 96",0.64),
("97 a 102",0.63),
("103 a 105",0.62),
("106 a 108",0.61),
("109 a 111",0.60),
("112 a 114",0.59),
("115 a 117",0.58),
("118 a 120",0.57),
("121 a 126",0.56),
("127 a 129",0.55),
("130 a 132",0.54),
("133 a 138",0.53),
("139 a 141",0.52),
("142 a 147",0.51),
("148 a 150",0.50),
("150 acima",0.50)

]

cursor.executemany("""
INSERT INTO TABELA_7 (
numero_apartamentos,
fator_simultaneidade
)
VALUES (?,?)
""", dados)

conn.commit()

cursor.execute("SELECT COUNT(*) FROM TABELA_7")
print("Registros inseridos:", cursor.fetchone()[0])

conn.close()

print("TABELA 7 criada e preenchida com sucesso.")