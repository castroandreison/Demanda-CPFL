import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"

conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar TABELA 8
cursor.execute("""
CREATE TABLE IF NOT EXISTS TABELA_8 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipamento TEXT,
    potencia_kva TEXT,
    comprimento_cm TEXT,
    largura_cm TEXT,
    altura_cm TEXT,
    peso_kg TEXT,
    pe_direito_min_cm TEXT,
    espaco_compartimento TEXT
)
""")

# limpar dados antigos
cursor.execute("DELETE FROM TABELA_8")

dados = [

("Transformador","Até 75","122","82","104 (119)","505","315 (400)","200 x 260"),
("Transformador","112.5","141","90","106 (122)","640","315 (400)","200 x 260"),
("Transformador","150","145","90","115 (126)","765","315 (400)","200 x 260"),
("Transformador","225","170","107","125 (134)","1090","315 (400)","200 x 260"),
("Transformador","300","177","127","132 (142)","1250","315 (400)","200 x 260"),
("Transformador","500","200","125","142 (148)","1780","315 (400)","200 x 260"),
("Transformador","750","173","160","225","3065","400","200 x 260"),
("Transformador","1000","173 (186)","195","235","3650","400","250 x 260"),
("Transformador","1500","181 (203)","205","257","4885","450","250 x 260"),

("Disjuntor PVO","-","84","66","156 (158)","150 (210)","-","140 (200) x 260"),
("Prateleira TP e TC","-","130","45","140","-","-","-"),
("Muflas","-","-","-","-","-","-","100 x 260")

]

cursor.executemany("""
INSERT INTO TABELA_8 (
equipamento,
potencia_kva,
comprimento_cm,
largura_cm,
altura_cm,
peso_kg,
pe_direito_min_cm,
espaco_compartimento
)
VALUES (?,?,?,?,?,?,?,?)
""", dados)

conn.commit()

cursor.execute("SELECT COUNT(*) FROM TABELA_8")
print("Registros inseridos:", cursor.fetchone()[0])

conn.close()

print("TABELA 8 criada e preenchida com sucesso.")