import sqlite3

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar Tabela 4
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela4 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero_aparelhos INTEGER,
    fator_demanda REAL
)
""")

# Dados da Tabela 4
dados = [
(1,1.00),
(2,1.00),
(3,0.84),
(4,0.76),
(5,0.70),
(6,0.65),
(7,0.60),
(8,0.57),
(9,0.54),
(10,0.52),
(11,0.49),
(12,0.48),
(13,0.46),
(14,0.45),
(15,0.44),
(16,0.43),
(17,0.42),
(18,0.41),
(19,0.40),
(20,0.40),
(21,0.39),
(22,0.39),
(23,0.39),
(24,0.38),
(25,0.38),
(26,0.38)  # representa "acima de 25"
]

# Inserir dados
cursor.executemany("""
INSERT INTO tabela4
(numero_aparelhos, fator_demanda)
VALUES (?,?)
""", dados)

# Salvar alterações
conn.commit()

# Fechar conexão
conn.close()

print("Tabela 4 criada e preenchida com sucesso.")