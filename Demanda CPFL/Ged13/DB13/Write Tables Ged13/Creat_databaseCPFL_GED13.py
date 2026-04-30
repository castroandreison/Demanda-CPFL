import sqlite3
import os

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Criar o banco (arquivo .db)
conn = sqlite3.connect(nome_banco)

# Fechar conexão
conn.close()

# Verificar se foi criado
if os.path.exists(nome_banco):
    print("Banco criado com sucesso.")
else:
    print("Erro ao criar o banco.")