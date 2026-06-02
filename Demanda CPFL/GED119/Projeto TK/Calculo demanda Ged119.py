# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# -----------------------------------
# BANCO DE DADOS
# -----------------------------------

banco = r"C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\GED119\DB119\databaseCPFLGed119.db"

conn = sqlite3.connect(banco)
cursor = conn.cursor()

# -----------------------------------
# BANCO DE PROJETOS
# -----------------------------------

caminho_proj = r"C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\GED119\Projeto TK\projetos_ged119.db"

conn_proj = sqlite3.connect(caminho_proj)
cursor_proj = conn_proj.cursor()

cursor_proj.execute("""
CREATE TABLE IF NOT EXISTS projetos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT UNIQUE,
    aptos INTEGER,
    area_apto REAL,
    area_adm REAL,
    iluminacao REAL,
    tomadas REAL,
    chuveiro_kw REAL,
    torneira_kw REAL,
    chuveiros_apto INTEGER,
    torneiras_apto INTEGER,
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor_proj.execute("""
CREATE TABLE IF NOT EXISTS motores_projeto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    projeto_id INTEGER,
    cv REAL,
    quantidade INTEGER,
    FOREIGN KEY (projeto_id) REFERENCES projetos(id) ON DELETE CASCADE
)
""")

for col in ("chuveiros_adm", "torneiras_adm", "secar_kw", "lavar_kw", "secar_apto", "lavar_apto"):
    try:
        cursor_proj.execute(f"ALTER TABLE projetos ADD COLUMN {col} REAL DEFAULT 0")
    except sqlite3.OperationalError:
        pass
conn_proj.commit()

# -----------------------------------
# FUNÇÕES DO BANCO
# -----------------------------------

def normalizar_cv(cv):
    if isinstance(cv, float) and cv == int(cv):
        cv = int(cv)
    mapa = {
        "0.33": "1/3", "0.5": "1/2", "0.75": "3/4",
        "1": "1", "1.5": "1 1/2", "2": "2", "3": "3",
        "5": "5", "7.5": "7 1/2", "10": "10"
    }
    return mapa.get(str(cv), str(cv))

def cv_para_kva(cv):
    chave = normalizar_cv(cv)

    cursor.execute("""
        SELECT potencia_kva
        FROM TABELA_4
        WHERE potencia_cv_hp = ?
    """, (chave,))

    r = cursor.fetchone()
    return r[0] if r else 0


def fator_aparelho(coluna, qtd):

    cursor.execute("SELECT * FROM TABELA_2")
    linhas = cursor.fetchall()
    colunas = [d[0] for d in cursor.description]
    idx = colunas.index(coluna)

    for linha in linhas:
        faixa = linha[1]

        if " a " in faixa:
            min_v, max_v = map(int, faixa.split(" a "))
        else:
            min_v = max_v = int(faixa)

        if min_v <= qtd <= max_v:
            return linha[idx] / 100

    return 1


def fator_simultaneidade(qtd):

    cursor.execute("""
        SELECT numero_apartamentos, fator_simultaneidade
        FROM TABELA_7
    """)

    for faixa, fator in cursor.fetchall():

        if "acima" in faixa:
            min_v = int(faixa.split()[0])
            max_v = 999999
        else:
            min_v, max_v = map(int, faixa.split(" a "))

        if min_v <= qtd <= max_v:
            return fator

    return 1

# -----------------------------------
# MOTORES (LISTA DINÂMICA)
# -----------------------------------

motores = []
current_projeto_id = None
ultimo_Dg = None

def atualizar_tabela_motores():
    lista_motores.delete(*lista_motores.get_children())
    for cv, qtd in motores:
        lista_motores.insert("", "end", values=(cv, qtd))

def adicionar_motor():
    try:
        cv = float(entry_cv.get())
        qtd = int(entry_qtd_motor.get())
        if cv <= 0 or qtd <= 0:
            raise ValueError

        motores.append((cv, qtd))
        atualizar_tabela_motores()

        entry_cv.delete(0, tk.END)
        entry_qtd_motor.delete(0, tk.END)
        entry_cv.focus()

    except:
        messagebox.showerror("Erro", "CV e Quantidade devem ser números positivos!")

def excluir_motor():
    selecionado = lista_motores.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um motor para excluir!")
        return

    item = selecionado[0]
    valores = lista_motores.item(item)["values"]
    cv = valores[0]
    qtd = valores[1]

    if messagebox.askyesno("Confirmar", f"Excluir motor {cv} CV (qtd: {qtd})?"):
        idx = lista_motores.index(item)
        motores.pop(idx)
        atualizar_tabela_motores()

        entry_cv.delete(0, tk.END)
        entry_qtd_motor.delete(0, tk.END)
        entry_cv.focus()

def editar_motor():
    selecionado = lista_motores.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um motor para editar!")
        return

    item = selecionado[0]
    valores = lista_motores.item(item)["values"]
    idx = lista_motores.index(item)

    entry_cv.delete(0, tk.END)
    entry_cv.insert(0, valores[0])
    entry_qtd_motor.delete(0, tk.END)
    entry_qtd_motor.insert(0, valores[1])

    motores.pop(idx)
    atualizar_tabela_motores()

    entry_cv.focus()

def carregar_motor_selecionado(event):
    selecionado = lista_motores.selection()
    if selecionado:
        item = selecionado[0]
        valores = lista_motores.item(item)["values"]
        entry_cv.delete(0, tk.END)
        entry_cv.insert(0, valores[0])
        entry_qtd_motor.delete(0, tk.END)
        entry_qtd_motor.insert(0, valores[1])

# -----------------------------------
# CÁLCULO PRINCIPAL
# -----------------------------------

def calcular():

    def ler_valor(entry, nome, tipo):
        try:
            raw = entry.get().strip()
            if not raw:
                raise ValueError("campo vazio")
            if tipo == int:
                return int(float(raw))
            return float(raw)
        except:
            raise ValueError("{}: '{}' invalido".format(nome, raw))

    try:
        global ultimo_Dg
        aptos = ler_valor(entry_aptos, "Nº de Apartamentos", int)
        area_apto = ler_valor(entry_area_apto, "Área do Apartamento", float)
        area_adm = ler_valor(entry_area_adm, "Área Administrativa", float)
        iluminacao = ler_valor(entry_iluminacao, "Iluminação", float)
        tomadas = ler_valor(entry_tomadas, "Tomadas", float)
        chuveiro_kw = ler_valor(entry_chuveiro, "Pot. Chuveiro", float)
        torneira_kw = ler_valor(entry_torneira, "Pot. Torneira", float)
        chuveiros_apto = ler_valor(entry_qtd_chuveiros, "Chuveiros por apto", int)
        torneiras_apto = ler_valor(entry_qtd_torneiras, "Torneiras por apto", int)
        chuveiros_adm = ler_valor(entry_qtd_chuveiros_adm, "Chuveiros adm", int)
        torneiras_adm = ler_valor(entry_qtd_torneiras_adm, "Torneiras adm", int)
        secar_kw = ler_valor(entry_secar_kw, "Pot. Secar Roupa", float)
        secar_apto = ler_valor(entry_secar_apto, "Secar Roupa por apto", int)
        lavar_kw = ler_valor(entry_lavar_kw, "Pot. Lavar Louça", float)
        lavar_apto = ler_valor(entry_lavar_apto, "Lavar Louça por apto", int)

        # -------------------------
        # 1 - ILUMINAÇÃO
        # -------------------------
        w_m2 = 5

        D1a = (area_apto * aptos * w_m2) / 1000
        D1b = (area_adm * w_m2) / 1000
        D1 = D1a + D1b

        # -------------------------
        # 2 - APARELHOS
        # -------------------------
        total_chuveiros_apt = aptos * chuveiros_apto
        total_torneiras_apt = aptos * torneiras_apto
        total_aparelhos = total_chuveiros_apt + chuveiros_adm + torneiras_adm

        f_ch = fator_aparelho("chuveiro_torneira_ferro", total_aparelhos)

        apt_chuveiros = total_chuveiros_apt * chuveiro_kw * f_ch
        adm_chuveiros = chuveiros_adm * chuveiro_kw * f_ch
        adm_torneiras = torneiras_adm * torneira_kw * f_ch

        total_secar = aptos * secar_apto
        total_lavar = aptos * lavar_apto
        f_secar = fator_aparelho("maquina_secar_roupa", total_secar)
        f_lavar = fator_aparelho("maquinas_lavar_louca", total_lavar)

        D2b = total_secar * secar_kw * f_secar
        D2c = total_lavar * lavar_kw * f_lavar

        D2_apt = apt_chuveiros + D2b + D2c
        D2_adm = adm_chuveiros + adm_torneiras
        D2 = D2_apt + D2_adm

        # -------------------------
        # 3 - MOTORES
        # -------------------------
        total = 0
        maior = 0

        for cv, qtd in motores:
            kva = cv_para_kva(cv)
            total_kva = kva * qtd
            total += total_kva
            maior = max(maior, kva)

        restantes = total - maior
        D3 = (maior * 1.0) + (restantes * 0.5)

        # -------------------------
        # 4 - DEMANDA GERAL
        # -------------------------
        f_sim = fator_simultaneidade(aptos)

        Dapt = (D1a + D2_apt) * f_sim
        Dadm = D1b + D2_adm + D3

        Dg = Dapt + Dadm
        ultimo_Dg = Dg

        # -------------------------
        # RESULTADO
        # -------------------------
        txt_resultado.delete("1.0", tk.END)

        txt_resultado.insert(tk.END, "=" * 55 + "\n")
        txt_resultado.insert(tk.END, "  GED-119 - MEMORIAL DE CÁLCULO\n")
        txt_resultado.insert(tk.END, "=" * 55 + "\n\n")

        # =====================================
        # 1 - ILUMINAÇÃO
        # =====================================
        txt_resultado.insert(tk.END, "1 - ILUMINAÇÃO (Item 5.1 - GED-119)\n")
        txt_resultado.insert(tk.END, "   Fórmula: D1 = (Área x w/m²) / 1000\n\n")

        txt_resultado.insert(tk.END, "   w/m² adotado = {} W/m²\n".format(w_m2))

        txt_resultado.insert(tk.END, "   a) Apartamentos:\n")
        txt_resultado.insert(tk.END, "      D1a = ({:.0f} m² x {} aptos x {} W/m²) / 1000\n".format(area_apto, aptos, w_m2))
        txt_resultado.insert(tk.END, "      D1a = ({:.0f} x {} x {}) / 1000\n".format(area_apto, aptos, w_m2))
        txt_resultado.insert(tk.END, "      D1a = {:.1f} / 1000\n".format(area_apto * aptos * w_m2))
        txt_resultado.insert(tk.END, "      D1a = {:.2f} kVA\n".format(D1a))

        txt_resultado.insert(tk.END, "   b) Administração:\n")
        txt_resultado.insert(tk.END, "      D1b = ({:.0f} m² x {} W/m²) / 1000\n".format(area_adm, w_m2))
        txt_resultado.insert(tk.END, "      D1b = {:.0f} / 1000\n".format(area_adm * w_m2))
        txt_resultado.insert(tk.END, "      D1b = {:.2f} kVA\n".format(D1b))

        txt_resultado.insert(tk.END, "\n   D1 Total = D1a + D1b\n")
        txt_resultado.insert(tk.END, "   D1 = {:.2f} + {:.2f} = {:.2f} kVA\n\n".format(D1a, D1b, D1))

        # =====================================
        # 2 - APARELHOS
        # =====================================
        txt_resultado.insert(tk.END, "2 - APARELHOS (Item 5.2 - GED-119)\n")
        txt_resultado.insert(tk.END, "   Fórmula: D2 = Σ(Qtd x Potência x FD)\n\n")

        txt_resultado.insert(tk.END, "   a) Apartamentos:\n")
        txt_resultado.insert(tk.END, "      Chuveiros: {} aptos x {} un = {} un\n".format(aptos, chuveiros_apto, total_chuveiros_apt))
        txt_resultado.insert(tk.END, "      Torneiras: {} aptos x {} un = {} un\n".format(aptos, torneiras_apto, total_torneiras_apt))

        txt_resultado.insert(tk.END, "   b) Administração:\n")
        txt_resultado.insert(tk.END, "      Chuveiros: {} un\n".format(chuveiros_adm))
        txt_resultado.insert(tk.END, "      Torneiras: {} un\n".format(torneiras_adm))

        txt_resultado.insert(tk.END, "\n   Total de aparelhos = {} + {} + {} = {}\n".format(total_chuveiros_apt, chuveiros_adm, torneiras_adm, total_aparelhos))
        txt_resultado.insert(tk.END, "   FD conforme Tabela 2 (chuveiro_torneira_ferro): para {} aparelhos = {:.2f}\n\n".format(total_aparelhos, f_ch))

        txt_resultado.insert(tk.END, "   Chuveiros (aptos):\n")
        txt_resultado.insert(tk.END, "      = {} un x {:.1f} kW x {:.2f} = {:.2f} kVA\n".format(total_chuveiros_apt, chuveiro_kw, f_ch, apt_chuveiros))

        if chuveiros_adm > 0:
            txt_resultado.insert(tk.END, "   Chuveiros (adm):\n")
            txt_resultado.insert(tk.END, "      = {} un x {:.1f} kW x {:.2f} = {:.2f} kVA\n".format(chuveiros_adm, chuveiro_kw, f_ch, adm_chuveiros))

        if torneiras_adm > 0:
            txt_resultado.insert(tk.END, "   Torneiras (adm):\n")
            txt_resultado.insert(tk.END, "      = {} un x {:.1f} kW x {:.2f} = {:.2f} kVA\n".format(torneiras_adm, torneira_kw, f_ch, adm_torneiras))

        txt_resultado.insert(tk.END, "\n   b) Máquina de Secar Roupa:\n")
        txt_resultado.insert(tk.END, "      Total: {} aptos x {} un = {} un\n".format(aptos, secar_apto, total_secar))
        txt_resultado.insert(tk.END, "      FD (Tabela 2 - maquina_secar_roupa): para {} un = {:.2f}\n".format(total_secar, f_secar))
        txt_resultado.insert(tk.END, "      D2b = {} x {:.1f} x {:.2f} = {:.2f} kVA\n\n".format(total_secar, secar_kw, f_secar, D2b))

        txt_resultado.insert(tk.END, "   c) Máquina de Lavar Louça:\n")
        txt_resultado.insert(tk.END, "      Total: {} aptos x {} un = {} un\n".format(aptos, lavar_apto, total_lavar))
        txt_resultado.insert(tk.END, "      FD (Tabela 2 - maquinas_lavar_louca): para {} un = {:.2f}\n".format(total_lavar, f_lavar))
        txt_resultado.insert(tk.END, "      D2c = {} x {:.1f} x {:.2f} = {:.2f} kVA\n\n".format(total_lavar, lavar_kw, f_lavar, D2c))

        txt_resultado.insert(tk.END, "   D2 (Apartamentos) = {:.2f} kVA\n".format(D2_apt))
        txt_resultado.insert(tk.END, "   D2 (Administração) = {:.2f} kVA\n".format(D2_adm))
        txt_resultado.insert(tk.END, "   D2 Total = {:.2f} kVA\n\n".format(D2))

        # =====================================
        # 3 - MOTORES
        # =====================================
        txt_resultado.insert(tk.END, "3 - MOTORES (Item 5.3 - GED-119)\n")
        txt_resultado.insert(tk.END, "   Fórmula: D3 = Maior motor x 1,0 + (Restante) x 0,5\n\n")

        if motores:
            txt_resultado.insert(tk.END, "   Motores cadastrados:\n")
            for i, (cv, qtd) in enumerate(motores):
                kva = cv_para_kva(cv)
                txt_resultado.insert(tk.END, "      {}) {} CV x {} un = {:.2f} kVA (Tabela 4)\n".format(i+1, cv, qtd, kva * qtd))

            txt_resultado.insert(tk.END, "\n   Total de potência de motores = {:.2f} kVA\n".format(total))
            txt_resultado.insert(tk.END, "   Maior motor = {:.2f} kVA\n".format(maior))
            txt_resultado.insert(tk.END, "   Restante = {:.2f} - {:.2f} = {:.2f} kVA\n".format(total, maior, restantes))
            txt_resultado.insert(tk.END, "\n   D3 = {:.2f} x 1,0 + {:.2f} x 0,5\n".format(maior, restantes))
            txt_resultado.insert(tk.END, "   D3 = {:.2f} + {:.2f}\n".format(maior * 1.0, restantes * 0.5))
            txt_resultado.insert(tk.END, "   D3 = {:.2f} kVA\n\n".format(D3))
        else:
            txt_resultado.insert(tk.END, "   Nenhum motor cadastrado. D3 = 0,00 kVA\n\n")

        # =====================================
        # 4 - DEMANDA GERAL
        # =====================================
        txt_resultado.insert(tk.END, "4 - DEMANDA GERAL (Item 5.4 - GED-119)\n")
        txt_resultado.insert(tk.END, "   Fórmula: Dg = Dapt + Dadm\n\n")
        txt_resultado.insert(tk.END, "   Onde:\n")
        txt_resultado.insert(tk.END, "      Dapt = (D1a + D2_apt) x Fator de Simultaneidade\n")
        txt_resultado.insert(tk.END, "      Dadm = D1b + D2_adm + D3\n\n")

        txt_resultado.insert(tk.END, "   Fator de simultaneidade (Tabela 7):\n")
        txt_resultado.insert(tk.END, "      Para {} apartamentos = {:.2f}\n\n".format(aptos, f_sim))

        txt_resultado.insert(tk.END, "   Dapt = (D1a + D2_apt) x F.Sim\n")
        txt_resultado.insert(tk.END, "   Dapt = ({:.2f} + {:.2f}) x {:.2f}\n".format(D1a, D2_apt, f_sim))
        txt_resultado.insert(tk.END, "   Dapt = {:.2f} x {:.2f}\n".format(D1a + D2_apt, f_sim))
        txt_resultado.insert(tk.END, "   Dapt = {:.2f} kVA\n\n".format(Dapt))

        txt_resultado.insert(tk.END, "   Dadm = D1b + D2_adm + D3\n")
        txt_resultado.insert(tk.END, "   Dadm = {:.2f} + {:.2f} + {:.2f}\n".format(D1b, D2_adm, D3))
        txt_resultado.insert(tk.END, "   Dadm = {:.2f} kVA\n\n".format(Dadm))

        txt_resultado.insert(tk.END, "   Dg = Dapt + Dadm\n")
        txt_resultado.insert(tk.END, "   Dg = {:.2f} + {:.2f}\n".format(Dapt, Dadm))
        txt_resultado.insert(tk.END, "   Dg = {:.2f} kVA\n\n".format(Dg))

        # =====================================
        # RESUMO FINAL
        # =====================================
        txt_resultado.insert(tk.END, "=" * 55 + "\n")
        txt_resultado.insert(tk.END, "  RESUMO FINAL\n")
        txt_resultado.insert(tk.END, "=" * 55 + "\n\n")

        txt_resultado.insert(tk.END, "  D1 (Iluminação)    = {:.2f} kVA\n".format(D1))
        txt_resultado.insert(tk.END, "  D2 (Aparelhos)     = {:.2f} kVA\n".format(D2))
        txt_resultado.insert(tk.END, "    D2a - Chuv/Torn  = {:.2f} kVA\n".format(apt_chuveiros + adm_chuveiros + adm_torneiras))
        txt_resultado.insert(tk.END, "    D2b - Secar Roupa = {:.2f} kVA\n".format(D2b))
        txt_resultado.insert(tk.END, "    D2c - Lavar Louça = {:.2f} kVA\n".format(D2c))
        txt_resultado.insert(tk.END, "    - Apartamentos   = {:.2f} kVA\n".format(D2_apt))
        txt_resultado.insert(tk.END, "    - Administração  = {:.2f} kVA\n".format(D2_adm))
        txt_resultado.insert(tk.END, "  D3 (Motores)       = {:.2f} kVA\n".format(D3))
        txt_resultado.insert(tk.END, "  ---------------------------------\n")
        txt_resultado.insert(tk.END, "  Dg (Demanda Geral) = {:.2f} kVA\n".format(Dg))

        txt_resultado.insert(tk.END, "\n" + "=" * 55 + "\n")
        txt_resultado.insert(tk.END, "  DEMANDA TOTAL (Dg): {:.2f} kVA\n".format(Dg))
        txt_resultado.insert(tk.END, "=" * 55 + "\n")

    except Exception as e:
        messagebox.showerror("Erro", "Verifique os dados inseridos!\n{}".format(str(e)))


# -----------------------------------
# GERENCIAMENTO DE PROJETOS
# -----------------------------------

def salvar_projeto():
    nome = entry_nome_projeto.get().strip()
    if not nome:
        messagebox.showwarning("Aviso", "Digite um nome para o projeto!")
        return

    def vazio_zero(entry, tipo):
        raw = entry.get().strip()
        if raw == "":
            return 0
        if tipo == int:
            return int(float(raw))
        return float(raw)

    try:
        aptos = vazio_zero(entry_aptos, int)
        area_apto = vazio_zero(entry_area_apto, float)
        area_adm = vazio_zero(entry_area_adm, float)
        iluminacao = vazio_zero(entry_iluminacao, float)
        tomadas = vazio_zero(entry_tomadas, float)
        chuveiro_kw = vazio_zero(entry_chuveiro, float)
        torneira_kw = vazio_zero(entry_torneira, float)
        chuveiros_apto = vazio_zero(entry_qtd_chuveiros, int)
        torneiras_apto = vazio_zero(entry_qtd_torneiras, int)
        chuveiros_adm = vazio_zero(entry_qtd_chuveiros_adm, int)
        torneiras_adm = vazio_zero(entry_qtd_torneiras_adm, int)
        secar_kw = vazio_zero(entry_secar_kw, float)
        secar_apto = vazio_zero(entry_secar_apto, int)
        lavar_kw = vazio_zero(entry_lavar_kw, float)
        lavar_apto = vazio_zero(entry_lavar_apto, int)
    except ValueError:
        messagebox.showerror("Erro", "Verifique os dados inseridos!")
        return

    global current_projeto_id

    if current_projeto_id:
        projeto_id = current_projeto_id
        cursor_proj.execute("""
            UPDATE projetos SET
            nome=?, aptos=?, area_apto=?, area_adm=?, iluminacao=?, tomadas=?,
            chuveiro_kw=?, torneira_kw=?, chuveiros_apto=?, torneiras_apto=?,
            chuveiros_adm=?, torneiras_adm=?,
            secar_kw=?, secar_apto=?, lavar_kw=?, lavar_apto=?
            WHERE id=?
        """, (nome, aptos, area_apto, area_adm, iluminacao, tomadas,
              chuveiro_kw, torneira_kw, chuveiros_apto, torneiras_apto,
              chuveiros_adm, torneiras_adm,
              secar_kw, secar_apto, lavar_kw, lavar_apto,
              projeto_id))
    else:
        cursor_proj.execute("""
            INSERT INTO projetos
            (nome, aptos, area_apto, area_adm, iluminacao, tomadas,
             chuveiro_kw, torneira_kw, chuveiros_apto, torneiras_apto,
             chuveiros_adm, torneiras_adm,
             secar_kw, secar_apto, lavar_kw, lavar_apto)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, aptos, area_apto, area_adm, iluminacao, tomadas,
              chuveiro_kw, torneira_kw, chuveiros_apto, torneiras_apto,
              chuveiros_adm, torneiras_adm,
              secar_kw, secar_apto, lavar_kw, lavar_apto))
        projeto_id = cursor_proj.lastrowid
    current_projeto_id = projeto_id
    conn_proj.commit()

    cursor_proj.execute("DELETE FROM motores_projeto WHERE projeto_id = ?", (projeto_id,))
    for cv, qtd in motores:
        cursor_proj.execute("""
            INSERT INTO motores_projeto (projeto_id, cv, quantidade)
            VALUES (?, ?, ?)
        """, (projeto_id, cv, qtd))
    conn_proj.commit()

    listar_projetos()
    messagebox.showinfo("Sucesso", f"Projeto '{nome}' salvo com sucesso!")


