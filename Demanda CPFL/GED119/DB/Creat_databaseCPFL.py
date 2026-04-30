import sqlite3
import os

# Nome do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"

# Criar conexão (isso já cria o arquivo do banco se não existir)
conn = sqlite3.connect(nome_banco)

# Fechar conexão
conn.close()

# Confirmação
if os.path.exists(nome_banco):
    print(f"Banco '{nome_banco}' criado com sucesso.")
else:
    print("Erro ao criar o banco.")