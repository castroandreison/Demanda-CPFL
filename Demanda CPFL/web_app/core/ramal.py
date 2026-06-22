import sqlite3
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, '..', '..', 'db5410', 'nbr5410.db')
_db_path = os.path.normpath(_db_path)

def get_conn():
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn

# Mapeamento método -> (tabela_sufixo, coluna_2cond, coluna_3cond)
# Tabelas 36/37: colunas fixas A1,A2,B1,B2,C,D
# Tabelas 38/39: colunas variam por método

METODOS_36_37 = {'A1', 'A2', 'B1', 'B2', 'C', 'D'}
METODOS_38_39 = {'E', 'F', 'G'}

COL_MAP_38_39 = {
    ('E', 2): 'E_2cond',
    ('E', 3): 'E_3cond',
    ('F', 2): 'F_2cond_justapostos',
    ('F', 3, 'trifolio'): 'F_3cond_trifolio',
    ('F', 3, 'justapostos'): 'F_3cond_justapostos',
    ('G', 3, 'horizontal'): 'G_horizontal',
    ('G', 3, 'vertical'): 'G_vertical',
}

def buscar_condutor(isolacao, material, metodo, condutores, corrente, sub_tipo=None):
    """
    Busca o menor condutor que atende a corrente exigida.
    Retorna dict com secao, capacidade, etc.
    """
    if isolacao == 'PVC':
        if metodo in METODOS_36_37:
            tabela = 'tabela36_pvc_70c'
        else:
            tabela = 'tabela38_pvc_70c_efg'
    else:  # EPR/XLPE
        if metodo in METODOS_36_37:
            tabela = 'tabela37_epr_xlpe_90c'
        else:
            tabela = 'tabela39_epr_xlpe_90c_efg'

    conn = get_conn()
    cursor = conn.cursor()

    if metodo in METODOS_36_37:
        col = metodo
        cursor.execute(f"""
            SELECT secao_mm2, [{col}] as capacidade
            FROM [{tabela}]
            WHERE material = ? AND condutores = ? AND [{col}] IS NOT NULL
            ORDER BY secao_mm2
        """, (material, condutores))
    else:
        if metodo == 'E':
            col = COL_MAP_38_39[('E', condutores)]
        elif metodo == 'F':
            if condutores == 2:
                col = COL_MAP_38_39[('F', 2)]
            else:
                col = COL_MAP_38_39[('F', 3, sub_tipo or 'trifolio')]
        else:  # G
            if condutores == 2:
                cursor.close()
                conn.close()
                return None
            col = COL_MAP_38_39[('G', 3, sub_tipo or 'horizontal')]

        cursor.execute(f"""
            SELECT secao_mm2, [{col}] as capacidade
            FROM [{tabela}]
            WHERE material = ? AND [{col}] IS NOT NULL
            ORDER BY secao_mm2
        """, (material,))

    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        cap = row['capacidade']
        if cap is not None and cap >= corrente:
            return {
                'secao_mm2': row['secao_mm2'],
                'capacidade_A': cap,
                'tabela': tabela,
                'coluna': col,
            }
    return None


def get_formas_agrupamento_nbr():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT forma_agrupamento, metodos_referencia FROM tabela42_fator_agrupamento")
    formas = [{'forma': r[0], 'metodos': r[1]} for r in cursor.fetchall()]
    conn.close()
    return formas


def calcular_fator_correcao(forma_agrupamento, num_circuitos):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tabela42_fator_agrupamento WHERE forma_agrupamento = ?", (forma_agrupamento,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return 1.0
    colunas = [d[0] for d in cursor.description]
    row_dict = dict(zip(colunas, row))
    n = int(num_circuitos)
    if n <= 8:
        col = f'c{n}'
    elif n <= 11:
        col = 'c9_11'
    elif n <= 15:
        col = 'c12_15'
    elif n <= 19:
        col = 'c16_19'
    else:
        col = 'c20_mais'
    fator = row_dict.get(col)
    return float(fator) if fator is not None else 1.0


