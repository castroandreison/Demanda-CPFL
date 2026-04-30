import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

# =================================================
# BANCO
# =================================================

nome_banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

conn = sqlite3.connect(nome_banco)
cursor = conn.cursor()

# =================================================
# FUNÇÕES
# =================================================

def fd_kw(tabela, valor):
    cursor.execute(f"""
        SELECT fator_demanda
        FROM {tabela}
        WHERE ? BETWEEN carga_min_kw AND carga_max_kw
        LIMIT 1
    """, (valor,))
    
    r = cursor.fetchone()
    return r[0] if r else 0


def fd_qtd_faixa(tabela, qtd):
    cursor.execute(f"""
        SELECT fator_demanda
        FROM {tabela}
        WHERE ? BETWEEN qtd_min AND qtd_max
        LIMIT 1
    """, (qtd,))
    
    r = cursor.fetchone()
    return r[0] if r else 0


def fd_qtd_exata(tabela, qtd):
    cursor.execute(f"""
        SELECT fator_demanda
        FROM {tabela}
        WHERE numero_aparelhos = ?
        LIMIT 1
    """, (qtd,))
    
    r = cursor.fetchone()
    return r[0] if r else 0


def get_valor(tabela, campo_busca, valor, campo_saida):

    cursor.execute(f"""
        SELECT {campo_saida}
        FROM {tabela}
        WHERE {campo_busca} = ?
        LIMIT 1
    """, (valor,))
    
    r = cursor.fetchone()
    return r[0] if r else 0


def get_categoria_entrada(demanda_kva):
    
    # MONOFÁSICO
    cursor.execute("""
    SELECT categoria
    FROM tabela1a_monofasico
    WHERE ? BETWEEN carga_min_kw AND carga_max_kw
    LIMIT 1
    """, (demanda_kva,))
    mono = cursor.fetchone()
    mono = mono[0] if mono else None


    # BIFÁSICO
    cursor.execute("""
    SELECT categoria
    FROM tabela1b_bifasico
    WHERE ? BETWEEN carga_min_kw AND carga_max_kw
    LIMIT 1
    """, (demanda_kva,))
    bi = cursor.fetchone()
    bi = bi[0] if bi else None


    # TRIFÁSICO
    cursor.execute("""
    SELECT categoria
    FROM tabela1c_trifasico_127_220
    WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva
    LIMIT 1
    """, (demanda_kva,))
    tri = cursor.fetchone()
    tri = tri[0] if tri else None

    return mono, bi, tri


