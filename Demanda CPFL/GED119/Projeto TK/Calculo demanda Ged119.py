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
# FUNÇÕES DO BANCO
# -----------------------------------

def normalizar_cv(cv):
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

def adicionar_motor():
    try:
        cv = float(entry_cv.get())
        qtd = int(entry_qtd_motor.get())

        motores.append((cv, qtd))
        lista_motores.insert("", "end", values=(cv, qtd))

    except:
        messagebox.showerror("Erro", "Dados inválidos")

# -----------------------------------
# CÁLCULO PRINCIPAL
# -----------------------------------

def calcular():

    try:
        aptos = int(entry_aptos.get())
        area_apto = float(entry_area_apto.get())
        area_adm = float(entry_area_adm.get())

        iluminacao = float(entry_iluminacao.get())
        tomadas = float(entry_tomadas.get())

        chuveiro_kw = float(entry_chuveiro.get())
        torneira_kw = float(entry_torneira.get())

        chuveiros_apto = int(entry_qtd_chuveiros.get())
        torneiras_apto = int(entry_qtd_torneiras.get())

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
        total_chuveiros = (aptos * chuveiros_apto)

        f_ch = fator_aparelho("chuveiro_torneira_ferro", total_chuveiros)

        D2a = (
            aptos * chuveiros_apto * chuveiro_kw * f_ch +
            aptos * torneiras_apto * torneira_kw * f_ch
        )

        D2 = D2a

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

        Dapt = (D1a + D2) * f_sim
        Dadm = D1b + D3

        Dg = Dapt + Dadm

        # -------------------------
        # RESULTADO
        # -------------------------
        txt_resultado.delete("1.0", tk.END)

        txt_resultado.insert(tk.END, f"""
1 - ILUMINAÇÃO
D1 = {D1:.2f} kVA

2 - APARELHOS
D2 = {D2:.2f} kVA

3 - MOTORES
D3 = {D3:.2f} kVA

4 - DEMANDA GERAL
Dg = {Dg:.2f} kVA
""")

    except Exception as e:
        messagebox.showerror("Erro", str(e))


# -----------------------------------
# INTERFACE
# -----------------------------------

janela = tk.Tk()
janela.title("GED119 - Cálculo de Demanda")
janela.geometry("800x600")

notebook = ttk.Notebook(janela)
notebook.pack(fill="both", expand=True)

# -----------------------------------
# ABA 1 - DADOS
# -----------------------------------

aba1 = ttk.Frame(notebook)
notebook.add(aba1, text="Dados")

def criar(label, linha):
    ttk.Label(aba1, text=label).grid(row=linha, column=0)
    e = ttk.Entry(aba1)
    e.grid(row=linha, column=1)
    return e

entry_aptos = criar("Aptos", 0)
entry_area_apto = criar("Área Apto", 1)
entry_area_adm = criar("Área Adm", 2)

entry_iluminacao = criar("Iluminação W", 3)
entry_tomadas = criar("Tomadas W", 4)

entry_chuveiro = criar("Chuveiro kW", 5)
entry_torneira = criar("Torneira kW", 6)

entry_qtd_chuveiros = criar("Qtd Chuveiros", 7)
entry_qtd_torneiras = criar("Qtd Torneiras", 8)

# -----------------------------------
# ABA 2 - MOTORES
# -----------------------------------

aba2 = ttk.Frame(notebook)
notebook.add(aba2, text="Motores")

entry_cv = ttk.Entry(aba2)
entry_cv.grid(row=0, column=0)

entry_qtd_motor = ttk.Entry(aba2)
entry_qtd_motor.grid(row=0, column=1)

btn_add = ttk.Button(aba2, text="Adicionar", command=adicionar_motor)
btn_add.grid(row=0, column=2)

# Frame para tabela
frame_tabela = ttk.Frame(aba2)
frame_tabela.grid(row=1, column=0, columnspan=3, sticky="nsew")

# Ajustar expansão
aba2.rowconfigure(1, weight=1)
aba2.columnconfigure(0, weight=1)

# Treeview dentro do frame
lista_motores = ttk.Treeview(frame_tabela, columns=("cv", "qtd"), show="headings")

lista_motores.heading("cv", text="CV")
lista_motores.heading("qtd", text="Qtd")

lista_motores.pack(fill="both", expand=True)
# -----------------------------------
# ABA 3 - RESULTADO
# -----------------------------------

aba3 = ttk.Frame(notebook)
notebook.add(aba3, text="Resultado")

btn_calc = ttk.Button(aba3, text="Calcular", command=calcular)
btn_calc.pack(pady=10)

txt_resultado = tk.Text(aba3, height=20)
txt_resultado.pack(fill="both", expand=True)

# -----------------------------------
# START
# -----------------------------------

janela.mainloop()