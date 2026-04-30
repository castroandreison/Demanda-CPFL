import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS TABELA_1 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT,
    fator_demanda REAL,
    observacao TEXT
)
""")

# Dados da GED119
dados = [

("Auditórios, salões para exposição e semelhantes", 1.00, None),
("Bancos, lojas e semelhantes", 0.75, None),
("Barbearias, salões de beleza e semelhantes", 1.00, None),
("Clubes e semelhantes", 1.00, None),

("Escolas e semelhantes", 1.00, "Primeiros 12 kW"),
("Escolas e semelhantes", 0.50, "Excedente acima de 12 kW"),

("Escritórios", 1.00, "Primeiros 20 kW"),
("Escritórios", 0.70, "Excedente acima de 20 kW"),

("Garagens comerciais e semelhantes", 1.00, None),

("Hospitais e semelhantes", 0.40, "Primeiros 50 kW"),
("Hospitais e semelhantes", 0.20, "Excedente acima de 50 kW"),

("Igrejas e semelhantes", 1.00, None),
("Indústrias", 1.00, None),
("Restaurantes", 1.00, None),

]

# Inserir dados
cursor.executemany("""
INSERT INTO TABELA_1 (descricao, fator_demanda, observacao)
VALUES (?, ?, ?)
""", dados)

conn.commit()
conn.close()

print("Tabela 1 inserida no banco com sucesso.")