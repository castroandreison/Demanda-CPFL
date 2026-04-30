import sqlite3
import sys

# Corrigir acentuação no terminal
sys.stdout.reconfigure(encoding="utf-8")

# Caminho do banco
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

# Conectar ao banco
conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# ------------------------------------------------
# CRIAR TABELA 12
# ------------------------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS tabela_12 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo_partida TEXT,
    tipo_chave TEXT,
    potencia_motor TEXT,
    tipo_motor TEXT,
    tipo_rotor TEXT,
    tensao_rede TEXT,
    tensao_placa_motor TEXT,
    numero_terminais TEXT,
    taps TEXT,
    taps_partida TEXT
)
""")

# ------------------------------------------------
# LIMPAR TABELA (evita duplicar registros)
# ------------------------------------------------

cursor.execute("DELETE FROM tabela_12")

# ------------------------------------------------
# DADOS DA TABELA GED13
# ------------------------------------------------

dados = [

("Direta", "-", "P ≤ 5", "-", "-", "220/127", "380/220", "6 Δ", "-", "-"),
("Direta", "-", "P ≤ 7,5", "-", "-", "380/220", "380/220", "6 Y", "-", "-"),

("Indireta Manual", "Estrela-Triângulo", "5 < P ≤ 15", "Indução", "Gaiola", "220/127", "380/220", "6 Y ou 6 Δ", "-", "-"),
("Indireta Manual", "Estrela-Triângulo", "7,5 < P ≤ 25", "Indução", "Gaiola", "380/220", "660/380", "6 Y ou 6 Δ", "-", "-"),

("Indireta Manual", "Série-Paralelo", "5 < P ≤ 15", "Indução", "Gaiola", "220/127", "220/380/440/760", "12 ou 12 Δ//", "-", "-"),
("Indireta Manual", "Série-Paralelo", "7,5 < P ≤ 25", "Indução", "Gaiola", "380/220", "220/380/440/760", "9 Y S ou 9 Y//", "-", "-"),

("Indireta Manual", "Chave Compensadora", "5 < P ≤ 15", "Indução", "Gaiola", "220/127", "380/220", "6 Y ou 6 Δ", "50,65,80", "50"),
("Indireta Manual", "Chave Compensadora", "7,5 < P ≤ 25", "Indução", "Gaiola", "380/220", "220/380/440/760", "12 Δ// ou 12 Y//", "50,65,80", "50"),

("Indireta Automática", "Estrela-Triângulo", "5 < P ≤ 50", "Indução", "Gaiola", "-", "-", "-", "-", "-"),
("Indireta Automática", "Série-Paralelo", "5 < P ≤ 50", "Indução", "Gaiola", "-", "-", "-", "-", "-"),
("Indireta Automática", "Soft Starter", "5 < P ≤ 50", "Indução", "Gaiola", "-", "-", "-", "-", "-"),
("Indireta Automática", "Inversor de Frequência", "5 ≤ P ≤ 50", "Indução", "Gaiola", "-", "-", "-", "-", "-"),
("Indireta Automática", "Chave Compensadora", "5 < P ≤ 50", "Indução", "Gaiola", "-", "-", "-", "-", "-")

]

# ------------------------------------------------
# INSERIR DADOS
# ------------------------------------------------

cursor.executemany("""
INSERT INTO tabela_12 (
tipo_partida,
tipo_chave,
potencia_motor,
tipo_motor,
tipo_rotor,
tensao_rede,
tensao_placa_motor,
numero_terminais,
taps,
taps_partida
)
VALUES (?,?,?,?,?,?,?,?,?,?)
""", dados)

# Salvar alterações
conn.commit()

print("✔ Tabela 12 criada e preenchida com sucesso.")

# Fechar conexão
conn.close()