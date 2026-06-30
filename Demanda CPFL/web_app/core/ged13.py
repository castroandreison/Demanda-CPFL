import sqlite3
import os
import re

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

def fd_ar_condicionado(qtd):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabela_9")
    for row in cursor.fetchall():
        faixa = row[1]
        fd = row[2]
        if "Acima" in faixa:
            parts = faixa.split()
            if len(parts) >= 3 and qtd >= int(parts[2]):
                conn.close()
                return float(fd)
        elif "a" in faixa:
            parts = faixa.split(" a ")
            if len(parts) == 2 and int(parts[0]) <= qtd <= int(parts[1]):
                conn.close()
                return float(fd)
    conn.close()
    return 1.0

def fd_tabela15(tipo, carga_kw):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT fator_demanda FROM tabela_15 WHERE descricao = ?", (tipo,))
    row = cursor.fetchone()
    conn.close()
    if not row: return 1.0
    fd_text = str(row[0]).strip()
    if fd_text == '1': return 1.0
    import re
    parts = fd_text.split(';')
    if len(parts) == 2:
        m1 = re.match(r'([\d,]+)\s+para os primeiros\s+([\d.]+)\s*kW', parts[0].strip())
        m2 = re.match(r'([\d,]+)\s+para o que exceder a\s+([\d.]+)\s*kW', parts[1].strip())
        if m1 and m2:
            fd1 = float(m1.group(1).replace(',', '.'))
            limit = float(m2.group(2))
            fd2 = float(m2.group(1).replace(',', '.'))
            if carga_kw <= 0: return 1.0
            if carga_kw <= limit: return fd1
            return (limit * fd1 + (carga_kw - limit) * fd2) / carga_kw
    return 1.0

def get_valor(tabela, campo_busca, valor, campo_saida):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(f"SELECT {campo_saida} FROM {tabela} WHERE {campo_busca} = ? LIMIT 1", (valor,))
    r = cursor.fetchone()
    conn.close()
    return float(r[0]) if r else 0

def get_motor_va(cv_val):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT potencia_nominal, potencia_kva FROM tabela_14")
    target = float(cv_val)
    for row in cursor.fetchall():
        db_cv = str(row[0]).strip()
        db_kva = float(row[1])
        try:
            if '/' in db_cv and ' ' not in db_cv:
                a, b = db_cv.split('/')
                if float(a) / float(b) == target:
                    conn.close()
                    return db_kva * 1000
            if ' ' in db_cv:
                parts = db_cv.split()
                total = 0.0
                for p in parts:
                    if '/' in p:
                        a, b = p.split('/')
                        total += float(a) / float(b)
                    else:
                        total += float(p)
                if abs(total - target) < 0.01:
                    conn.close()
                    return db_kva * 1000
            if abs(float(db_cv) - target) < 0.01:
                conn.close()
                return db_kva * 1000
        except:
            pass
    conn.close()
    return 0

TABELA1_MAP = {
    'Residencial': 15.0,
    'Comercial': 30.0,
    'Industrial': 0.0,
}

