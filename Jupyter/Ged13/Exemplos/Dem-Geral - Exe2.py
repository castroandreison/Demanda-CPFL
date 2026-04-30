import sqlite3
import sys
import math

sys.stdout.reconfigure(encoding="utf-8")

# =================================================
# BANCO
# =================================================
nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# =================================================
# FUNÇÕES BASE
# =================================================

def fd_kw(tabela, valor):
    cursor.execute(f"""
        SELECT fator_demanda
        FROM {tabela}
        WHERE ? BETWEEN carga_min_kw AND carga_max_kw
        LIMIT 1
    """, (valor,))
    r = cursor.fetchone()
    return r[0] if r else 1


# =================================================
# ENQUADRAMENTO MONO / BI
# =================================================

def enquadrar_mono(carga_kw):
    carga_kw = math.ceil(carga_kw)

    cursor.execute("""
    SELECT categoria
    FROM tabela1a_monofasico
    WHERE ? > carga_min_kw AND ? <= carga_max_kw
    LIMIT 1
    """, (carga_kw, carga_kw))

    r = cursor.fetchone()
    return r[0] if r else "Não permitido"


def enquadrar_bifasico(carga_kw):
    carga_kw = math.ceil(carga_kw)

    cursor.execute("""
    SELECT categoria
    FROM tabela1b_bifasico
    WHERE ? >= carga_min_kw AND ? <= carga_max_kw
    """, (carga_kw, carga_kw))

    resultados = cursor.fetchall()

    saida = []

    for r in resultados:
        cat = r[0]

        if cat in ["B1", "B2"]:
            saida.append(("127/220 V", cat))

        elif cat == "B3":
            saida.append(("220/380 V", cat))

    return saida


# =================================================
# ENQUADRAMENTO TRIFÁSICO
# =================================================

def enquadrar_trifasico(demanda_kva):

    # 127/220
    cursor.execute("""
    SELECT categoria
    FROM tabela1c_trifasico_127_220
    WHERE ? > demanda_min_kva AND ? <= demanda_max_kva
    LIMIT 1
    """, (demanda_kva, demanda_kva))

    tri_127 = cursor.fetchone()
    tri_127 = tri_127[0] if tri_127 else None

    # 220/380
    cursor.execute("""
    SELECT categoria
    FROM tabela1c_trifasico_220_380
    WHERE ? > demanda_min_kva AND ? <= demanda_max_kva
    LIMIT 1
    """, (demanda_kva, demanda_kva))

    tri_220 = cursor.fetchone()
    tri_220 = tri_220[0] if tri_220 else None

    return tri_127, tri_220


# =================================================
# DIMENSIONAMENTO PADRÃO
# =================================================

def dimensionar_padrao(carga_kw, demanda_kva):

    print("\n==============================")
    print("🔌 PADRÃO DE ENTRADA")
    print("==============================")

    print(f"Carga instalada = {carga_kw:.2f} kW")
    print(f"Demanda = {demanda_kva:.2f} kVA\n")

    # MONOFÁSICO
    cursor.execute("""
    SELECT categoria,cobre_mm2,eletroduto,disjuntor,poste,caixa
    FROM tabela1a_monofasico
    WHERE ? > carga_min_kw AND ? <= carga_max_kw
    LIMIT 1
    """,(carga_kw,carga_kw))

    mono = cursor.fetchone()

    if mono:
        print("Tipo: MONOFÁSICO")
        print(f"Categoria: {mono[0]}")
        print(f"Disjuntor: {mono[3]}")
        print(f"Cabo: {mono[1]}")
        print(f"Eletroduto: {mono[2]}")
        print(f"Poste: {mono[4]}")
        print(f"Caixa: {mono[5]}")
        return mono[0]

    # BIFÁSICO
    cursor.execute("""
    SELECT categoria,cobre_mm2,eletroduto,disjuntor,poste,caixa
    FROM tabela1b_bifasico
    WHERE ? >= carga_min_kw AND ? <= carga_max_kw
    LIMIT 1
    """,(carga_kw,carga_kw))

    bi = cursor.fetchone()

    if bi:
        print("Tipo: BIFÁSICO")
        print(f"Categoria: {bi[0]}")
        print(f"Disjuntor: {bi[3]}")
        print(f"Cabo: {bi[1]}")
        print(f"Eletroduto: {bi[2]}")
        print(f"Poste: {bi[4]}")
        print(f"Caixa: {bi[5]}")
        return bi[0]

    # TRIFÁSICO
    cursor.execute("""
    SELECT categoria,cobre_mm2,eletroduto,disjuntor,poste,caixa
    FROM tabela1c_trifasico_127_220
    WHERE ? > demanda_min_kva AND ? <= demanda_max_kva
    LIMIT 1
    """,(demanda_kva,demanda_kva))

    tri = cursor.fetchone()

    if tri:
        print("Tipo: TRIFÁSICO")
        print(f"Categoria: {tri[0]}")
        print(f"Disjuntor: {tri[3]}")
        print(f"Cabo: {tri[1]}")
        print(f"Eletroduto: {tri[2]}")
        print(f"Poste: {tri[4]}")
        print(f"Caixa: {tri[5]}")
        return tri[0]

    print("Nenhum enquadramento encontrado")
    return None


