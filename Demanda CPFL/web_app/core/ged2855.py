import sqlite3
import os

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

def fd_chuveiros(qtd):
    conn = get_conn(); cursor = conn.cursor()
    if qtd >= 11:
        cursor.execute("SELECT fator_demanda FROM tabela11 WHERE descricao LIKE '11 ou mais%' LIMIT 1")
    else:
        cursor.execute("SELECT fator_demanda FROM tabela11 WHERE descricao LIKE ? LIMIT 1", (f'{qtd} aparelho%',))
        if not cursor.fetchone():
            cursor.execute("SELECT fator_demanda FROM tabela11 WHERE descricao LIKE ? LIMIT 1", (f'{qtd} aparelhos%',))
        else:
            pass
    r = cursor.fetchone(); conn.close()
    return float(r[0]) if r else 1.0

def fd_eletrodomesticos(carga_kw):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT fator_demanda FROM tabela12 WHERE ? BETWEEN carga_min_kva AND carga_max_kva LIMIT 1", (carga_kw,))
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
    cursor.execute("SELECT trafo_kva FROM tabela15 WHERE ? >= demanda_kva ORDER BY demanda_kva DESC LIMIT 1", (demanda_kva,))
    r = cursor.fetchone()
    if not r:
        cursor.execute("SELECT trafo_kva FROM tabela15 ORDER BY trafo_kva DESC LIMIT 1")
        r = cursor.fetchone()
    conn.close()
    return float(r[0]) if r else demanda_kva

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

def get_fp_correction(fp_atual, fp_desejado=0.92):
    conn = get_conn(); cursor = conn.cursor()
    fp_atual = round(fp_atual, 2)
    cursor.execute("SELECT kvar_por_kw FROM tabela17 WHERE fp_atual = ? AND fp_desejado = ? LIMIT 1", (fp_atual, fp_desejado))
    r = cursor.fetchone()
    if not r:
        cursor.execute("SELECT kvar_por_kw FROM tabela17 WHERE fp_atual <= ? AND fp_desejado = ? ORDER BY fp_atual DESC LIMIT 1", (fp_atual, fp_desejado))
        r = cursor.fetchone()
    conn.close()
    return float(r[0]) if r else 0.0

