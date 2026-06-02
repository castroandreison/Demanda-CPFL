import sqlite3
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, '..', '..', 'Ged13', 'DB13', 'databaseCPFLGed13.db')
_db_path = os.path.normpath(_db_path)

def get_conn():
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn

def fd_kw(valor):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT fator_demanda FROM tabela3 WHERE ? BETWEEN carga_min_kw AND carga_max_kw LIMIT 1", (valor,))
    r = cursor.fetchone()
    conn.close()
    return float(r[0]) if r else 1

def fd_qtd_exata(qtd):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT fator_demanda FROM tabela4 WHERE numero_aparelhos = ? LIMIT 1", (qtd,))
    r = cursor.fetchone()
    conn.close()
    return float(r[0]) if r else 1

def fd_qtd_faixa(qtd):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT fator_demanda FROM tabela6 WHERE ? BETWEEN qtd_min AND qtd_max LIMIT 1", (qtd,))
    r = cursor.fetchone()
    conn.close()
    return float(r[0]) if r else 1

def get_valor(tabela, campo_busca, valor, campo_saida):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {campo_saida} FROM {tabela} WHERE {campo_busca} = ? LIMIT 1", (valor,))
    r = cursor.fetchone()
    conn.close()
    return float(r[0]) if r else 0

def get_categoria(D):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT categoria FROM tabela1a_monofasico WHERE ? BETWEEN carga_min_kw AND carga_max_kw", (D,))
    mono = cursor.fetchone()
    mono = mono[0] if mono else None
    cursor.execute("SELECT categoria FROM tabela1b_bifasico WHERE ? BETWEEN carga_min_kw AND carga_max_kw", (D,))
    bi = cursor.fetchone()
    bi = bi[0] if bi else None
    cursor.execute("SELECT categoria FROM tabela1c_trifasico_127_220 WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva", (D,))
    tri = cursor.fetchone()
    tri = tri[0] if tri else None
    conn.close()
    return mono, bi, tri

def calcular(dados):
    cargas = dados.get('cargas', [])

    tomadas = 0
    iluminacao = 0
    chuveiros = 0
    torneira = 0
    ferro = 0
    eletro = 0
    ar_qtd = 0
    motores_qtd = 0

    for c in cargas:
        nome = c.get('nome', '')
        pot = float(c.get('potencia', 0))
        qtd = int(c.get('qtd', 1))
        total = pot * qtd
        if "Tomada" in nome:
            tomadas += total
        elif "Iluminação" in nome or "Iluminacao" in nome:
            iluminacao += total
        elif "Chuveiro" in nome:
            chuveiros += total
        elif "Torneira" in nome:
            torneira += total
        elif "Ferro" in nome:
            ferro += total
        elif "Ar" in nome:
            ar_qtd += qtd
        elif "Motor" in nome:
            motores_qtd += qtd
        else:
            eletro += total

    carga_a = (tomadas + iluminacao) / 1000
    fdA = fd_kw(carga_a)
    A = carga_a * fdA

    carga_b = (chuveiros + torneira + ferro) / 1000
    qtd_b = (1 if chuveiros > 0 else 0) + (1 if torneira > 0 else 0) + (1 if ferro > 0 else 0)
    fdB = fd_qtd_exata(qtd_b if qtd_b else 1)
    B = carga_b * fdB

    carga_d = eletro / 1000
    fdD = fd_qtd_faixa(3)
    Dd = carga_d * fdD

    va_ar = get_valor("tabela8", "btu_h", 14000, "potencia_va")
    F = (va_ar * ar_qtd) / 1000

    motor_kva = get_valor("tabela_14", "potencia_nominal", "1", "potencia_kva")
    if motores_qtd >= 2:
        G = motor_kva * 1 + motor_kva * 0.9
    else:
        G = motor_kva

    D_total = A + B + Dd + F + G
    carga_instalada = carga_a + carga_b + carga_d + F + G

    mono, bi, tri = get_categoria(D_total)

    padrao = None
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT categoria,cobre_mm2,aluminio_mm2,eletroduto,disjuntor,
               aterramento_condutor,poste,caixa,motor_fn,motor_ff,motor_fff
        FROM tabela1c_trifasico_127_220
        WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva
    """, (D_total,))
    row = cursor.fetchone()
    if row:
        padrao = {
            'categoria': row[0],
            'cobre_mm2': row[1],
            'aluminio_mm2': row[2],
            'eletroduto': row[3],
            'disjuntor': row[4],
            'aterramento': row[5],
            'poste': row[6],
            'caixa': row[7],
            'motor_fn': row[8],
            'motor_ff': row[9],
            'motor_fff': row[10],
        }
    conn.close()

    return {
        'tomadas': tomadas,
        'iluminacao': iluminacao,
        'chuveiros': chuveiros,
        'torneira': torneira,
        'ferro': ferro,
        'eletro': eletro,
        'ar_qtd': ar_qtd,
        'motores_qtd': motores_qtd,
        'carga_a': round(carga_a, 2),
        'fdA': round(fdA, 4),
        'A': round(A, 2),
        'carga_b': round(carga_b, 2),
        'qtd_b': qtd_b,
        'fdB': round(fdB, 4),
        'B': round(B, 2),
        'carga_d': round(carga_d, 2),
        'fdD': round(fdD, 4),
        'D': round(Dd, 2),
        'va_ar': round(va_ar, 2),
        'F': round(F, 2),
        'motor_kva': round(motor_kva, 2),
        'G': round(G, 2),
        'D_total': round(D_total, 2),
        'carga_instalada': round(carga_instalada, 2),
        'mono': mono,
        'bi': bi,
        'tri': tri,
        'padrao': padrao,
    }
