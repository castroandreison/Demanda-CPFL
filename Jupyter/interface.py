import tkinter as tk
from tkinter import ttk, messagebox
import database_manager as db
from dimensionamento import selecionar_transformador


class SistemaGED:

    def __init__(self, root):

        self.root = root
        self.root.title("Sistema GED119")

        self.projeto_atual = None
        self.carga_atual = None

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.aba_projetos = ttk.Frame(notebook)
        self.aba_edificio = ttk.Frame(notebook)
        self.aba_cargas = ttk.Frame(notebook)
        self.aba_demanda = ttk.Frame(notebook)

        notebook.add(self.aba_projetos, text="Projetos")
        notebook.add(self.aba_edificio, text="Edifício")
        notebook.add(self.aba_cargas, text="Cargas")
        notebook.add(self.aba_demanda, text="Demanda")

        self.tela_projetos()
        self.tela_edificio()
        self.tela_cargas()
        self.tela_demanda()

    # ==================================================
    # PROJETOS
    # ==================================================

    def tela_projetos(self):

        frame = ttk.Frame(self.aba_projetos, padding=10)
        frame.pack()

        ttk.Label(frame, text="Nome").grid(row=0, column=0)
        self.nome = ttk.Entry(frame)
        self.nome.grid(row=0, column=1)

        ttk.Label(frame, text="Cliente").grid(row=1, column=0)
        self.cliente = ttk.Entry(frame)
        self.cliente.grid(row=1, column=1)

        ttk.Label(frame, text="Endereço").grid(row=2, column=0)
        self.endereco = ttk.Entry(frame)
        self.endereco.grid(row=2, column=1)

        ttk.Label(frame, text="Área").grid(row=3, column=0)
        self.area = ttk.Entry(frame)
        self.area.grid(row=3, column=1)

        ttk.Label(frame, text="Tipo").grid(row=4, column=0)
        self.tipo = ttk.Combobox(frame, values=[
            "Residencial", "Comercial", "Industrial"
        ])
        self.tipo.grid(row=4, column=1)

        ttk.Button(frame, text="Adicionar", command=self.adicionar_projeto).grid(row=5, column=0, columnspan=2)

        self.tree_proj = ttk.Treeview(frame, columns=("id", "nome", "cliente", "area"), show="headings")

        for c in ("id", "nome", "cliente", "area"):
            self.tree_proj.heading(c, text=c)

        self.tree_proj.grid(row=6, column=0, columnspan=2)

        self.tree_proj.bind("<<TreeviewSelect>>", self.on_select_projeto)

        ttk.Button(frame, text="Editar", command=self.editar_projeto).grid(row=7, column=0)
        ttk.Button(frame, text="Excluir", command=self.excluir_projeto).grid(row=7, column=1)

        self.carregar_projetos()

    def carregar_projetos(self):

        self.tree_proj.delete(*self.tree_proj.get_children())

        for p in db.listar_projetos():
            self.tree_proj.insert("", "end", values=(p[0], p[1], p[2], p[5]))

    def adicionar_projeto(self):

        db.adicionar_projeto(
            self.nome.get(),
            self.cliente.get(),
            self.endereco.get(),
            self.area.get(),
            self.tipo.get()
        )

        self.carregar_projetos()

    def on_select_projeto(self, event):

        item = self.tree_proj.selection()
        if not item:
            return

        valores = self.tree_proj.item(item[0])["values"]

        self.projeto_atual = valores[0]

        self.nome.delete(0, tk.END)
        self.nome.insert(0, valores[1])

        self.cliente.delete(0, tk.END)
        self.cliente.insert(0, valores[2])

        self.area.delete(0, tk.END)
        self.area.insert(0, valores[3])

        self.carregar_cargas()

    def editar_projeto(self):

        if not self.projeto_atual:
            return

        db.atualizar_projeto(
            self.projeto_atual,
            self.nome.get(),
            self.cliente.get(),
            self.endereco.get(),
            self.area.get(),
            self.tipo.get()
        )

        self.carregar_projetos()

    def excluir_projeto(self):

        if not self.projeto_atual:
            return

        db.deletar_projeto(self.projeto_atual)

        self.projeto_atual = None

        self.carregar_projetos()

    # ==================================================
    # EDIFÍCIO
    # ==================================================

    def tela_edificio(self):

        frame = ttk.Frame(self.aba_edificio, padding=10)
        frame.pack()

        ttk.Label(frame, text="Adm m²").grid(row=0, column=0)
        self.adm = ttk.Entry(frame)
        self.adm.grid(row=0, column=1)

        ttk.Label(frame, text="Apto m²").grid(row=1, column=0)
        self.apto = ttk.Entry(frame)
        self.apto.grid(row=1, column=1)

        ttk.Label(frame, text="Qtd Aptos").grid(row=2, column=0)
        self.qtd_ap = ttk.Entry(frame)
        self.qtd_ap.grid(row=2, column=1)

        ttk.Button(frame, text="Salvar", command=self.salvar_edificio).grid(row=3, column=0, columnspan=2)

    def salvar_edificio(self):

        if not self.projeto_atual:
            return

        db.salvar_edificio(
            self.projeto_atual,
            self.adm.get(),
            self.apto.get(),
            self.qtd_ap.get()
        )

        messagebox.showinfo("OK", "Salvo")

    # ==================================================
    # CARGAS
    # ==================================================

    def tela_cargas(self):
        
        frame = ttk.Frame(self.aba_cargas, padding=10)
        frame.pack()

        # ======================
        # CAMPOS
        # ======================

        ttk.Label(frame, text="Desc").grid(row=0, column=0)
        self.desc = ttk.Entry(frame)
        self.desc.grid(row=0, column=1)

        ttk.Label(frame, text="kW").grid(row=1, column=0)
        self.pot = ttk.Entry(frame)
        self.pot.grid(row=1, column=1)

        ttk.Label(frame, text="Qtd").grid(row=2, column=0)
        self.qtd = ttk.Entry(frame)
        self.qtd.grid(row=2, column=1)

        ttk.Label(frame, text="Cat").grid(row=3, column=0)
        self.cat = ttk.Combobox(frame, values=["Iluminacao", "Tomadas", "Motor"])
        self.cat.grid(row=3, column=1)

        ttk.Label(frame, text="Tipo Carga").grid(row=4, column=0)
        self.tipo_carga = ttk.Combobox(frame, values=["APTO", "ADM"])
        self.tipo_carga.grid(row=4, column=1)

        ttk.Button(frame, text="Add", command=self.adicionar_carga).grid(row=5, column=0)
        ttk.Button(frame, text="Edit", command=self.editar_carga).grid(row=5, column=1)
        ttk.Button(frame, text="Del", command=self.excluir_carga).grid(row=5, column=2)

    # ======================
    # APTO
    # ======================

        ttk.Label(frame, text="Cargas APTO").grid(row=6, column=0, columnspan=3)

        self.tree_apto = ttk.Treeview(frame,
            columns=("id", "desc", "pot", "qtd", "cat"),
            show="headings")

        for c in ("id", "desc", "pot", "qtd", "cat"):
            self.tree_apto.heading(c, text=c)

        self.tree_apto.grid(row=7, column=0, columnspan=3)

        self.tree_apto.bind("<<TreeviewSelect>>", self.on_select_carga)

    # ======================
    # ADM
    # ======================

        ttk.Label(frame, text="Cargas ADM").grid(row=8, column=0, columnspan=3)

        self.tree_adm = ttk.Treeview(frame,
            columns=("id", "desc", "pot", "qtd", "cat"),
            show="headings")

        for c in ("id", "desc", "pot", "qtd", "cat"):
            self.tree_adm.heading(c, text=c)

        self.tree_adm.grid(row=9, column=0, columnspan=3)

        self.tree_adm.bind("<<TreeviewSelect>>", self.on_select_carga)

        self.carregar_cargas()
        
    
    
    
    
    def carregar_cargas(self):
        
        if not self.projeto_atual:
            return

        self.tree_apto.delete(*self.tree_apto.get_children())
        self.tree_adm.delete(*self.tree_adm.get_children())

        dados_apto = db.listar_cargas_tipo(self.projeto_atual, "APTO")
        dados_adm = db.listar_cargas_tipo(self.projeto_atual, "ADM")

        for d in dados_apto:
            self.tree_apto.insert("", "end", values=d)

        for d in dados_adm:
            self.tree_adm.insert("", "end", values=d)
            
            
        
        
    def adicionar_carga(self):
        
        if not self.projeto_atual:
            return

        if not self.tipo_carga.get():
            messagebox.showwarning("Aviso", "Selecione o tipo de carga (APTO ou ADM)")
            return

        db.adicionar_carga(
            self.projeto_atual,
            self.desc.get(),
            self.pot.get(),
            self.qtd.get(),
            self.cat.get(),
            self.tipo_carga.get()
        )

        self.carregar_cargas()

    def on_select_carga(self, event):
        
        tree = event.widget
        item = tree.selection()

        if not item:
            return

        v = tree.item(item[0])["values"]

        self.carga_atual = v[0]

        self.desc.delete(0, tk.END)
        self.desc.insert(0, v[1])

        self.pot.delete(0, tk.END)
        self.pot.insert(0, v[2])

        self.qtd.delete(0, tk.END)
        self.qtd.insert(0, v[3])

        self.cat.set(v[4])

    def editar_carga(self):

        if not self.carga_atual:
            return

        db.atualizar_carga(
            self.carga_atual,
            self.desc.get(),
            self.pot.get(),
            self.qtd.get(),
            self.cat.get()
        )

        self.carregar_cargas()

    def excluir_carga(self):

        if not self.carga_atual:
            return

        db.deletar_carga(self.carga_atual)

        self.carregar_cargas()

    # ==================================================
    # DEMANDA
    # ==================================================

    def tela_demanda(self):
        
        frame = ttk.Frame(self.aba_demanda, padding=10)
        frame.pack()

        ttk.Button(frame, text="Calcular", command=self.calcular).pack(pady=10)

        ttk.Label(frame, text="Iluminação APTO").pack()
        self.lbl_ilum = ttk.Label(frame, text="0 W")
        self.lbl_ilum.pack()

        ttk.Label(frame, text="Tomadas APTO").pack()
        self.lbl_tom = ttk.Label(frame, text="0 W")
        self.lbl_tom.pack()

        ttk.Label(frame, text="Total Iluminação + Tomadas").pack()
        self.lbl_it = ttk.Label(frame, text="0 W")
        self.lbl_it.pack()

        ttk.Label(frame, text="Equipamentos APTO").pack()
        self.lbl_equip = ttk.Label(frame, text="0 W")
        self.lbl_equip.pack()

        ttk.Label(frame, text="Carga total apartamento").pack()
        self.lbl_total_apto = ttk.Label(frame, text="0 kW")
        self.lbl_total_apto.pack()

        ttk.Label(frame, text="Tipo de fornecimento").pack()
        self.lbl_forn = ttk.Label(frame, text="-")
        self.lbl_forn.pack()

        ttk.Separator(frame).pack(fill="x", pady=10)

        ttk.Label(frame, text="Carga Administração").pack()
        self.lbl_adm = ttk.Label(frame, text="0 kW")
        self.lbl_adm.pack()

        ttk.Label(frame, text="Demanda Total").pack()
        self.lbl_total = ttk.Label(frame, text="0 kW")
        self.lbl_total.pack()

    def calcular(self):
        
        if not self.projeto_atual:
            messagebox.showwarning("Aviso", "Selecione um projeto")
            return

        # =============================
        # Iluminação e tomadas automáticas
        # =============================

        iluminacao, tomadas = self.calcular_iluminacao_tomadas()

        total_it = iluminacao + tomadas

        # =============================
        # Cargas cadastradas
        # =============================

        cargas_apto = db.listar_cargas_tipo(self.projeto_atual, "APTO")
        cargas_adm = db.listar_cargas_tipo(self.projeto_atual, "ADM")

        equipamentos = 0
        total_adm = 0

        # Equipamentos apartamento
        for c in cargas_apto:

            pot = float(c[2])
            qtd = int(c[3])

            equipamentos += pot * qtd

        total_apto = total_it + equipamentos

        # =============================
        # Tipo de fornecimento
        # =============================

        if total_apto <= 8000:
            fornecimento = "Monofásico (item 8)"

        elif total_apto <= 25000:
            fornecimento = "Bifásico"

        else:
            fornecimento = "Trifásico"

        # =============================
        # Administração
        # =============================

        for c in cargas_adm:

            pot = float(c[2])
            qtd = int(c[3])

            total_adm += pot * qtd

        # =============================
        # Demanda total
        # =============================

        demanda_total = (total_apto / 1000) + total_adm

        # =============================
        # Atualizar tela
        # =============================

        self.lbl_ilum.config(text=f"{iluminacao:.0f} W")
        self.lbl_tom.config(text=f"{tomadas:.0f} W")
        self.lbl_it.config(text=f"{total_it:.0f} W")

        self.lbl_equip.config(text=f"{equipamentos:.0f} W")

        self.lbl_total_apto.config(text=f"{total_apto/1000:.2f} kW")
        self.lbl_forn.config(text=fornecimento)

        self.lbl_adm.config(text=f"{total_adm:.2f} kW")
        self.lbl_total.config(text=f"{demanda_total:.2f} kW")

    def calcular_iluminacao_tomadas(self):
    
        try:
            area = float(self.apto.get())   # ← área do apartamento
        except:
            return 0, 0

        conn = db.conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT iluminacao_w_m2, tomadas_w_m2
            FROM tabela_iluminacao_tomadas
            LIMIT 1
        """)

        regra = cursor.fetchone()

        conn.close()

        if not regra:
            return 0, 0

        w_ilum = float(regra[0])
        w_tom = float(regra[1])

        iluminacao = area * w_ilum
        tomadas = area * w_tom

        return iluminacao, tomadas