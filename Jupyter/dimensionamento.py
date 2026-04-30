import sqlite3

# banco da GED119
banco_norma = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"

def selecionar_transformador(demanda):
    
    conn = sqlite3.connect(banco_norma)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT transformador_kva
        FROM TABELA_10
        WHERE ? BETWEEN demanda_min AND demanda_max
    """, (demanda,))

    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return resultado[0]

    return "Medição em média tensão"