import sqlite3
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, '..', '..', 'GED119', 'DB119', 'databaseCPFLGed119.db')
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

def cv_para_kva(cv):
    conn = get_conn()
    cursor = conn.cursor()
    chave = normalizar_cv(cv)
    cursor.execute("SELECT potencia_kva FROM TABELA_4 WHERE potencia_cv_hp = ?", (chave,))
    r = cursor.fetchone()
    conn.close()
    return r[0] if r else 0

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

def calcular(dados):
    aptos = int(dados['aptos'])
    area_apto = float(dados['area_apto'])
    area_adm = float(dados['area_adm'])
    iluminacao = float(dados['iluminacao'])
    tomadas = float(dados['tomadas'])
    chuveiro_kw = float(dados['chuveiro_kw'])
    torneira_kw = float(dados['torneira_kw'])
    qtd_chuveiros = int(dados['qtd_chuveiros'])
    qtd_torneiras = int(dados['qtd_torneiras'])
    qtd_chuveiros_adm = int(dados.get('qtd_chuveiros_adm', 0))
    qtd_torneiras_adm = int(dados.get('qtd_torneiras_adm', 0))
    secar_kw = float(dados.get('secar_kw', 0))
    secar_apto = int(dados.get('secar_apto', 0))
    lavar_kw = float(dados.get('lavar_kw', 0))
    lavar_apto = int(dados.get('lavar_apto', 0))
    motores = dados.get('motores', [])
    outras_cargas_apt = dados.get('outras_cargas_apt', [])
    outras_cargas_adm = dados.get('outras_cargas_adm', [])
    tipo = dados.get('tipo', 'Residencial')

    w_m2 = 5
    D1a = (area_apto * aptos * w_m2) / 1000
    D1b = (area_adm * w_m2) / 1000
    D1 = D1a + D1b

    # --- D2 - APARELHOS ---
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

    # --- OUTRAS CARGAS ---
    total_outras_apt = sum(pot * qtd for desc, pot, qtd in outras_cargas_apt) if outras_cargas_apt else 0
    total_outras_adm = sum(pot * qtd for desc, pot, qtd in outras_cargas_adm) if outras_cargas_adm else 0

    # --- D3 - MOTORES ---
    total = 0
    maior = 0
    motores_detalhes = []
    for m in motores:
        cv = float(m['cv'])
        qtd = int(m['qtd'])
        kva = cv_para_kva(cv)
        total_kva = kva * qtd
        total += total_kva
        maior = max(maior, kva)
        motores_detalhes.append({'cv': cv, 'qtd': qtd, 'kva': kva, 'total_kva': total_kva})

    restantes = total - maior
    D3 = (maior * 1.0) + (restantes * 0.5)

    f_sim = fator_simultaneidade(aptos)
    Dapt = (D1a + D2_apt) * f_sim
    Dadm = D1b + D2_adm + D3 + total_outras_adm
    Dg = Dapt + Dadm + total_outras_apt

    # --- REGRA 7.3 - LIMITES ---
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
