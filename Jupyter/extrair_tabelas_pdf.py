import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import camelot
import sqlite3
import pandas as pd
import os

class PDFtoSQLiteApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Extrator de Tabelas PDF → SQLite")
        self.root.geometry("700x500")

        self.pdf_path = ""

        # botão selecionar PDF
        btn_pdf = tk.Button(root, text="Selecionar PDF", command=self.selecionar_pdf)
        btn_pdf.pack(pady=10)

        # label arquivo
        self.label_pdf = tk.Label(root, text="Nenhum PDF selecionado")
        self.label_pdf.pack()

        # botão extrair
        btn_extract = tk.Button(root, text="Extrair Tabelas", command=self.extrair_tabelas)
        btn_extract.pack(pady=10)

        # log
        self.log = scrolledtext.ScrolledText(root, height=20)
        self.log.pack(fill="both", expand=True, padx=10, pady=10)

    def escrever_log(self, texto):
        self.log.insert(tk.END, texto + "\n")
        self.log.see(tk.END)
        self.root.update()

    def selecionar_pdf(self):

        caminho = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )

        if caminho:
            self.pdf_path = caminho
            self.label_pdf.config(text=caminho)

    def extrair_tabelas(self):

        if not self.pdf_path:
            messagebox.showerror("Erro", "Selecione um PDF primeiro")
            return

        try:

            pasta_pdf = os.path.dirname(self.pdf_path)
            nome_pdf = os.path.splitext(os.path.basename(self.pdf_path))[0]

            db_path = os.path.join(pasta_pdf, f"{nome_pdf}.db")

            self.escrever_log("Extraindo tabelas do PDF...")
            self.escrever_log(self.pdf_path)

            tables = camelot.read_pdf(
                self.pdf_path,
                pages="all",
                flavor="stream"
            )

            self.escrever_log(f"Tabelas encontradas: {tables.n}")

            conn = sqlite3.connect(db_path)

            for i, table in enumerate(tables):

                df = table.df

                nome_tabela = f"tabela_{i+1}"

                self.escrever_log(f"Salvando {nome_tabela}")

                df.to_sql(
                    nome_tabela,
                    conn,
                    if_exists="replace",
                    index=False
                )

            conn.close()

            self.escrever_log("")
            self.escrever_log("Processo finalizado!")
            self.escrever_log(f"Banco criado em:")
            self.escrever_log(db_path)

            messagebox.showinfo("Sucesso", "Banco SQLite criado com sucesso!")

        except Exception as e:

            messagebox.showerror("Erro", str(e))
            self.escrever_log("ERRO:")
            self.escrever_log(str(e))


# iniciar app
root = tk.Tk()
app = PDFtoSQLiteApp(root)
root.mainloop()