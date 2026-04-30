import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Buscar dados
cursor.execute("SELECT * FROM tabela_8")

dados = cursor.fetchall()

print("\n==============================")
print("TABELA 8 - TIPOS DE PARTIDA DE MOTORES")
print("==============================\n")

for linha in dados:
    print(linha)

conn.close()