# =================================================
# POSTE 2 CLIENTES
# =================================================

def dimensionar_poste_duplo(cat1, cat2, tensao):

    cursor.execute("""
    SELECT ramal,tipo_rede,poste
    FROM tabela1d_dois_clientes
    WHERE tensao = ?
    AND (
        (cliente1 = ? AND cliente2 = ?)
        OR
        (cliente1 = ? AND cliente2 = ?)
    )
    """, (tensao, cat1, cat2, cat2, cat1))

    r = cursor.fetchone()

    print("\n==============================")
    print("🏗️ POSTE PARA 2 CLIENTES")
    print("==============================")

    print(f"Cliente 1: {cat1}")
    print(f"Cliente 2: {cat2}")
    print(f"Tensão: {tensao}")

    if r:
        print(f"Ramal: {r[0]}")
        print(f"Rede: {r[1]}")
        print(f"Poste: {r[2]}")
    else:
        print("Combinação não encontrada")


# =================================================
# EXEMPLO 2 - GED
# =================================================

print("\n==============================")
print("📘 EXEMPLO 2 - GED 13")
print("==============================")

# DADOS
tomadas = 2800
iluminacao = 1000
chuveiros = 2 * 6500
torneira = 5500
ferro = 1000

# CARGA TOTAL
total_w = tomadas + iluminacao + chuveiros + torneira + ferro
carga_kw = total_w / 1000
carga_kw_arred = math.ceil(carga_kw)

print(f"Carga total = {total_w} W")
print(f"Carga total = {carga_kw:.2f} kW")
print(f"Carga arredondada = {carga_kw_arred} kW")

# DEMANDA
fd = fd_kw("tabela3", carga_kw_arred)
demanda = carga_kw_arred * fd

print(f"Demanda estimada = {demanda:.2f} kVA")

# =================================================
# ENQUADRAMENTO
# =================================================

mono = enquadrar_mono(carga_kw_arred)
bi_lista = enquadrar_bifasico(carga_kw_arred)
tri_127, tri_220 = enquadrar_trifasico(demanda)

print("\n🔹 ENQUADRAMENTO (GED CORRETO)")

print(f"Monofásico: {mono}")

print("\nBifásico:")
for t, c in bi_lista:
    print(f"{t} → {c}")

print("\nTrifásico:")
print(f"127/220 V → {tri_127}")
print(f"220/380 V → {tri_220}")

# =================================================
# PADRÃO
# =================================================

categoria_escolhida = dimensionar_padrao(carga_kw_arred, demanda)

# =================================================
# EXEMPLO POSTE DUPLO
# =================================================

print("\n🔹 EXEMPLO POSTE DUPLO")

dimensionar_poste_duplo("B2", "A1", "127/220V")

# =================================================
# FINAL
# =================================================

conn.close()