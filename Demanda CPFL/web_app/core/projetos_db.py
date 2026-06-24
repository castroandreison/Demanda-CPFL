import json
import sqlite3
import os
from datetime import datetime

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, '..', '..', 'GED119', 'Projeto TK', 'projetos_ged119.db')
_db_path = os.path.normpath(_db_path)

def get_conn():
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            aptos INTEGER,
            area_apto REAL,
            area_adm REAL,
            iluminacao REAL,
            tomadas REAL,
            chuveiro_kw REAL,
            torneira_kw REAL,
            chuveiros_apto INTEGER,
            torneiras_apto INTEGER,
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS motores_projeto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            descricao TEXT DEFAULT '',
            cv REAL,
            quantidade INTEGER,
            FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outras_cargas_projeto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            tipo TEXT,
            descricao TEXT,
            potencia REAL,
            quantidade INTEGER,
            FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
        )
    """)
    for col in ("chuveiros_adm", "torneiras_adm", "secar_kw", "lavar_kw", "secar_apto", "lavar_apto"):
        try:
            cursor.execute(f"ALTER TABLE projetos ADD COLUMN {col} REAL DEFAULT 0")
        except sqlite3.OperationalError:
            pass
    try:
        cursor.execute("ALTER TABLE projetos ADD COLUMN tipo TEXT DEFAULT 'Residencial'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE motores_projeto ADD COLUMN descricao TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    for col in ("campos_extras", "resultados"):
        try:
            cursor.execute(f"ALTER TABLE projetos ADD COLUMN {col} TEXT DEFAULT '{{}}'")
        except sqlite3.OperationalError:
            pass
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ac_projeto (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            tipo TEXT,
            descricao TEXT,
            potencia_w REAL DEFAULT 0,
            quantidade INTEGER DEFAULT 1,
            btu INTEGER DEFAULT 0,
            tipo_equipamento TEXT DEFAULT '',
            FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
        )
    """)
    try:
        cursor.execute("ALTER TABLE ac_projeto ADD COLUMN tipo_equipamento TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE ac_projeto ADD COLUMN incluir INTEGER DEFAULT 1")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE projetos ADD COLUMN usuario_id INTEGER")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def listar_projetos(usuario_id=None):
    conn = get_conn()
    cursor = conn.cursor()
    if usuario_id:
        cursor.execute("SELECT id, nome, aptos, data_criacao FROM projetos WHERE usuario_id = ? ORDER BY data_criacao DESC", (usuario_id,))
    else:
        cursor.execute("SELECT id, nome, aptos, data_criacao FROM projetos ORDER BY data_criacao DESC")
    rows = [{'id': r[0], 'nome': r[1], 'aptos': r[2], 'data_criacao': r[3]} for r in cursor.fetchall()]
    conn.close()
    return rows