def carregar_projeto():
    selecionado = lista_projetos.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um projeto para carregar!")
        return

    item = selecionado[0]
    valores = lista_projetos.item(item)["values"]
    projeto_id = valores[0]

    global current_projeto_id
    current_projeto_id = projeto_id

    cursor_proj.execute("SELECT * FROM projetos WHERE id = ?", (projeto_id,))
    proj = cursor_proj.fetchone()
    if not proj:
        return

    entry_nome_projeto.delete(0, tk.END)
    entry_nome_projeto.insert(0, proj[1])

    entry_aptos.delete(0, tk.END); entry_aptos.insert(0, proj[2])
    entry_area_apto.delete(0, tk.END); entry_area_apto.insert(0, proj[3])
    entry_area_adm.delete(0, tk.END); entry_area_adm.insert(0, proj[4])
    entry_iluminacao.delete(0, tk.END); entry_iluminacao.insert(0, proj[5])
    entry_tomadas.delete(0, tk.END); entry_tomadas.insert(0, proj[6])
    entry_chuveiro.delete(0, tk.END); entry_chuveiro.insert(0, proj[7])
    entry_torneira.delete(0, tk.END); entry_torneira.insert(0, proj[8])
    entry_qtd_chuveiros.delete(0, tk.END); entry_qtd_chuveiros.insert(0, proj[9])
    entry_qtd_torneiras.delete(0, tk.END); entry_qtd_torneiras.insert(0, proj[10])
    entry_qtd_chuveiros_adm.delete(0, tk.END); entry_qtd_chuveiros_adm.insert(0, proj[12] if len(proj) > 12 else 0)
    entry_qtd_torneiras_adm.delete(0, tk.END); entry_qtd_torneiras_adm.insert(0, proj[13] if len(proj) > 13 else 0)
    entry_secar_kw.delete(0, tk.END); entry_secar_kw.insert(0, proj[14] if len(proj) > 14 else 0)
    entry_lavar_kw.delete(0, tk.END); entry_lavar_kw.insert(0, proj[15] if len(proj) > 15 else 0)
    entry_secar_apto.delete(0, tk.END); entry_secar_apto.insert(0, proj[16] if len(proj) > 16 else 0)
    entry_lavar_apto.delete(0, tk.END); entry_lavar_apto.insert(0, proj[17] if len(proj) > 17 else 0)

    motores.clear()
    cursor_proj.execute("SELECT cv, quantidade FROM motores_projeto WHERE projeto_id = ?", (projeto_id,))
    for cv, qtd in cursor_proj.fetchall():
        motores.append((cv, qtd))
    atualizar_tabela_motores()

    notebook.select(aba1_container)
    messagebox.showinfo("Sucesso", f"Projeto '{proj[1]}' carregado!")


