import sqlite3

# Caminho do banco
banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"
conn = sqlite3.connect(banco)
cursor = conn.cursor()

# Criar TABELA 3
cursor.execute("""
CREATE TABLE IF NOT EXISTS TABELA_3 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    finalidade TEXT,
    potencia_minima_w INTEGER
)
""")

# limpar registros antigos (opcional)
cursor.execute("DELETE FROM TABELA_3")

# dados da GED119
dados = [

("Torneira Elétrica", 3000),
("Chuveiro Elétrico", 5400),
("Máquina Lavar Louça", 2000),
("Máquina Secar Roupa", 2500),
("Forno de Microondas", 1500),
("Forno Elétrico", 1500),
("Ferro Elétrico", 1000)

]

# inserir dados
cursor.executemany("""
INSERT INTO TABELA_3 (finalidade, potencia_minima_w)
VALUES (?,?)
""", dados)

conn.commit()

# verificar inserção
cursor.execute("SELECT COUNT(*) FROM TABELA_3")
print("Registros inseridos:", cursor.fetchone()[0])

conn.close()

print("TABELA 3 criada e preenchida com sucesso.")