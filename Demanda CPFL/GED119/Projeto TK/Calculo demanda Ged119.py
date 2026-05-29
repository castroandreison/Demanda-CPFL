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

        total_chuveiros_geral = aptos * chuveiros_apto
        total_torneiras_geral = aptos * torneiras_apto

        txt_resultado.insert(tk.END, "   Total de chuveiros: {} aptos x {} = {}\n".format(aptos, chuveiros_apto, total_chuveiros_geral))
        txt_resultado.insert(tk.END, "   Total de torneiras: {} aptos x {} = {}\n".format(aptos, torneiras_apto, total_torneiras_geral))
        txt_resultado.insert(tk.END, "   Total de aparelhos (chuveiros + torneiras) = {} + {} = {}\n".format(total_chuveiros_geral, total_torneiras_geral, total_chuveiros))
        txt_resultado.insert(tk.END, "   FD conforme Tabela 2 (chuveiro_torneira_ferro): para {} aparelhos = {:.2f}\n\n".format(total_chuveiros, f_ch))

        txt_resultado.insert(tk.END, "   Chuveiros:\n")
        txt_resultado.insert(tk.END, "      = {} aptos x {} un x {:.1f} kW x {:.2f}\n".format(aptos, chuveiros_apto, chuveiro_kw, f_ch))
        chuveiros_contrib = aptos * chuveiros_apto * chuveiro_kw * f_ch
        txt_resultado.insert(tk.END, "      = {:.2f} kVA\n".format(chuveiros_contrib))

        txt_resultado.insert(tk.END, "   Torneiras:\n")
        txt_resultado.insert(tk.END, "      = {} aptos x {} un x {:.1f} kW x {:.2f}\n".format(aptos, torneiras_apto, torneira_kw, f_ch))
        torneiras_contrib = aptos * torneiras_apto * torneira_kw * f_ch
        txt_resultado.insert(tk.END, "      = {:.2f} kVA\n".format(torneiras_contrib))

        txt_resultado.insert(tk.END, "\n   D2 = {:.2f} + {:.2f} = {:.2f} kVA\n\n".format(chuveiros_contrib, torneiras_contrib, D2))

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
        txt_resultado.insert(tk.END, "      Dapt = (D1a + D2) x Fator de Simultaneidade\n")
        txt_resultado.insert(tk.END, "      Dadm = D1b + D3\n\n")

        txt_resultado.insert(tk.END, "   Fator de simultaneidade (Tabela 7):\n")
        txt_resultado.insert(tk.END, "      Para {} apartamentos = {:.2f}\n\n".format(aptos, f_sim))

        txt_resultado.insert(tk.END, "   Dapt = (D1a + D2) x F.Sim\n")
        txt_resultado.insert(tk.END, "   Dapt = ({:.2f} + {:.2f}) x {:.2f}\n".format(D1a, D2, f_sim))
        txt_resultado.insert(tk.END, "   Dapt = {:.2f} x {:.2f}\n".format(D1a + D2, f_sim))
        txt_resultado.insert(tk.END, "   Dapt = {:.2f} kVA\n\n".format(Dapt))

        txt_resultado.insert(tk.END, "   Dadm = D1b + D3\n")
        txt_resultado.insert(tk.END, "   Dadm = {:.2f} + {:.2f}\n".format(D1b, D3))
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

        txt_resultado.insert(tk.END, "  D1 (Iluminação)  = {:.2f} kVA\n".format(D1))
        txt_resultado.insert(tk.END, "  D2 (Aparelhos)   = {:.2f} kVA\n".format(D2))
        txt_resultado.insert(tk.END, "  D3 (Motores)     = {:.2f} kVA\n".format(D3))
        txt_resultado.insert(tk.END, "  ---------------------------------\n")
        txt_resultado.insert(tk.END, "  Dg (Demanda Geral) = {:.2f} kVA\n".format(Dg))

        txt_resultado.insert(tk.END, "\n" + "=" * 55 + "\n")
        txt_resultado.insert(tk.END, "  DEMANDA TOTAL (Dg): {:.2f} kVA\n".format(Dg))
        txt_resultado.insert(tk.END, "=" * 55 + "\n")

    except Exception as e:
        messagebox.showerror("Erro", "Verifique os dados inseridos!\n{}".format(str(e)))


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

aba1 = ttk.Frame(notebook)
notebook.add(aba1, text="Dados do Edifício")

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
# START
# -----------------------------------

janela.mainloop()
