import sqlite3

banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\projetos_ged119.db"


def conectar():
    return sqlite3.connect(banco)

# ---------------------------
# PROJETOS
# ---------------------------

def listar_projetos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM PROJETOS")
    dados = cursor.fetchall()

    conn.close()
    return dados


def adicionar_projeto(nome, cliente, endereco, area, tipo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO PROJETOS
        (nome, cliente, endereco, data_criacao, area_total, tipo_edificacao)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (nome, cliente, endereco, "2026", area, tipo))

    conn.commit()
    conn.close()


def atualizar_projeto(id_projeto, nome, cliente, endereco, area, tipo):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE PROJETOS
        SET nome=?, cliente=?, endereco=?, area_total=?, tipo_edificacao=?
        WHERE id=?
    """, (nome, cliente, endereco, area, tipo, id_projeto))

    conn.commit()
    conn.close()


def deletar_projeto(id_projeto):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM PROJETOS
        WHERE id = ?
    """, (id_projeto,))

    conn.commit()
    conn.close()


# ---------------------------
# CARGAS
# ---------------------------

def adicionar_carga(projeto_id, descricao, potencia, quantidade, categoria, tipo_carga):
    
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO CARGAS
        (projeto_id, descricao, potencia_kw, quantidade, categoria, tipo_carga)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (projeto_id, descricao, potencia, quantidade, categoria, tipo_carga))

    conn.commit()
    conn.close()

def listar_cargas_tipo(projeto_id, tipo):
    
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, descricao, potencia_kw, quantidade, categoria
        FROM CARGAS
        WHERE projeto_id=? AND tipo_carga=?
    """, (projeto_id, tipo))

    dados = cursor.fetchall()

    conn.close()

    return dados


def atualizar_carga(id_carga, descricao, potencia, quantidade, categoria):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE CARGAS
        SET descricao=?, potencia_kw=?, quantidade=?, categoria=?
        WHERE id=?
    """, (descricao, potencia, quantidade, categoria, id_carga))

    conn.commit()
    conn.close()


def deletar_carga(id_carga):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM CARGAS
        WHERE id = ?
    """, (id_carga,))

    conn.commit()
    conn.close()


# ---------------------------
# CÁLCULOS
# ---------------------------

def calcular_carga_instalada(projeto_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT potencia_kw, quantidade
        FROM CARGAS
        WHERE projeto_id=?
    """, (projeto_id,))

    dados = cursor.fetchall()
    conn.close()

    total = 0
    for p, q in dados:
        try:
            total += float(p) * float(q)
        except:
            continue

    return total


def calcular_demanda(projeto_id):
    carga = calcular_carga_instalada(projeto_id)

    if carga <= 25:
        return carga

    return carga * 0.7


# ---------------------------
# EDIFÍCIO
# ---------------------------

def criar_tabela_edificio():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS EDIFICIO (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            projeto_id INTEGER,
            area_administracao REAL,
            area_apartamento REAL,
            quantidade_apartamentos INTEGER
        )
    """)

    conn.commit()
    conn.close()


def salvar_edificio(projeto_id, adm, apto, qtd):
    
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO EDIFICIO
        (projeto_id, area_administracao, area_apartamento, quantidade_apartamentos)
        VALUES (?, ?, ?, ?)
    """, (projeto_id, adm, apto, qtd))

    conn.commit()
    conn.close()


def carregar_edificio(projeto_id):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT area_administracao, area_apartamento, quantidade_apartamentos
        FROM EDIFICIO
        WHERE projeto_id=?
    """, (projeto_id,))

    dado = cursor.fetchone()
    conn.close()

    return dado