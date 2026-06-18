import sqlite3
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, 'nbr5410.db')

conn = sqlite3.connect(_db_path)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS tabela48_neutro_reduzido")
cursor.execute("""
CREATE TABLE tabela48_neutro_reduzido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fase_mm2 REAL NOT NULL,
    neutro_mm2 REAL NOT NULL
)
""")

# Para fase <= 25, neutro = fase (mesma seção)
# Para os demais, conforme tabela
dados = [
    (35, 25),
    (50, 25),
    (70, 35),
    (95, 50),
    (120, 70),
    (150, 70),
    (185, 95),
    (240, 120),
    (300, 150),
    (400, 185),
]

cursor.executemany("""
INSERT INTO tabela48_neutro_reduzido (fase_mm2, neutro_mm2)
VALUES (?,?)
""", dados)

conn.commit()
conn.close()
print(f"Tabela 48 inserida em: {_db_path}")
print("tabela48_neutro_reduzido - 10 linhas")
