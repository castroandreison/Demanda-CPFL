import pandas as pd
from IPython.display import display

dados = {
    "Capacidade Transformador (kVA)": ["30", "45", "75", "112.5", "150"],
    "Fusível 23.1kV": ["1H", "2H", "2H", "3H", "5H"],
    "Fusível 13.8kV": ["1H", "2H", "3H", "5H", "8K"],
    "Fusível 11.9kV": ["1H", "2H", "5H", "5H", "8K"]
}

df = pd.DataFrame(dados)

display(df)