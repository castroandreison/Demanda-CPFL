import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar Tabela 6
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela6 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    qtd_min INTEGER,
    qtd_max INTEGER,
    fator_demanda REAL
)
""")

# Dados da Tabela 6
dados = [
(1,1,1.00),
(2,4,0.70),
(5,6,0.60),
(7,8,0.50),
(9,999,0.50)  # representa "acima de 8"
]

# Inserir dados
cursor.executemany("""
INSERT INTO tabela6
(qtd_min, qtd_max, fator_demanda)
VALUES (?,?,?)
""", dados)

# Salvar alterações
conn.commit()

# Fechar conexão
conn.close()

print("Tabela 6 criada e preenchida com sucesso.")