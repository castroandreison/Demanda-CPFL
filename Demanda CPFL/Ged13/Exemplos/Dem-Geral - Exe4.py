import sqlite3
import math
import sys

sys.stdout.reconfigure(encoding="utf-8")

# =================================================
# BANCO
# =================================================
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\Ged13\DB13\databaseCPFLGed13.db"

conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# =================================================
# DADOS (EXEMPLO 4)
# =================================================
cargas = {

    "iluminacao": [
        {"descricao": "Lâmpadas mistas", "potencia": 3000, "fp": 1},
        {"descricao": "Fluorescentes", "potencia": 960, "fp": 0.95},
        {"descricao": "Reatores", "potencia": 240, "fp": 1},
    ],

    "chuveiros": [
        {"descricao": "Chuveiro", "potencia": 6500, "fp": 1}
    ],

    "ar_condicionado": [
        {"descricao": "Ar 14000 BTU", "potencia": 4200, "fp": 1}
    ],

    "motores": [
        {"descricao": "Motor 10cv", "potencia_va": 11540},
        {"descricao": "Serra 7.5cv", "potencia_va": 8650},
        {"descricao": "Prensa 7.5cv", "potencia_va": 8650},
        {"descricao": "Motor 5cv", "potencia_va": 6020},
        {"descricao": "Motor 5cv", "potencia_va": 6020},
        {"descricao": "Motor 5cv", "potencia_va": 6020},
        {"descricao": "Serras 2cv", "potencia_va": 5400},
        {"descricao": "Furadeiras 1cv", "potencia_va": 6240},
    ],

    "solda": [
        {"descricao": "Solda 1", "potencia": 4000, "fp": 0.75, "fd": 1},
        {"descricao": "Solda 2", "potencia": 4000, "fp": 0.75, "fd": 0.6},
    ]
}

# =================================================
# FUNÇÕES
# =================================================

def arredonda_kw(valor):
    return math.ceil(valor)

def enquadrar(demanda):
    cursor.execute("""
    SELECT categoria FROM tabela1c_trifasico_127_220
    WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva
    """, (demanda,))
    cat127 = cursor.fetchone()

    cursor.execute("""
    SELECT categoria FROM tabela1c_trifasico_220_380
    WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva
    """, (demanda,))
    cat220 = cursor.fetchone()

    return (
        cat127[0] if cat127 else "Não definido",
        cat220[0] if cat220 else "Não definido"
    )

# =================================================
# CÁLCULO A (ILUMINAÇÃO)
# =================================================
print("\n🔹 a) ILUMINAÇÃO + TOMADAS")

total_va = 0

for item in cargas["iluminacao"]:
    va = item["potencia"] / item["fp"]
    total_va += va
    print(f"{item['descricao']}: {item['potencia']}W / FP {item['fp']} = {va:.2f} VA")

a = total_va / 1000
print(f"Total a = {a:.2f} kVA")

# =================================================
# CÁLCULO B (CHUVEIRO)
# =================================================
print("\n🔹 b) CHUVEIROS")

total_va = 0
for item in cargas["chuveiros"]:
    va = item["potencia"] / item["fp"]
    total_va += va
    print(f"{item['descricao']}: {va:.2f} VA")

b = total_va / 1000
print(f"Total b = {b:.2f} kVA")

# =================================================
# CÁLCULO F (AR)
# =================================================
print("\n🔹 f) AR CONDICIONADO")

total_va = 0
for item in cargas["ar_condicionado"]:
    va = item["potencia"] / item["fp"]
    total_va += va
    print(f"{item['descricao']}: {va:.2f} VA")

f = total_va / 1000
print(f"Total f = {f:.2f} kVA")

# =================================================
# CÁLCULO G (MOTORES)
# =================================================
print("\n🔹 g) MOTORES")

motores = sorted([m["potencia_va"] for m in cargas["motores"]], reverse=True)

g = 0

for i, pot in enumerate(motores):

    if i == 0:
        fd = 1
    elif i == 1:
        fd = 0.9
    elif i in [2, 3, 4]:
        fd = 0.8
    else:
        fd = 0.7

    demanda = pot * fd
    g += demanda

    print(f"Motor {i+1}: {pot} VA x {fd} = {demanda:.2f} VA")

g = g / 1000
print(f"Total g = {g:.2f} kVA")

# =================================================
# CÁLCULO H (SOLDA)
# =================================================
print("\n🔹 h) SOLDA")

total_va = 0
for item in cargas["solda"]:
    va = (item["potencia"] / item["fp"]) * item["fd"]
    total_va += va
    print(f"{item['descricao']}: {va:.2f} VA")

h = total_va / 1000
print(f"Total h = {h:.2f} kVA")

# =================================================
# DEMANDA TOTAL
# =================================================
print("\n==============================")
print("📊 DEMANDA TOTAL")
print("==============================")

D = a + b + f + g + h

print(f"a = {a:.2f}")
print(f"b = {b:.2f}")
print(f"f = {f:.2f}")
print(f"g = {g:.2f}")
print(f"h = {h:.2f}")

print(f"\n👉 D = {D:.2f} kVA")

# =================================================
# CARGA INSTALADA
# =================================================
print("\n🔹 CARGA INSTALADA")

carga_w = 0

for grupo in cargas:
    for item in cargas[grupo]:
        carga_w += item.get("potencia", 0)

carga_kw = carga_w / 1000
carga_kw_arred = arredonda_kw(carga_kw)

print(f"Carga total = {carga_kw:.2f} kW")
print(f"Carga arredondada = {carga_kw_arred} kW")

# =================================================
# ENQUADRAMENTO
# =================================================
print("\n🔹 ENQUADRAMENTO")

cat127, cat220 = enquadrar(D)

print(f"127/220V → {cat127}")
print(f"220/380V → {cat220}")

# =================================================
# PADRÃO
# =================================================
print("\n==============================")
print("🔌 PADRÃO DE ENTRADA")
print("==============================")

cursor.execute("""
SELECT disjuntor,cobre_mm2,eletroduto,poste,caixa
FROM tabela1c_trifasico_127_220
WHERE categoria = ?
""", (cat127,))

padrao = cursor.fetchone()

if padrao:
    print(f"Categoria: {cat127}")
    print(f"Disjuntor: {padrao[0]}")
    print(f"Cabo: {padrao[1]}")
    print(f"Eletroduto: {padrao[2]}")
    print(f"Poste: {padrao[3]}")
    print(f"Caixa: {padrao[4]}")

conn.close()