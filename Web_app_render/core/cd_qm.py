import math

# Tabela 2 - Fatores de Demanda (valores em %)
TABELA2_FD = [
    (1,      [1.00, 1.00, 1.00, 1.00, 1.00]),
    (2,      [0.72, 0.72, 0.66, 0.66, 1.00]),
    (3,      [0.55, 0.55, 0.52, 0.52, 1.00]),
    (4,      [0.46, 0.46, 0.42, 0.42, 1.00]),
    (5,      [0.40, 0.40, 0.36, 0.36, 1.00]),
    (6, 10,  [0.34, 0.34, 0.30, 0.30, 1.00]),
    (11, 15, [0.32, 0.32, 0.28, 0.28, 0.90]),
    (16, 20, [0.28, 0.28, 0.26, 0.26, 0.86]),
    (21, 30, [0.25, 0.25, 0.25, 0.25, 0.82]),
    (31, 40, [0.24, 0.24, 0.24, 0.24, 0.76]),
    (41, 50, [0.23, 0.23, 0.24, 0.24, 0.72]),
    (51, 75, [0.22, 0.22, 0.24, 0.24, 0.72]),
    (76, 100,[0.22, 0.22, 0.23, 0.23, 0.71]),
    (101,150,[0.21, 0.21, 0.23, 0.23, 0.71]),
    (151,999,[0.21, 0.21, 0.23, 0.23, 0.70]),
]

# Tabela 7 - Coeficiente de Simultaneidade
TABELA7_SIM = [
    (1, 1,   1.00),
    (2, 2,   0.93),
    (3, 3,   0.90),
    (4, 4,   0.87),
    (5, 5,   0.84),
    (6, 10,  0.80),
    (11, 15, 0.93),
    (16, 18, 0.89),
    (19, 21, 0.86),
    (22, 25, 0.83),
    (26, 30, 0.80),
    (31, 40, 0.68),
    (41, 50, 0.62),
    (51, 75, 0.55),
    (76, 100,0.52),
    (101,150,0.51),
    (151,999,0.50),
]

# Tabela 11A - Condutores EPR/XLPE 90C (coluna B/C metodos)
TABELA11_EPR = [
    (101, 25), (130, 35), (175, 50), (210, 70),
    (260, 95), (305, 120), (360, 150), (415, 185), (480, 240),
]

# Tabela 11B - Condutores PVC 70C 750V
TABELA11_PVC = [
    (86, 25), (110, 35), (142, 50), (171, 70),
    (210, 95), (240, 120), (278, 150), (318, 185), (363, 240),
]

# Tabela 12 - Barramento BT (por demanda kVA)
# GED-119: BARRAMENTO DE BAIXA TENSÃO DAS CAIXAS E DO QUADRO DE MEDIDORES E DA CABINE
TABELA12_BARRAMENTO = [
    (60,   '25,4 x 6,4',   '1" x 1/4"'),
    (120,  '31,8 x 6,4',   '1.1/4" x 1/4"'),
    (150,  '38,1 x 6,4',   '1.1/2" x 1/4"'),
    (200,  '50,8 x 6,4',   '2" x 1/4"'),
    (250,  '38,1 x 12,7',  '1.1/2" x 1/2"'),
    (300,  '50,8 x 12,7',  '2" x 1/2"'),
    (350,  '63,5 x 12,7',  '2.1/2" x 1/2"'),
    (450,  '88,9 x 12,7',  '3" x 1/2"'),
    (550,  '101,6 x 12,7', '4" x 1/2"'),
    (700,  '127 x 12,7',   '5" x 1/2"'),
]

# Disjuntores termomagnéticos padronizados (por corrente A)
TABELA12_DISJ = [
    (100,  100),
    (125,  125),
    (150,  150),
    (160,  160),
    (175,  175),
    (200,  200),
    (225,  225),
    (250,  250),
    (300,  300),
    (350,  350),
    (400,  400),
    (450,  450),
    (500,  500),
    (600,  600),
]

# Tabela 14 - Condutor de Aterramento (BT)
TABELA14_ATER = [
    (50,    16, 25),
    (100,   16, 25),
    (200,   25, 35),
    (300,   35, 50),
    (400,   50, 70),
    (500,   70, 95),
    (600,   95, 120),
    (800,   120, 150),
    (1000,  150, 185),
]

