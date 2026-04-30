import tkinter as tk

# Definição dos fatores de demanda conforme a tabela
fatores_demanda = [
    (0, 1, 0.86),
    (1, 2, 0.75),
    (2, 3, 0.66),
    (3, 4, 0.59),
    (4, 5, 0.52),
    (5, 6, 0.45),
    (6, 7, 0.40),
    (7, 8, 0.35),
    (8, 9, 0.31),
    (9, 10, 0.27),
    (10, float("inf"), 0.24)  # Para C > 10
]

def calcular_demanda():
    try:
        carga_instalada = float(entry_carga.get())
        fator = 0.24  # Valor padrão para C > 10
        faixa_utilizada = "C > 10"

        for limite_inferior, limite_superior, fd in fatores_demanda:
            if limite_inferior < carga_instalada <= limite_superior:
                fator = fd
                faixa_utilizada = f"{limite_inferior} < C ≤ {limite_superior}"
                break
        
        demanda = carga_instalada * fator
        label_resultado.config(text=f"Demanda Calculada: {demanda:.2f} kW\n"
                                    f"Fator de Demanda Utilizado: {faixa_utilizada} ({fator})")
    except ValueError:
        label_resultado.config(text="Erro: Insira um valor numérico válido.")

# Configuração da interface
top = tk.Tk()
top.title("Cálculo de Demanda Residencial")
top.geometry("400x200")

tk.Label(top, text="Carga Instalada (kW):").pack(pady=5)
entry_carga = tk.Entry(top)
entry_carga.pack(pady=5)

tk.Button(top, text="Calcular Demanda", command=calcular_demanda).pack(pady=5)

label_resultado = tk.Label(top, text="Demanda Calculada:")
label_resultado.pack(pady=10)

# Iniciar loop da interface gráfica
top.mainloop()
