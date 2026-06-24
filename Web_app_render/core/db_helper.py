import os

DATABASE_URL = os.environ.get('DATABASE_URL')
USING_PG = bool(DATABASE_URL)
PLACEHOLDER = '%s' if USING_PG else '?'

if USING_PG:
    import psycopg2
    import psycopg2.extras
    def connect_projetos():
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    def connect_projetos_ged13():
        conn = psycopg2.connect(DATABASE_URL)
        return conn
else:
    import sqlite3
    _dir = os.path.dirname(os.path.abspath(__file__))
    _db_path = os.path.join(_dir, '..', 'db', 'projetos_ged119.db')
    _db_path13 = os.path.join(_dir, '..', 'db', 'projetos_ged13.db')
    def connect_projetos():
        conn = sqlite3.connect(os.path.normpath(_db_path))
        conn.row_factory = sqlite3.Row
        return conn
    def connect_projetos_ged13():
        conn = sqlite3.connect(os.path.normpath(_db_path13))
        conn.row_factory = sqlite3.Row
        return conn

def adapt(sql, params=None):
    if not USING_PG:
        return sql, params
    if params:
        psql = sql
        for k in params:
            psql = psql.replace('?', '%s', 1) if isinstance(k, (int, float, str)) else psql
    return sql, params

def migrate_ged119(pg_conn):
    import json
    P = '%s'
    sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db', 'projetos_ged119.db')
    if not os.path.exists(sqlite_path):
        return
    sq = sqlite3.connect(sqlite_path)
    sq.row_factory = sqlite3.Row
    cur = pg_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM projetos")
    if cur.fetchone()[0] > 0:
        sq.close(); return
    rows = sq.execute("SELECT * FROM projetos ORDER BY id").fetchall()
    for r in rows:
        d = dict(r)
        old_id = d.pop('id')
        d['nome'] = str(d.get('nome', '')) + ' (Migrado)'
        cols = tuple(d.keys())
        vals = [d[c] if d[c] is not None else ('' if isinstance(d[c], str) else 0) for c in cols]
        placeholders = ','.join(P for _ in cols)
        cur.execute(f"INSERT INTO projetos ({','.join(cols)}) VALUES ({placeholders}) RETURNING id", vals)
        new_id = cur.fetchone()[0]
        for tbl, fk_col in [('motores_projeto', 'projeto_id'), ('outras_cargas_projeto', 'projeto_id'), ('ac_projeto', 'projeto_id')]:
            for sr in sq.execute(f"SELECT * FROM {tbl} WHERE projeto_id = ?", (old_id,)).fetchall():
                sd = dict(sr)
                sd.pop('id', None)
                sd[fk_col] = new_id
                tcols = tuple(sd.keys())
                tv = [sd[c] if sd[c] is not None else ('' if isinstance(sd[c], str) else 0) for c in tcols]
                cur.execute(f"INSERT INTO {tbl} ({','.join(tcols)}) VALUES ({','.join(P for _ in tcols)})", tv)
    pg_conn.commit()
    sq.close()

def migrate_ged13(pg_conn):
    P = '%s'
    sqlite_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'db', 'projetos_ged13.db')
    if not os.path.exists(sqlite_path):
        return
    sq = sqlite3.connect(sqlite_path)
    sq.row_factory = sqlite3.Row
    cur = pg_conn.cursor()
    cur.execute("SELECT COUNT(*) FROM projetos_ged13")
    if cur.fetchone()[0] > 0:
        sq.close(); return
    rows = sq.execute("SELECT * FROM projetos_ged13 ORDER BY id").fetchall()
    for r in rows:
        d = dict(r)
        old_id = d.pop('id')
        d['nome'] = str(d.get('nome', '')) + ' (Migrado)'
        cols = tuple(d.keys())
        vals = [d[c] if d[c] is not None else ('' if isinstance(d[c], str) else 0) for c in cols]
        placeholders = ','.join(P for _ in cols)
        cur.execute(f"INSERT INTO projetos_ged13 ({','.join(cols)}) VALUES ({placeholders}) RETURNING id", vals)
        new_id = cur.fetchone()[0]
        for sr in sq.execute("SELECT * FROM itens_projeto_ged13 WHERE projeto_id = ?", (old_id,)).fetchall():
            sd = dict(sr)
            sd.pop('id', None)
            sd['projeto_id'] = new_id
            tcols = tuple(sd.keys())
            tv = [sd[c] if sd[c] is not None else ('' if isinstance(sd[c], str) else 0) for c in tcols]
            cur.execute(f"INSERT INTO itens_projeto_ged13 ({','.join(tcols)}) VALUES ({','.join(P for _ in tcols)})", tv)
    pg_conn.commit()
    sq.close()
