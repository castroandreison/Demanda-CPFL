import sqlite3
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')
# =================================================
# CAMINHO DO BANCO
# =================================================
caminho_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\Jupyter\Ged13\Projeto TK\projetos.db"

os.makedirs(os.path.dirname(caminho_banco), exist_ok=True)

# =================================================
# CONEXÃO
# =================================================
conn = sqlite3.connect(caminho_banco)
cursor = conn.cursor()

print("Banco conectado")

# =================================================
# TABELA CARGAS (CATÁLOGO)
# =================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS cargas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    potencia REAL NOT NULL,
    tipo TEXT NOT NULL
)
""")

# Índice (melhora performance depois)
cursor.execute("CREATE INDEX IF NOT EXISTS idx_tipo ON cargas(tipo)")

print("✔ Tabela cargas pronta")

# =================================================
# DADOS PADRÃO (SEM DUPLICAR)
# =================================================
dados = [
    ("Tomadas", 100, "geral"),
    ("Iluminação", 100, "geral"),
    ("Chuveiro", 6500, "chuveiro"),
    ("Torneira", 5500, "chuveiro"),
    ("Ferro", 1000, "chuveiro"),
    ("Ar-condicionado", 1900, "ar"),
    ("Forno", 1500, "eletro"),
    ("Lava-louça", 1500, "eletro"),
    ("Secadora", 2500, "eletro"),
    ("Motor 1cv", 1050, "motor"),
]

for nome, potencia, tipo in dados:
    cursor.execute("""
    INSERT OR IGNORE INTO cargas (nome, potencia, tipo)
    VALUES (?, ?, ?)
    """, (nome, potencia, tipo))

print("✔ Cargas padrão garantidas")

# =================================================
# TABELA PROJETOS (NOVO)
# =================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS projetos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# =================================================
# ITENS DO PROJETO (RELACIONAMENTO)
# =================================================
cursor.execute("""
CREATE TABLE IF NOT EXISTS itens_projeto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER,
    carga_id INTEGER,
    quantidade INTEGER,
    
    FOREIGN KEY (projeto_id) REFERENCES projetos(id),
    FOREIGN KEY (carga_id) REFERENCES cargas(id)
)
""")

print("✔ Estrutura de projetos criada")

# =================================================
# TESTE
# =================================================
print("\n📊 CARGAS CADASTRADAS:")
cursor.execute("SELECT id, nome, potencia, tipo FROM cargas")

for linha in cursor.fetchall():
    print(linha)

# =================================================
# SALVAR E FECHAR
# =================================================
conn.commit()
conn.close()

print("\n✅ Banco pronto para uso profissional!")