def excluir_projeto():
    selecionado = lista_projetos.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione um projeto para excluir!")
        return

    item = selecionado[0]
    valores = lista_projetos.item(item)["values"]
    projeto_id = valores[0]
    nome = valores[1]

    if messagebox.askyesno("Confirmar", f"Excluir o projeto '{nome}'?"):
        cursor_proj.execute("DELETE FROM motores_projeto WHERE projeto_id = ?", (projeto_id,))
        cursor_proj.execute("DELETE FROM projetos WHERE id = ?", (projeto_id,))
        conn_proj.commit()
        listar_projetos()
        messagebox.showinfo("Sucesso", f"Projeto '{nome}' excluido!")


def novo_projeto():
    global current_projeto_id
    current_projeto_id = None
    entry_nome_projeto.delete(0, tk.END)
    entry_aptos.delete(0, tk.END)
    entry_area_apto.delete(0, tk.END)
    entry_area_adm.delete(0, tk.END)
    entry_iluminacao.delete(0, tk.END)
    entry_tomadas.delete(0, tk.END)
    entry_chuveiro.delete(0, tk.END)
    entry_torneira.delete(0, tk.END)
    entry_qtd_chuveiros.delete(0, tk.END)
    entry_qtd_torneiras.delete(0, tk.END)
    entry_qtd_chuveiros_adm.delete(0, tk.END)
    entry_qtd_torneiras_adm.delete(0, tk.END)
    entry_secar_kw.delete(0, tk.END)
    entry_secar_apto.delete(0, tk.END)
    entry_lavar_kw.delete(0, tk.END)
    entry_lavar_apto.delete(0, tk.END)
    motores.clear()
    atualizar_tabela_motores()
    entry_nome_projeto.focus()


