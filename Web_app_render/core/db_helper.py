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