def calcular(dados):
    tipo = dados.get('tipo', 'Comercial')
    tensao = dados.get('tensao', '220/380V')
    fp_atual = float(dados.get('fp_atual', 0.85))
    fp_desejado = float(dados.get('fp_desejado', 0.92))
    cargas = dados.get('cargas', [])

    itens_iluminacao = []
    total_ilum_va = 0
    chuveiros_w = 0
    chuveiros_qtd = 0
    eletro_w = 0
    ar_va_total = 0
    ar_qtd = 0
    motores = []
    equipamentos_especiais_va = []

    for c in cargas:
        nome = str(c.get('nome', '')).strip()
        potencia = float(c.get('potencia', 0))
        qtd = int(c.get('qtd', 1))
        tipo_carga = c.get('tipo', None)
        fp = float(c.get('fp', 1.0))

        if tipo_carga == 0:
            va = potencia / fp
            itens_iluminacao.append({'nome': nome, 'w': potencia, 'va': va, 'qtd': qtd})
            total_ilum_va += va * qtd
        elif tipo_carga == 1:
            va = potencia / fp
            itens_iluminacao.append({'nome': nome, 'w': potencia, 'va': va, 'qtd': qtd})
            total_ilum_va += va * qtd
        elif tipo_carga == 2:
            chuveiros_w += potencia * qtd
            chuveiros_qtd += qtd
        elif tipo_carga == 3:
            eletro_w += potencia * qtd
        elif tipo_carga == 4:
            ar_va_total += (potencia / fp) * qtd
            ar_qtd += qtd
        elif tipo_carga == 5:
            cv = float(c.get('cv', 0))
            va = potencia / fp if potencia > 0 else cv * 736 / fp
            for _ in range(qtd):
                motores.append({'nome': nome, 'cv': cv, 'va': va})
        elif tipo_carga == 6:
            equipamentos_especiais_va.append({'nome': nome, 'va': potencia / fp, 'qtd': qtd})

    carga_ilum_kw = total_ilum_va / 1000
    fd_ilum = fd_iluminacao_tomadas(carga_ilum_kw, tipo)
    d_ilum = carga_ilum_kw * fd_ilum

    carga_chuveiros_kw = chuveiros_w / 1000
    fd_chuv = fd_chuveiros(chuveiros_qtd) if chuveiros_qtd > 0 else 0
    d_chuv = carga_chuveiros_kw * fd_chuv if chuveiros_qtd > 0 else 0

    carga_eletro_kw = eletro_w / 1000
    fd_eletro = fd_eletrodomesticos(carga_eletro_kw) if eletro_w > 0 else 0
    d_eletro = carga_eletro_kw * fd_eletro if eletro_w > 0 else 0

    carga_ar_kw = ar_va_total / 1000
    fd_ar = fd_ar_condicionado(ar_qtd) if ar_qtd > 0 else 0
    d_ar = carga_ar_kw * fd_ar if ar_qtd > 0 else 0

    motores.sort(key=lambda m: m['va'], reverse=True)
    d_motores = 0
    motores_detalhes = []
    for i, m in enumerate(motores):
        if i == 0: fd_m = 1.0
        elif i == 1: fd_m = 0.9
        elif i <= 4: fd_m = 0.8
        else: fd_m = 0.7
        parcela = m['va'] * fd_m
        d_motores += parcela
        motores_detalhes.append({'nome': m['nome'], 'cv': m['cv'], 'va': round(m['va'], 0), 'fd': fd_m, 'parcela_kva': round(parcela / 1000, 2)})

    d_especiais = sum(e['va'] * e['qtd'] for e in equipamentos_especiais_va) / 1000

    D_total = d_ilum + d_chuv + d_eletro + d_ar + (d_motores / 1000) + d_especiais

    trafo_kva = get_trafo(D_total)

    kw_total = D_total * fp_atual
    kvar_por_kw = get_fp_correction(fp_atual, fp_desejado)
    kvar_correcao = kw_total * kvar_por_kw

    padrao = get_padrao(D_total, 'Trifásico')
    if padrao:
        padrao = {k: v for k, v in padrao.items()}

    carga_instalada_kw = carga_ilum_kw + carga_chuveiros_kw + carga_eletro_kw + carga_ar_kw + (d_motores / 1000) + d_especiais

    return {
        'd_ilum': round(d_ilum, 2),
        'carga_ilum_kw': round(carga_ilum_kw, 2),
        'fd_ilum': round(fd_ilum, 4),
        'd_chuv': round(d_chuv, 2),
        'carga_chuveiros_kw': round(carga_chuveiros_kw, 2),
        'fd_chuv': round(fd_chuv, 4),
        'qtd_chuveiros': chuveiros_qtd,
        'd_eletro': round(d_eletro, 2),
        'carga_eletro_kw': round(carga_eletro_kw, 2),
        'fd_eletro': round(fd_eletro, 4),
        'd_ar': round(d_ar, 2),
        'carga_ar_kw': round(carga_ar_kw, 2),
        'fd_ar': round(fd_ar, 4),
        'ar_qtd': ar_qtd,
        'd_motores': round(d_motores / 1000, 2),
        'motores': motores_detalhes,
        'd_especiais': round(d_especiais, 2),
        'D_total': round(D_total, 2),
        'trafo_kva': round(trafo_kva, 1),
        'fp_atual': fp_atual,
        'fp_desejado': fp_desejado,
        'kvar_por_kw': round(kvar_por_kw, 3),
        'kvar_correcao': round(kvar_correcao, 1),
        'carga_instalada_kw': round(carga_instalada_kw, 2),
        'padrao': padrao,
        'tipo': tipo,
        'tensao': tensao,
        'unidade': dados.get('unidade', ''),
        'itens_iluminacao': itens_iluminacao,
    }

init_db()
