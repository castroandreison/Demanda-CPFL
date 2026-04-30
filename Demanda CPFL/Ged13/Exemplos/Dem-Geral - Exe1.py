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
# FUNÇÃO DE ARREDONDAMENTO GED-13
# =================================================
def arredondar_kw(valor):
    return math.ceil(valor)

# =================================================
# ENQUADRAMENTO COMPLETO (CORRIGIDO)
# =================================================
def get_categorias(carga_kw, demanda_kva):

    # -------------------------
    # 127/220V
    # -------------------------
    cursor.execute("""
    SELECT categoria FROM tabela1a_monofasico
    WHERE categoria IN ('A1','A2')
    AND ? BETWEEN carga_min_kw AND carga_max_kw
    """, (carga_kw,))
    mono_127 = cursor.fetchone()
    mono_127 = mono_127[0] if mono_127 else None

    cursor.execute("""
    SELECT categoria FROM tabela1b_bifasico
    WHERE categoria IN ('B1','B2')
    AND ? BETWEEN carga_min_kw AND carga_max_kw
    """, (carga_kw,))
    bi_127 = cursor.fetchone()
    bi_127 = bi_127[0] if bi_127 else None

    cursor.execute("""
    SELECT categoria FROM tabela1c_trifasico_127_220
    WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva
    """, (demanda_kva,))
    tri_127 = cursor.fetchone()
    tri_127 = tri_127[0] if tri_127 else None

    # -------------------------
    # 220/380V
    # -------------------------
    cursor.execute("""
    SELECT categoria FROM tabela1a_monofasico
    WHERE categoria IN ('A3','A4')
    AND ? BETWEEN carga_min_kw AND carga_max_kw
    """, (carga_kw,))
    mono_220 = cursor.fetchone()
    mono_220 = mono_220[0] if mono_220 else None

    cursor.execute("""
    SELECT categoria FROM tabela1b_bifasico
    WHERE categoria = 'B3'
    AND ? BETWEEN carga_min_kw AND carga_max_kw
    """, (carga_kw,))
    bi_220 = cursor.fetchone()
    bi_220 = bi_220[0] if bi_220 else None

    cursor.execute("""
    SELECT categoria FROM tabela1c_trifasico_220_380
    WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva
    """, (demanda_kva,))
    tri_220 = cursor.fetchone()
    tri_220 = tri_220[0] if tri_220 else None

    return {
        "127/220V": (mono_127, bi_127, tri_127),
        "220/380V": (mono_220, bi_220, tri_220)
    }

# =================================================
# DIMENSIONAMENTO PADRÃO
# =================================================
def dimensionar_padrao(categoria):

    # MONOFÁSICO
    cursor.execute("""
    SELECT cobre_mm2,eletroduto,disjuntor,poste,caixa
    FROM tabela1a_monofasico
    WHERE categoria = ?
    """, (categoria,))
    r = cursor.fetchone()

    if r:
        print("\n🔌 PADRÃO DE ENTRADA")
        print("Tipo: MONOFÁSICO")
        print(f"Categoria: {categoria}")
        print(f"Disjuntor: {r[2]}")
        print(f"Cabo: {r[0]}")
        print(f"Eletroduto: {r[1]}")
        print(f"Poste: {r[3]}")
        print(f"Caixa: {r[4]}")
        return

    # BIFÁSICO
    cursor.execute("""
    SELECT cobre_mm2,eletroduto,disjuntor,poste,caixa
    FROM tabela1b_bifasico
    WHERE categoria = ?
    """, (categoria,))
    r = cursor.fetchone()

    if r:
        print("\n🔌 PADRÃO DE ENTRADA")
        print("Tipo: BIFÁSICO")
        print(f"Categoria: {categoria}")
        print(f"Disjuntor: {r[2]}")
        print(f"Cabo: {r[0]}")
        print(f"Eletroduto: {r[1]}")
        print(f"Poste: {r[3]}")
        print(f"Caixa: {r[4]}")
        return

    # TRIFÁSICO
    cursor.execute("""
    SELECT cobre_mm2,eletroduto,disjuntor,poste,caixa
    FROM tabela1c_trifasico_127_220
    WHERE categoria = ?
    """, (categoria,))
    r = cursor.fetchone()

    if not r:
        cursor.execute("""
        SELECT cobre_mm2,eletroduto,disjuntor,poste,caixa
        FROM tabela1c_trifasico_220_380
        WHERE categoria = ?
        """, (categoria,))
        r = cursor.fetchone()

    if r:
        print("\n🔌 PADRÃO DE ENTRADA")
        print("Tipo: TRIFÁSICO")
        print(f"Categoria: {categoria}")
        print(f"Disjuntor: {r[2]}")
        print(f"Cabo: {r[0]}")
        print(f"Eletroduto: {r[1]}")
        print(f"Poste: {r[3]}")
        print(f"Caixa: {r[4]}")
        return

# =================================================
# EXEMPLO 1 - GED 13
# =================================================

print("\n📘 EXEMPLO 1 - GED 13")
print("========================================")

# Cargas
tomadas = 2400
iluminacao = 400
chuveiro = 6500
ferro = 1000

print("\n🔹 CARGAS DECLARADAS")
print(f"Tomadas = {tomadas} W")
print(f"Iluminação = {iluminacao} W")
print(f"Chuveiro = {chuveiro} W")
print(f"Ferro = {ferro} W")

# -------------------------
# CARGA INSTALADA
# -------------------------
print("\n========================================")
print("📊 CÁLCULO DA CARGA INSTALADA")
print("========================================")

total_w = tomadas + iluminacao + chuveiro + ferro
print(f"Total = {total_w} W")

carga_kw = total_w / 1000
print(f"C = {carga_kw:.2f} kW")

# ARREDONDAMENTO
C = arredondar_kw(carga_kw)
print(f"C arredondado = {C} kW")

# -------------------------
# DEMANDA (SIMPLIFICADA)
# -------------------------
demanda_kva = C * 0.52  # aproximação tabela
print(f"\nDemanda estimada = {demanda_kva:.2f} kVA")

# -------------------------
# ENQUADRAMENTO
# -------------------------
cats = get_categorias(C, demanda_kva)

print("\n========================================")
print("🔎 ENQUADRAMENTO NA TABELA 1")
print("========================================")

print("\n127/220V:")
print(f"Monofásico → {cats['127/220V'][0]}")
print(f"Bifásico → {cats['127/220V'][1]}")
print(f"Trifásico → {cats['127/220V'][2]}")

print("\n220/380V:")
print(f"Monofásico → {cats['220/380V'][0]}")
print(f"Bifásico → {cats['220/380V'][1]}")
print(f"Trifásico → {cats['220/380V'][2]}")

# -------------------------
# RESULTADO FINAL
# -------------------------
print("\n========================================")
print("📌 CONCLUSÃO FINAL")
print("========================================")

print(f"Carga instalada = {C} kW")

print("\n👉 Conforme GED-13:")
print(f"127/220V → {cats['127/220V'][0]}")
print(f"220/380V → {cats['220/380V'][0]}")

# Escolhe automaticamente melhor opção
categoria_final = cats['127/220V'][0] or cats['127/220V'][1] or cats['127/220V'][2]

dimensionar_padrao(categoria_final)

# =================================================
# FINAL
# =================================================
conn.close()