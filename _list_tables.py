import sqlite3, os
dir_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.normpath(os.path.join(dir_path, 'Web_app_render', 'db', 'databaseCPFLGed119.db'))
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
for t in cursor.fetchall():
    print(t[0])
conn.close()
