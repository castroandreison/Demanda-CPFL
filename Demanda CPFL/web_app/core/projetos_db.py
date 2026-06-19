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
    conn.commit()
    conn.close()

def listar_projetos():
    conn = get_conn()
    cursor = conn.cursor()
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

def salvar_projeto(projeto_id, dados):
    conn = get_conn()
    cursor = conn.cursor()
    cols = ('nome', 'aptos', 'area_apto', 'area_adm', 'iluminacao', 'tomadas',
            'chuveiro_kw', 'torneira_kw', 'chuveiros_apto', 'torneiras_apto',
            'chuveiros_adm', 'torneiras_adm',
            'secar_kw', 'secar_apto', 'lavar_kw', 'lavar_apto', 'tipo')
    vals = tuple(dados.get(c, 0) for c in cols)
    if projeto_id:
        sql = f"UPDATE projetos SET {'=?,'.join(cols)}=? WHERE id=?"
        cursor.execute(sql, vals + (projeto_id,))
    else:
        placeholders = ','.join('?' * len(cols))
        cursor.execute(f"INSERT INTO projetos ({','.join(cols)}) VALUES ({placeholders})", vals)
        projeto_id = cursor.lastrowid
    cursor.execute("DELETE FROM motores_projeto WHERE projeto_id = ?", (projeto_id,))
    for m in dados.get('motores', []):
        desc = m.get('desc', m.get('descricao', ''))
        cursor.execute("INSERT INTO motores_projeto (projeto_id, descricao, cv, quantidade) VALUES (?, ?, ?, ?)",
                       (projeto_id, desc, float(m['cv']), int(m['qtd'])))
    cursor.execute("DELETE FROM outras_cargas_projeto WHERE projeto_id = ?", (projeto_id,))
    for c in dados.get('outras_cargas_apt', []):
        cursor.execute("INSERT INTO outras_cargas_projeto (projeto_id, tipo, descricao, potencia, quantidade) VALUES (?, 'apt', ?, ?, ?)",
                       (projeto_id, c[0] if isinstance(c, list) else c['descricao'],
                        float(c[1] if isinstance(c, list) else c['potencia']),
                        int(c[2] if isinstance(c, list) else c['quantidade'])))
    for c in dados.get('outras_cargas_adm', []):
        cursor.execute("INSERT INTO outras_cargas_projeto (projeto_id, tipo, descricao, potencia, quantidade) VALUES (?, 'adm', ?, ?, ?)",
                       (projeto_id, c[0] if isinstance(c, list) else c['descricao'],
                        float(c[1] if isinstance(c, list) else c['potencia']),
                        int(c[2] if isinstance(c, list) else c['quantidade'])))
    cursor.execute("DELETE FROM ac_projeto WHERE projeto_id = ?", (projeto_id,))
    for ac in dados.get('ac_apt', []):
        desc = ac.get('descricao', ac.get('desc', ''))
        pot = float(ac.get('potencia', ac.get('pot', 0)))
        qtd = int(ac.get('quantidade', ac.get('qtd', 1)))
        btu = int(ac.get('btu', 0))
        tipo_eq = ac.get('tipo_equipamento', '')
        incluir = 1 if ac.get('incluir', 1) else 0
        cursor.execute("INSERT INTO ac_projeto (projeto_id, tipo, descricao, potencia_w, quantidade, btu, tipo_equipamento, incluir) VALUES (?, 'apt', ?, ?, ?, ?, ?, ?)",
                       (projeto_id, desc, pot, qtd, btu, tipo_eq, incluir))
    for ac in dados.get('ac_adm', []):
        desc = ac.get('descricao', ac.get('desc', ''))
        pot = float(ac.get('potencia', ac.get('pot', 0)))
        qtd = int(ac.get('quantidade', ac.get('qtd', 1)))
        btu = int(ac.get('btu', 0))
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
