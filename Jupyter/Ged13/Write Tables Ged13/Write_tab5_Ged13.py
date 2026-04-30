import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar Tabela 5
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela5 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quantidade_aparelhos INTEGER,
    fator_demanda REAL
)
""")

# Dados da Tabela 5
dados = [
(1, 1.00),
(2, 0.72),
(3, 0.62),
(4, 0.62)  # representa "acima de 3"
]

# Inserir dados
cursor.executemany("""
INSERT INTO tabela5
(quantidade_aparelhos, fator_demanda)
VALUES (?,?)
""", dados)

# Salvar alterações
conn.commit()

# Fechar conexão
conn.close()

print("Tabela 5 criada e preenchida com sucesso.")