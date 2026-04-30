from APIBanco import GED119API

db = GED119API() 

# listar tabelas
print(db.list_tables())

# potência de chuveiro
p = db.get_potencia_aparelho("chuveiro")
print("Potência:", p)

# fator demanda aparelhos
f = db.get_fator_demanda_aparelhos(10)
print("Fator:", f)

# coeficiente simultaneidade
c = db.get_coeficiente_apartamentos(20)
print("Coeficiente:", c)

# capacidade cabo
print(db.get_capacidade_cabo(50))