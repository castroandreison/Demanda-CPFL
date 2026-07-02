import sqlite3, os
dir_path = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.normpath(os.path.join(dir_path, 'Web_app_render', 'db', 'databaseCPFLGed119.db'))
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
# Check TABELA_2 structure
cursor.execute("PRAGMA table_info(TABELA_2)")
print("TABELA_2 columns:")
for r in cursor.fetchall():
    print(f"  {r}")
cursor.execute("SELECT * FROM TABELA_2")
print("\nTABELA_2 data:")
for r in cursor.fetchall():
    print(f"  {r}")
# Check TABELA_7
cursor.execute("PRAGMA table_info(TABELA_7)")
print("\nTABELA_7 columns:")
for r in cursor.fetchall():
    print(f"  {r}")
cursor.execute("SELECT * FROM TABELA_7")
print("\nTABELA_7 data:")
for r in cursor.fetchall():
    print(f"  {r}")
# Check tabela11_cabos_bt
cursor.execute("PRAGMA table_info(tabela11_cabos_bt)")
print("\ntabela11_cabos_bt columns:")
for r in cursor.fetchall():
    print(f"  {r}")
cursor.execute("SELECT secao_mm2, A, B, C, D, E, F FROM tabela11_cabos_bt LIMIT 5")
print("\ntabela11_cabos_bt data (first 5):")
for r in cursor.fetchall():
    print(f"  {r}")
# Check tabela12_barramento_bt
cursor.execute("PRAGMA table_info(tabela12_barramento_bt)")
print("\ntabela12_barramento_bt columns:")
for r in cursor.fetchall():
    print(f"  {r}")
cursor.execute("SELECT * FROM tabela12_barramento_bt")
print("\ntabela12_barramento_bt data:")
for r in cursor.fetchall():
    print(f"  {r}")
# Check tabela14 for aterramento
cursor.execute("PRAGMA table_info(tabela_14)")
print("\ntabela_14 columns:")
for r in cursor.fetchall():
    print(f"  {r}")
# Check tabela_13 for eletroduto  
cursor.execute("PRAGMA table_info(tabela_13)")
print("\ntabela_13 columns:")
for r in cursor.fetchall():
    print(f"  {r}")
# Check tabela_11 and tabela_12
cursor.execute("SELECT * FROM tabela_11 LIMIT 5")
print("\ntabela_11 data:")
for r in cursor.fetchall():
    print(f"  {r}")
cursor.execute("SELECT * FROM tabela_12 LIMIT 5")
print("\ntabela_12 data:")
for r in cursor.fetchall():
    print(f"  {r}")
# Check tabela_13 for eletroduto
cursor.execute("SELECT * FROM tabela_13 LIMIT 5")
print("\ntabela_13 data:")
for r in cursor.fetchall():
    print(f"  {r}")
conn.close()
