import sqlite3
import os
from datetime import datetime

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, '..', '..', 'Ged13', 'Projeto TK', 'projetos_ged13.db')
_db_path = os.path.normpath(_db_path)

def get_conn():
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projetos_ged13 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE,
            unidade TEXT DEFAULT '',
            m2 REAL DEFAULT 0,
            tipo TEXT DEFAULT 'Residencial',
            tensao TEXT DEFAULT '127/220V',
            data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migrate existing tables
    try:
        cursor.execute("ALTER TABLE projetos_ged13 ADD COLUMN unidade TEXT DEFAULT ''")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE projetos_ged13 ADD COLUMN m2 REAL DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE projetos_ged13 ADD COLUMN tipo TEXT DEFAULT 'Residencial'")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE projetos_ged13 ADD COLUMN tensao TEXT DEFAULT '127/220V'")
    except:
        pass
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS itens_projeto_ged13 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            nome TEXT,
            potencia REAL,
            tipo INTEGER,
            quantidade INTEGER DEFAULT 1,
            cv REAL DEFAULT 0,
            btu INTEGER DEFAULT 0,
            fp REAL DEFAULT 1.0,
            FOREIGN KEY (projeto_id) REFERENCES projetos_ged13(id) ON DELETE CASCADE
        )
    """)
    # Migrate existing tables
    try:
        cursor.execute("ALTER TABLE itens_projeto_ged13 ADD COLUMN cv REAL DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE itens_projeto_ged13 ADD COLUMN btu INTEGER DEFAULT 0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE itens_projeto_ged13 ADD COLUMN fp REAL DEFAULT 1.0")
    except:
        pass
    try:
        cursor.execute("ALTER TABLE projetos_ged13 ADD COLUMN usuario_id INTEGER")
    except:
        pass
    conn.commit()
    conn.close()

def listar_projetos(usuario_id=None):
    conn = get_conn()
    cursor = conn.cursor()
    if usuario_id:
        cursor.execute("SELECT id, nome, unidade, m2, tipo, tensao, data_criacao FROM projetos_ged13 WHERE usuario_id = ? OR nome LIKE '%Exemplo%' ORDER BY data_criacao DESC", (usuario_id,))
    else:
        cursor.execute("SELECT id, nome, unidade, m2, tipo, tensao, data_criacao FROM projetos_ged13 ORDER BY data_criacao DESC")
    rows = [{'id': r[0], 'nome': r[1], 'unidade': r[2], 'm2': r[3], 'tipo': r[4], 'tensao': r[5], 'data_criacao': r[6]} for r in cursor.fetchall()]
    conn.close()
    return rows

def carregar_projeto(projeto_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM projetos_ged13 WHERE id = ?", (projeto_id,))
    proj = cursor.fetchone()
    if not proj:
        conn.close()
        return None
    proj_dict = dict(proj)
    cursor.execute("SELECT nome, potencia, tipo, quantidade, cv, btu, fp FROM itens_projeto_ged13 WHERE projeto_id = ? ORDER BY tipo, id", (projeto_id,))
    itens = [{'nome': r[0], 'potencia': r[1], 'tipo': r[2], 'quantidade': r[3], 'cv': r[4], 'btu': r[5], 'fp': r[6]} for r in cursor.fetchall()]
    conn.close()
    proj_dict['cargas'] = itens
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
    unidade = dados.get('unidade', '')
    m2 = _n(dados.get('m2'))
    tipo = dados.get('tipo', 'Residencial')
    tensao = dados.get('tensao', '127/220V')
    if projeto_id:
        cursor.execute("UPDATE projetos_ged13 SET nome = ?, unidade = ?, m2 = ?, tipo = ?, tensao = ? WHERE id = ?", (dados['nome'], unidade, m2, tipo, tensao, projeto_id))
    else:
        cursor.execute("INSERT INTO projetos_ged13 (nome, unidade, m2, tipo, tensao, usuario_id) VALUES (?, ?, ?, ?, ?, ?)", (dados['nome'], unidade, m2, tipo, tensao, usuario_id))
        projeto_id = cursor.lastrowid
    cursor.execute("DELETE FROM itens_projeto_ged13 WHERE projeto_id = ?", (projeto_id,))
    for item in dados.get('cargas', []):
        nome = item.get('nome', '')
        potencia = _n(item.get('potencia'))
        tipoi = _i(item.get('tipo'))
        quantidade = _i(item.get('quantidade'), 1)
        cv = _n(item.get('cv'))
        btu = _i(item.get('btu'))
        fp = _n(item.get('fp'), 1.0)
        cursor.execute("INSERT INTO itens_projeto_ged13 (projeto_id, nome, potencia, tipo, quantidade, cv, btu, fp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                       (projeto_id, nome, potencia, tipoi, quantidade, cv, btu, fp))
    conn.commit()
    conn.close()
    return projeto_id

def excluir_projeto(projeto_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM itens_projeto_ged13 WHERE projeto_id = ?", (projeto_id,))
    cursor.execute("DELETE FROM projetos_ged13 WHERE id = ?", (projeto_id,))
    conn.commit()
    conn.close()

init_db()
