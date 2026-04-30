import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar Tabela 7
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela7 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qtd_min INTEGER,
    qtd_max INTEGER,
    fator_demanda REAL
)
""")

# Dados da Tabela 7
dados = [
(1,1,1.00),
(2,2,0.60),
(3,3,0.48),
(4,4,0.40),
(5,5,0.37),
(6,6,0.35),
(7,7,0.33),
(8,8,0.32),
(9,9,0.31),
(10,11,0.30),
(12,15,0.28),
(16,20,0.26),
(21,25,0.26),
(26,999,0.26)  # representa "acima de 25"
]

# Inserir dados
cursor.executemany("""
INSERT INTO tabela7
(qtd_min, qtd_max, fator_demanda)
VALUES (?,?,?)
""", dados)

# Salvar
conn.commit()

# Fechar conexão
conn.close()

print("Tabela 7 criada e preenchida com sucesso.")