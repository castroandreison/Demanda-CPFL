import sqlite3
import os

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Criar conexão
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# Criar Tabela 8 - Ar Condicionado
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela_8_ar_condicionado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    btu_h INTEGER,
    kcal_h INTEGER,
    tensao INTEGER,
    corrente REAL,
    potencia_va INTEGER,
    potencia_w INTEGER
)
""")

# Dados da tabela GED-13
dados = [
    (7100, 1775, 110, 10, 1100, 900),
    (7100, 1775, 220, 5, 1100, 900),

    (8500, 2125, 110, 14, 1550, 1300),
    (8500, 2125, 220, 7, 1550, 1300),

    (10000, 2500, 110, 15, 1650, 1400),
    (10000, 2500, 220, 7.5, 1650, 1400),

    (12000, 3000, 110, 17, 1900, 1600),
    (12000, 3000, 220, 8.5, 1900, 1600),

    (14000, 3500, 220, 9.5, 2100, 1900),

    (18000, 4500, 220, 13, 2860, 2600),

    (21000, 5250, 220, 14, 3080, 2800),

    (30000, 7500, 220, 18, 4000, 3600)
]

# Inserir dados
cursor.executemany("""
INSERT INTO tabela_8_ar_condicionado 
(btu_h, kcal_h, tensao, corrente, potencia_va, potencia_w)
VALUES (?, ?, ?, ?, ?, ?)
""", dados)

conn.commit()

# Mostrar quantidade inserida
cursor.execute("SELECT COUNT(*) FROM tabela_8_ar_condicionado")
total = cursor.fetchone()[0]

print(f"Tabela 8 criada com sucesso.")
print(f"Registros inseridos: {total}")

# Fechar conexão
conn.close()

# Confirmação do banco
if os.path.exists(nome_banco):
    print(f"\nBanco '{nome_banco}' pronto para uso.")
else:
    print("Erro ao criar o banco.")