# Eletrodutos (diametro mm, polegada, capacidade maxima mm2)
TABELA13_ELETRODUTO = [
    (20,  '1/2"',   3*6),
    (25,  '3/4"',   3*10),
    (32,  '1"',     3*16),
    (40,  '1.1/4"', 3*25),
    (50,  '1.1/2"', 3*35),
    (60,  '2"',     3*50),
    (75,  '2.1/2"', 3*70),
    (85,  '3"',     3*95),
    (100, '4"',     3*185),
]

# Area de condutores por secao (mm2) - diametro externo aprox para EPR 0.6/1kV
SECAO_DIAMETRO = {
    16: 8.5, 25: 10.5, 35: 12.0, 50: 14.0, 70: 16.5,
    95: 19.0, 120: 21.0, 150: 23.5, 185: 26.0, 240: 29.5,
}

def _buscar_faixa(valor, tabela):
    for linha in tabela:
        if len(linha) == 2:
            lim, res = linha
            if valor <= lim:
                return res
        elif len(linha) == 3:
            lim, res, res2 = linha
            if valor <= lim:
                return res, res2
        elif len(linha) >= 4:
            faixa_min = linha[0]
            if isinstance(faixa_min, int) and len(linha) >= 3:
                if len(linha) == 3:
                    faixa_min, faixa_max, res = linha
                    if faixa_min <= valor <= faixa_max:
                        return res
                elif len(linha) == 4:
                    faixa_min, faixa_max, res1, res2 = linha
                    if faixa_min <= valor <= faixa_max:
                        return res1, res2
    return None

def _buscar_faixa_tabela2(qtd):
    for linha in TABELA2_FD:
        if len(linha) == 2:
            if qtd == linha[0]:
                return linha[1]
        elif len(linha) == 3:
            if linha[0] <= qtd <= linha[1]:
                return linha[2]
    return [1.0, 1.0, 1.0, 1.0, 1.0]

def _buscar_simultaneidade(qtd):
    for linha in TABELA7_SIM:
        if linha[0] <= qtd <= linha[1]:
            return linha[2]
    return 1.0

def _escolher_bitola_condutor(i, isolacao):
    tabela = TABELA11_EPR if isolacao == 'EPR' else TABELA11_PVC
    for lim, bitola in tabela:
        if i <= lim:
            return bitola
    return 240

def _escolher_disjuntor(i):
    for lim, disj in TABELA12_DISJ:
        if i <= lim:
            return disj
    return 600

def _escolher_barramento(demanda_kva):
    for lim, barra_mm, barra_pol in TABELA12_BARRAMENTO:
        if demanda_kva <= lim:
            return barra_mm, barra_pol
    return '127 x 12,7', '5" x 1/2"'

def _escolher_aterramento(demanda_kva):
    for lim, cobre, aluminio in TABELA14_ATER:
        if demanda_kva <= lim:
            return cobre, aluminio
    return 150, 185

def _escolher_eletroduto(secao_fase):
    area_cond = SECAO_DIAMETRO.get(secao_fase, 10.0)
    area_circ = (area_cond/2)**2 * math.pi
    area_total_cond = area_circ * 4
    area_min = area_total_cond / 0.40
    for diam, pol, cap in TABELA13_ELETRODUTO:
        if cap >= area_total_cond:
            return diam, pol
    return 100, '4"'

