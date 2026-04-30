import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import math
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

# =================================================
# CAMINHOS DOS BANCOS
# =================================================
caminho_proj = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\Jupyter\Ged13\Projeto TK\projetos.db"
caminho_ged = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed13.db"

os.makedirs(os.path.dirname(caminho_proj), exist_ok=True)

conn_proj = sqlite3.connect(caminho_proj)
cursor_proj = conn_proj.cursor()

conn_ged = sqlite3.connect(caminho_ged)
cursor_ged = conn_ged.cursor()

print("Bancos conectados com sucesso")

# =================================================
# FUNÇÕES GED
# =================================================

def fd_kw(valor):
    cursor_ged.execute("""
        SELECT fator_demanda
        FROM tabela3
        WHERE ? BETWEEN carga_min_kw AND carga_max_kw
        LIMIT 1
    """, (valor,))
    r = cursor_ged.fetchone()
    return float(r[0]) if r else 1


def fd_qtd_exata(qtd):
    cursor_ged.execute("""
        SELECT fator_demanda
        FROM tabela4
        WHERE numero_aparelhos = ?
        LIMIT 1
    """, (qtd,))
    r = cursor_ged.fetchone()
    return float(r[0]) if r else 1


def fd_qtd_faixa(qtd):
    cursor_ged.execute("""
        SELECT fator_demanda
        FROM tabela6
        WHERE ? BETWEEN qtd_min AND qtd_max
        LIMIT 1
    """, (qtd,))
    r = cursor_ged.fetchone()
    return float(r[0]) if r else 1


def get_valor(tabela, campo_busca, valor, campo_saida):
    cursor_ged.execute(f"""
        SELECT {campo_saida}
        FROM {tabela}
        WHERE {campo_busca} = ?
        LIMIT 1
    """, (valor,))
    r = cursor_ged.fetchone()
    return float(r[0]) if r else 0


def get_categoria(D):
    # MONO
    cursor_ged.execute("""
    SELECT categoria FROM tabela1a_monofasico
    WHERE ? BETWEEN carga_min_kw AND carga_max_kw
    """, (D,))
    mono = cursor_ged.fetchone()
    mono = mono[0] if mono else None

    # BI
    cursor_ged.execute("""
    SELECT categoria FROM tabela1b_bifasico
    WHERE ? BETWEEN carga_min_kw AND carga_max_kw
    """, (D,))
    bi = cursor_ged.fetchone()
    bi = bi[0] if bi else None

    # TRI
    cursor_ged.execute("""
    SELECT categoria FROM tabela1c_trifasico_127_220
    WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva
    """, (D,))
    tri = cursor_ged.fetchone()
    tri = tri[0] if tri else None

    return mono, bi, tri


# =================================================
# INTERFACE
# =================================================

janela = tk.Tk()
janela.title("GED-13 Completo")
janela.geometry("1000x700")

cols = ("Nome", "Potência (W)", "Qtd")
tree = ttk.Treeview(janela, columns=cols, show="headings")

for col in cols:
    tree.heading(col, text=col)

tree.pack(fill="both", expand=True)

# =================================================
# CARREGAR CARGAS
# =================================================

def carregar():
    tree.delete(*tree.get_children())
    cursor_proj.execute("SELECT nome,potencia FROM cargas")

    for nome, pot in cursor_proj.fetchall():
        tree.insert("", "end", values=(nome, float(pot), 1))

carregar()

# =================================================
# EDITAR
# =================================================

def editar(event):
    item = tree.selection()[0]
    col = tree.identify_column(event.x)

    if col == "#3":
        x, y, w, h = tree.bbox(item, col)

        entry = tk.Entry(janela)
        entry.place(x=x, y=y, width=w)

        def salvar(e):
            tree.set(item, "Qtd", entry.get())
            entry.destroy()

        entry.bind("<Return>", salvar)

tree.bind("<Double-1>", editar)

# =================================================
# SAÍDA
# =================================================

saida = tk.Text(janela, height=20)
saida.pack(fill="x")