def get_sugestao(area, tipo):
    area = float(area)
    tipo = str(tipo)

    conn = get_conn()
    cursor = conn.cursor()

    # Tabela 1: minimum illumination W/m²
    va_m2 = TABELA1_MAP.get(tipo)
    if va_m2 is None:
        cursor.execute("SELECT carga_minima_w_m2 FROM tabela_15 WHERE descricao = ?", (tipo,))
        row = cursor.fetchone()
        va_m2 = float(row[0]) if row else 15.0
    if va_m2 > 0:
        sug_ilum = max(100, int(-(-(area * va_m2) // 100)) * 100)
    else:
        sug_ilum = 0

    # Tabela 2: minimum outlet VA by area range
    cursor.execute("SELECT MAX(area_max) FROM tabela2")
    max_row = cursor.fetchone()
    max_area = float(max_row[0]) if max_row and max_row[0] else 250
    if area > max_area:
        area = max_area
    cursor.execute("SELECT subtotal_II, total_W FROM tabela2 WHERE ? BETWEEN area_min AND area_max LIMIT 1", (area,))
    row = cursor.fetchone()
    if row:
        sug_tom = row[0]
        total = row[1]
    else:
        sug_tom = 1800
        total = 0

    conn.close()
    return {
        'ilum_sugestao': sug_ilum,
        'tom_sugestao': sug_tom,
    }

def get_categoria(D, tensao):
    conn = get_conn()
    cursor = conn.cursor()
    tabela = "tabela1c_trifasico_220_380" if tensao == "220/380V" else "tabela1c_trifasico_127_220"
    cursor.execute(f"SELECT * FROM {tabela} WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva", (D,))
    row = cursor.fetchone()
    conn.close()
    if row:
        cols = [d[0] for d in cursor.description]
        return dict(zip(cols, row))
    return None

def calcular(dados):
    cargas = dados.get('cargas', [])
    tensao = dados.get('tensao', '127/220V')
    tipo = dados.get('tipo', 'Residencial')
    fp_padrao = 1.0

    # Parse all loads
    itens_iluminacao = []   # list of (nome, w, fp)
    chuveiros_w = 0
    chuveiros_qtd = 0
    ar_cond_va_total = 0
    ar_qtd = 0
    motores = []  # list of (nome, cv, va)
    solda_va = []  # list of va_per_unit
    eletro_w = 0
    eletro_qtd = 0

    for c in cargas:
        nome = str(c.get('nome', '')).strip().lower()
        pot_w = float(c.get('potencia', 0))
        qtd = int(c.get('qtd', 1))
        tipo_carga = c.get('tipo', None)

        # Use explicit tipo if provided (from UI tabs)
        if tipo_carga is not None:
            if tipo_carga == 0 or tipo_carga == 1:
                fp = float(c.get('fp', 1.0))
                itens_iluminacao.append((nome, pot_w * qtd, fp))
            elif tipo_carga == 2:
                chuveiros_w += pot_w * qtd
                chuveiros_qtd += qtd
            elif tipo_carga == 3:
                eletro_w += pot_w * qtd
                eletro_qtd += qtd
            elif tipo_carga == 4:
                btu = c.get('btu', 0)
                va = 0
                if btu:
                    va = get_valor("tabela8", "btu_h", btu, "potencia_va")
                if va == 0:
                    va = pot_w / fp_padrao
                ar_cond_va_total += va * qtd
                ar_qtd += qtd
            elif tipo_carga == 5:
                cv = float(c.get('cv', 0))
                if cv == 0:
                    cv = pot_w / 1000
                va = get_motor_va(str(cv))
                if va == 0:
                    va = pot_w / 0.8
                for _ in range(qtd):
                    motores.append((nome, cv, va))
            elif tipo_carga == 6:
                fp = float(c.get('fp', 0.75))
                va = pot_w / fp
                for _ in range(qtd):
                    solda_va.append(va)
            continue

        # Fallback: name-based detection
        if 'solda' in nome:
            fp = float(c.get('fp', 0.75))
            va = pot_w / fp
            for _ in range(qtd):
                solda_va.append(va)
        elif 'chuveiro' in nome or 'torneira' in nome:
            chuveiros_w += pot_w * qtd
            chuveiros_qtd += qtd
        elif 'ar-condicionado' in nome or 'ar condicionado' in nome:
            btu = c.get('btu', 0)
            va = 0
            if btu:
                va = get_valor("tabela8", "btu_h", btu, "potencia_va")
            if va == 0:
                va = pot_w / fp_padrao
            ar_cond_va_total += va * qtd
            ar_qtd += qtd
        elif 'motor' in nome or 'compressor' in nome or 'serra' in nome or 'prensa' in nome or 'furadeira' in nome:
            cv = float(c.get('cv', 0))
            if cv == 0:
                # Try to extract CV from name or estimate from watts
                cv_match = re.search(r'(\d+[\.\d]?)\s*cv', nome)
                if cv_match:
                    cv = float(cv_match.group(1))
                else:
                    cv = pot_w / 1000  # rough estimate
            va = get_motor_va(str(cv))
            if va == 0:
                va = pot_w / 0.8  # estimate with PF ~0.8
            for _ in range(qtd):
                motores.append((nome, cv, va))
        elif 'reator' in nome:
            itens_iluminacao.append((nome, pot_w * qtd, fp_padrao))
        elif 'lampada' in nome or 'luminaria' in nome or 'fluorescente' in nome:
            fp = float(c.get('fp', 0.95 if 'fluorescente' in nome else 1.0))
            itens_iluminacao.append((nome, pot_w * qtd, fp))
        elif 'iluminacao' in nome or 'tomada' in nome or 'ilumina' in nome:
            itens_iluminacao.append((nome, pot_w * qtd, fp_padrao))
        else:
            eletro_w += pot_w * qtd

    # (a) Iluminacao e Tomadas
    ilum_va = sum(w / fp for _, w, fp in itens_iluminacao)
    carga_a_kw = ilum_va / 1000
    tabela15_tipos = ['Escolas e semelhantes','Escritórios (edifícios)','Hospitais e semelhantes','Hotéis e semelhantes']
    if tipo in tabela15_tipos:
        fd_a = fd_tabela15(tipo, carga_a_kw)
    elif tipo == "Industrial":
        fd_a = 1.0  # Tabela 15 - Industrias: FD=1
    else:
        fd_a = fd_kw(carga_a_kw)
    a = carga_a_kw * fd_a

    # (b) Chuveiros
    carga_b_kw = chuveiros_w / 1000
    fd_b = fd_qtd_exata(max(chuveiros_qtd, 1)) if chuveiros_qtd > 0 else 0
    b = carga_b_kw * fd_b if carga_b_kw > 0 else 0

    # (f) Ar Condicionado
    fd_f = fd_ar_condicionado(max(ar_qtd, 1))
    f = (ar_cond_va_total * fd_f) / 1000 if ar_qtd > 0 else 0

    # (g) Motores Eletricos
    # Sort by VA descending, then apply graduated FDs
    motores.sort(key=lambda m: m[2], reverse=True)
    g = 0.0
    motor_detalhes = []
    for i, (nome, cv, va) in enumerate(motores):
        if i == 0:
            fd_motor = 1.0  # 1st (maior)
        elif i == 1:
            fd_motor = 0.9  # 2nd
        elif i <= 4:
            fd_motor = 0.8  # 3rd-5th
        else:
            fd_motor = 0.7  # restante
        parcela = va * fd_motor
        g += parcela
        motor_detalhes.append({
            'nome': nome, 'cv': cv, 'va': round(va, 0),
            'fd': fd_motor, 'parcela_kva': round(parcela / 1000, 2)
        })
    g_kva = g / 1000

    # (h) Equipamentos Especiais (Maquinas de Solda)
    h = 0.0
    solda_detalhes = []
    for i, va in enumerate(solda_va):
        if i == 0:
            fd_solda = 1.0
        elif i == 1:
            fd_solda = 0.6
        elif i == 2:
            fd_solda = 0.4
        else:
            fd_solda = 0.3
        parcela = va * fd_solda
        h += parcela
        solda_detalhes.append({
            'va': round(va, 0),
            'fd': fd_solda,
            'parcela_kva': round(parcela / 1000, 2)
        })
    h_kva = h / 1000

    # (d) Outros eletrodomesticos (if any)
    carga_d_kw = eletro_w / 1000
    fd_d = fd_qtd_faixa(max(eletro_qtd, 1)) if eletro_qtd > 0 else 0
    d_kva = carga_d_kw * fd_d if carga_d_kw > 0 else 0

    # Total Demand
    D_total = a + b + f + g_kva + h_kva + d_kva

    # Carga Instalada
    total_w_ilum = sum(w for _, w, _ in itens_iluminacao)
    # For installed load, use nominal W for each category
    carga_ilum_kw = total_w_ilum / 1000
    carga_chuveiros_kw = chuveiros_w / 1000
    carga_eletro_kw = eletro_w / 1000
    carga_ar_w = ar_cond_va_total
    carga_ar_kw = carga_ar_w / 1000
    carga_motores_w = sum(m[2] for m in motores)
    carga_motores_kw = carga_motores_w / 1000
    carga_solda_w = sum(solda_va)
    carga_solda_kw = carga_solda_w / 1000
    carga_instalada_kw = carga_ilum_kw + carga_chuveiros_kw + carga_eletro_kw + carga_ar_kw + carga_motores_kw + carga_solda_kw
    carga_instalada_kw_arred = int(-(-carga_instalada_kw // 1))  # round up to nearest kW
    excede_25kw = carga_instalada_kw > 25

    # Enquadramento
    padrao = get_categoria(D_total, tensao)

    return {
        'a_ilum_va': round(ilum_va, 0),
        'carga_a_kw': round(carga_a_kw, 2),
        'fd_a': round(fd_a, 4),
        'a_kva': round(a, 2),
        'b_w': round(chuveiros_w, 0),
        'carga_b_kw': round(carga_b_kw, 2),
        'fd_b': round(fd_b, 4),
        'b_kva': round(b, 2),
        'qtd_chuveiros': chuveiros_qtd,
        'ar_va': round(ar_cond_va_total, 0),
        'ar_qtd': ar_qtd,
        'fd_f': round(fd_f, 4),
        'f_kva': round(f, 2),
        'motores': motor_detalhes,
        'g_kva': round(g_kva, 2),
        'solda': solda_detalhes,
        'h_kva': round(h_kva, 2),
        'd_kva': round(d_kva, 2),
        'qtd_eletro': eletro_qtd,
        'fd_d': round(fd_d, 4),
        'D_total': round(D_total, 2),
        'carga_instalada': round(carga_instalada_kw, 2),
        'carga_instalada_kw_arred': carga_instalada_kw_arred,
        'excede_25kw': excede_25kw,
        'carga_ilum_kw': round(carga_ilum_kw, 2),
        'carga_chuveiros_kw': round(carga_chuveiros_kw, 2),
        'carga_eletro_kw': round(carga_eletro_kw, 2),
        'carga_ar_kw': round(carga_ar_kw, 2),
        'carga_motores_kw': round(carga_motores_kw, 2),
        'carga_solda_kw': round(carga_solda_kw, 2),
        'itens_iluminacao': [{'nome': t[0], 'w': t[1], 'fp': t[2]} for t in itens_iluminacao],
        'tensao': tensao,
        'tipo': tipo,
        'unidade': dados.get('unidade', ''),
        'm2': dados.get('m2', 0),
        'padrao': padrao,
    }
