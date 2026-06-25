import os
from datetime import datetime
from . import db_helper

USING_PG = db_helper.USING_PG
P = db_helper.PLACEHOLDER

def get_conn():
    if USING_PG:
        return db_helper.connect_projetos()
    import sqlite3
    _dir = os.path.dirname(os.path.abspath(__file__))
    _db_path = os.path.normpath(os.path.join(_dir, '..', '..', 'Ged2855', 'Projeto TK', 'projetos_ged2855.db'))
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn(); cursor = conn.cursor()
    if USING_PG:
        cursor.execute("""CREATE TABLE IF NOT EXISTS projetos_ged2855 (id SERIAL PRIMARY KEY, nome TEXT UNIQUE, unidade TEXT DEFAULT '', tipo TEXT DEFAULT 'Comercial', tensao TEXT DEFAULT '220/380V', ramo TEXT DEFAULT 'Transformacao', fator_demanda DOUBLE PRECISION DEFAULT 0.35, fp_desejado DOUBLE PRECISION DEFAULT 0.92, data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP, usuario_id INTEGER)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS itens_projeto_ged2855 (id SERIAL PRIMARY KEY, projeto_id INTEGER REFERENCES projetos_ged2855(id) ON DELETE CASCADE, nome TEXT, potencia DOUBLE PRECISION DEFAULT 0, tipo INTEGER DEFAULT 0, quantidade INTEGER DEFAULT 1, cv DOUBLE PRECISION DEFAULT 0, fp DOUBLE PRECISION DEFAULT 1.0)""")
        try: cursor.execute("ALTER TABLE projetos_ged2855 ADD COLUMN usuario_id INTEGER")
        except: pass
        try: cursor.execute("ALTER TABLE projetos_ged2855 ADD COLUMN ramo TEXT DEFAULT 'Transformacao'")
        except: pass
        try: cursor.execute("ALTER TABLE projetos_ged2855 ADD COLUMN fator_demanda DOUBLE PRECISION DEFAULT 0.35")
        except: pass
    else:
        cursor.execute("""CREATE TABLE IF NOT EXISTS projetos_ged2855 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE, unidade TEXT DEFAULT '', tipo TEXT DEFAULT 'Comercial', tensao TEXT DEFAULT '220/380V', ramo TEXT DEFAULT 'Transformacao', fator_demanda REAL DEFAULT 0.35, fp_desejado REAL DEFAULT 0.92, data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP, usuario_id INTEGER)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS itens_projeto_ged2855 (id INTEGER PRIMARY KEY AUTOINCREMENT, projeto_id INTEGER, nome TEXT, potencia REAL DEFAULT 0, tipo INTEGER DEFAULT 0, quantidade INTEGER DEFAULT 1, cv REAL DEFAULT 0, fp REAL DEFAULT 1.0, FOREIGN KEY (projeto_id) REFERENCES projetos_ged2855(id) ON DELETE CASCADE)""")
        try: cursor.execute("ALTER TABLE projetos_ged2855 ADD COLUMN usuario_id INTEGER")
        except: pass
        try: cursor.execute("ALTER TABLE projetos_ged2855 ADD COLUMN ramo TEXT DEFAULT 'Transformacao'")
        except: pass
        try: cursor.execute("ALTER TABLE projetos_ged2855 ADD COLUMN fator_demanda REAL DEFAULT 0.35")
        except: pass
    conn.commit(); conn.close()

def listar_projetos(usuario_id=None):
    conn = get_conn(); cursor = conn.cursor()
    if usuario_id:
        cursor.execute(f"SELECT id, nome, unidade, tipo, tensao, data_criacao FROM projetos_ged2855 WHERE usuario_id = {P} OR nome LIKE '%Exemplo%' ORDER BY data_criacao DESC", (usuario_id,))
    else:
        cursor.execute("SELECT id, nome, unidade, tipo, tensao, data_criacao FROM projetos_ged2855 ORDER BY data_criacao DESC")
    rows = []
    for r in cursor.fetchall():
        dt = r[5].isoformat() if USING_PG and hasattr(r[5], 'isoformat') else r[5]
        rows.append({'id': r[0], 'nome': r[1], 'unidade': r[2], 'tipo': r[3], 'tensao': r[4], 'data_criacao': dt})
    conn.close(); return rows

