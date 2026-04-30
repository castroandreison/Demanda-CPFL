import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela_11 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    equipamento TEXT,
    classificacao TEXT,
    fator_demanda REAL
)
""")

# Dados da tabela
dados = [
    ("Solda a arco e Galvanização", "1º maior", 1.00),
    ("Solda a arco e Galvanização", "2º maior", 0.70),
    ("Solda a arco e Galvanização", "3º maior", 0.40),
    ("Solda a arco e Galvanização", "Soma dos demais", 0.30),

    ("Solda a resistência", "Maior", 1.00),
    ("Solda a resistência", "Soma dos demais", 0.60),

    ("Raios-x", "Maior", 1.00),
    ("Raios-x", "Soma dos demais", 0.70)
]

# Inserir dados
cursor.executemany("""
INSERT INTO tabela_11 (equipamento, classificacao, fator_demanda)
VALUES (?, ? ,?)
""", dados)

# Salvar
conn.commit()
conn.close()

print("Tabela 11 criada e dados inseridos com sucesso.")