# =================================================
# CÁLCULO COMPLETO GED
# =================================================
def calcular():
    
    saida.delete("1.0", tk.END)

    saida.insert(tk.END, "GED-13 - MEMORIAL COMPLETO\n")
    saida.insert(tk.END, "==============================\n\n")

    # =================================================
    # SEPARAÇÃO DE CARGAS AUTOMÁTICA
    # =================================================
    tomadas = 0
    iluminacao = 0
    chuveiros = 0
    torneira = 0
    ferro = 0
    eletro = 0
    ar_qtd = 0
    motores_qtd = 0

    for item in tree.get_children():
        nome, pot, qtd = tree.item(item)["values"]

        try:
            pot = float(pot)
            qtd = int(qtd)
        except:
            continue

        total = pot * qtd

        if "Tomada" in nome:
            tomadas += total
        elif "Iluminação" in nome:
            iluminacao += total
        elif "Chuveiro" in nome:
            chuveiros += total
        elif "Torneira" in nome:
            torneira += total
        elif "Ferro" in nome:
            ferro += total
        elif "Ar" in nome:
            ar_qtd += qtd
        elif "Motor" in nome:
            motores_qtd += qtd
        else:
            eletro += total

    # =================================================
    # 🔹 A - TOMADAS + ILUMINAÇÃO
    # =================================================
    saida.insert(tk.END, "🔹 TOMADAS + ILUMINAÇÃO\n")

    saida.insert(tk.END, f"Tomadas = {tomadas:.0f} W\n")
    saida.insert(tk.END, f"Iluminação = {iluminacao:.0f} W\n")

    carga_a = (tomadas + iluminacao) / 1000
    fdA = fd_kw(carga_a)
    A = carga_a * fdA

    saida.insert(tk.END, f"A base = {carga_a:.2f} kW\n")
    saida.insert(tk.END, f"FD A = {fdA}\n")
    saida.insert(tk.END, f"A = {A:.2f} kVA\n\n")

    # =================================================
    # 🔹 B - CHUVEIROS / TORNEIRA / FERRO
    # =================================================
    saida.insert(tk.END, "🔹 CHUVEIROS / TORNEIRA / FERRO\n")

    saida.insert(tk.END, f"Chuveiros = {chuveiros:.0f} W\n")
    saida.insert(tk.END, f"Torneira = {torneira:.0f} W\n")
    saida.insert(tk.END, f"Ferro = {ferro:.0f} W\n")

    carga_b = (chuveiros + torneira + ferro) / 1000
    qtd_b = (chuveiros > 0) + (torneira > 0) + (ferro > 0)
    fdB = fd_qtd_exata(qtd_b if qtd_b else 1)
    B = carga_b * fdB

    saida.insert(tk.END, f"B base = {carga_b:.2f} kW\n")
    saida.insert(tk.END, f"FD B = {fdB}\n")
    saida.insert(tk.END, f"B = {B:.2f} kVA\n\n")

    # =================================================
    # 🔹 D - ELETRODOMÉSTICOS
    # =================================================
    saida.insert(tk.END, "🔹 ELETRODOMÉSTICOS\n")

    saida.insert(tk.END, f"Total eletrodomésticos = {eletro:.0f} W\n")

    carga_d = eletro / 1000
    fdD = fd_qtd_faixa(3)  # ajuste depois se quiser automático por qtd real
    Dd = carga_d * fdD

    saida.insert(tk.END, f"D base = {carga_d:.2f} kW\n")
    saida.insert(tk.END, f"FD D = {fdD}\n")
    saida.insert(tk.END, f"D = {Dd:.2f} kVA\n\n")

    # =================================================
    # 🔹 F - AR CONDICIONADO
    # =================================================
    saida.insert(tk.END, "🔹 AR CONDICIONADO\n")

    va_ar = get_valor("tabela8", "btu_h", 14000, "potencia_va")

    saida.insert(tk.END, f"Ar-condicionado unitário = {va_ar:.0f} VA\n")
    saida.insert(tk.END, f"Quantidade = {ar_qtd}\n")

    F = (va_ar * ar_qtd) / 1000

    saida.insert(tk.END, f"F = {F:.2f} kVA\n\n")

    # =================================================
    # 🔹 G - MOTORES
    # =================================================
    saida.insert(tk.END, "🔹 MOTORES\n")

    motor_kva = get_valor("tabela_14", "potencia_nominal", "1", "potencia_kva")

    saida.insert(tk.END, f"Motor unitário = {motor_kva:.2f} kVA\n")
    saida.insert(tk.END, f"Quantidade = {motores_qtd}\n")

    if motores_qtd >= 2:
        G = motor_kva * 1 + motor_kva * 0.9
    else:
        G = motor_kva

    saida.insert(tk.END, f"G = {G:.2f} kVA\n\n")

    # =================================================
    # 📊 DEMANDA TOTAL
    # =================================================
    saida.insert(tk.END, "==============================\n")
    saida.insert(tk.END, "📊 DEMANDA TOTAL\n")
    saida.insert(tk.END, "==============================\n")

    D_total = A + B + Dd + F + G

    saida.insert(tk.END, f"A = {A:.2f} kVA\n")
    saida.insert(tk.END, f"B = {B:.2f} kVA\n")
    saida.insert(tk.END, f"D = {Dd:.2f} kVA\n")
    saida.insert(tk.END, f"F = {F:.2f} kVA\n")
    saida.insert(tk.END, f"G = {G:.2f} kVA\n\n")

    saida.insert(tk.END, "==============================\n")
    saida.insert(tk.END, "👉 RESULTADO FINAL\n")
    saida.insert(tk.END, "==============================\n")

    saida.insert(tk.END, f"Demanda Total = {D_total:.2f} kVA\n\n")

    # =================================================
    # 🔹 CARGA INSTALADA
    # =================================================
    carga_instalada = carga_a + carga_b + carga_d + F + G

    saida.insert(tk.END, "🔹 CARGA INSTALADA TOTAL\n")
    saida.insert(tk.END, f"Carga Instalada = {carga_instalada:.2f} kW\n\n")

    # =================================================
    # 🔹 ENQUADRAMENTO
    # =================================================
    mono, bi, tri = get_categoria(D_total)

    saida.insert(tk.END, "🔹 ENQUADRAMENTO PADRÃO DE ENTRADA (TABELA 1)\n")

    saida.insert(tk.END, f"Monofásico → Categoria {mono if mono else 'Não permitido'}\n")
    saida.insert(tk.END, f"Bifásico → Categoria {bi if bi else 'Não permitido'}\n")
    saida.insert(tk.END, f"Trifásico → Categoria {tri if tri else 'Não definido'}\n")

    # =================================================
    # 🔌 PADRÃO DE ENTRADA
    # =================================================
    cursor_ged.execute("""
    SELECT categoria,cobre_mm2,aluminio_mm2,eletroduto,disjuntor,
           aterramento_condutor,poste,caixa,motor_fn,motor_ff,motor_fff
    FROM tabela1c_trifasico_127_220
    WHERE ? BETWEEN demanda_min_kva AND demanda_max_kva
    """, (D_total,))

    padrao = cursor_ged.fetchone()

    if padrao:
        saida.insert(tk.END, "\n==============================\n")
        saida.insert(tk.END, "🔌 PADRÃO DE ENTRADA\n")
        saida.insert(tk.END, "==============================\n")

        saida.insert(tk.END, f"Demanda Total = {D_total:.2f} kVA\n\n")

        saida.insert(tk.END, "Tipo de ligação: TRIFÁSICO\n")
        saida.insert(tk.END, f"Categoria: {padrao[0]}\n")
        saida.insert(tk.END, f"Cabo cobre: {padrao[1]}\n")
        saida.insert(tk.END, f"Cabo alumínio: {padrao[2]}\n")
        saida.insert(tk.END, f"Eletroduto: {padrao[3]}\n")
        saida.insert(tk.END, f"Disjuntor: {padrao[4]}\n")
        saida.insert(tk.END, f"Aterramento: {padrao[5]}\n")
        saida.insert(tk.END, f"Poste padrão: {padrao[6]}\n")
        saida.insert(tk.END, f"Caixa de medição: {padrao[7]}\n")
        saida.insert(tk.END, f"Motor FN máx: {padrao[8]}\n")
        saida.insert(tk.END, f"Motor FF máx: {padrao[9]}\n")
        saida.insert(tk.END, f"Motor FFF máx: {padrao[10]}\n")

# botão
tk.Button(janela, text="Calcular GED Completo", command=calcular).pack()

# loop
janela.mainloop()