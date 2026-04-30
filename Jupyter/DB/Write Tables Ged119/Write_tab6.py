import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()


# criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS TABELA_6 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_aparelhos TEXT,
    fator_demanda_comercial INTEGER,
    fator_demanda_residencial INTEGER
)
""")

# limpar registros antigos
cursor.execute("DELETE FROM TABELA_6")

dados = [

("1 a 10",100,100),
("11 a 20",90,86),
("21 a 30",82,80),
("31 a 40",80,78),
("41 a 50",77,75),
("51 a 75",75,73),
("acima de 75",75,70)

]

cursor.executemany("""
INSERT INTO TABELA_6 (
numero_aparelhos,
fator_demanda_comercial,
fator_demanda_residencial
)
VALUES (?,?,?)
""", dados)

conn.commit()

cursor.execute("SELECT COUNT(*) FROM TABELA_6")
print("Registros inseridos:", cursor.fetchone()[0])

conn.close()

print("TABELA 6 criada e preenchida com sucesso.")