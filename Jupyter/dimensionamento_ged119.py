import sqlite3
import math

# banco da norma GED119
banco_norma = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"

# tensão padrão rede CPFL
TENSÃO = 220


# --------------------------------
# CALCULAR CORRENTE
# --------------------------------

def calcular_corrente(demanda_kw):

    corrente = (demanda_kw * 1000) / (math.sqrt(3) * TENSÃO)

    return corrente


# --------------------------------
# TRANSFORMADOR
# --------------------------------

import sqlite3

def selecionar_transformador(demanda):

    banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"

    conn = sqlite3.connect(banco)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT transformador_kva
    FROM TABELA_10
    WHERE ? BETWEEN demanda_min AND demanda_max
    """,(demanda,))

    resultado = cursor.fetchone()

    conn.close()

    if resultado:
        return resultado[0]
    else:
        return "Medição em média tensão"
# --------------------------------
# DISJUNTOR GERAL
# --------------------------------

def selecionar_disjuntor(corrente):

    disjuntores = [
        40,50,63,80,100,125,160,
        200,250,315,400,500,630,800,1000
    ]

    for d in disjuntores:

        if corrente <= d:
            return d

    return "Acima de 1000 A"


# --------------------------------
# BARRAMENTO
# --------------------------------

def selecionar_barramento(corrente):

    barramentos = [
        (100,"20x3 mm"),
        (200,"25x5 mm"),
        (400,"40x5 mm"),
        (600,"50x5 mm"),
        (800,"80x5 mm"),
        (1000,"100x5 mm")
    ]

    for limite,barra in barramentos:

        if corrente <= limite:
            return barra

    return "Especial"


# --------------------------------
# CONDUTOR
# --------------------------------

def selecionar_condutor(corrente):

    condutores = [
        (50,"16 mm²"),
        (70,"25 mm²"),
        (100,"35 mm²"),
        (140,"50 mm²"),
        (180,"70 mm²"),
        (240,"95 mm²"),
        (300,"120 mm²"),
        (400,"150 mm²"),
        (500,"185 mm²"),
        (630,"240 mm²"),
    ]

    for limite,cond in condutores:

        if corrente <= limite:
            return cond

    return "Acima de 240 mm²"


# --------------------------------
# FUSÍVEL
# --------------------------------

def selecionar_fusivel(corrente):

    fusivel = selecionar_disjuntor(corrente)

    return fusivel


# --------------------------------
# POSTE
# --------------------------------

def selecionar_poste(transformador):

    if transformador <= 75:
        return "Poste DT 9/300"

    if transformador <= 150:
        return "Poste DT 10/600"

    if transformador <= 300:
        return "Poste DT 11/1000"

    return "Poste especial"


# --------------------------------
# CURTO CIRCUITO
# --------------------------------

def calcular_curto(transformador_kva):

    Z = 4

    corrente = (transformador_kva * 1000) / (math.sqrt(3) * TENSÃO)

    curto = corrente / (Z/100)

    return round(curto/1000,2)


# --------------------------------
# DIMENSIONAMENTO COMPLETO
# --------------------------------

def dimensionar_rede(demanda):

    corrente = calcular_corrente(demanda)

    trafo = selecionar_transformador(demanda)

    disjuntor = selecionar_disjuntor(corrente)

    barramento = selecionar_barramento(corrente)

    condutor = selecionar_condutor(corrente)

    fusivel = selecionar_fusivel(corrente)

    poste = selecionar_poste(trafo)

    curto = calcular_curto(trafo)

    return {
        "demanda":demanda,
        "corrente":round(corrente,2),
        "transformador":trafo,
        "disjuntor":disjuntor,
        "barramento":barramento,
        "condutor":condutor,
        "fusivel":fusivel,
        "poste":poste,
        "curto_kA":curto
    }