def demanda_individual_qm(dados):
    total_med = int(dados.get('total_medidores', 0))
    limite_qm = int(dados.get('limite_por_qm', 18))
    medidores_list = dados.get('medidores_list', None)
    area_apto = float(dados.get('area_apto', 0))
    chuveiro_w = float(dados.get('chuveiro_w', 5500))
    microondas_w = float(dados.get('microondas_w', 1500))
    fogao_w = float(dados.get('fogao_w', 2000))
    ar_w = float(dados.get('ar_w', 1400))

    if medidores_list and isinstance(medidores_list, list) and len(medidores_list) > 0:
        qm_list = [int(x) for x in medidores_list if int(x) > 0]
        k = len(qm_list)
    else:
        if total_med <= 0 or limite_qm <= 0:
            return {'erro': 'Total de medidores ou limite invalido'}
        k = math.ceil(total_med / limite_qm)
        base = total_med // k
        resto = total_med % k
        qm_list = [base + (1 if i < resto else 0) for i in range(k)]

    resultado_qms = []
    for i, n_med in enumerate(qm_list):
        if n_med <= 0:
            continue
        fds = _buscar_faixa_tabela2(n_med)
        fd_ch = fds[0]
        fd_micro = fds[2]
        fd_fogao = fds[3]
        fd_ar = fds[4]

        d1a = n_med * area_apto * 5 / 1000

        p_ch = n_med * chuveiro_w * fd_ch / 1000
        p_micro = n_med * microondas_w * fd_micro / 1000
        p_fogao = n_med * fogao_w * fd_fogao / 1000
        p_ar = n_med * ar_w * fd_ar / 1000
        d2 = p_ch + p_micro + p_fogao + p_ar

        coef = _buscar_simultaneidade(n_med)
        dapt = (d1a + d2) * coef
        corrente = dapt * 1000 / (380 * math.sqrt(3)) if dapt > 0 else 0

        resultado_qms.append({
            'qm': i + 1,
            'medidores': n_med,
            'd1a_kva': round(d1a, 2),
            'fd_ch': round(fd_ch, 2),
            'fd_micro': round(fd_micro, 2),
            'fd_fogao': round(fd_fogao, 2),
            'fd_ar': round(fd_ar, 2),
            'd2_parcelas': {
                'chuveiro_kva': round(p_ch, 2),
                'microondas_kva': round(p_micro, 2),
                'fogao_kva': round(p_fogao, 2),
                'ar_kva': round(p_ar, 2),
            },
            'd2_kva': round(d2, 2),
            'coef_sim': round(coef, 2),
            'dapt_kva': round(dapt, 2),
            'corrente_A': round(corrente, 2),
        })

    return {
        'total_medidores': total_med,
        'limite_por_qm': limite_qm,
        'quantidade_qms': k,
        'qms': resultado_qms,
        'soma_dapt_kva': round(sum(q['dapt_kva'] for q in resultado_qms), 2),
        'soma_corrente_A': round(sum(q['corrente_A'] for q in resultado_qms), 2),
    }


def condutores_cd_qm(dados):
    qms = dados.get('qms', [])
    isolacao = dados.get('isolacao', 'EPR')
    fc_temp = float(dados.get('fc_temp', 1.0))
    fc_agrup = float(dados.get('fc_agrup', 1.0))
    resultado = []
    for qm in qms:
        i = float(qm.get('corrente_A', 0))
        i_corrigida = i / (fc_temp * fc_agrup) if (fc_temp * fc_agrup) > 0 else i
        bitola = _escolher_bitola_condutor(i_corrigida, isolacao)
        cap_max = 0
        tabela = TABELA11_EPR if isolacao == 'EPR' else TABELA11_PVC
        for lim, bit in tabela:
            if bit == bitola:
                cap_max = lim
                break
        resultado.append({
            'qm': qm.get('qm', 0),
            'corrente_A': round(i, 2),
            'I_corrigida_A': round(i_corrigida, 2),
            'isolacao': isolacao,
            'bitola_mm2': bitola,
            'capacidade_max_A': cap_max,
        })
    return {'condutores': resultado, 'isolacao': isolacao,
            'fc_temp': fc_temp, 'fc_agrup': fc_agrup}


def disjuntor_qm(dados):
    qms = dados.get('qms', [])
    resultado = []
    for qm in qms:
        i = float(qm.get('corrente_A', 0))
        disj = _escolher_disjuntor(i)
        qm_kva = float(qm.get('dapt_kva', 0))
        if qm_kva > 0:
            barra_mm, barra_pol = _escolher_barramento(qm_kva)
        else:
            barra_mm, barra_pol = '25,4 x 6,4', '1" x 1/4"'
        resultado.append({
            'qm': qm.get('qm', 0),
            'corrente_A': round(i, 2),
            'disjuntor_A': disj,
            'barramento_mm': barra_mm,
            'barramento_pol': barra_pol,
        })
    return {'disjuntores': resultado}