def dimensionar_poste_duplo(cat1, cat2, tensao="127/220V"):
    
    cursor.execute("""
    SELECT ramal, tipo_rede, poste
    FROM tabela1d_dois_clientes
    WHERE tensao = ?
    AND (
        (cliente1 = ? AND cliente2 = ?)
        OR
        (cliente1 = ? AND cliente2 = ?)
    )
    LIMIT 1
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
        print(f"Tipo de rede: {r[1]}")
        print(f"Poste: {r[2]}")
    else:
        print("Combinação não encontrada na tabela.")


def dimensionar_padrao(demanda_kva):
    
    # ---------------------------------------
    # MONOFÁSICO
    # ---------------------------------------
    cursor.execute("""
    SELECT categoria,cobre_mm2,aluminio_mm2,eletroduto,disjuntor,
           aterramento_condutor,poste,caixa,limite_motor
    FROM tabela1a_monofasico
    WHERE ? BETWEEN carga_min_kw AND carga_max_kw
    LIMIT 1
    """,(demanda_kva,))

    mono = cursor.fetchone()

    # ---------------------------------------
    # BIFÁSICO
    # ---------------------------------------
    cursor.execute("""
    SELECT categoria,cobre_mm2,aluminio_mm2,eletroduto,disjuntor,
           aterramento_condutor,poste,caixa,motor_fn,motor_ff
    FROM tabela1b_bifasico
    WHERE ? BETWEEN carga_min_kw AND carga_max_kw
    LIMIT 1
    """,(demanda_kva,))

    bi = cursor.fetchone()

    # ---------------------------------------
    # TRIFÁSICO
    # ---------------------------------------
    cursor.execute("""
    SELECT categoria,cobre_mm2,aluminio_mm2,eletroduto,disjuntor,
           aterramento_condutor,poste,caixa,motor_fn,motor_ff,motor_fff
    FROM tabela1c_trifasico_127_220
    WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva
    LIMIT 1
    """,(demanda_kva,))

    tri = cursor.fetchone()


    # ---------------------------------------
    # RESULTADO
    # ---------------------------------------

    print("\n==============================")
    print("🔌 PADRÃO DE ENTRADA")
    print("==============================")

    print(f"Demanda Total = {demanda_kva:.2f} kVA\n")


    if mono:
        print("Tipo de ligação: MONOFÁSICO")
        print(f"Categoria: {mono[0]}")
        print(f"Cabo cobre: {mono[1]}")
        print(f"Cabo alumínio: {mono[2]}")
        print(f"Eletroduto: {mono[3]}")
        print(f"Disjuntor: {mono[4]}")
        print(f"Aterramento: {mono[5]}")
        print(f"Poste padrão: {mono[6]}")
        print(f"Caixa de medição: {mono[7]}")
        print(f"Limite motor: {mono[8]}")
        return


    if bi:
        print("Tipo de ligação: BIFÁSICO")
        print(f"Categoria: {bi[0]}")
        print(f"Cabo cobre: {bi[1]}")
        print(f"Cabo alumínio: {bi[2]}")
        print(f"Eletroduto: {bi[3]}")
        print(f"Disjuntor: {bi[4]}")
        print(f"Aterramento: {bi[5]}")
        print(f"Poste padrão: {bi[6]}")
        print(f"Caixa de medição: {bi[7]}")
        print(f"Motor FN máx: {bi[8]}")
        print(f"Motor FF máx: {bi[9]}")
        return


    if tri:
        print("Tipo de ligação: TRIFÁSICO")
        print(f"Categoria: {tri[0]}")
        print(f"Cabo cobre: {tri[1]}")
        print(f"Cabo alumínio: {tri[2]}")
        print(f"Eletroduto: {tri[3]}")
        print(f"Disjuntor: {tri[4]}")
        print(f"Aterramento: {tri[5]}")
        print(f"Poste padrão: {tri[6]}")
        print(f"Caixa de medição: {tri[7]}")
        print(f"Motor FN máx: {tri[8]}")
        print(f"Motor FF máx: {tri[9]}")
        print(f"Motor FFF máx: {tri[10]}")
        return


    print("Nenhuma categoria encontrada.")

# =================================================
# INÍCIO
# =================================================

print("\n==============================")
print("GED-13 - MEMORIAL COMPLETO")
print("==============================\n")

# ------------------------------------------------
# TOMADAS + ILUMINAÇÃO
# ------------------------------------------------

print("🔹 TOMADAS + ILUMINAÇÃO")

tomadas = 3000
iluminacao = 1200

print(f"Tomadas = {tomadas} W")
print(f"Iluminação = {iluminacao} W")

carga_a = (tomadas + iluminacao) / 1000
fd_a = fd_kw("tabela3", carga_a)
a = carga_a * fd_a

print(f"A base = {carga_a:.2f} kW")
print(f"FD A = {fd_a}")
print(f"A = {a:.2f} kVA\n")

# ------------------------------------------------
# CHUVEIROS / TORNEIRA / FERRO
# ------------------------------------------------

print("🔹 CHUVEIROS / TORNEIRA / FERRO")

chuveiros = 4 * 6500
torneira = 5500
ferro = 1000

print(f"Chuveiros = {chuveiros} W")
print(f"Torneira = {torneira} W")
print(f"Ferro = {ferro} W")

carga_b = (chuveiros + torneira + ferro) / 1000
fd_b = fd_qtd_exata("tabela4", 6)
b = carga_b * fd_b

print(f"B base = {carga_b:.2f} kW")
print(f"FD B = {fd_b}")
print(f"B = {b:.2f} kVA\n")

# ------------------------------------------------
# ELETRODOMÉSTICOS
# ------------------------------------------------

print("🔹 ELETRODOMÉSTICOS")

forno = 1500
lava = 1500
secadora = 2500

print(f"Forno = {forno} W")
print(f"Lava-louça = {lava} W")
print(f"Secadora = {secadora} W")

carga_d = (forno + lava + secadora) / 1000
fd_d = fd_qtd_faixa("tabela6", 3)
d = carga_d * fd_d

print(f"D base = {carga_d:.2f} kW")
print(f"FD D = {fd_d}")
print(f"D = {d:.2f} kVA\n")

# ------------------------------------------------
# AR CONDICIONADO
# ------------------------------------------------

print("🔹 AR CONDICIONADO")

va_ar = get_valor("tabela8", "btu_h", 14000, "potencia_va")

print(f"Ar-condicionado unitário = {va_ar} VA")
print("Quantidade = 2")

f = (2 * va_ar) / 1000
print(f"F = {f:.2f} kVA\n")

# ------------------------------------------------
# MOTORES
# ------------------------------------------------

print("🔹 MOTORES")

motor_kva = get_valor("tabela_14", "potencia_nominal", "1", "potencia_kva")

print(f"Motor unitário = {motor_kva} kVA")
print("Quantidade = 2")

g = motor_kva * 1 + motor_kva * 0.9
print(f"G = {g:.2f} kVA\n")

# ------------------------------------------------
# DEMANDA TOTAL
# ------------------------------------------------

print("==============================")
print("📊 DEMANDA TOTAL")
print("==============================")

D = a + b + d + f + g

print(f"A = {a:.2f} kVA")
print(f"B = {b:.2f} kVA")
print(f"D = {d:.2f} kVA")
print(f"F = {f:.2f} kVA")
print(f"G = {g:.2f} kVA")

print("\n==============================")
print("👉 RESULTADO FINAL")
print("==============================")

print(f"Demanda Total = {D:.2f} kVA")

# ------------------------------------------------
# CARGA INSTALADA
# ------------------------------------------------

carga_instalada = carga_a + carga_b + carga_d + f + g

print("\n🔹 CARGA INSTALADA TOTAL")
print(f"Carga Instalada = {carga_instalada:.2f} kW")

# ------------------------------------------------
# ENQUADRAMENTO TABELA 1
# ------------------------------------------------
mono, bi, tri = get_categoria_entrada(D)

print("\n🔹 ENQUADRAMENTO PADRÃO DE ENTRADA (TABELA 1)")

print(f"Monofásico → Categoria {mono if mono else 'Não permitido'}")
print(f"Bifásico → Categoria {bi if bi else 'Não permitido'}")
print(f"Trifásico → Categoria {tri if tri else 'Não definido'}")

# ------------------------------------------------
# POSTE PARA DOIS CLIENTES
# ------------------------------------------------
tipo_projeto = "unico"  # ou "duplo"

if tipo_projeto == "unico":
    dimensionar_padrao(D)

elif tipo_projeto == "duplo":
    cliente1 = tri if tri else mono if mono else bi
    cliente2 = "A1"  # pode vir de input

    dimensionar_poste_duplo(cliente1, cliente2, "127/220V")
# ------------------------------------------------
# FINAL
# ------------------------------------------------

dimensionar_padrao(D)

conn.close()