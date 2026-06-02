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
    motores = dados.get('motores', [])

    w_m2 = 5
    D1a = (area_apto * aptos * w_m2) / 1000
    D1b = (area_adm * w_m2) / 1000
    D1 = D1a + D1b

    total_chuveiros = aptos * qtd_chuveiros
    f_ch = fator_aparelho("chuveiro_torneira_ferro", total_chuveiros)

    chuveiros_contrib = aptos * qtd_chuveiros * chuveiro_kw * f_ch
    torneiras_contrib = aptos * qtd_torneiras * torneira_kw * f_ch
    D2 = chuveiros_contrib + torneiras_contrib

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
    Dapt = (D1a + D2) * f_sim
    Dadm = D1b + D3
    Dg = Dapt + Dadm

    total_chuveiros_geral = aptos * qtd_chuveiros
    total_torneiras_geral = aptos * qtd_torneiras
    total_aparelhos = total_chuveiros_geral + total_torneiras_geral

    return {
        'D1': round(D1, 2),
        'D1a': round(D1a, 2),
        'D1b': round(D1b, 2),
        'D2': round(D2, 2),
        'D3': round(D3, 2),
        'Dg': round(Dg, 2),
        'Dapt': round(Dapt, 2),
        'Dadm': round(Dadm, 2),
        'f_sim': round(f_sim, 2),
        'w_m2': w_m2,
        'f_ch': round(f_ch, 2),
        'total_chuveiros': total_chuveiros,
        'total_chuveiros_geral': total_chuveiros_geral,
        'total_torneiras_geral': total_torneiras_geral,
        'total_aparelhos': total_aparelhos,
        'chuveiros_contrib': round(chuveiros_contrib, 2),
        'torneiras_contrib': round(torneiras_contrib, 2),
        'total_motores_kva': round(total, 2),
        'maior_motor_kva': round(maior, 2),
        'restantes_kva': round(restantes, 2),
        'motores': motores_detalhes,
        'area_apto': area_apto,
        'aptos': aptos,
        'area_adm': area_adm,
    }
