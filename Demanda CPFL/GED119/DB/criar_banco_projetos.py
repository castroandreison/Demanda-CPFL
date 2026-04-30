import sqlite3
import os

caminho = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\projetos_ged119.db"

os.makedirs(os.path.dirname(caminho), exist_ok=True)

conn = sqlite3.connect(caminho)
cursor = conn.cursor()

# ---------------- PROJETOS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS PROJETOS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    cliente TEXT,
    endereco TEXT,
    data_criacao TEXT,
    area_total REAL,
    tipo_edificacao TEXT
)
""")

# ---------------- CARGAS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS CARGAS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER,
    descricao TEXT,
    potencia_kw REAL,
    quantidade INTEGER,
    categoria TEXT,
    tipo_carga TEXT
)
""")

# ---------------- RESULTADOS ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS RESULTADOS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER,
    carga_instalada REAL,
    demanda_calculada REAL,
    transformador TEXT,
    disjuntor TEXT
)
""")

# ---------------- EDIFICIO ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS EDIFICIO (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER,
    area_administracao REAL,
    area_apartamento REAL,
    quantidade_apartamentos INTEGER
)
""")

# ---------------- Iluminacao   e tomadas ----------------
cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela_iluminacao_tomadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    iluminacao_w_m2 REAL,
    tomadas_w_m2 REAL

)
""")


conn.commit()
conn.close()

print("Banco de dados criado com sucesso.")