def listar_projetos():
    lista_projetos.delete(*lista_projetos.get_children())
    cursor_proj.execute("SELECT id, nome, aptos, data_criacao FROM projetos ORDER BY data_criacao DESC")
    for row in cursor_proj.fetchall():
        lista_projetos.insert("", "end", values=row)


# -----------------------------------
# CALCULAR TRANSFORMADOR
# -----------------------------------

def buscar_faixa_tabela(tabela, col_min, col_max, valor):
    cursor.execute(f"SELECT * FROM {tabela}")
    linhas = cursor.fetchall()
    colunas = [d[0] for d in cursor.description]
    for linha in linhas:
        min_v = linha[colunas.index(col_min)]
        max_v = linha[colunas.index(col_max)]
        if min_v is None and max_v is not None and valor <= max_v:
            return linha
        if max_v is None and min_v is not None and valor >= min_v:
            return linha
        if min_v is not None and max_v is not None and min_v <= valor <= max_v:
            return linha
    return None

def calcular_transformador():
    global ultimo_Dg
    if ultimo_Dg is None:
        messagebox.showwarning("Aviso", "Calcule a demanda primeiro (aba Resultado)!")
        return

    try:
        tensao_opcao = combo_tensao.get()
        metodo_inst = combo_metodo_inst.get()
        forma_agrup = combo_forma_agrup.get()
        num_circuitos_str = entry_num_circuitos.get().strip()

        num_circuitos = int(num_circuitos_str) if num_circuitos_str else 1
        if num_circuitos < 1:
            num_circuitos = 1

        if tensao_opcao == "380/220V (trifásico)":
            V = 380
            fator_380 = 1.73
        else:
            V = 220
            fator_380 = 1.0

        I = ultimo_Dg * 1000 / (V * 3**0.5)

        txt_transf.delete("1.0", tk.END)
        txt_transf.insert(tk.END, "=" * 60 + "\n")
        txt_transf.insert(tk.END, "  DIMENSIONAMENTO DO TRANSFORMADOR\n")
        txt_transf.insert(tk.END, "=" * 60 + "\n\n")

        txt_transf.insert(tk.END, f"Demanda Geral (Dg): {ultimo_Dg:.2f} kVA\n")
        txt_transf.insert(tk.END, f"Tensão: {tensao_opcao}\n")
        txt_transf.insert(tk.END, f"Corrente Calculada: I = {ultimo_Dg:.2f} x 1000 / ({V} x √3) = {I:.2f} A\n\n")

        # --- TRANSFORMADOR (TABELA_10) ---
        trafo = buscar_faixa_tabela("TABELA_10", "demanda_min", "demanda_max", ultimo_Dg)
        if trafo:
            trafo_kva = trafo[3]
            txt_transf.insert(tk.END, "1 - TRANSFORMADOR RECOMENDADO (Tabela 10)\n")
            txt_transf.insert(tk.END, f"   Demanda: {ultimo_Dg:.2f} kVA\n")
            txt_transf.insert(tk.END, f"   Transformador: {trafo_kva:.0f} kVA\n")
            txt_transf.insert(tk.END, f"   Faixa: {trafo[1]:.0f} a {trafo[2]:.0f} kVA\n\n")
        else:
            trafo_kva = None
            txt_transf.insert(tk.END, "1 - TRANSFORMADOR RECOMENDADO (Tabela 10)\n")
            txt_transf.insert(tk.END, "   Nenhum transformador encontrado para esta demanda.\n\n")

        # --- CAPACIDADE DE INTERRUPÇÃO ---
        if trafo_kva:
            cap = buscar_faixa_tabela("capacidade_interrupcao_transformador", "transformador_kva", "transformador_kva", trafo_kva)
            if cap:
                txt_transf.insert(tk.END, "   Capacidade de Interrupção:\n")
                txt_transf.insert(tk.END, f"      {cap[1]:.0f} kVA -> {cap[2]:.1f} kA  (Z% = {cap[3]:.2f}%)\n\n")

        # --- CONDUTORES (TABELA 11 - 1 de 2) ---
        cursor.execute("SELECT * FROM tabela11_cabos_bt ORDER BY secao_mm2")
        cabos = cursor.fetchall()
        col_cabos = [d[0] for d in cursor.description]

        cols_metodo = {"A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F"}
        if metodo_inst in cols_metodo:
            col_corrente = cols_metodo[metodo_inst]
        else:
            col_corrente = "C"

        idx_corrente = col_cabos.index(col_corrente)
        idx_secao = col_cabos.index("secao_mm2")

        txt_transf.insert(tk.END, "2 - CONDUTORES BT (Tabela 11 - 1 de 2)\n")
        txt_transf.insert(tk.END, f"   Método de Instalação: {metodo_inst}\n")
        txt_transf.insert(tk.END, f"   Tensão: {tensao_opcao}\n")
        if fator_380 > 1:
            txt_transf.insert(tk.END, f"   Fator 380V (x1,73): aplicado\n")

        I_correcao = I

        # --- FATOR DE CORREÇÃO (TABELA 11 - 2 de 2) ---
        cursor.execute("SELECT * FROM tabela11_fatores_correcao")
        fatores = cursor.fetchall()
        col_fat = [d[0] for d in cursor.description]

        fator_correcao = 1.0
        nome_forma = forma_agrup
        for linha in fatores:
            if linha[1] == nome_forma:
                if num_circuitos == 1:
                    fator_correcao = linha[2]
                elif num_circuitos == 2:
                    fator_correcao = linha[3]
                elif num_circuitos == 3:
                    fator_correcao = linha[4]
                elif num_circuitos == 4:
                    fator_correcao = linha[5]
                elif num_circuitos == 5:
                    fator_correcao = linha[6]
                elif num_circuitos == 6:
                    fator_correcao = linha[7]
                elif num_circuitos == 7:
                    fator_correcao = linha[8]
                elif num_circuitos == 8:
                    fator_correcao = linha[9]
                elif num_circuitos <= 11:
                    fator_correcao = linha[10]
                elif num_circuitos <= 15:
                    fator_correcao = linha[11]
                elif num_circuitos <= 19:
                    fator_correcao = linha[12]
                else:
                    fator_correcao = linha[13]
                break

        if fator_correcao is None or fator_correcao == 0:
            fator_correcao = 1.0

        I_corrigida = I_correcao / fator_correcao

        txt_transf.insert(tk.END, f"   Agrupamento: {nome_forma}\n")
        txt_transf.insert(tk.END, f"   Circuitos agrupados: {num_circuitos}\n")
        txt_transf.insert(tk.END, f"   Fator de Correção (F): {fator_correcao:.2f}\n")
        txt_transf.insert(tk.END, f"   Corrente Corrigida: I' = {I:.2f} / {fator_correcao:.2f} = {I_corrigida:.2f} A\n\n")

        # Encontrar seção do cabo
        cabo_sel = None
        for cabo in cabos:
            capacidade = cabo[idx_corrente]
            if fator_380 > 1:
                capacidade = capacidade * fator_380
            if capacidade >= I_corrigida:
                cabo_sel = cabo
                break

        if cabo_sel:
            secao = cabo_sel[idx_secao]
            capacidade_real = cabo_sel[idx_corrente]
            if fator_380 > 1:
                capacidade_real = capacidade_real * fator_380
            txt_transf.insert(tk.END, f"   Seção Recomendada: {secao:.0f} mm²\n")
            txt_transf.insert(tk.END, f"   Capacidade (Tabela): {cabo_sel[idx_corrente]:.0f} A")
            if fator_380 > 1:
                txt_transf.insert(tk.END, f" x {fator_380} = {capacidade_real:.0f} A")
            txt_transf.insert(tk.END, f" >= {I_corrigida:.2f} A ✓\n")
        else:
            txt_transf.insert(tk.END, "   Nenhum cabo encontrado com capacidade suficiente.\n")
            secao = None

        if secao:
            diametro = cabo_sel[col_cabos.index("diametro_externo_mm")]
            txt_transf.insert(tk.END, f"   Diâmetro Externo: {diametro:.1f} mm\n")
        txt_transf.insert(tk.END, "\n")

        # --- BARRAMENTO BT (TABELA 12) ---
        barra = buscar_faixa_tabela("tabela12_barramento_bt", "demanda_min_kva", "demanda_max_kva", ultimo_Dg)
        txt_transf.insert(tk.END, "3 - BARRAMENTO DE BAIXA TENSÃO (Tabela 12)\n")
        if barra:
            txt_transf.insert(tk.END, f"   Demanda: {ultimo_Dg:.2f} kVA\n")
            txt_transf.insert(tk.END, f"   Barramento: {barra[3]} mm  ({barra[4]} pol)\n\n")
        else:
            txt_transf.insert(tk.END, "   Nenhum barramento encontrado para esta demanda.\n\n")

        # --- DISJUNTOR ---
        cursor.execute("SELECT corrente_nominal_A FROM disjuntores_termomagneticos ORDER BY corrente_nominal_A")
        disjuntores = [r[0] for r in cursor.fetchall()]
        disjuntor_sel = None
        for d in disjuntores:
            if d >= I:
                disjuntor_sel = d
                break

        txt_transf.insert(tk.END, "4 - DISJUNTOR TERMOMAGNÉTICO\n")
        txt_transf.insert(tk.END, f"   Corrente Calculada: {I:.2f} A\n")
        if disjuntor_sel:
            txt_transf.insert(tk.END, f"   Disjuntor Padronizado: {disjuntor_sel:.0f} A\n")
            txt_transf.insert(tk.END, f"   Correntes Nominais Padronizadas (A): 100 - 125 - 150 - 160 - 175 - 200 - 225 - 250 - 300 - 350 - 400 - 450 - 500 - 600\n\n")
        else:
            txt_transf.insert(tk.END, "   Nenhum disjuntor padronizado encontrado (acima de 600A).\n\n")

        # --- RESUMO ---
        txt_transf.insert(tk.END, "=" * 60 + "\n")
        txt_transf.insert(tk.END, "  RESUMO DO DIMENSIONAMENTO\n")
        txt_transf.insert(tk.END, "=" * 60 + "\n\n")
        if trafo_kva:
            txt_transf.insert(tk.END, f"  Transformador: {trafo_kva:.0f} kVA\n")
            if cap:
                txt_transf.insert(tk.END, f"  Capacidade de Interrupção: {cap[2]:.1f} kA\n")
        if secao:
            txt_transf.insert(tk.END, f"  Condutor: {secao:.0f} mm²\n")
        if barra:
            txt_transf.insert(tk.END, f"  Barramento BT: {barra[3]} mm\n")
        if disjuntor_sel:
            txt_transf.insert(tk.END, f"  Disjuntor: {disjuntor_sel:.0f} A\n")
        txt_transf.insert(tk.END, f"  Corrente Total: {I:.2f} A\n")
        txt_transf.insert(tk.END, "=" * 60 + "\n")

    except Exception as e:
        messagebox.showerror("Erro", f"Erro no dimensionamento:\n{str(e)}")


