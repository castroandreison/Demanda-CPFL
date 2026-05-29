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
caminho_proj = r"C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\Ged13\Projeto TK\projetos.db"
caminho_ged = r"C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\Ged13\DB13\databaseCPFLGed13.db"

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
# FUNÇÕES DE MANIPULAÇÃO DE DADOS
# =================================================

def adicionar_carga():
    # Determinar qual aba está ativa
    aba_atual = notebook.index(notebook.select())
    
    # Mapear índices para as variáveis corretas
    entradas = [
        (entry_nome_geral, entry_potencia_geral),
        (entry_nome_chuveiros, entry_potencia_chuveiros),
        (entry_nome_eletro, entry_potencia_eletro),
        (entry_nome_ar, entry_potencia_ar),
        (entry_nome_motor, entry_potencia_motor)
    ]
    
    entry_nome, entry_potencia = entradas[aba_atual]
    
    nome = entry_nome.get().strip()
    potencia = entry_potencia.get().strip()
    
    if not nome or not potencia:
        messagebox.showwarning("Aviso", "Preencha todos os campos!")
        return
    
    try:
        potencia_float = float(potencia)
        if potencia_float <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Aviso", "Potência deve ser um número positivo!")
        return
    
    # Inserir no banco de dados
    cursor_proj.execute("INSERT INTO cargas (nome, potencia) VALUES (?, ?)", (nome, potencia))
    conn_proj.commit()
    
    # Limpar campos
    entry_nome.delete(0, tk.END)
    entry_potencia.delete(0, tk.END)
    
    # Recarregar a lista correspondente
    carregar_por_aba(aba_atual)

def excluir_carga():
    # Determinar qual aba está ativa
    aba_atual = notebook.index(notebook.select())
    
    # Mapear índices para as árvores corretas
    arvores = [tree_geral, tree_chuveiros, tree_eletro, tree_ar, tree_motor]
    tree_atual = arvores[aba_atual]
    
    selecionado = tree_atual.selection()
    if not selecionado:
        messagebox.showwarning("Aviso", "Selecione uma carga para excluir!")
        return
    
    item = selecionado[0]
    valores = tree_atual.item(item)["values"]
    nome = valores[0]
    
    # Confirmar exclusão
    if messagebox.askyesno("Confirmar", f"Excluir a carga '{nome}'?"):
        # Excluir do banco de dados
        cursor_proj.execute("DELETE FROM cargas WHERE nome = ?", (nome,))
        conn_proj.commit()
        
        # Recarregar a lista correspondente
        carregar_por_aba(aba_atual)

def carregar_detalhes_selecionado(event):
    """Carrega os detalhes da carga selecionada nos campos de entrada"""
    # Determinar qual aba está ativa
    aba_atual = notebook.index(notebook.select())
    
    # Mapear índices para as árvores e entradas corretas
    arvores = [tree_geral, tree_chuveiros, tree_eletro, tree_ar, tree_motor]
    entradas = [
        (entry_nome_geral, entry_potencia_geral),
        (entry_nome_chuveiros, entry_potencia_chuveiros),
        (entry_nome_eletro, entry_potencia_eletro),
        (entry_nome_ar, entry_potencia_ar),
        (entry_nome_motor, entry_potencia_motor)
    ]
    
    tree_atual = arvores[aba_atual]
    entry_nome, entry_potencia = entradas[aba_atual]
    
    selecionado = tree_atual.selection()
    if selecionado:
        item = selecionado[0]
        valores = tree_atual.item(item)["values"]
        # Limpar campos atuais
        entry_nome.delete(0, tk.END)
        entry_potencia.delete(0, tk.END)
        # Inserir valores da carga selecionada
        entry_nome.insert(0, valores[0])  # Nome
        entry_potencia.insert(0, valores[1])  # Potência

def editar(event):
    # Determinar qual aba está ativa
    aba_atual = notebook.index(notebook.select())
    
    # Mapear índices para as árvores corretas
    arvores = [tree_geral, tree_chuveiros, tree_eletro, tree_ar, tree_motor]
    tree_atual = arvores[aba_atual]
    
    item = tree_atual.selection()[0]
    col = tree_atual.identify_column(event.x)
    
    # Get the column name from the column identifier
    col_name = tree_atual.heading(col, "text") if col else None
    
    if col_name:  # Only proceed if we clicked on a column header
        x, y, w, h = tree_atual.bbox(item, col)
        
        entry = tk.Entry(janela)
        entry.place(x=x, y=y, width=w)
        
        # Set the current value in the entry field
        current_value = tree_atual.set(item, col)
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()
        
        def salvar(e):
            novo_valor = entry.get()
            tree_atual.set(item, col, novo_valor)
            entry.destroy()
        
        def cancelar(e):
            entry.destroy()
            
        entry.bind("<Return>", salvar)
        entry.bind("<Escape>", cancelar)
        entry.bind("<FocusOut>", lambda e: entry.destroy())  # Destroy when losing focus

# =================================================
# INTERFACE
# =================================================

janela = tk.Tk()
janela.title("GED-13 Completo")
janela.geometry("1200x800")

# Notebook para abas categorizadas
notebook = ttk.Notebook(janela)
notebook.pack(fill="both", expand=True, padx=10, pady=10)

# Aba Geral (Tomadas e Iluminação)
frame_geral = ttk.Frame(notebook)
notebook.add(frame_geral, text="Geral")

# Aba Chuveiros e Aquecimento
frame_chuveiros = ttk.Frame(notebook)
notebook.add(frame_chuveiros, text="Chuveiros/Aquecimento")

