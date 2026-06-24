import sqlite3
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, '..', 'db', 'databaseCPFLGed119.db')
_db_path = os.path.normpath(_db_path)

def get_conn():
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn

def normalizar_cv(cv):
    if isinstance(cv, float) and cv == int(cv):
        cv = int(cv)
    mapa = {
        "0.33": "1/3", "0.5": "1/2", "0.75": "3/4",
        "1": "1", "1.5": "1 1/2", "2": "2", "3": "3",
        "5": "5", "7.5": "7 1/2", "10": "10"
    }
    return mapa.get(str(cv), str(cv))

def cv_str_para_float(cv_str):
    cv_str = cv_str.strip()
    if ' ' in cv_str and '/' in cv_str:
        parts = cv_str.split(' ')
        whole = float(parts[0])
        frac = parts[1].split('/')
        return whole + float(frac[0]) / float(frac[1])
    elif '/' in cv_str:
        parts = cv_str.split('/')
        return float(parts[0]) / float(parts[1])
    else:
        return float(cv_str)

def cv_para_kva(cv):
    cv = float(cv)
    conn = get_conn()
    cursor = conn.cursor()
    chave = normalizar_cv(cv)
    cursor.execute("SELECT potencia_kva, potencia_kw FROM TABELA_4 WHERE potencia_cv_hp = ?", (chave,))
    r = cursor.fetchone()
    if r:
        conn.close()
        return r[0], r[1]
    cursor.execute("SELECT potencia_cv_hp, potencia_kva, potencia_kw FROM TABELA_4")
    rows = cursor.fetchall()
    conn.close()
    entries = [(cv_str_para_float(row[0]), row[1], row[2]) for row in rows]
    entries.sort(key=lambda x: x[0])
    lower = upper = None
    for e in entries:
        if e[0] <= cv:
            lower = e
        if e[0] >= cv and upper is None:
            upper = e
    if lower and upper and lower[0] != upper[0]:
        ratio = (cv - lower[0]) / (upper[0] - lower[0])
        kva = lower[1] + ratio * (upper[1] - lower[1])
        kw = lower[2] + ratio * (upper[2] - lower[2])
        return round(kva, 4), round(kw, 4)
    if upper:
        return upper[1], upper[2]
    if lower:
        return lower[1], lower[2]
    return 0, 0

def get_tabela4():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT potencia_cv_hp, potencia_kw, potencia_kva FROM TABELA_4 ORDER BY id")
    rows = cursor.fetchall()
    conn.close()
    result = []
    for r in rows:
        cv_num = cv_str_para_float(r[0])
        result.append({'cv_label': r[0], 'cv': cv_num, 'kw': r[1], 'kva': r[2]})
    return result

def fator_aparelho(coluna, qtd):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM TABELA_2")
    linhas = cursor.fetchall()
    colunas = [d[0] for d in cursor.description]
    idx = colunas.index(coluna)
    conn.close()
    for linha in linhas:
        faixa = linha[1]
        if " a " in faixa:
            min_v, max_v = map(int, faixa.split(" a "))
        else:
            min_v = max_v = int(faixa)
        if min_v <= qtd <= max_v:
            return linha[idx] / 100
    return 1

def fator_simultaneidade(qtd):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT numero_apartamentos, fator_simultaneidade FROM TABELA_7")
    for faixa, fator in cursor.fetchall():
        if "acima" in faixa:
            min_v = int(faixa.split()[0])
            max_v = 999999
        else:
            min_v, max_v = map(int, faixa.split(" a "))
        if min_v <= qtd <= max_v:
            conn.close()
            return fator
    conn.close()
    return 1

def buscar_faixa_tabela(cursor, tabela, col_min, col_max, valor):
    cursor.execute(f"SELECT * FROM {tabela}")
    linhas = cursor.fetchall()
    colunas = [d[0] for d in cursor.description]
    for linha in linhas:
        min_v = linha[colunas.index(col_min)]
        max_v = linha[colunas.index(col_max)]
        if min_v is None and max_v is not None and valor <= max_v:
            return dict(zip(colunas, linha))
        if max_v is None and min_v is not None and valor >= min_v:
            return dict(zip(colunas, linha))
        if min_v is not None and max_v is not None and min_v <= valor <= max_v:
            return dict(zip(colunas, linha))
    return None

