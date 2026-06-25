import sqlite3
import os
import math

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.normpath(os.path.join(_dir, '..', 'GED2855DB.sql'))

def get_conn():
    db_file = _db_path.replace('.sql', '.db')
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn(); cursor = conn.cursor()
    with open(_db_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit(); conn.close()

def fd_iluminacao_tomadas(carga_kw, tipo):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT fator_demanda FROM tabela10 WHERE descricao LIKE ? AND ? BETWEEN carga_min_kva AND carga_max_kva LIMIT 1", (f'Iluminação e Tomadas - {tipo}%', carga_kw))
    r = cursor.fetchone(); conn.close()
    return float(r[0]) if r else 1.0

def fd_equip_especifico(qtd):
    conn = get_conn(); cursor = conn.cursor()
    if qtd >= 11:
        cursor.execute("SELECT fator_demanda FROM tabela11 WHERE descricao LIKE '11 ou mais%' LIMIT 1")
    else:
        cursor.execute("SELECT fator_demanda FROM tabela11 WHERE descricao LIKE ? LIMIT 1", (f'{qtd} aparelho%',))
        if not cursor.fetchone():
            cursor.execute("SELECT fator_demanda FROM tabela11 WHERE descricao LIKE ? LIMIT 1", (f'{qtd} aparelhos%',))
    r = cursor.fetchone(); conn.close()
    return float(r[0]) if r else 1.0

def fd_ar_condicionado(qtd):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT fator_demanda FROM tabela13 WHERE faixa LIKE ? LIMIT 1", (f'%{qtd} aparelhos%',))
    if not cursor.fetchone():
        cursor.execute("SELECT fator_demanda FROM tabela13 WHERE faixa LIKE ? LIMIT 1", (f'%{qtd} aparelho%',))
        if not cursor.fetchone():
            cursor.execute("SELECT fator_demanda FROM tabela13 WHERE faixa LIKE 'Acima%' LIMIT 1")
    r = cursor.fetchone(); conn.close()
    return float(r[0]) if r else 1.0

def get_trafo(demanda_kva):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT trafo_kva FROM tabela15 ORDER BY trafo_kva")
    sizes = [float(r[0]) for r in cursor.fetchall()]
    conn.close()
    if not sizes: return demanda_kva
    best = sizes[0]
    for s in sizes:
        if abs(s - demanda_kva) < abs(best - demanda_kva):
            best = s
    return best

def get_padrao(demanda_kva, tipo_ligacao='Trifásico'):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabela16 WHERE tipo_ligacao = ? AND ? BETWEEN demanda_min_kva AND demanda_max_kva LIMIT 1", (tipo_ligacao, demanda_kva))
    r = cursor.fetchone()
    if not r:
        cursor.execute("SELECT * FROM tabela16 WHERE tipo_ligacao = ? ORDER BY demanda_max_kva DESC LIMIT 1", (tipo_ligacao,))
        r = cursor.fetchone()
    conn.close()
    if r: return dict(r)
    return None

def calcular_fp_medio(itens):
    sum_kw = 0.0
    sum_kw_div_fp = 0.0
    for item in itens:
        kw = item['kw']
        fp = item.get('fp', 1.0)
        if fp <= 0: fp = 1.0
        sum_kw += kw
        sum_kw_div_fp += kw / fp
    if sum_kw_div_fp <= 0:
        return 0.92
    return sum_kw / sum_kw_div_fp

def get_k_factor(fp_atual, fp_desejado):
    if fp_atual >= fp_desejado:
        return 0.0
    return math.tan(math.acos(fp_atual)) - math.tan(math.acos(fp_desejado))

def calcular(dados):
    ramo = dados.get('ramo', 'Transformacao')
    tensao = dados.get('tensao', '220/380V')
    fp_desejado = float(dados.get('fp_desejado', 0.92))
    fator_demanda = float(dados.get('fator_demanda', 0.35))
    cargas = dados.get('cargas', [])

    itens_detalhados = []
    total_kw = 0.0
    carga_ilum_kw = 0.0; carga_chuveiros_kw = 0.0; carga_eletro_kw = 0.0
    carga_ar_kw = 0.0; carga_motores_kw = 0.0; carga_especiais_kw = 0.0
    chuveiros_qtd = 0; ar_qtd = 0
    motores = []; especiais = []

    fp_por_tipo = {
        0: 1.0, 1: 1.0, 2: 1.0, 3: 0.67, 4: 0.83, 5: 0.75, 6: 0.80
    }

    for c in cargas:
        nome = str(c.get('nome', '')).strip()
        potencia = float(c.get('potencia', 0))
        qtd = int(c.get('qtd', 1))
        tipo_carga = c.get('tipo', None)
        fp_item = float(c.get('fp', fp_por_tipo.get(tipo_carga, 0.85)))
        if fp_item <= 0: fp_item = 0.85

        kw = potencia * qtd / 1000
        total_kw += kw

        item = {'nome': nome, 'kw': kw, 'fp': fp_item, 'tipo': tipo_carga, 'qtd': qtd}
        itens_detalhados.append(item)

        if tipo_carga == 0 or tipo_carga == 1:
            carga_ilum_kw += kw
        elif tipo_carga == 2:
            carga_chuveiros_kw += kw; chuveiros_qtd += qtd
        elif tipo_carga == 3:
            carga_eletro_kw += kw
        elif tipo_carga == 4:
            carga_ar_kw += kw; ar_qtd += qtd
        elif tipo_carga == 5:
            carga_motores_kw += kw
            cv = float(c.get('cv', 0))
            for _ in range(qtd):
                motores.append({'nome': nome, 'cv': cv, 'kw': potencia * qtd / (1000 * qtd)})
        elif tipo_carga == 6:
            carga_especiais_kw += kw
            especiais.append({'nome': nome, 'kw': kw, 'qtd': qtd})

    fp_medio = calcular_fp_medio(itens_detalhados)
    if ramo == 'Transformacao':
        demanda_kw = total_kw * fator_demanda
        demanda_kva = demanda_kw / fp_desejado
        detalhes_demanda = None
    else:
        d_ilum = carga_ilum_kw * fd_iluminacao_tomadas(carga_ilum_kw, 'Comercial')
        d_chuv = 0
        if chuveiros_qtd > 0:
            fd_chuv = fd_equip_especifico(chuveiros_qtd)
            d_chuv = carga_chuveiros_kw * fd_chuv
        d_ar = 0
        if ar_qtd > 0:
            fd_ar = fd_ar_condicionado(ar_qtd)
            d_ar = carga_ar_kw * fd_ar
        motores.sort(key=lambda m: m['kw'], reverse=True)
        d_mot = 0
        motores_det = []
        for i, m in enumerate(motores):
            fd_m = [1.0, 0.9, 0.8, 0.8, 0.8, 0.7][min(i, 5)]
            parcela = m['kw'] * fd_m
            d_mot += parcela
            motores_det.append({'nome': m['nome'], 'cv': m['cv'], 'kw': round(m['kw'], 2), 'fd': fd_m, 'parcela_kva': round(parcela, 2)})
        d_esp = sum(e['kw'] for e in especiais) * 0.5
        d_eletro = carga_eletro_kw * 0.5
        demanda_kva = d_ilum + d_chuv + d_ar + d_mot + d_esp + d_eletro
        demanda_kw = demanda_kva * fp_medio
        detalhes_demanda = {
            'd_ilum': round(d_ilum, 2), 'd_chuv': round(d_chuv, 2), 'd_ar': round(d_ar, 2),
            'd_motores': round(d_mot, 2), 'd_especiais': round(d_esp, 2), 'd_eletro': round(d_eletro, 2),
            'motores': motores_det,
        }

    k_factor = get_k_factor(fp_medio, fp_desejado)
    kvar_correcao = demanda_kw * k_factor
    trafo_kva = get_trafo(demanda_kva)
    padrao = get_padrao(demanda_kva, 'Trifásico')
    if padrao:
        padrao = {k: v for k, v in padrao.items()}

    result = {
        'ramo': ramo,
        'tensao': tensao,
        'unidade': dados.get('unidade', ''),
        'carga_instalada_kw': round(total_kw, 2),
        'carga_ilum_kw': round(carga_ilum_kw, 2),
        'carga_chuveiros_kw': round(carga_chuveiros_kw, 2),
        'carga_eletro_kw': round(carga_eletro_kw, 2),
        'carga_ar_kw': round(carga_ar_kw, 2),
        'carga_motores_kw': round(carga_motores_kw, 2),
        'carga_especiais_kw': round(carga_especiais_kw, 2),
        'fp_medio': round(fp_medio, 4),
        'fp_desejado': fp_desejado,
        'k_factor': round(k_factor, 3),
        'kvar_correcao': round(kvar_correcao, 1),
        'demanda_kw': round(demanda_kw, 2),
        'demanda_kva': round(demanda_kva, 2),
        'trafo_kva': round(trafo_kva, 1),
        'fator_demanda': fator_demanda if ramo == 'Transformacao' else None,
        'padrao': padrao,
        'itens': itens_detalhados,
        'chuveiros_qtd': chuveiros_qtd,
        'ar_qtd': ar_qtd,
    }
    if detalhes_demanda:
        result.update(detalhes_demanda)
    return result

init_db()