# Aba Eletrodomésticos
frame_eletro = ttk.Frame(notebook)
notebook.add(frame_eletro, text="Eletrodomésticos")

# Aba Ar Condicionado
frame_ar = ttk.Frame(notebook)
notebook.add(frame_ar, text="Ar Condicionado")

# Aba Motores
frame_motor = ttk.Frame(notebook)
notebook.add(frame_motor, text="Motores")

# Função para criar interface de carga em cada aba
def criar_interface_carga(frame, titulo):
    # Frame para entrada de dados
    frame_input = tk.Frame(frame)
    frame_input.pack(pady=10, padx=10, fill="x")
    
    tk.Label(frame_input, text=f"Nome da Carga ({titulo}):").grid(row=0, column=0, padx=5)
    entry_nome = tk.Entry(frame_input, width=20)
    entry_nome.grid(row=0, column=1, padx=5)
    
    tk.Label(frame_input, text="Potência (W):").grid(row=0, column=2, padx=5)
    entry_potencia = tk.Entry(frame_input, width=10)
    entry_potencia.grid(row=0, column=3, padx=5)
    
    tk.Button(frame_input, text="Adicionar Carga", command=adicionar_carga).grid(row=0, column=4, padx=5)
    tk.Button(frame_input, text="Excluir Carga", command=excluir_carga).grid(row=0, column=5, padx=5)
    
    cols = ("Nome", "Potência (W)", "Qtd")
    tree = ttk.Treeview(frame, columns=cols, show="headings")
    
    for col in cols:
        tree.heading(col, text=col)
    
    tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    return frame_input, entry_nome, entry_potencia, tree

# Criar interfaces para cada aba
frame_input_geral, entry_nome_geral, entry_potencia_geral, tree_geral = criar_interface_carga(frame_geral, "Geral")
frame_input_chuveiros, entry_nome_chuveiros, entry_potencia_chuveiros, tree_chuveiros = criar_interface_carga(frame_chuveiros, "Chuveiros/Aquecimento")
frame_input_eletro, entry_nome_eletro, entry_potencia_eletro, tree_eletro = criar_interface_carga(frame_eletro, "Eletrodomésticos")
frame_input_ar, entry_nome_ar, entry_potencia_ar, tree_ar = criar_interface_carga(frame_ar, "Ar Condicionado")
frame_input_motor, entry_nome_motor, entry_potencia_motor, tree_motor = criar_interface_carga(frame_motor, "Motores")

# =================================================
# FUNÇÕES DE CARREGAMENTO
# =================================================

def carregar():
    """Carrega todas as cargas em todas as abas"""
    carregar_por_aba(0)  # Geral
    carregar_por_aba(1)  # Chuveiros/Aquecimento
    carregar_por_aba(2)  # Eletrodomésticos
    carregar_por_aba(3)  # Ar Condicionado
    carregar_por_aba(4)  # Motores

def carregar_por_aba(aba_index):
    """Carrega as cargas de uma aba específica com base no tipo"""
    # Mapear índices de aba para tipos de carga
    tipos_por_aba = {
        0: ["geral"],  # Geral
        1: ["chuveiro"],  # Chuveiros/Aquecimento
        2: ["eletro"],  # Eletrodomésticos
        3: ["ar"],  # Ar Condicionado
        4: ["motor"]  # Motores
    }
    
    # Mapear índices de aba para árvores corretas
    arvores = [tree_geral, tree_chuveiros, tree_eletro, tree_ar, tree_motor]
    tree_atual = arvores[aba_index]
    
    # Limpar a árvore atual
    tree_atual.delete(*tree_atual.get_children())
    
    # Buscar cargas do tipo específico
    tipos = tipos_por_aba[aba_index]
    placeholders = ','.join(['?' for _ in tipos])
    query = f"SELECT nome,potencia FROM cargas WHERE tipo IN ({placeholders})"
    cursor_proj.execute(query, tipos)
    
    for nome, pot in cursor_proj.fetchall():
        tree_atual.insert("", "end", values=(nome, float(pot), 1))

# Carregar inicialmente
carregar()

# Bind events para cada árvore
tree_geral.bind("<Double-1>", editar)
tree_geral.bind("<<TreeviewSelect>>", carregar_detalhes_selecionado)
tree_chuveiros.bind("<Double-1>", editar)
tree_chuveiros.bind("<<TreeviewSelect>>", carregar_detalhes_selecionado)
tree_eletro.bind("<Double-1>", editar)
tree_eletro.bind("<<TreeviewSelect>>", carregar_detalhes_selecionado)
tree_ar.bind("<Double-1>", editar)
tree_ar.bind("<<TreeviewSelect>>", carregar_detalhes_selecionado)
tree_motor.bind("<Double-1>", editar)
tree_motor.bind("<<TreeviewSelect>>", carregar_detalhes_selecionado)

# =================================================
# SAÍDA
# =================================================

saida = tk.Text(janela, height=20)
saida.pack(fill="x", padx=10, pady=10)

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
    
    # Coletar dados de todas as árvores
    arvores = [tree_geral, tree_chuveiros, tree_eletro, tree_ar, tree_motor]
    
    for tree_atual in arvores:
        for item in tree_atual.get_children():
            nome, pot, qtd = tree_atual.item(item)["values"]
            
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

# botão calcular (os botões de adicionar/excluir já estão em cada aba)
tk.Button(janela, text="Calcular GED Completo", command=calcular).pack(pady=10)

# loop
janela.mainloop()