def calcular_transformador(dados):
    dg = float(dados.get('dg') or 0)
    tipo = dados.get('tipo', 'Residencial')
    tensao_opcao = dados.get('tensao', '380/220V (trifásico)')
    metodo_inst = dados.get('metodo_inst', 'C')
    forma_agrup = dados.get('forma_agrup', 'Em feixe: ao ar livre ou sobre superfície; embutidos; em duto fechado')
    num_circuitos = int(dados.get('num_circuitos') or 1)
    if num_circuitos < 1:
        num_circuitos = 1

    if tensao_opcao == "380/220V (trifásico)":
        V = 380
        fator_380 = 1.73
    else:
        V = 220
        fator_380 = 1.0

    I = dg * 1000 / (V * 3**0.5)

    conn = get_conn()
    cursor = conn.cursor()

    limite = 400 if tipo == "Residencial" else 300
    acima_limite = dg > limite

    trafo = buscar_faixa_tabela(cursor, "TABELA_10", "demanda_min", "demanda_max", dg)
    trafo_kva = trafo['transformador_kva'] if trafo else None
    trafo_acima_tabela = dg > 308
    if trafo_acima_tabela:
        trafo_kva = None

    cap = None
    if trafo_kva:
        cap = buscar_faixa_tabela(cursor, "capacidade_interrupcao_transformador", "transformador_kva", "transformador_kva", trafo_kva)

    cursor.execute("SELECT * FROM tabela11_cabos_bt ORDER BY secao_mm2")
    cabos = cursor.fetchall()
    col_cabos = [d[0] for d in cursor.description]
    col_corrente = metodo_inst if metodo_inst in ("A","B","C","D","E","F") else "C"
    idx_corrente = col_cabos.index(col_corrente)
    idx_secao = col_cabos.index("secao_mm2")

    cursor.execute("SELECT * FROM tabela11_fatores_correcao")
    fatores = cursor.fetchall()
    col_fat = [d[0] for d in cursor.description]

    fator_correcao = 1.0
    for linha in fatores:
        if linha[1] == forma_agrup:
            idx_map = {1:2,2:3,3:4,4:5,5:6,6:7,7:8,8:9}
            if num_circuitos in idx_map:
                fator_correcao = linha[idx_map[num_circuitos]]
            elif num_circuitos <= 11:
                fator_correcao = linha[10]
            elif num_circuitos <= 15:
                fator_correcao = linha[11]
            elif num_circuitos <= 19:
                fator_correcao = linha[12]
            else:
                fator_correcao = linha[13]
            break

    if fator_correcao is None or fator_correcao == 0:
        fator_correcao = 1.0

    I_corrigida = I / fator_correcao

    cabo_sel = None
    for cabo in cabos:
        capacidade = cabo[idx_corrente]
        if fator_380 > 1:
            capacidade = capacidade * fator_380
        if capacidade >= I_corrigida:
            cabo_sel = dict(zip(col_cabos, cabo))
            break

    secao = cabo_sel['secao_mm2'] if cabo_sel else None
    diametro = cabo_sel['diametro_externo_mm'] if cabo_sel and 'diametro_externo_mm' in col_cabos else None
    cap_tabela = cabo_sel[col_corrente] if cabo_sel else None

    barra = buscar_faixa_tabela(cursor, "tabela12_barramento_bt", "demanda_min_kva", "demanda_max_kva", dg)

    cursor.execute("SELECT corrente_nominal_A FROM disjuntores_termomagneticos ORDER BY corrente_nominal_A")
    disjuntores = [r[0] for r in cursor.fetchall()]
    disjuntor_sel = None
    for d in disjuntores:
        if d >= I:
            disjuntor_sel = d
            break

    conn.close()

    return {
        'dg': round(dg, 2),
        'tipo': tipo,
        'limite': limite,
        'acima_limite': acima_limite,
        'tensao': tensao_opcao,
        'V': V,
        'I': round(I, 2),
        'trafo_kva': trafo_kva,
        'trafo_acima_tabela': trafo_acima_tabela,
        'trafo_faixa_min': round(trafo['demanda_min'], 1) if trafo else None,
        'trafo_faixa_max': round(trafo['demanda_max'], 1) if trafo else None,
        'cap_interrupcao_kA': round(cap['capacidade_interrupcao_ka'], 2) if cap else None,
        'cap_z_percent': round(cap['z_percent'], 2) if cap else None,
        'metodo_inst': metodo_inst,
        'forma_agrup': forma_agrup,
        'num_circuitos': num_circuitos,
        'fator_correcao': round(fator_correcao, 2),
        'I_corrigida': round(I_corrigida, 2),
        'secao_mm2': secao,
        'diametro_externo_mm': round(diametro, 1) if diametro else None,
        'capacidade_cabo_A': round(cap_tabela, 1) if cap_tabela else None,
        'fator_380': fator_380,
        'barramento_mm': barra['barra_mm'] if barra else None,
        'barramento_pol': barra['barra_polegada'] if barra else None,
        'disjuntor_A': disjuntor_sel,
    }

def get_tabela_ac():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabela_ac ORDER BY id")
    rows = cursor.fetchall()
    cols = [d[0] for d in cursor.description]
    conn.close()
    return [dict(zip(cols, r)) for r in rows]

