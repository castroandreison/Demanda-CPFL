import sqlite3
import os

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, '..', 'db', 'nbr5410.db')
_db_path = os.path.normpath(_db_path)

def get_conn():
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn

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
    if isolacao == 'PVC':
        if metodo in METODOS_36_37:
            tabela = 'tabela36_pvc_70c'
        else:
            tabela = 'tabela38_pvc_70c_efg'
    else:
        if metodo in METODOS_36_37:
            tabela = 'tabela37_epr_xlpe_90c'
        else:
            tabela = 'tabela39_epr_xlpe_90c_efg'
    conn = get_conn()
    cursor = conn.cursor()
    if metodo in METODOS_36_37:
        col = metodo
        cursor.execute(f"SELECT secao_mm2, [{col}] as capacidade FROM [{tabela}] WHERE material = ? AND condutores = ? AND [{col}] IS NOT NULL ORDER BY secao_mm2", (material, condutores))
    else:
        if metodo == 'E':
            col = COL_MAP_38_39[('E', condutores)]
        elif metodo == 'F':
            if condutores == 2:
                col = COL_MAP_38_39[('F', 2)]
            else:
                col = COL_MAP_38_39[('F', 3, sub_tipo or 'trifolio')]
        else:
            if condutores == 2:
                cursor.close(); conn.close(); return None
            col = COL_MAP_38_39[('G', 3, sub_tipo or 'horizontal')]
        cursor.execute(f"SELECT secao_mm2, [{col}] as capacidade FROM [{tabela}] WHERE material = ? AND [{col}] IS NOT NULL ORDER BY secao_mm2", (material,))
    rows = cursor.fetchall()
    conn.close()
    for row in rows:
        cap = row['capacidade']
        if cap is not None and cap >= corrente:
            return {'secao_mm2': row['secao_mm2'], 'capacidade_A': cap, 'tabela': tabela, 'coluna': col}
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
    if not row: return 1.0
    colunas = [d[0] for d in cursor.description]
    row_dict = dict(zip(colunas, row))
    n = int(num_circuitos)
    if n <= 8: col = f'c{n}'
    elif n <= 11: col = 'c9_11'
    elif n <= 15: col = 'c12_15'
    elif n <= 19: col = 'c16_19'
    else: col = 'c20_mais'
    fator = row_dict.get(col)
    return float(fator) if fator is not None else 1.0

def get_fator_temperatura(tipo_temp, temperatura, isolacao):
    conn = get_conn()
    cursor = conn.cursor()
    col = 'epr_xlpe' if isolacao == 'EPR' else 'pvc'
    cursor.execute(f"SELECT {col} FROM tabela40_fator_temperatura WHERE tipo = ? AND temperatura = ?", (tipo_temp, temperatura))
    row = cursor.fetchone()
    conn.close()
    return float(row[0]) if row and row[0] is not None else 1.0

def calcular_protecao(fase_mm2):
    if not fase_mm2: return None
    fase = float(fase_mm2)
    if fase <= 16: return f'{fase:.0f}' if fase == int(fase) else str(fase)
    if fase <= 35: return '16'
    return f'{fase/2:.0f}'

SECOES_DISPONIVEIS = [1.5, 2.5, 4, 6, 10, 16, 25, 35, 50, 70, 95, 120, 150, 185, 240, 300, 400, 500]

def _next_secao(min_mm2):
    for s in SECOES_DISPONIVEIS:
        if s >= min_mm2: return s
    return None

def _format_condutor_display(secao_mm2, n_paralelo=None):
    if not secao_mm2: return None, None
    v = float(secao_mm2)
    if n_paralelo:
        por_cabo = _next_secao(v / n_paralelo)
        if por_cabo: return por_cabo, f'{n_paralelo}x{por_cabo}'
    return v, str(int(v)) if v == int(v) else str(v)

