import os, json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from . import db_helper

USING_PG = db_helper.USING_PG
P = db_helper.PLACEHOLDER

def get_conn():
    return db_helper.connect_projetos()

def init_db():
    conn = get_conn(); cursor = conn.cursor()
    if USING_PG:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nome_completo TEXT NOT NULL DEFAULT '',
                cidade TEXT NOT NULL DEFAULT '',
                concessionaria TEXT NOT NULL DEFAULT '',
                contato TEXT DEFAULT '',
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_log (
                id SERIAL PRIMARY KEY,
                usuario_id INTEGER REFERENCES usuarios(id) ON DELETE CASCADE,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logout_time TIMESTAMP,
                ip_address TEXT DEFAULT '',
                user_agent TEXT DEFAULT ''
            )
        """)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nome_completo TEXT NOT NULL DEFAULT '',
                cidade TEXT NOT NULL DEFAULT '',
                concessionaria TEXT NOT NULL DEFAULT '',
                contato TEXT DEFAULT '',
                is_admin INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS login_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER,
                login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                logout_time DATETIME,
                ip_address TEXT DEFAULT '',
                user_agent TEXT DEFAULT '',
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
            )
        """)
    conn.commit(); conn.close()

def seed_admin():
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM usuarios WHERE username = {P}", ('Andreison',))
    if not cursor.fetchone():
        h = generate_password_hash('K60gyui')
        cursor.execute(f"INSERT INTO usuarios (username, password_hash, nome_completo, cidade, concessionaria, is_admin) VALUES ({P},{P},{P},{P},{P},1)", ('Andreison', h, 'Andreison', '', 'CPFL'))
        conn.commit()
    conn.close()

def registrar_usuario(username, password, nome_completo, cidade, concessionaria, contato=''):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"SELECT id FROM usuarios WHERE username = {P}", (username,))
    if cursor.fetchone():
        conn.close(); return None, 'Username ja existe'
    h = generate_password_hash(password)
    cursor.execute(f"INSERT INTO usuarios (username, password_hash, nome_completo, cidade, concessionaria, contato) VALUES ({P},{P},{P},{P},{P},{P})", (username, h, nome_completo, cidade, concessionaria, contato))
    conn.commit()
    uid = cursor.lastrowid if not USING_PG else None
    if USING_PG:
        cursor.execute("SELECT LASTVAL()")
        uid = cursor.fetchone()[0]
    conn.close()
    return {'id': uid, 'username': username, 'nome_completo': nome_completo, 'cidade': cidade, 'concessionaria': concessionaria, 'contato': contato, 'is_admin': 0}, None

def autenticar(username, password):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM usuarios WHERE username = {P}", (username,))
    row = cursor.fetchone()
    conn.close()
    if not row: return None, 'Usuario nao encontrado'
    u = dict(row)
    if not check_password_hash(u['password_hash'], password):
        return None, 'Senha incorreta'
    return {'id': u['id'], 'username': u['username'], 'nome_completo': u['nome_completo'], 'cidade': u['cidade'], 'concessionaria': u['concessionaria'], 'contato': u.get('contato', ''), 'is_admin': u['is_admin']}, None

def registrar_login(usuario_id, ip_address='', user_agent=''):
    conn = get_conn(); cursor = conn.cursor()
    cursor.execute(f"INSERT INTO login_log (usuario_id, ip_address, user_agent) VALUES ({P},{P},{P})", (usuario_id, ip_address, user_agent))
    conn.commit()
    log_id = cursor.lastrowid if not USING_PG else None
    if USING_PG:
        cursor.execute("SELECT LASTVAL()")
        log_id = cursor.fetchone()[0]
    conn.close()
    return log_id

def registrar_logout(log_id):
    if not log_id: return
    conn = get_conn(); cursor = conn.cursor()
    if USING_PG:
        cursor.execute(f"UPDATE login_log SET logout_time = NOW() WHERE id = {P}", (log_id,))
    else:
        cursor.execute(f"UPDATE login_log SET logout_time = CURRENT_TIMESTAMP WHERE id = {P}", (log_id,))
    conn.commit(); conn.close()

def listar_usuarios_com_estatisticas():
    conn = get_conn(); cursor = conn.cursor()
    if USING_PG:
        cursor.execute("""
            SELECT u.id, u.username, u.nome_completo, u.cidade, u.concessionaria, u.contato, u.is_admin, u.created_at,
                (SELECT COUNT(*) FROM projetos WHERE usuario_id = u.id) as qtd_ged119,
                (SELECT COUNT(*) FROM projetos_ged13 WHERE usuario_id = u.id) as qtd_ged13,
                (SELECT MAX(login_time) FROM login_log WHERE usuario_id = u.id) as ultimo_login,
                (SELECT COALESCE(SUM(EXTRACT(EPOCH FROM (COALESCE(logout_time, NOW()) - login_time))), 0) FROM login_log WHERE usuario_id = u.id) as tempo_total_seg
            FROM usuarios u ORDER BY u.created_at DESC
        """)
        rows = cursor.fetchall(); conn.close()
        result = []
        for r in rows:
            d = dict(r)
            d['ultimo_login'] = d['ultimo_login'].isoformat() if d['ultimo_login'] and hasattr(d['ultimo_login'], 'isoformat') else d['ultimo_login']
            d['created_at'] = d['created_at'].isoformat() if d['created_at'] and hasattr(d['created_at'], 'isoformat') else d['created_at']
            result.append(d)
        return result
    else:
        cursor.execute("""SELECT u.id, u.username, u.nome_completo, u.cidade, u.concessionaria, u.contato, u.is_admin, u.created_at,
                (SELECT MAX(login_time) FROM login_log WHERE usuario_id = u.id) as ultimo_login,
                (SELECT COALESCE(SUM(CAST((julianday(COALESCE(logout_time, CURRENT_TIMESTAMP)) - julianday(login_time)) * 86400 AS INTEGER)), 0) FROM login_log WHERE usuario_id = u.id) as tempo_total_seg
            FROM usuarios u ORDER BY u.created_at DESC""")
        usuarios = [dict(r) for r in cursor.fetchall()]; conn.close()
        import sqlite3
        _dir = os.path.dirname(os.path.abspath(__file__))
        g119_path = os.path.join(_dir, '..', '..', 'GED119', 'Projeto TK', 'projetos_ged119.db')
        g13_path = os.path.join(_dir, '..', '..', 'Ged13', 'Projeto TK', 'projetos_ged13.db')
        for u in usuarios:
            u['qtd_ged119'] = 0; u['qtd_ged13'] = 0
            try:
                c = sqlite3.connect(os.path.normpath(g119_path))
                u['qtd_ged119'] = c.execute("SELECT COUNT(*) FROM projetos WHERE usuario_id = ?", (u['id'],)).fetchone()[0]
                c.close()
            except: pass
            try:
                c = sqlite3.connect(os.path.normpath(g13_path))
                u['qtd_ged13'] = c.execute("SELECT COUNT(*) FROM projetos_ged13 WHERE usuario_id = ?", (u['id'],)).fetchone()[0]
                c.close()
            except: pass
        return usuarios

init_db()
seed_admin()
