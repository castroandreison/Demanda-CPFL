import json
import os
from datetime import datetime

from . import db_helper

USING_PG = db_helper.USING_PG
P = db_helper.PLACEHOLDER

def get_conn():
    return db_helper.connect_projetos()

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    if USING_PG:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projetos (
                id SERIAL PRIMARY KEY, nome TEXT UNIQUE, aptos INTEGER,
                area_apto DOUBLE PRECISION DEFAULT 0, area_adm DOUBLE PRECISION DEFAULT 0,
                iluminacao DOUBLE PRECISION DEFAULT 0, tomadas DOUBLE PRECISION DEFAULT 0,
                chuveiro_kw DOUBLE PRECISION DEFAULT 0, torneira_kw DOUBLE PRECISION DEFAULT 0,
                chuveiros_apto INTEGER DEFAULT 0, torneiras_apto INTEGER DEFAULT 0,
                chuveiros_adm DOUBLE PRECISION DEFAULT 0, torneiras_adm DOUBLE PRECISION DEFAULT 0,
                secar_kw DOUBLE PRECISION DEFAULT 0, secar_apto DOUBLE PRECISION DEFAULT 0,
                lavar_kw DOUBLE PRECISION DEFAULT 0, lavar_apto DOUBLE PRECISION DEFAULT 0,
                tipo TEXT DEFAULT 'Residencial', campos_extras TEXT DEFAULT '{}',
                resultados TEXT DEFAULT '{}', data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS motores_projeto (
                id SERIAL PRIMARY KEY, projeto_id INTEGER REFERENCES projetos(id) ON DELETE CASCADE,
                descricao TEXT DEFAULT '', cv DOUBLE PRECISION, quantidade INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outras_cargas_projeto (
                id SERIAL PRIMARY KEY, projeto_id INTEGER REFERENCES projetos(id) ON DELETE CASCADE,
                tipo TEXT, descricao TEXT, potencia DOUBLE PRECISION, quantidade INTEGER
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ac_projeto (
                id SERIAL PRIMARY KEY, projeto_id INTEGER REFERENCES projetos(id) ON DELETE CASCADE,
                tipo TEXT, descricao TEXT, potencia_w DOUBLE PRECISION DEFAULT 0,
                quantidade INTEGER DEFAULT 1, btu INTEGER DEFAULT 0,
                tipo_equipamento TEXT DEFAULT '', incluir INTEGER DEFAULT 1
            )
        """)
    else:
        cursor.execute("""CREATE TABLE IF NOT EXISTS projetos (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE, aptos INTEGER, area_apto REAL, area_adm REAL, iluminacao REAL, tomadas REAL, chuveiro_kw REAL, torneira_kw REAL, chuveiros_apto INTEGER, torneiras_apto INTEGER, data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS motores_projeto (id INTEGER PRIMARY KEY AUTOINCREMENT, projeto_id INTEGER, descricao TEXT DEFAULT '', cv REAL, quantidade INTEGER, FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS outras_cargas_projeto (id INTEGER PRIMARY KEY AUTOINCREMENT, projeto_id INTEGER, tipo TEXT, descricao TEXT, potencia REAL, quantidade INTEGER, FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS ac_projeto (id INTEGER PRIMARY KEY AUTOINCREMENT, projeto_id INTEGER, tipo TEXT, descricao TEXT, potencia_w REAL DEFAULT 0, quantidade INTEGER DEFAULT 1, btu INTEGER DEFAULT 0, tipo_equipamento TEXT DEFAULT '', FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE)""")
        for col in ("chuveiros_adm", "torneiras_adm", "secar_kw", "lavar_kw", "secar_apto", "lavar_apto"):
            try: cursor.execute(f"ALTER TABLE projetos ADD COLUMN {col} REAL DEFAULT 0")
            except: pass
        try: cursor.execute("ALTER TABLE projetos ADD COLUMN tipo TEXT DEFAULT 'Residencial'")
        except: pass
        try: cursor.execute("ALTER TABLE motores_projeto ADD COLUMN descricao TEXT DEFAULT ''")
        except: pass
        for col in ("campos_extras", "resultados"):
            try: cursor.execute(f"ALTER TABLE projetos ADD COLUMN {col} TEXT DEFAULT '{{}}'")
            except: pass
        try: cursor.execute("ALTER TABLE ac_projeto ADD COLUMN tipo_equipamento TEXT DEFAULT ''")
        except: pass
        try: cursor.execute("ALTER TABLE ac_projeto ADD COLUMN incluir INTEGER DEFAULT 1")
        except: pass
    conn.commit(); conn.close()

def listar_projetos():
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"SELECT id, nome, aptos, data_criacao FROM projetos ORDER BY data_criacao DESC")
    if USING_PG:
        rows = [{'id': r[0], 'nome': r[1], 'aptos': r[2], 'data_criacao': r[3].isoformat() if hasattr(r[3], 'isoformat') else r[3]} for r in cursor.fetchall()]
    else:
        rows = [{'id': r[0], 'nome': r[1], 'aptos': r[2], 'data_criacao': r[3]} for r in cursor.fetchall()]
    conn.close(); return rows

def carregar_projeto(projeto_id):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM projetos WHERE id = {P}", (projeto_id,))
    proj = cursor.fetchone()
    if not proj: conn.close(); return None
    col_names = [d[0] for d in cursor.description]
    proj_dict = dict(zip(col_names, proj))
    try:
        extra = json.loads(proj_dict.pop('campos_extras', '{}'))
        if isinstance(extra, dict): proj_dict.update(extra)
    except (json.JSONDecodeError, TypeError): pass
    try:
        resultados_raw = proj_dict.pop('resultados', '{}')
        proj_dict['resultados'] = json.loads(resultados_raw) if isinstance(resultados_raw, str) and resultados_raw else {}
    except (json.JSONDecodeError, TypeError): proj_dict['resultados'] = {}
    cursor.execute(f"SELECT descricao, cv, quantidade FROM motores_projeto WHERE projeto_id = {P}", (projeto_id,))
    motores = [{'descricao': r[0], 'cv': r[1], 'qtd': r[2]} for r in cursor.fetchall()]
    cursor.execute(f"SELECT descricao, potencia, quantidade FROM outras_cargas_projeto WHERE projeto_id = {P} AND tipo = 'apt'", (projeto_id,))
    outras_apt = [{'descricao': r[0], 'potencia': r[1], 'quantidade': r[2]} for r in cursor.fetchall()]
    cursor.execute(f"SELECT descricao, potencia, quantidade FROM outras_cargas_projeto WHERE projeto_id = {P} AND tipo = 'adm'", (projeto_id,))
    outras_adm = [{'descricao': r[0], 'potencia': r[1], 'quantidade': r[2]} for r in cursor.fetchall()]
    cursor.execute(f"SELECT descricao, potencia_w, quantidade, btu, tipo_equipamento, incluir FROM ac_projeto WHERE projeto_id = {P} AND tipo = 'apt' ORDER BY id", (projeto_id,))
    ac_apt = [{'descricao': r[0], 'potencia': r[1], 'quantidade': r[2], 'btu': r[3], 'tipo_equipamento': r[4], 'incluir': r[5]} for r in cursor.fetchall()]
    cursor.execute(f"SELECT descricao, potencia_w, quantidade, btu, tipo_equipamento, incluir FROM ac_projeto WHERE projeto_id = {P} AND tipo = 'adm' ORDER BY id", (projeto_id,))
    ac_adm = [{'descricao': r[0], 'potencia': r[1], 'quantidade': r[2], 'btu': r[3], 'tipo_equipamento': r[4], 'incluir': r[5]} for r in cursor.fetchall()]
    conn.close()
    proj_dict['motores'] = motores; proj_dict['outras_cargas_apt'] = outras_apt; proj_dict['outras_cargas_adm'] = outras_adm; proj_dict['ac_apt'] = ac_apt; proj_dict['ac_adm'] = ac_adm
    return proj_dict

def salvar_projeto(projeto_id, dados):
    conn = get_conn(); cursor = conn.cursor()
    cols = ('nome', 'aptos', 'area_apto', 'area_adm', 'iluminacao', 'tomadas', 'chuveiro_kw', 'torneira_kw', 'chuveiros_apto', 'torneiras_apto', 'chuveiros_adm', 'torneiras_adm', 'secar_kw', 'secar_apto', 'lavar_kw', 'lavar_apto', 'tipo')
    extra_keys = ('ramal_corrente','ramal_isolacao','ramal_material','ramal_tensao','ramal_metodo','ramal_condutores','ramal_subtipo','ramal_forma_agrup','ramal_num_circuitos','ramal_tipo_temp','ramal_temperatura','ramal_comprimento','ramal_paralelo_idx','ramal_par_chk_neutro_0','ramal_par_chk_neutro_1','ramal_par_chk_neutro_2','ramal_par_chk_protecao_0','ramal_par_chk_protecao_1','ramal_par_chk_protecao_2','ramal_par_chk_tabela48_0','ramal_par_chk_tabela48_1','ramal_par_chk_tabela48_2','ramal_tipo_eletroduto','ramal_lig_dg','ramal_lig_tensao','ramal_lig_comprimento','qm_aptos','qm_adm','qm_material','qm_adm_tc','qm_dg','dps_spda','dps_ramal_aereo','dps_material','dps_qtd_qms','aterr_solo','aterr_multiblocos','aterr_qtd_qms','aterr_num_hastes','aterr_haste','aterr_comprimento','aterr_conexao')
    campos_extras = {k: dados.get(k) for k in extra_keys if k in dados}
    resultados = dados.get('resultados', {})
    vals = tuple(dados.get(c, 0) for c in cols)
    if projeto_id:
        set_clause = ','.join(f"{c}={P}" for c in cols)
        cursor.execute(f"UPDATE projetos SET {set_clause}, campos_extras={P}, resultados={P} WHERE id={P}", vals + (json.dumps(campos_extras), json.dumps(resultados), projeto_id))
    else:
        placeholders = ','.join(P for _ in cols)
        cursor.execute(f"INSERT INTO projetos ({','.join(cols)}, campos_extras, resultados) VALUES ({placeholders},{P},{P})", vals + (json.dumps(campos_extras), json.dumps(resultados)))
        if USING_PG:
            cursor.execute("SELECT LASTVAL()")
            projeto_id = cursor.fetchone()[0]
        else:
            projeto_id = cursor.lastrowid
    cursor.execute(f"DELETE FROM motores_projeto WHERE projeto_id = {P}", (projeto_id,))
    for m in dados.get('motores', []):
        desc = m.get('desc', m.get('descricao', ''))
        cursor.execute(f"INSERT INTO motores_projeto (projeto_id, descricao, cv, quantidade) VALUES ({P}, {P}, {P}, {P})", (projeto_id, desc, float(m['cv']), int(m['qtd'])))
    cursor.execute(f"DELETE FROM outras_cargas_projeto WHERE projeto_id = {P}", (projeto_id,))
    for c in dados.get('outras_cargas_apt', []):
        cursor.execute(f"INSERT INTO outras_cargas_projeto (projeto_id, tipo, descricao, potencia, quantidade) VALUES ({P}, 'apt', {P}, {P}, {P})", (projeto_id, c[0] if isinstance(c, list) else c['descricao'], float(c[1] if isinstance(c, list) else c['potencia']), int(c[2] if isinstance(c, list) else c['quantidade'])))
    for c in dados.get('outras_cargas_adm', []):
        cursor.execute(f"INSERT INTO outras_cargas_projeto (projeto_id, tipo, descricao, potencia, quantidade) VALUES ({P}, 'adm', {P}, {P}, {P})", (projeto_id, c[0] if isinstance(c, list) else c['descricao'], float(c[1] if isinstance(c, list) else c['potencia']), int(c[2] if isinstance(c, list) else c['quantidade'])))
    cursor.execute(f"DELETE FROM ac_projeto WHERE projeto_id = {P}", (projeto_id,))
    for ac in dados.get('ac_apt', []):
        desc = ac.get('descricao', ac.get('desc', '')); pot = float(ac.get('potencia', ac.get('pot', 0))); qtd = int(ac.get('quantidade', ac.get('qtd', 1))); btu = int(ac.get('btu', 0)); tipo_eq = ac.get('tipo_equipamento', ''); incluir = 1 if ac.get('incluir', 1) else 0
        cursor.execute(f"INSERT INTO ac_projeto (projeto_id, tipo, descricao, potencia_w, quantidade, btu, tipo_equipamento, incluir) VALUES ({P}, 'apt', {P}, {P}, {P}, {P}, {P}, {P})", (projeto_id, desc, pot, qtd, btu, tipo_eq, incluir))
    for ac in dados.get('ac_adm', []):
        desc = ac.get('descricao', ac.get('desc', '')); pot = float(ac.get('potencia', ac.get('pot', 0))); qtd = int(ac.get('quantidade', ac.get('qtd', 1))); btu = int(ac.get('btu', 0)); tipo_eq = ac.get('tipo_equipamento', ''); incluir = 1 if ac.get('incluir', 1) else 0
        cursor.execute(f"INSERT INTO ac_projeto (projeto_id, tipo, descricao, potencia_w, quantidade, btu, tipo_equipamento, incluir) VALUES ({P}, 'adm', {P}, {P}, {P}, {P}, {P}, {P})", (projeto_id, desc, pot, qtd, btu, tipo_eq, incluir))
    conn.commit(); conn.close(); return projeto_id

def excluir_projeto(projeto_id):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"DELETE FROM motores_projeto WHERE projeto_id = {P}", (projeto_id,))
    cursor.execute(f"DELETE FROM outras_cargas_projeto WHERE projeto_id = {P}", (projeto_id,))
    cursor.execute(f"DELETE FROM ac_projeto WHERE projeto_id = {P}", (projeto_id,))
    cursor.execute(f"DELETE FROM projetos WHERE id = {P}", (projeto_id,))
    conn.commit(); conn.close()

init_db()
if USING_PG:
    import sqlite3
    conn = get_conn()
    db_helper.migrate_ged119(conn)
    conn.close()