def carregar_projeto(projeto_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projetos WHERE id = ?", (projeto_id,))
    proj = cursor.fetchone()
    if not proj:
        conn.close()
        return None
    col_names = [d[0] for d in cursor.description]
    proj_dict = dict(zip(col_names, proj))
    try:
        extra = json.loads(proj_dict.pop('campos_extras', '{}'))
        if isinstance(extra, dict):
            proj_dict.update(extra)
    except (json.JSONDecodeError, TypeError):
        pass
    try:
        resultados_raw = proj_dict.pop('resultados', '{}')
        proj_dict['resultados'] = json.loads(resultados_raw) if isinstance(resultados_raw, str) and resultados_raw else {}
    except (json.JSONDecodeError, TypeError):
        proj_dict['resultados'] = {}
    cursor.execute("SELECT descricao, cv, quantidade FROM motores_projeto WHERE projeto_id = ?", (projeto_id,))
    motores = [{'descricao': r[0], 'cv': r[1], 'qtd': r[2]} for r in cursor.fetchall()]
    cursor.execute("SELECT descricao, potencia, quantidade FROM outras_cargas_projeto WHERE projeto_id = ? AND tipo = 'apt'", (projeto_id,))
    outras_apt = [{'descricao': r[0], 'potencia': r[1], 'quantidade': r[2]} for r in cursor.fetchall()]
    cursor.execute("SELECT descricao, potencia, quantidade FROM outras_cargas_projeto WHERE projeto_id = ? AND tipo = 'adm'", (projeto_id,))
    outras_adm = [{'descricao': r[0], 'potencia': r[1], 'quantidade': r[2]} for r in cursor.fetchall()]
    cursor.execute("SELECT descricao, potencia_w, quantidade, btu, tipo_equipamento, incluir FROM ac_projeto WHERE projeto_id = ? AND tipo = 'apt' ORDER BY id", (projeto_id,))
    ac_apt = [{'descricao': r[0], 'potencia': r[1], 'quantidade': r[2], 'btu': r[3], 'tipo_equipamento': r[4], 'incluir': r[5]} for r in cursor.fetchall()]
    cursor.execute("SELECT descricao, potencia_w, quantidade, btu, tipo_equipamento, incluir FROM ac_projeto WHERE projeto_id = ? AND tipo = 'adm' ORDER BY id", (projeto_id,))
    ac_adm = [{'descricao': r[0], 'potencia': r[1], 'quantidade': r[2], 'btu': r[3], 'tipo_equipamento': r[4], 'incluir': r[5]} for r in cursor.fetchall()]
    conn.close()
    proj_dict['motores'] = motores
    proj_dict['outras_cargas_apt'] = outras_apt
    proj_dict['outras_cargas_adm'] = outras_adm
    proj_dict['ac_apt'] = ac_apt
    proj_dict['ac_adm'] = ac_adm
    return proj_dict

def _n(v, default=0):
    if v is None or v == '': return default
    try: return float(v)
    except: return default

def _i(v, default=0):
    if v is None or v == '': return default
    try: return int(v)
    except: return default

def salvar_projeto(projeto_id, dados, usuario_id=None):
    conn = get_conn()
    cursor = conn.cursor()
    cols = ('nome', 'aptos', 'area_apto', 'area_adm', 'iluminacao', 'tomadas',
            'chuveiro_kw', 'torneira_kw', 'chuveiros_apto', 'torneiras_apto',
            'chuveiros_adm', 'torneiras_adm',
            'secar_kw', 'secar_apto', 'lavar_kw', 'lavar_apto', 'tipo')
    extra_keys = ('ramal_corrente','ramal_isolacao','ramal_material','ramal_tensao','ramal_metodo',
                  'ramal_condutores','ramal_subtipo','ramal_forma_agrup','ramal_num_circuitos',
                  'ramal_tipo_temp','ramal_temperatura','ramal_comprimento','ramal_paralelo_idx',
                  'ramal_par_chk_neutro_0','ramal_par_chk_neutro_1','ramal_par_chk_neutro_2',
                  'ramal_par_chk_protecao_0','ramal_par_chk_protecao_1','ramal_par_chk_protecao_2',
                  'ramal_par_chk_tabela48_0','ramal_par_chk_tabela48_1','ramal_par_chk_tabela48_2',
                  'ramal_tipo_eletroduto','ramal_lig_dg','ramal_lig_tensao','ramal_lig_comprimento',
                  'qm_aptos','qm_adm','qm_material','qm_adm_tc','qm_dg',
                  'dps_spda','dps_ramal_aereo','dps_material','dps_qtd_qms',
                  'aterr_solo','aterr_multiblocos','aterr_qtd_qms','aterr_num_hastes',
                  'aterr_haste','aterr_comprimento','aterr_conexao')
    campos_extras = {k: dados.get(k) for k in extra_keys if k in dados}
    resultados = dados.get('resultados', {})
    vals = tuple(dados.get(c, '') if c in ('nome','tipo') else _n(dados.get(c)) for c in cols)
    if projeto_id:
        sql = f"UPDATE projetos SET {'=?,'.join(cols)}=?, campos_extras=?, resultados=? WHERE id=?"
        cursor.execute(sql, vals + (json.dumps(campos_extras), json.dumps(resultados), projeto_id))
    else:
        placeholders = ','.join('?' * len(cols))
        cursor.execute(f"INSERT INTO projetos ({','.join(cols)}, campos_extras, resultados, usuario_id) VALUES ({placeholders},?,?,?)", vals + (json.dumps(campos_extras), json.dumps(resultados), usuario_id))
        projeto_id = cursor.lastrowid
    cursor.execute("DELETE FROM motores_projeto WHERE projeto_id = ?", (projeto_id,))
    for m in dados.get('motores', []):
        desc = m.get('desc', m.get('descricao', ''))
        cursor.execute("INSERT INTO motores_projeto (projeto_id, descricao, cv, quantidade) VALUES (?, ?, ?, ?)",
                       (projeto_id, desc, _n(m.get('cv')), _i(m.get('qtd'), 1)))
    cursor.execute("DELETE FROM outras_cargas_projeto WHERE projeto_id = ?", (projeto_id,))
    for c in dados.get('outras_cargas_apt', []):
        cdesc = c[0] if isinstance(c, list) else c.get('descricao','')
        cpot = _n(c[1] if isinstance(c, list) else c.get('potencia'))
        cqtd = _i(c[2] if isinstance(c, list) else c.get('quantidade'), 1)
        cursor.execute("INSERT INTO outras_cargas_projeto (projeto_id, tipo, descricao, potencia, quantidade) VALUES (?, 'apt', ?, ?, ?)",
                       (projeto_id, cdesc, cpot, cqtd))
    for c in dados.get('outras_cargas_adm', []):
        cdesc = c[0] if isinstance(c, list) else c.get('descricao','')
        cpot = _n(c[1] if isinstance(c, list) else c.get('potencia'))
        cqtd = _i(c[2] if isinstance(c, list) else c.get('quantidade'), 1)
        cursor.execute("INSERT INTO outras_cargas_projeto (projeto_id, tipo, descricao, potencia, quantidade) VALUES (?, 'adm', ?, ?, ?)",
                       (projeto_id, cdesc, cpot, cqtd))
    cursor.execute("DELETE FROM ac_projeto WHERE projeto_id = ?", (projeto_id,))
    for ac in dados.get('ac_apt', []):
        desc = ac.get('descricao', ac.get('desc', ''))
        pot = _n(ac.get('potencia', ac.get('pot')))
        qtd = _i(ac.get('quantidade', ac.get('qtd')), 1)
        btu = _i(ac.get('btu'))
        tipo_eq = ac.get('tipo_equipamento', '')
        incluir = 1 if ac.get('incluir', 1) else 0
        cursor.execute("INSERT INTO ac_projeto (projeto_id, tipo, descricao, potencia_w, quantidade, btu, tipo_equipamento, incluir) VALUES (?, 'apt', ?, ?, ?, ?, ?, ?)",
                       (projeto_id, desc, pot, qtd, btu, tipo_eq, incluir))
    for ac in dados.get('ac_adm', []):
        desc = ac.get('descricao', ac.get('desc', ''))
        pot = _n(ac.get('potencia', ac.get('pot')))
        qtd = _i(ac.get('quantidade', ac.get('qtd')), 1)
        btu = _i(ac.get('btu'))
        tipo_eq = ac.get('tipo_equipamento', '')
        incluir = 1 if ac.get('incluir', 1) else 0
        cursor.execute("INSERT INTO ac_projeto (projeto_id, tipo, descricao, potencia_w, quantidade, btu, tipo_equipamento, incluir) VALUES (?, 'adm', ?, ?, ?, ?, ?, ?)",
                       (projeto_id, desc, pot, qtd, btu, tipo_eq, incluir))
    conn.commit()
    conn.close()
    return projeto_id

def excluir_projeto(projeto_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM motores_projeto WHERE projeto_id = ?", (projeto_id,))
    cursor.execute("DELETE FROM outras_cargas_projeto WHERE projeto_id = ?", (projeto_id,))
    cursor.execute("DELETE FROM ac_projeto WHERE projeto_id = ?", (projeto_id,))
    cursor.execute("DELETE FROM projetos WHERE id = ?", (projeto_id,))
    conn.commit()
    conn.close()

init_db()