def queda_tensao(dados):
    qms = dados.get('qms', [])
    tensao = float(dados.get('tensao', 380))
    comprimento_default = float(dados.get('comprimento', 50))
    condutividade = float(dados.get('condutividade', 56))
    resultado = []
    for qm in qms:
        i = float(qm.get('corrente_A', 0))
        bitola = int(qm.get('bitola_mm2', 25))
        comprimento = float(qm.get('distancia_m', comprimento_default))
        if bitola <= 0 or i <= 0:
            resultado.append({'qm': qm.get('qm', 0), 'dV_percent': 0, 'situacao': 'OK'})
            continue
        for tentativa_bitola in sorted([b for _, b in TABELA11_EPR] + [b for _, b in TABELA11_PVC], reverse=True):
            if tentativa_bitola < bitola:
                continue
            dV = (math.sqrt(3) * i * comprimento * 100) / (tensao * tentativa_bitola * condutividade)
            if dV <= 3:
                resultado.append({
                    'qm': qm.get('qm', 0),
                    'comprimento_m': comprimento,
                    'corrente_A': round(i, 2),
                    'bitola_mm2': tentativa_bitola,
                    'bitola_sugerida_mm2': tentativa_bitola if tentativa_bitola != bitola else None,
                    'dV_percent': round(dV, 2),
                    'situacao': 'OK' if dV <= 3 else 'EXCEDEU',
                })
                break
        else:
            resultado.append({
                'qm': qm.get('qm', 0),
                'comprimento_m': comprimento,
                'corrente_A': round(i, 2),
                'bitola_mm2': 240,
                'dV_percent': round(dV, 2) if 'dV' in dir() else 99,
                'situacao': 'EXCEDEU',
            })
    return {
        'resultados': resultado,
        'tensao_V': tensao,
        'condutividade': condutividade,
        'limite_percent': 3,
    }


def barramento_cd(dados):
    demanda_total_kva = float(dados.get('demanda_total_kva', 0))
    corrente_total_A = float(dados.get('corrente_total_A', 0))
    if corrente_total_A <= 0 and demanda_total_kva > 0:
        corrente_total_A = demanda_total_kva * 1000 / (380 * math.sqrt(3))

    disj = _escolher_disjuntor(corrente_total_A)
    barra_mm, barra_pol = _escolher_barramento(demanda_total_kva)

    return {
        'corrente_total_A': round(corrente_total_A, 2),
        'demanda_total_kva': round(demanda_total_kva, 2),
        'disjuntor_geral_A': disj,
        'barramento_mm': barra_mm,
        'barramento_pol': barra_pol,
    }


def aterramento(dados):
    demanda_kva = float(dados.get('demanda_kva', 0))
    tensao = dados.get('tensao', 'BT')
    if tensao == 'MT':
        cobre = '5,16 mm2 (fio continuo)'
        aluminio = '6,35 mm2 (fio continuo)'
    else:
        cobre_mm2, aluminio_mm2 = _escolher_aterramento(demanda_kva)
        cobre = f'{cobre_mm2} mm2'
        aluminio = f'{aluminio_mm2} mm2'
    return {
        'demanda_kva': round(demanda_kva, 2),
        'tensao': tensao,
        'condutor_cobre': cobre,
        'condutor_aluminio': aluminio,
        'vergalhao': '5/8" x 3,0 m (15,8 mm x 3,0 m)',
    }


def eletroduto(dados):
    qms = dados.get('qms', [])
    resultado = []
    for qm in qms:
        bitola = int(qm.get('bitola_mm2', 25))
        diam, pol = _escolher_eletroduto(bitola)
        resultado.append({
            'qm': qm.get('qm', 0),
            'bitola_condutor_mm2': bitola,
            'eletroduto_mm': diam,
            'eletroduto_pol': pol,
        })
    return {'eletrodutos': resultado}


def memorial_completo(dados):
    etapa1 = dados.get('etapa1', {})
    etapa2 = dados.get('etapa2', {})
    etapa3 = dados.get('etapa3', {})
    etapa4 = dados.get('etapa4', {})
    etapa5 = dados.get('etapa5', {})
    etapa6 = dados.get('etapa6', {})
    etapa7 = dados.get('etapa7', {})
    return {
        'demanda_individual': etapa1,
        'condutores': etapa2,
        'disjuntores': etapa3,
        'queda_tensao': etapa4,
        'barramento_cd': etapa5,
        'aterramento': etapa6,
        'eletrodutos': etapa7,
    }
