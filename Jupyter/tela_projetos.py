import tkinter as tk
from tkinter import ttk, messagebox
import database_manager as db


class TelaProjetos:

    def __init__(self, root):

        self.root = root
        self.root.title("GED119 - Gerenciamento de Projetos")

        self.projeto_atual = None  # ✔ FIX IMPORTANTE

        frame = ttk.Frame(root, padding=20)
        frame.pack(fill="both", expand=True)

        # CAMPOS
        ttk.Label(frame, text="Nome Projeto").grid(row=0, column=0)
        self.nome = ttk.Entry(frame, width=30)
        self.nome.grid(row=0, column=1)

        ttk.Label(frame, text="Cliente").grid(row=1, column=0)
        self.cliente = ttk.Entry(frame)
        self.cliente.grid(row=1, column=1)

        ttk.Label(frame, text="Endereço").grid(row=2, column=0)
        self.endereco = ttk.Entry(frame)
        self.endereco.grid(row=2, column=1)

        ttk.Label(frame, text="Área m²").grid(row=3, column=0)
        self.area = ttk.Entry(frame)
        self.area.grid(row=3, column=1)

        ttk.Label(frame, text="Tipo").grid(row=4, column=0)
        self.tipo = ttk.Combobox(frame, values=["Residencial", "Comercial", "Industrial"])
        self.tipo.grid(row=4, column=1)

        ttk.Button(frame, text="Adicionar Projeto",
                   command=self.adicionar).grid(row=5, column=0, columnspan=2, pady=10)

        # TABELA
        self.tree = ttk.Treeview(frame, columns=("id","nome","cliente","area"), show="headings")

        self.tree.heading("id", text="ID")
        self.tree.heading("nome", text="Projeto")
        self.tree.heading("cliente", text="Cliente")
        self.tree.heading("area", text="Área")

        self.tree.grid(row=6, column=0, columnspan=2)

        # ✔ seleção automática
        self.tree.bind("<<TreeviewSelect>>", self.selecionar)

        ttk.Button(frame, text="Excluir Projeto",
                   command=self.excluir).grid(row=7, column=0)

        ttk.Button(frame, text="Atualizar",
                   command=self.carregar).grid(row=7, column=1)

        self.carregar()

    # ----------------------
    def carregar(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        dados = db.listar_projetos()

        for d in dados:
            self.tree.insert("", "end", values=(d[0], d[1], d[2], d[5]))

    # ----------------------
    def adicionar(self):

        db.adicionar_projeto(
            self.nome.get(),
            self.cliente.get(),
            self.endereco.get(),
            self.area.get(),
            self.tipo.get()
        )

        self.carregar()

    # ----------------------
    def selecionar(self, event):

        item = self.tree.selection()

        if not item:
            return

        dados = self.tree.item(item[0])

        self.projeto_atual = dados["values"][0]

        print("Projeto selecionado:", self.projeto_atual)

    # ----------------------
    def excluir(self):

        if not self.projeto_atual:
            messagebox.showwarning("Aviso", "Selecione um projeto")
            return

        db.deletar_projeto(self.projeto_atual)

        self.projeto_atual = None

        self.carregar()