def carregar_projeto(projeto_id):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM projetos_ged2855 WHERE id = {P}", (projeto_id,))
    proj = cursor.fetchone()
    if not proj: conn.close(); return None
    proj_dict = dict(proj)
    cursor.execute(f"SELECT nome, potencia, tipo, quantidade, cv, fp FROM itens_projeto_ged2855 WHERE projeto_id = {P} ORDER BY tipo, id", (projeto_id,))
    itens = [{'nome': r[0], 'potencia': r[1], 'tipo': r[2], 'quantidade': r[3], 'cv': r[4], 'fp': r[5]} for r in cursor.fetchall()]
    conn.close(); proj_dict['cargas'] = itens; return proj_dict

def _n(v, default=0):
    if v is None or v == '': return default
    try: return float(v)
    except: return default

def _i(v, default=0):
    if v is None or v == '': return default
    try: return int(v)
    except: return default

def salvar_projeto(projeto_id, dados, usuario_id=None):
    conn = get_conn(); cursor = conn.cursor()
    unidade = dados.get('unidade', '')
    tipo = dados.get('tipo', 'Comercial')
    tensao = dados.get('tensao', '220/380V')
    ramo = dados.get('ramo', 'Transformacao')
    fator_demanda = _n(dados.get('fator_demanda', 0.35))
    fp_desejado = _n(dados.get('fp_desejado', 0.92))
    if projeto_id:
        cursor.execute(f"UPDATE projetos_ged2855 SET nome = {P}, unidade = {P}, tipo = {P}, tensao = {P}, ramo = {P}, fator_demanda = {P}, fp_desejado = {P} WHERE id = {P}", (dados['nome'], unidade, tipo, tensao, ramo, fator_demanda, fp_desejado, projeto_id))
    else:
        cursor.execute(f"INSERT INTO projetos_ged2855 (nome, unidade, tipo, tensao, ramo, fator_demanda, fp_desejado, usuario_id) VALUES ({P}, {P}, {P}, {P}, {P}, {P}, {P}, {P})", (dados['nome'], unidade, tipo, tensao, ramo, fator_demanda, fp_desejado, usuario_id))
        if USING_PG:
            cursor.execute("SELECT LASTVAL()")
            projeto_id = cursor.fetchone()[0]
        else:
            projeto_id = cursor.lastrowid
    cursor.execute(f"DELETE FROM itens_projeto_ged2855 WHERE projeto_id = {P}", (projeto_id,))
    for item in dados.get('cargas', []):
        cursor.execute(f"INSERT INTO itens_projeto_ged2855 (projeto_id, nome, potencia, tipo, quantidade, cv, fp) VALUES ({P}, {P}, {P}, {P}, {P}, {P}, {P})", (projeto_id, item.get('nome',''), _n(item.get('potencia')), _i(item.get('tipo')), _i(item.get('quantidade'), 1), _n(item.get('cv')), _n(item.get('fp'), 1.0)))
    conn.commit(); conn.close(); return projeto_id

def excluir_projeto(projeto_id):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"DELETE FROM itens_projeto_ged2855 WHERE projeto_id = {P}", (projeto_id,))
    cursor.execute(f"DELETE FROM projetos_ged2855 WHERE id = {P}", (projeto_id,))
    conn.commit(); conn.close()

init_db()
if USING_PG:
    conn = get_conn()
    db_helper.migrate_ged2855(conn) if hasattr(db_helper, 'migrate_ged2855') else None
    conn.close()