def get_fator_temperatura(tipo_temp, temperatura, isolacao):
    conn = get_conn()
    cursor = conn.cursor()
    col = 'epr_xlpe' if isolacao == 'EPR' else 'pvc'
    cursor.execute("SELECT {} FROM tabela40_fator_temperatura WHERE tipo = ? AND temperatura = ?".format(col),
                   (tipo_temp, temperatura))
    row = cursor.fetchone()
    conn.close()
    return float(row[0]) if row and row[0] is not None else 1.0


def calcular_protecao(fase_mm2):
    if not fase_mm2:
        return None
    fase = float(fase_mm2)
    if fase <= 16:
        return f'{fase:.0f}' if fase == int(fase) else str(fase)
    if fase <= 35:
        return '16'
    return f'{fase/2:.0f}'


def calcular_ramal(dados):
    corrente = float(dados['corrente'])
    isolacao = dados.get('isolacao', 'PVC')
    material = dados.get('material', 'cobre')
    metodo = dados.get('metodo', 'C')
    condutores = int(dados.get('condutores', 3))
    sub_tipo = dados.get('sub_tipo')

    # Fator de correção - agrupamento (Tabela 42)
    forma_agrup = dados.get('forma_agrupamento')
    num_circ = dados.get('num_circuitos_agrupados')
    fator_correcao = 1.0
    if forma_agrup and num_circ:
        fator_correcao = calcular_fator_correcao(forma_agrup, int(num_circ))

    # Fator de correção - temperatura (Tabela 40)
    tipo_temp = dados.get('tipo_temperatura')
    temperatura = dados.get('temperatura')
    fator_temp = 1.0
    if tipo_temp and temperatura is not None:
        fator_temp = get_fator_temperatura(tipo_temp, int(temperatura), isolacao)
        fator_correcao *= fator_temp

    corrente_corrigida = corrente / fator_correcao

    resultado = {
        'corrente': round(corrente, 2),
        'isolacao': isolacao,
        'material': material,
        'metodo': metodo,
        'condutores': condutores,
        'fator_correcao': round(fator_correcao, 2),
        'fator_temp': round(fator_temp, 2),
        'corrente_corrigida': round(corrente_corrigida, 2),
    }

    # Busca condutor para corrente corrigida
    cond = buscar_condutor(isolacao, material, metodo, condutores, corrente_corrigida, sub_tipo)
    if cond:
        resultado['secao_mm2'] = cond['secao_mm2']
        resultado['capacidade_A'] = cond['capacidade_A']
        resultado['secao_unica'] = cond['secao_mm2']
        resultado['capacidade_unica'] = cond['capacidade_A']
        resultado['neutro_mm2'] = calcular_neutro(cond['secao_mm2'])
        resultado['protecao_mm2'] = calcular_protecao(cond['secao_mm2'])

        if cond['secao_mm2'] >= 95:
            opcoes_paralelo = []
            for n in [2, 3, 4]:
                corrente_parcial = corrente_corrigida / n
                sub_cond = buscar_condutor(isolacao, material, metodo, condutores, corrente_parcial, sub_tipo)
                if sub_cond:
                    cap_total = sub_cond['capacidade_A'] * n
                    opcoes_paralelo.append({
                        'n_condutores': n,
                        'secao_mm2': sub_cond['secao_mm2'],
                        'capacidade_por_condutor': sub_cond['capacidade_A'],
                        'capacidade_total': cap_total,
                        'neutro_mm2': calcular_neutro(sub_cond['secao_mm2']),
                        'protecao_mm2': calcular_protecao(sub_cond['secao_mm2']),
                    })
            if opcoes_paralelo:
                resultado['opcoes_paralelo'] = opcoes_paralelo
    else:
        resultado['secao_mm2'] = None
        resultado['capacidade_A'] = None

    return resultado


def calcular_neutro(fase_mm2):
    if not fase_mm2:
        return None
    fase_mm2 = float(fase_mm2)
    if fase_mm2 <= 25:
        return fase_mm2
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT neutro_mm2 FROM tabela48_neutro_reduzido WHERE fase_mm2 >= ? ORDER BY fase_mm2 LIMIT 1", (fase_mm2,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else fase_mm2
