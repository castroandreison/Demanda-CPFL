import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()


# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela_15 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    carga_minima_w_m2 REAL,
    fator_demanda TEXT
)
""")

dados = [

("Auditório, salões para exposições e semelhantes",10,"1"),

("Bancos, lojas e semelhantes",30,"1"),

("Barbearias, salões de beleza e semelhantes",30,"1"),

("Clubes e semelhantes",20,"1"),

("Escolas e semelhantes",30,"1 para os primeiros 12 kW; 0,50 para o que exceder a 12 kW"),

("Escritórios (edifícios)",30,"1 para os primeiros 20 kW; 0,70 para o que exceder a 20 kW"),

("Garagens comerciais e semelhantes",5,"1"),

("Hospitais e semelhantes",20,"0,40 para os primeiros 50 kW; 0,20 para o que exceder a 50 kW"),

("Hotéis e semelhantes",20,"0,50 para os primeiros 20 kW; 0,40 para o que exceder a 20 kW"),

("Igrejas e semelhantes",10,"1"),

("Indústrias","Conforme declarado","1"),

("Restaurantes e semelhantes",20,"1")

]

cursor.executemany("""
INSERT INTO tabela_15 (
descricao,
carga_minima_w_m2,
fator_demanda
)
VALUES (?,?,?)
""", dados)

conn.commit()
conn.close()

print("Tabela 15 criada e preenchida com sucesso.")