def calcular_ramal(dados):
    corrente = float(dados.get('corrente') or 0)
    isolacao = dados.get('isolacao', 'PVC')
    material = dados.get('material', 'cobre')
    metodo = dados.get('metodo', 'C')
    condutores = int(dados.get('condutores', 3))
    sub_tipo = dados.get('sub_tipo')
    forma_agrup = dados.get('forma_agrupamento')
    num_circ = dados.get('num_circuitos_agrupados')
    fator_correcao = 1.0
    if forma_agrup and num_circ: fator_correcao = calcular_fator_correcao(forma_agrup, int(num_circ))
    tipo_temp = dados.get('tipo_temperatura')
    temperatura = dados.get('temperatura')
    fator_temp = 1.0
    if tipo_temp and temperatura is not None:
        fator_temp = get_fator_temperatura(tipo_temp, int(temperatura), isolacao)
        fator_correcao *= fator_temp
    corrente_corrigida = corrente / fator_correcao
    resultado = {'corrente': round(corrente, 2), 'isolacao': isolacao, 'material': material, 'metodo': metodo, 'condutores': condutores, 'fator_correcao': round(fator_correcao, 2), 'fator_temp': round(fator_temp, 2), 'corrente_corrigida': round(corrente_corrigida, 2)}
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
                    neutro_val = calcular_neutro(sub_cond['secao_mm2'])
                    prot_val = calcular_protecao(sub_cond['secao_mm2'])
                    neutro_real, neutro_disp = _format_condutor_display(neutro_val, n)
                    prot_real, prot_disp = _format_condutor_display(prot_val, n)
                    secao_parcial = sub_cond['secao_mm2']
                    opcoes_paralelo.append({'n_condutores': n, 'secao_mm2': secao_parcial, 'capacidade_por_condutor': sub_cond['capacidade_A'], 'capacidade_total': cap_total, 'neutro_mm2': neutro_real or neutro_val, 'neutro_display': neutro_disp or str(neutro_val), 'neutro_cheio_mm2': secao_parcial, 'protecao_mm2': prot_real or prot_val, 'protecao_display': prot_disp or str(prot_val), 'protecao_cheio_mm2': secao_parcial})
            if opcoes_paralelo: resultado['opcoes_paralelo'] = opcoes_paralelo
        neutro_val = resultado.get('neutro_mm2')
        prot_val = resultado.get('protecao_mm2')
        if neutro_val: _, resultado['neutro_display'] = _format_condutor_display(neutro_val)
        if prot_val: _, resultado['protecao_display'] = _format_condutor_display(prot_val)
    else:
        resultado['secao_mm2'] = None; resultado['capacidade_A'] = None
    return resultado

def calcular_neutro(fase_mm2):
    if not fase_mm2: return None
    fase_mm2 = float(fase_mm2)
    if fase_mm2 <= 25: return fase_mm2
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT neutro_mm2 FROM tabela48_neutro_reduzido WHERE fase_mm2 >= ? ORDER BY fase_mm2 LIMIT 1", (fase_mm2,))
    row = cursor.fetchone(); conn.close()
    return row[0] if row else fase_mm2

def get_tipos_eletroduto():
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT tipo FROM eletrodutos_cabos ORDER BY tipo")
    tipos = [r[0] for r in cursor.fetchall()]; conn.close()
    return tipos

def calcular_eletroduto(tipo_cabo, secao_mm2, n_condutores):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT eletroduto_pol FROM eletrodutos_resumida WHERE secao_mm2 = ? AND n_condutores = ?", (secao_mm2, n_condutores))
    row = cursor.fetchone()
    if row:
        conn.close()
        return {'eletroduto': row[0], 'metodo': 'tabela_resumida', 'secao_mm2': secao_mm2, 'n_condutores': n_condutores, 'passos': [f'1) Dados: Seção = {secao_mm2} mm², Condutores = {n_condutores}', '2) Consulta direta na Tabela Resumida (NBR 5410)', f'3) Eletroduto mínimo: {row[0]}']}
    cursor.execute("SELECT diam_externo_mm, area_condutor_mm2 FROM eletrodutos_cabos WHERE tipo = ? AND secao_mm2 = ?", (tipo_cabo, secao_mm2))
    cabo = cursor.fetchone()
    if not cabo: conn.close(); return None
    d_ext = cabo[0]
    if not d_ext or d_ext <= 0: conn.close(); return None
    area_cond = 3.14159265 * (d_ext / 2.0) ** 2
    area_total_necessaria = area_cond * n_condutores
    cursor.execute("SELECT eletroduto_pol, diam_mm, area_total_mm2, area_ocupavel_40_mm2 FROM eletrodutos_conduites WHERE tipo = ? ORDER BY area_total_mm2", (tipo_cabo,))
    conduites = cursor.fetchall(); conn.close()
    for c in conduites:
        if c[3] and c[3] >= area_total_necessaria:
            return {'eletroduto': c[0], 'diam_mm': c[1], 'area_total': c[2], 'area_ocupavel': c[3], 'area_necessaria': round(area_total_necessaria, 2), 'metodo': 'area_ocupavel', 'secao_mm2': secao_mm2, 'n_condutores': n_condutores, 'diam_externo_mm': d_ext, 'area_por_condutor_mm2': round(area_cond, 2), 'passos': [f'1) Dados: Seção = {secao_mm2} mm², Condutores = {n_condutores}, Tipo = {tipo_cabo}', f'2) Diâmetro externo do condutor (tabela): D_ext = {d_ext} mm', f'3) Área por condutor: A_cond = π × (D_ext/2)² = 3,1416 × ({d_ext}/2)² = {round(area_cond, 2)} mm²', f'4) Área total ocupada: A_total = {n_condutores} × {round(area_cond, 2)} = {round(area_total_necessaria, 2)} mm²', f'5) Conduíte escolhido: {c[0]} (Ø{c[1]} mm)', f'6) Área útil (40%): A_útil = {round(c[3], 2)} mm²', f'7) Verificação: {round(area_total_necessaria, 2)} mm² <= {round(c[3], 2)} mm² ✓']}
    return None
