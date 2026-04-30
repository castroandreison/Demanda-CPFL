import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar Tabela 3
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela3 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    carga_min_kw REAL,
    carga_max_kw REAL,
    fator_demanda REAL
)
""")

# Dados da Tabela 3
dados = [
(0,1,0.86),
(1,2,0.75),
(2,3,0.66),
(3,4,0.59),
(4,5,0.52),
(5,6,0.45),
(6,7,0.40),
(7,8,0.35),
(8,9,0.31),
(9,10,0.27),
(10,9999,0.24)
]

# Inserir dados
cursor.executemany("""
INSERT INTO tabela3
(carga_min_kw, carga_max_kw, fator_demanda)
VALUES (?,?,?)
""", dados)

# Salvar alterações
conn.commit()

# Fechar conexão
conn.close()

print("Tabela 3 criada e preenchida com sucesso.")