# -----------------------------------
# INTERFACE
# -----------------------------------

janela = tk.Tk()
janela.title("GED-119 - Cálculo de Demanda")
janela.geometry("900x700")

style = ttk.Style()
style.theme_use("clam")

notebook = ttk.Notebook(janela)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# -----------------------------------
# ABA 1 - DADOS
# -----------------------------------

aba1_container = ttk.Frame(notebook)
notebook.add(aba1_container, text="Dados do Edifício")

canvas1 = tk.Canvas(aba1_container, highlightthickness=0, width=860)
scroll1 = ttk.Scrollbar(aba1_container, orient="vertical", command=canvas1.yview)
aba1 = ttk.Frame(canvas1, padding=5)

def _config_inner(event):
    canvas1.configure(scrollregion=canvas1.bbox("all"))
    canvas1.itemconfig(inner_id, width=canvas1.winfo_width())

aba1.bind("<Configure>", _config_inner)
inner_id = canvas1.create_window((0, 0), window=aba1, anchor="nw")
canvas1.configure(yscrollcommand=scroll1.set)

canvas1.pack(side="left", fill="both", expand=True)
scroll1.pack(side="right", fill="y")

def _on_mousewheel(event):
    canvas1.yview_scroll(int(-1 * (event.delta / 120)), "units")