def get_formas_agrupamento():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT forma_agrupamento FROM tabela11_fatores_correcao")
    formas = [r[0] for r in cursor.fetchall()]
    conn.close()
    return formas

def calcular_poste(dados):
    dg = float(dados.get('dg') or 0)
    tensao = dados.get('tensao', '220/380')
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabela20_dimensionamento_poste WHERE tensao_fornecimento = ? ORDER BY demanda_min_kva", (tensao,))
    linhas = cursor.fetchall()
    colunas = [d[0] for d in cursor.description]
    conn.close()
    for linha in linhas:
        row = dict(zip(colunas, linha))
        if row['demanda_min_kva'] <= dg <= row['demanda_max_kva']:
            return {
                'dg': round(dg, 2),
                'tensao': tensao,
                'tipo_poste': row['tipo_poste'],
                'capacidade_dan': row['capacidade_dan'],
                'faixa_min': row['demanda_min_kva'],
                'faixa_max': row['demanda_max_kva'],
            }
    return {
        'dg': round(dg, 2),
        'tensao': tensao,
        'tipo_poste': None,
        'capacidade_dan': None,
        'faixa_min': None,
        'faixa_max': None,
        'erro': 'Demanda acima do limite da tabela (400 kVA)'
    }

def calcular_ramal_ligacao(dados):
    dg = float(dados.get('dg') or 0)
    tensao_kv = int(dados.get('tensao_kv') or 15)
    V = tensao_kv * 1000
    I = dg * 1000 / (V * 3**0.5)
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabela15_ramal_subterraneo_mt WHERE tensao_kv = ? ORDER BY corrente_A", (tensao_kv,))
    linhas = cursor.fetchall()
    colunas = [d[0] for d in cursor.description]
    conn.close()
    resultado = {
        'dg': round(dg, 2),
        'tensao_kv': tensao_kv,
        'I': round(I, 2),
        'cabo_sel': None,
    }
    for linha in linhas:
        row = dict(zip(colunas, linha))
        if row['corrente_A'] >= I:
            resultado['cabo_sel'] = {
                'tipo_cabo': row['tipo_cabo'],
                'corrente_A': row['corrente_A'],
                'potencia_MVA': row['potencia_MVA'],
            }
            break
    if not resultado['cabo_sel'] and linhas:
        row = dict(zip(colunas, linhas[-1]))
        resultado['cabo_sel'] = {
            'tipo_cabo': row['tipo_cabo'],
            'corrente_A': row['corrente_A'],
            'potencia_MVA': row['potencia_MVA'],
            'acima_limite': True,
        }
    return resultado

