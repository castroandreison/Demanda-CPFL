import os
from datetime import datetime

from . import db_helper

USING_PG = db_helper.USING_PG
P = db_helper.PLACEHOLDER

def get_conn():
    return db_helper.connect_projetos_ged13()

def init_db():
    conn = get_conn(); cursor = conn.cursor()
    if USING_PG:
        cursor.execute("""CREATE TABLE IF NOT EXISTS projetos_ged13 (id SERIAL PRIMARY KEY, nome TEXT UNIQUE, unidade TEXT DEFAULT '', m2 DOUBLE PRECISION DEFAULT 0, tipo TEXT DEFAULT 'Residencial', tensao TEXT DEFAULT '127/220V', data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS itens_projeto_ged13 (id SERIAL PRIMARY KEY, projeto_id INTEGER REFERENCES projetos_ged13(id) ON DELETE CASCADE, nome TEXT, potencia DOUBLE PRECISION, tipo INTEGER, quantidade INTEGER DEFAULT 1, cv DOUBLE PRECISION DEFAULT 0, btu INTEGER DEFAULT 0, fp DOUBLE PRECISION DEFAULT 1.0)""")
    else:
        cursor.execute("""CREATE TABLE IF NOT EXISTS projetos_ged13 (id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT UNIQUE, unidade TEXT DEFAULT '', m2 REAL DEFAULT 0, tipo TEXT DEFAULT 'Residencial', tensao TEXT DEFAULT '127/220V', data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS itens_projeto_ged13 (id INTEGER PRIMARY KEY AUTOINCREMENT, projeto_id INTEGER, nome TEXT, potencia REAL, tipo INTEGER, quantidade INTEGER DEFAULT 1, cv REAL DEFAULT 0, btu INTEGER DEFAULT 0, fp REAL DEFAULT 1.0, FOREIGN KEY (projeto_id) REFERENCES projetos_ged13(id) ON DELETE CASCADE)""")
        for col in ("unidade","m2","tipo","tensao"):
            try: cursor.execute(f"ALTER TABLE projetos_ged13 ADD COLUMN {col} TEXT DEFAULT ''")
            except: pass
        for col in ("cv","btu","fp"):
            try: cursor.execute(f"ALTER TABLE itens_projeto_ged13 ADD COLUMN {col} REAL DEFAULT 0")
            except: pass
    conn.commit(); conn.close()

def listar_projetos():
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute("SELECT id, nome, unidade, m2, tipo, tensao, data_criacao FROM projetos_ged13 ORDER BY data_criacao DESC")
    rows = []
    for r in cursor.fetchall():
        dt = r[6].isoformat() if USING_PG and hasattr(r[6], 'isoformat') else r[6]
        rows.append({'id': r[0], 'nome': r[1], 'unidade': r[2], 'm2': r[3], 'tipo': r[4], 'tensao': r[5], 'data_criacao': dt})
    conn.close(); return rows

def carregar_projeto(projeto_id):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM projetos_ged13 WHERE id = {P}", (projeto_id,))
    proj = cursor.fetchone()
    if not proj: conn.close(); return None
    proj_dict = dict(proj)
    cursor.execute(f"SELECT nome, potencia, tipo, quantidade, cv, btu, fp FROM itens_projeto_ged13 WHERE projeto_id = {P} ORDER BY tipo, id", (projeto_id,))
    itens = [{'nome': r[0], 'potencia': r[1], 'tipo': r[2], 'quantidade': r[3], 'cv': r[4], 'btu': r[5], 'fp': r[6]} for r in cursor.fetchall()]
    conn.close(); proj_dict['cargas'] = itens; return proj_dict

def salvar_projeto(projeto_id, dados):
    conn = get_conn(); cursor = conn.cursor()
    unidade = dados.get('unidade', ''); m2 = float(dados.get('m2', 0)); tipo = dados.get('tipo', 'Residencial'); tensao = dados.get('tensao', '127/220V')
    if projeto_id:
        cursor.execute(f"UPDATE projetos_ged13 SET nome = {P}, unidade = {P}, m2 = {P}, tipo = {P}, tensao = {P} WHERE id = {P}", (dados['nome'], unidade, m2, tipo, tensao, projeto_id))
    else:
        cursor.execute(f"INSERT INTO projetos_ged13 (nome, unidade, m2, tipo, tensao) VALUES ({P}, {P}, {P}, {P}, {P})", (dados['nome'], unidade, m2, tipo, tensao))
        if USING_PG:
            cursor.execute("SELECT LASTVAL()")
            projeto_id = cursor.fetchone()[0]
        else:
            projeto_id = cursor.lastrowid
    cursor.execute(f"DELETE FROM itens_projeto_ged13 WHERE projeto_id = {P}", (projeto_id,))
    for item in dados.get('cargas', []):
        cursor.execute(f"INSERT INTO itens_projeto_ged13 (projeto_id, nome, potencia, tipo, quantidade, cv, btu, fp) VALUES ({P}, {P}, {P}, {P}, {P}, {P}, {P}, {P})", (projeto_id, item.get('nome',''), float(item.get('potencia',0)), int(item.get('tipo',0)), int(item.get('quantidade',1)), float(item.get('cv',0)), int(item.get('btu',0)), float(item.get('fp',1.0))))
    conn.commit(); conn.close(); return projeto_id

def excluir_projeto(projeto_id):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"DELETE FROM itens_projeto_ged13 WHERE projeto_id = {P}", (projeto_id,))
    cursor.execute(f"DELETE FROM projetos_ged13 WHERE id = {P}", (projeto_id,))
    conn.commit(); conn.close()

init_db()