canvas1.bind("<MouseWheel>", _on_mousewheel)

aba1_container.rowconfigure(0, weight=1)
aba1_container.columnconfigure(0, weight=1)

# --- Grupo: Edifício ---
frame_edificio = ttk.LabelFrame(aba1, text="Edifício", padding=10)
frame_edificio.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_edificio, text="Nº de Apartamentos:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_aptos = ttk.Entry(frame_edificio, width=15)
entry_aptos.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_edificio, text="Área do Apartamento (m²):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_area_apto = ttk.Entry(frame_edificio, width=15)
entry_area_apto.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_edificio, text="Área Administrativa (m²):").grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_area_adm = ttk.Entry(frame_edificio, width=15)
entry_area_adm.grid(row=2, column=1, padx=5, pady=5)

# --- Grupo: Cargas ---
frame_cargas = ttk.LabelFrame(aba1, text="Cargas de Iluminação e Tomadas", padding=10)
frame_cargas.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_cargas, text="Iluminação (W):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_iluminacao = ttk.Entry(frame_cargas, width=15)
entry_iluminacao.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_cargas, text="Tomadas (W):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_tomadas = ttk.Entry(frame_cargas, width=15)
entry_tomadas.grid(row=1, column=1, padx=5, pady=5)

# --- Grupo: Aparelhos ---
frame_aparelhos = ttk.LabelFrame(aba1, text="Aparelhos (por apartamento)", padding=10)
frame_aparelhos.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_aparelhos, text="Potência do Chuveiro (kW):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_chuveiro = ttk.Entry(frame_aparelhos, width=15)
entry_chuveiro.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_aparelhos, text="Potência da Torneira (kW):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_torneira = ttk.Entry(frame_aparelhos, width=15)
entry_torneira.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_aparelhos, text="Qtd. de Chuveiros por apto:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
entry_qtd_chuveiros = ttk.Entry(frame_aparelhos, width=15)
entry_qtd_chuveiros.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(frame_aparelhos, text="Qtd. de Torneiras por apto:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
entry_qtd_torneiras = ttk.Entry(frame_aparelhos, width=15)
entry_qtd_torneiras.grid(row=3, column=1, padx=5, pady=5)

# --- Grupo: Aparelhos (Administração) ---
frame_aparelhos_adm = ttk.LabelFrame(aba1, text="Aparelhos (administração)", padding=10)
frame_aparelhos_adm.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_aparelhos_adm, text="Qtd. de Chuveiros:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_qtd_chuveiros_adm = ttk.Entry(frame_aparelhos_adm, width=15)
entry_qtd_chuveiros_adm.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_aparelhos_adm, text="Qtd. de Torneiras:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_qtd_torneiras_adm = ttk.Entry(frame_aparelhos_adm, width=15)
entry_qtd_torneiras_adm.grid(row=1, column=1, padx=5, pady=5)

# --- Grupo: Eletrodomésticos (por apartamento) ---
frame_eletro = ttk.LabelFrame(aba1, text="Eletrodomésticos (por apartamento)", padding=10)
frame_eletro.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_eletro, text="Pot. Máq. Secar Roupa (kW):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_secar_kw = ttk.Entry(frame_eletro, width=15)
entry_secar_kw.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_eletro, text="Qtd. por apto:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_secar_apto = ttk.Entry(frame_eletro, width=15)
entry_secar_apto.grid(row=0, column=3, padx=5, pady=5)

ttk.Label(frame_eletro, text="Pot. Máq. Lavar Louça (kW):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_lavar_kw = ttk.Entry(frame_eletro, width=15)
entry_lavar_kw.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(frame_eletro, text="Qtd. por apto:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
entry_lavar_apto = ttk.Entry(frame_eletro, width=15)
entry_lavar_apto.grid(row=1, column=3, padx=5, pady=5)

# -----------------------------------
# ABA 2 - MOTORES
# -----------------------------------

aba2 = ttk.Frame(notebook)
notebook.add(aba2, text="Motores")

# Frame de entrada
frame_motor_input = ttk.LabelFrame(aba2, text="Adicionar / Editar Motor", padding=10)
frame_motor_input.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_motor_input, text="Potência (CV):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_cv = ttk.Entry(frame_motor_input, width=12)
entry_cv.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(frame_motor_input, text="Quantidade:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
entry_qtd_motor = ttk.Entry(frame_motor_input, width=12)
entry_qtd_motor.grid(row=0, column=3, padx=5, pady=5)

frame_botoes = ttk.Frame(frame_motor_input)
frame_botoes.grid(row=0, column=4, padx=10, pady=5)

btn_add = ttk.Button(frame_botoes, text="Adicionar", command=adicionar_motor)
btn_add.pack(side="left", padx=2)

btn_edit = ttk.Button(frame_botoes, text="Editar", command=editar_motor)
btn_edit.pack(side="left", padx=2)

btn_del = ttk.Button(frame_botoes, text="Excluir", command=excluir_motor)
btn_del.pack(side="left", padx=2)

# Frame para tabela
frame_tabela_motor = ttk.LabelFrame(aba2, text="Motores Cadastrados", padding=5)
frame_tabela_motor.pack(fill="both", expand=True, padx=10, pady=10)

aba2.rowconfigure(1, weight=1)
aba2.columnconfigure(0, weight=1)

scroll_motor = ttk.Scrollbar(frame_tabela_motor, orient="vertical")
lista_motores = ttk.Treeview(
    frame_tabela_motor,
    columns=("cv", "qtd"),
    show="headings",
    yscrollcommand=scroll_motor.set
)
scroll_motor.config(command=lista_motores.yview)

lista_motores.heading("cv", text="Potência (CV)")
lista_motores.heading("qtd", text="Quantidade")

lista_motores.column("cv", width=150, anchor="center")
lista_motores.column("qtd", width=150, anchor="center")

lista_motores.pack(side="left", fill="both", expand=True)
scroll_motor.pack(side="right", fill="y")

lista_motores.bind("<<TreeviewSelect>>", carregar_motor_selecionado)

# -----------------------------------
# ABA 3 - RESULTADO
# -----------------------------------

aba3 = ttk.Frame(notebook)
notebook.add(aba3, text="Resultado")

frame_resultado = ttk.LabelFrame(aba3, text="Memorial de Cálculo", padding=10)
frame_resultado.pack(fill="both", expand=True, padx=10, pady=10)

btn_calc = ttk.Button(frame_resultado, text="Calcular Demanda", command=calcular)
btn_calc.pack(pady=10)

scroll_resultado = ttk.Scrollbar(frame_resultado, orient="vertical")
txt_resultado = tk.Text(
    frame_resultado,
    height=20,
    font=("Consolas", 10),
    yscrollcommand=scroll_resultado.set
)
scroll_resultado.config(command=txt_resultado.yview)

txt_resultado.pack(side="left", fill="both", expand=True)
scroll_resultado.pack(side="right", fill="y")

# -----------------------------------
# ABA 4 - GERENCIAMENTO DE PROJETOS
# -----------------------------------

aba4 = ttk.Frame(notebook)
notebook.add(aba4, text="Gerenciamento de Projetos")

# Frame nome do projeto
frame_proj_nome = ttk.LabelFrame(aba4, text="Projeto", padding=10)
frame_proj_nome.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_proj_nome, text="Nome do Projeto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
entry_nome_projeto = ttk.Entry(frame_proj_nome, width=40)
entry_nome_projeto.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
frame_proj_nome.columnconfigure(1, weight=1)

frame_botoes_proj = ttk.Frame(frame_proj_nome)
frame_botoes_proj.grid(row=0, column=2, padx=10, pady=5)

btn_novo = ttk.Button(frame_botoes_proj, text="Novo", command=novo_projeto)
btn_novo.pack(side="left", padx=2)

btn_salvar = ttk.Button(frame_botoes_proj, text="Salvar Alterações", command=salvar_projeto)
btn_salvar.pack(side="left", padx=2)

btn_carregar = ttk.Button(frame_botoes_proj, text="Carregar", command=carregar_projeto)
btn_carregar.pack(side="left", padx=2)

btn_excluir = ttk.Button(frame_botoes_proj, text="Excluir", command=excluir_projeto)
btn_excluir.pack(side="left", padx=2)

# Frame lista de projetos
frame_lista_proj = ttk.LabelFrame(aba4, text="Projetos Salvos", padding=5)
frame_lista_proj.pack(fill="both", expand=True, padx=10, pady=10)

aba4.rowconfigure(1, weight=1)
aba4.columnconfigure(0, weight=1)

scroll_proj = ttk.Scrollbar(frame_lista_proj, orient="vertical")
lista_projetos = ttk.Treeview(
    frame_lista_proj,
    columns=("id", "nome", "aptos", "data"),
    show="headings",
    yscrollcommand=scroll_proj.set
)
scroll_proj.config(command=lista_projetos.yview)

lista_projetos.heading("id", text="ID")
lista_projetos.heading("nome", text="Nome do Projeto")
lista_projetos.heading("aptos", text="Aptos")
lista_projetos.heading("data", text="Data Criação")

lista_projetos.column("id", width=40, anchor="center")
lista_projetos.column("nome", width=250)
lista_projetos.column("aptos", width=60, anchor="center")
lista_projetos.column("data", width=150, anchor="center")

lista_projetos.pack(side="left", fill="both", expand=True)
scroll_proj.pack(side="right", fill="y")

listar_projetos()

# -----------------------------------
# ABA 5 - CALCULAR TRANSFORMADOR
# -----------------------------------

aba5 = ttk.Frame(notebook)
notebook.add(aba5, text="Calcular Transformador")

canvas5 = tk.Canvas(aba5, highlightthickness=0, width=860)
scroll5 = ttk.Scrollbar(aba5, orient="vertical", command=canvas5.yview)
aba5_inner = ttk.Frame(canvas5, padding=5)

def _config_inner5(event):
    canvas5.configure(scrollregion=canvas5.bbox("all"))
    canvas5.itemconfig(inner5_id, width=canvas5.winfo_width())

aba5_inner.bind("<Configure>", _config_inner5)
inner5_id = canvas5.create_window((0, 0), window=aba5_inner, anchor="nw")
canvas5.configure(yscrollcommand=scroll5.set)

canvas5.pack(side="left", fill="both", expand=True)
scroll5.pack(side="right", fill="y")

def _on_mousewheel5(event):
    canvas5.yview_scroll(int(-1 * (event.delta / 120)), "units")
canvas5.bind("<MouseWheel>", _on_mousewheel5)

aba5.rowconfigure(0, weight=1)
aba5.columnconfigure(0, weight=1)

# --- Frame: Dados de Entrada ---
frame_dados_transf = ttk.LabelFrame(aba5_inner, text="Dados de Entrada", padding=10)
frame_dados_transf.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_dados_transf, text="Demanda Geral (Dg):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
lbl_dg_transf = ttk.Label(frame_dados_transf, text="---", font=("Consolas", 10, "bold"))
lbl_dg_transf.grid(row=0, column=1, padx=5, pady=5, sticky="w")

ttk.Label(frame_dados_transf, text="Tensão:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
combo_tensao = ttk.Combobox(frame_dados_transf, values=["380/220V (trifásico)", "220/127V (trifásico)"], state="readonly", width=25)
combo_tensao.grid(row=1, column=1, padx=5, pady=5, sticky="w")
combo_tensao.current(0)

ttk.Label(frame_dados_transf, text="Método de Instalação:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
combo_metodo_inst = ttk.Combobox(frame_dados_transf, values=["A", "B", "C", "D", "E", "F"], state="readonly", width=10)
combo_metodo_inst.grid(row=2, column=1, padx=5, pady=5, sticky="w")
combo_metodo_inst.current(2)

# --- Frame: Forma de Agrupamento (Tabela 11 - 2 de 2) ---
frame_agrup = ttk.LabelFrame(aba5_inner, text="Fatores de Correção para Condutores Agrupados (Tabela 11 - 2 de 2)", padding=10)
frame_agrup.pack(fill="x", padx=10, pady=10)

ttk.Label(frame_agrup, text="Forma de Agrupamento:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
cursor.execute("SELECT forma_agrupamento FROM tabela11_fatores_correcao")
formas = [r[0] for r in cursor.fetchall()]
combo_forma_agrup = ttk.Combobox(frame_agrup, values=formas, state="readonly", width=70)
combo_forma_agrup.grid(row=0, column=1, padx=5, pady=5, sticky="w")
combo_forma_agrup.current(0)

ttk.Label(frame_agrup, text="Nº de Circuitos Agrupados:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
entry_num_circuitos = ttk.Entry(frame_agrup, width=10)
entry_num_circuitos.grid(row=1, column=1, padx=5, pady=5, sticky="w")
entry_num_circuitos.insert(0, "1")

# --- Botão Calcular ---
frame_btn_transf = ttk.Frame(aba5_inner)
frame_btn_transf.pack(fill="x", padx=10, pady=10)

def atualizar_dg_transf():
    if ultimo_Dg is not None:
        lbl_dg_transf.config(text=f"{ultimo_Dg:.2f} kVA")
    else:
        lbl_dg_transf.config(text="--- (calcule primeiro)")

btn_calc_transf = ttk.Button(frame_btn_transf, text="Calcular Transformador", command=lambda: [atualizar_dg_transf(), calcular_transformador()])
btn_calc_transf.pack(side="left", padx=5)

btn_atualizar_dg = ttk.Button(frame_btn_transf, text="Atualizar Dg", command=atualizar_dg_transf)
btn_atualizar_dg.pack(side="left", padx=5)

# --- Frame Resultado ---
frame_res_transf = ttk.LabelFrame(aba5_inner, text="Resultado do Dimensionamento", padding=10)
frame_res_transf.pack(fill="both", expand=True, padx=10, pady=10)

scroll_transf = ttk.Scrollbar(frame_res_transf, orient="vertical")
txt_transf = tk.Text(
    frame_res_transf,
    height=25,
    font=("Consolas", 10),
    yscrollcommand=scroll_transf.set
)
scroll_transf.config(command=txt_transf.yview)

txt_transf.pack(side="left", fill="both", expand=True)
scroll_transf.pack(side="right", fill="y")

# Atualizar Dg automaticamente ao trocar para a aba "Calcular Transformador"
def on_tab_change(event):
    if notebook.tab("current", "text") == "Calcular Transformador":
        atualizar_dg_transf()

notebook.bind("<<NotebookTabChanged>>", on_tab_change)


# -----------------------------------
# CRIAR PROJETO TESTE DIMENSIONAMENTO
# -----------------------------------

cursor_proj.execute("SELECT COUNT(*) FROM projetos WHERE nome = 'Teste Dimensionamento'")
if cursor_proj.fetchone()[0] == 0:
    cursor_proj.execute("""
        INSERT INTO projetos
        (nome, aptos, area_apto, area_adm, iluminacao, tomadas,
         chuveiro_kw, torneira_kw, chuveiros_apto, torneiras_apto,
         chuveiros_adm, torneiras_adm,
         secar_kw, secar_apto, lavar_kw, lavar_apto)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, ("Teste Dimensionamento", 20, 180, 2884, 5, 5, 5.4, 3.0, 4, 0, 5, 2, 2.5, 1, 2.5, 1))
    proj_id = cursor_proj.lastrowid

    motores_teste = [(1.0, 1), (5.0, 1), (7.5, 1), (10.0, 3)]
    for cv, qtd in motores_teste:
        cursor_proj.execute("""
            INSERT INTO motores_projeto (projeto_id, cv, quantidade)
            VALUES (?, ?, ?)
        """, (proj_id, cv, qtd))
    conn_proj.commit()
    listar_projetos()

# Atualizar projeto existente se ainda nao tem campos de adm
cursor_proj.execute("UPDATE projetos SET chuveiros_adm = 5, torneiras_adm = 2, secar_kw = 2.5, secar_apto = 1, lavar_kw = 2.5, lavar_apto = 1 WHERE nome = 'Teste Dimensionamento' AND (chuveiros_adm IS NULL OR chuveiros_adm = 0)")
if cursor_proj.rowcount > 0:
    conn_proj.commit()
    listar_projetos()

# -----------------------------------
# START
# -----------------------------------

janela.mainloop()