def calcular(dados):
    aptos = int(dados.get('aptos') or 0)
    area_apto = float(dados.get('area_apto') or 0)
    area_adm = float(dados.get('area_adm') or 0)
    iluminacao = float(dados.get('iluminacao') or 0)
    tomadas = float(dados.get('tomadas') or 0)
    chuveiro_kw = float(dados.get('chuveiro_kw') or 0)
    torneira_kw = float(dados.get('torneira_kw') or 0)
    qtd_chuveiros = int(dados.get('chuveiros_apto') or dados.get('qtd_chuveiros') or 1)
    qtd_torneiras = int(dados.get('torneiras_apto') or dados.get('qtd_torneiras') or 0)
    qtd_chuveiros_adm = int(dados.get('chuveiros_adm') or dados.get('qtd_chuveiros_adm') or 0)
    qtd_torneiras_adm = int(dados.get('torneiras_adm') or dados.get('qtd_torneiras_adm') or 0)
    secar_kw = float(dados.get('secar_kw') or 0)
    secar_apto = int(dados.get('secar_apto') or 0)
    lavar_kw = float(dados.get('lavar_kw') or 0)
    lavar_apto = int(dados.get('lavar_apto') or 0)
    motores = dados.get('motores', [])
    outras_cargas_apt = dados.get('outras_cargas_apt', [])
    outras_cargas_adm = dados.get('outras_cargas_adm', [])
    ac_apt = dados.get('ac_apt', [])
    ac_adm = dados.get('ac_adm', [])
    tipo = dados.get('tipo', 'Residencial')

    w_m2 = 5
    D1a = (area_apto * aptos * w_m2) / 1000
    D1b = (area_adm * w_m2) / 1000
    D1 = D1a + D1b

    total_chuveiros_apt = aptos * qtd_chuveiros
    total_torneiras_apt = aptos * qtd_torneiras
    total_aparelhos = total_chuveiros_apt + qtd_chuveiros_adm + qtd_torneiras_adm
    f_ch = fator_aparelho("chuveiro_torneira_ferro", total_aparelhos)

    apt_chuveiros = total_chuveiros_apt * chuveiro_kw * f_ch
    adm_chuveiros = qtd_chuveiros_adm * chuveiro_kw * f_ch
    adm_torneiras = qtd_torneiras_adm * torneira_kw * f_ch

    total_secar = aptos * secar_apto
    total_lavar = aptos * lavar_apto
    f_secar = fator_aparelho("maquina_secar_roupa", total_secar)
    f_lavar = fator_aparelho("maquinas_lavar_louca", total_lavar)

    D2b = total_secar * secar_kw * f_secar
    D2c = total_lavar * lavar_kw * f_lavar

    D2_apt = apt_chuveiros + D2b + D2c
    D2_adm = adm_chuveiros + adm_torneiras
    D2 = D2_apt + D2_adm

    total_outras_apt = sum(pot * qtd for desc, pot, qtd in outras_cargas_apt) if outras_cargas_apt else 0
    total_outras_adm = sum(pot * qtd for desc, pot, qtd in outras_cargas_adm) if outras_cargas_adm else 0

    total_ac_apt_kw = sum((ac.get('potencia', ac.get('pot', 0)) / 1000) * ac.get('quantidade', ac.get('qtd', 1)) for ac in ac_apt if ac.get('incluir', 1)) if ac_apt else 0
    total_ac_adm_kw = sum((ac.get('potencia', ac.get('pot', 0)) / 1000) * ac.get('quantidade', ac.get('qtd', 1)) for ac in ac_adm if ac.get('incluir', 1)) if ac_adm else 0
    total_outras_apt += total_ac_apt_kw
    total_outras_adm += total_ac_adm_kw

    total = 0
    maior = 0
    motores_detalhes = []
    for m in motores:
        cv = float(m.get('cv') or 0)
        qtd = int(m.get('qtd') or 1)
        kva, kw = cv_para_kva(cv)
        total_kva = kva * qtd
        total += total_kva
        maior = max(maior, kva)
        motores_detalhes.append({'cv': cv, 'qtd': qtd, 'kva': kva, 'kw': kw, 'total_kva': total_kva, 'total_kw': kw * qtd})

    restantes = total - maior
    D3 = (maior * 1.0) + (restantes * 0.5)

    f_sim = fator_simultaneidade(aptos)
    Dapt = (D1a + D2_apt) * f_sim
    Dadm = D1b + D2_adm + D3 + total_outras_adm
    Dg = Dapt + Dadm + total_outras_apt

    limite = 400 if tipo == "Residencial" else 300
    acima_limite = Dg > limite

    return {
        'D1': round(D1, 2),
        'D1a': round(D1a, 2),
        'D1b': round(D1b, 2),
        'D2': round(D2, 2),
        'D2_apt': round(D2_apt, 2),
        'D2_adm': round(D2_adm, 2),
        'D2b': round(D2b, 2),
        'D2c': round(D2c, 2),
        'D3': round(D3, 2),
        'Dg': round(Dg, 2),
        'Dapt': round(Dapt, 2),
        'Dadm': round(Dadm, 2),
        'f_sim': round(f_sim, 2),
        'w_m2': w_m2,
        'f_ch': round(f_ch, 2),
        'f_secar': round(f_secar, 2),
        'f_lavar': round(f_lavar, 2),
        'total_chuveiros_apt': total_chuveiros_apt,
        'total_chuveiros_geral': total_chuveiros_apt + qtd_chuveiros_adm,
        'total_torneiras_geral': total_torneiras_apt + qtd_torneiras_adm,
        'total_aparelhos': total_aparelhos,
        'chuveiros_adm': qtd_chuveiros_adm,
        'torneiras_adm': qtd_torneiras_adm,
        'apt_chuveiros': round(apt_chuveiros, 2),
        'adm_chuveiros': round(adm_chuveiros, 2),
        'adm_torneiras': round(adm_torneiras, 2),
        'total_secar': total_secar,
        'total_lavar': total_lavar,
        'total_motores_kva': round(total, 2),
        'maior_motor_kva': round(maior, 2),
        'restantes_kva': round(restantes, 2),
        'motores': motores_detalhes,
        'outras_cargas_apt': outras_cargas_apt,
        'outras_cargas_adm': outras_cargas_adm,
        'ac_apt': ac_apt,
        'ac_adm': ac_adm,
        'total_ac_apt_kw': round(total_ac_apt_kw, 2),
        'total_ac_adm_kw': round(total_ac_adm_kw, 2),
        'total_outras_apt': round(total_outras_apt, 2),
        'total_outras_adm': round(total_outras_adm, 2),
        'area_apto': area_apto,
        'aptos': aptos,
        'area_adm': area_adm,
        'chuveiro_kw': chuveiro_kw,
        'torneira_kw': torneira_kw,
        'secar_kw': secar_kw,
        'lavar_kw': lavar_kw,
        'tipo': tipo,
        'limite': limite,
        'acima_limite': acima_limite,
    }
