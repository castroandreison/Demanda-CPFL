import os
import sqlite3

USING_PG = False
PLACEHOLDER = '?'

_dir = os.path.dirname(os.path.abspath(__file__))
_db_path = os.path.join(_dir, '..', '..', 'GED119', 'Projeto TK', 'projetos_ged119.db')
_db_path13 = os.path.join(_dir, '..', '..', 'Ged13', 'Projeto TK', 'projetos_ged13.db')

def connect_projetos():
    conn = sqlite3.connect(os.path.normpath(_db_path))
    conn.row_factory = sqlite3.Row
    return conn

def connect_projetos_ged13():
    conn = sqlite3.connect(os.path.normpath(_db_path13))
    conn.row_factory = sqlite3.Row
    return conn

_db_path2855 = os.path.join(_dir, '..', '..', 'Ged2855', 'Projeto TK', 'projetos_ged2855.db')

def connect_projetos_ged2855():
    conn = sqlite3.connect(os.path.normpath(_db_path2855))
    conn.row_factory = sqlite3.Row
    return conn
