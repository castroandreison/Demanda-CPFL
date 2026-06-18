import sqlite3
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, 'nbr5410.db')

conn = sqlite3.connect(_db_path)
cursor = conn.cursor()

# ─────────────────────────────────────────────────────
# TABELA 42 - Fatores de correção para condutores
# agrupados em feixe ou em camada única
# ─────────────────────────────────────────────────────
cursor.execute("DROP TABLE IF EXISTS tabela42_fator_agrupamento")
cursor.execute("""
CREATE TABLE tabela42_fator_agrupamento (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    forma_agrupamento TEXT,
    metodos_referencia TEXT,
    c1 REAL,
    c2 REAL,
    c3 REAL,
    c4 REAL,
    c5 REAL,
    c6 REAL,
    c7 REAL,
    c8 REAL,
    c9_11 REAL,
    c12_15 REAL,
    c16_19 REAL,
    c20_mais REAL
)
""")

dados_t42 = [
    ("Em feixe: ao ar livre ou sobre superficie; embutidos; em conduto fechado",
     "36 a 39 (metodos A a F)",
     1.00, 0.80, 0.70, 0.65, 0.60, 0.57, 0.54, 0.52, 0.50, 0.45, 0.41, 0.38),
    ("Camada unica sobre parede, piso, ou em bandeja nao perfurada ou prateleira",
     "36 e 37 (metodo C)",
     1.00, 0.85, 0.79, 0.75, 0.73, 0.72, 0.72, 0.71, 0.70, None, None, None),
    ("Camada unica no teto",
     "36 e 37 (metodo C)",
     0.95, 0.81, 0.72, 0.68, 0.66, 0.64, 0.63, 0.62, 0.61, None, None, None),
    ("Camada unica em bandeja perfurada",
     "38 e 39 (metodos E e F)",
     1.00, 0.88, 0.82, 0.77, 0.75, 0.73, 0.73, 0.72, 0.72, None, None, None),
    ("Camada unica sobre leito, suporte etc.",
     "38 e 39 (metodos E e F)",
     1.00, 0.87, 0.82, 0.80, 0.80, 0.79, 0.79, 0.78, 0.78, None, None, None),
]

cursor.executemany("""
INSERT INTO tabela42_fator_agrupamento
(forma_agrupamento, metodos_referencia,
 c1,c2,c3,c4,c5,c6,c7,c8,
 c9_11,c12_15,c16_19,c20_mais)
VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", dados_t42)

# ─────────────────────────────────────────────────────
# TABELA 43 - Fatores de correção para múltiplas camadas
# Métodos C (tabelas 36/37), E e F (tabelas 38/39)
# ─────────────────────────────────────────────────────
cursor.execute("DROP TABLE IF EXISTS tabela43_fator_multicamada")
cursor.execute("""
CREATE TABLE tabela43_fator_multicamada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    camadas TEXT,
    circuitos_2 REAL,
    circuitos_3 REAL,
    circuitos_4_5 REAL,
    circuitos_6_8 REAL,
    circuitos_9_mais REAL
)
""")

dados_t43 = [
    ("2", 0.68, 0.62, 0.60, 0.58, 0.56),
    ("3", 0.62, 0.57, 0.55, 0.53, 0.51),
    ("4 ou 5", 0.60, 0.55, 0.52, 0.51, 0.49),
    ("6 a 8", 0.58, 0.53, 0.51, 0.49, 0.48),
    ("9 e mais", 0.56, 0.51, 0.49, 0.48, 0.46),
]

cursor.executemany("""
INSERT INTO tabela43_fator_multicamada
(camadas, circuitos_2, circuitos_3, circuitos_4_5, circuitos_6_8, circuitos_9_mais)
VALUES (?,?,?,?,?,?)
""", dados_t43)

# ─────────────────────────────────────────────────────
# TABELA 44 - Fatores de agrupamento para cabos
# diretamente enterrados
# ─────────────────────────────────────────────────────
cursor.execute("DROP TABLE IF EXISTS tabela44_fator_enterrado_direto")
cursor.execute("""
CREATE TABLE tabela44_fator_enterrado_direto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    num_circuitos INTEGER,
    distancia_nula REAL,
    distancia_um_diametro REAL,
    distancia_0125m REAL,
    distancia_025m REAL,
    distancia_05m REAL
)
""")

dados_t44 = [
    (2, 0.75, 0.80, 0.85, 0.90, 0.90),
    (3, 0.65, 0.70, 0.75, 0.80, 0.85),
    (4, 0.60, 0.60, 0.70, 0.75, 0.80),
    (5, 0.55, 0.55, 0.65, 0.70, 0.80),
    (6, 0.50, 0.55, 0.60, 0.70, 0.80),
]

cursor.executemany("""
INSERT INTO tabela44_fator_enterrado_direto
(num_circuitos, distancia_nula, distancia_um_diametro, distancia_0125m, distancia_025m, distancia_05m)
VALUES (?,?,?,?,?,?)
""", dados_t44)

# ─────────────────────────────────────────────────────
# TABELA 45 - Fatores de agrupamento para linhas em
# eletrodutos enterrados
# ─────────────────────────────────────────────────────
cursor.execute("DROP TABLE IF EXISTS tabela45_fator_eletroduto_enterrado")
cursor.execute("""
CREATE TABLE tabela45_fator_eletroduto_enterrado (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_cabo TEXT,
    num_circuitos INTEGER,
    espacamento_nulo REAL,
    espacamento_025m REAL,
    espacamento_05m REAL,
    espacamento_1m REAL
)
""")

# Cabos multipolares em eletrodutos - um cabo por eletroduto
dados_t45 = [
    ("multipolar", 2, 0.85, 0.90, 0.95, 0.95),
    ("multipolar", 3, 0.75, 0.85, 0.90, 0.95),
    ("multipolar", 4, 0.70, 0.80, 0.85, 0.90),
    ("multipolar", 5, 0.65, 0.80, 0.85, 0.90),
    ("multipolar", 6, 0.60, 0.80, 0.80, 0.80),
    # Condutores isolados ou cabos unipolares - um condutor por eletroduto
    ("unipolar", 2, 0.80, 0.90, 0.90, 0.95),
    ("unipolar", 3, 0.70, 0.80, 0.85, 0.90),
    ("unipolar", 4, 0.65, 0.75, 0.80, 0.90),
    ("unipolar", 5, 0.60, 0.70, 0.80, 0.90),
    ("unipolar", 6, 0.60, 0.70, 0.80, 0.90),
]

cursor.executemany("""
INSERT INTO tabela45_fator_eletroduto_enterrado
(tipo_cabo, num_circuitos, espacamento_nulo, espacamento_025m, espacamento_05m, espacamento_1m)
VALUES (?,?,?,?,?,?)
""", dados_t45)

conn.commit()
conn.close()

print("Tabelas 42 a 45 inseridas com sucesso em:")
print(_db_path)
print()
print("tabela42_fator_agrupamento         - 5 linhas")
print("tabela43_fator_multicamada          - 5 linhas")
print("tabela44_fator_enterrado_direto     - 5 linhas")
print("tabela45_fator_eletroduto_enterrado - 10 linhas")
