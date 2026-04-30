# -*- coding: utf-8 -*-

import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------
# CONEXÃO BANCO
# ---------------------------------------------------------

conn = sqlite3.connect(
    r"C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\GED119\DB119\databaseCPFLGed119.db"
)

cursor = conn.cursor()

# ---------------------------------------------------------
# BUSCAR kVA MOTOR (TABELA 4)
# ---------------------------------------------------------

def cv_para_kva(cv):

    cursor.execute("""
        SELECT potencia_kva
        FROM TABELA_4
        WHERE REPLACE(potencia_cv_hp,' ','') =
              REPLACE(?,' ','')
    """, (str(cv),))

    r = cursor.fetchone()

    return r[0] if r else 0


# ---------------------------------------------------------
# DEMANDA MOTORES
# ---------------------------------------------------------

def demanda_motores(motores):

    print("\n3- Demanda Referente a Motores\n")

    total = 0
    maior = 0

    for cv, qtd in motores:

        kva = cv_para_kva(cv)

        total_kva = kva * qtd

        print(f"{cv} CV x {qtd} = {kva:.2f} kVA x {qtd} = {total_kva:.2f} kVA")

        total += total_kva

        if kva > maior:
            maior = kva

    restantes = total - maior

    D3 = (maior * 1.0) + (restantes * 0.5)

    print(f"\nTotal: {total:.2f} kVA")
    print(f"Maior motor: {maior:.2f} kVA")
    print(f"Demais motores: {restantes:.2f} kVA")
    print(f"D3 = {D3:.2f} kVA")

    return D3


# ---------------------------------------------------------
# FATOR DEMANDA APARELHOS (TABELA 2)
# ---------------------------------------------------------

def fator_aparelho(cursor, coluna, quantidade):

    cursor.execute("SELECT * FROM TABELA_2")

    linhas = cursor.fetchall()

    colunas = [d[0] for d in cursor.description]

    idx = colunas.index(coluna)

    for linha in linhas:

        faixa = linha[1]

        if " a " in faixa:

            minimo, maximo = faixa.split(" a ")

            minimo = int(minimo)
            maximo = int(maximo)

        else:

            minimo = int(faixa)
            maximo = int(faixa)

        if minimo <= quantidade <= maximo:

            return linha[idx] / 100

    return 1


# ---------------------------------------------------------
# FATOR SIMULTANEIDADE (TABELA 7)
# ---------------------------------------------------------

def fator_simultaneidade(qtd):

    cursor.execute("""
        SELECT numero_apartamentos,
               fator_simultaneidade
        FROM TABELA_7
    """)

    linhas = cursor.fetchall()

    for faixa, fator in linhas:

        if "acima" in faixa:

            minimo = int(faixa.split()[0])
            maximo = 10**9

        else:

            minimo, maximo = faixa.split(" a ")

            minimo = int(minimo)
            maximo = int(maximo)

        if minimo <= qtd <= maximo:

            return fator

    return 1


# ---------------------------------------------------------
# DADOS DO EMPREENDIMENTO
# ---------------------------------------------------------

descricao = "Edifício residencial"

area_total_edificio_m2 = 12713
area_administracao_m2 = 5710
area_apartamento_tipo_m2 = 47

aptos = 149


# ---------------------------------------------------------
# CARGA INSTALADA APARTAMENTO (ITEM 15.2.1)
# ---------------------------------------------------------

print("\n0- Carga Instalada do Apartamento (Item 15.2.1 GED119)\n")

# dados apartamento

iluminacao_w = 620
tomadas_w = 2600
chuveiro_kw = 5.4
lava_louca_kw = 2.0

carga_ilum_tom = (iluminacao_w + tomadas_w) / 1000

carga_instalada_apto = carga_ilum_tom + chuveiro_kw + lava_louca_kw

print(f"Iluminação = {iluminacao_w} W")
print(f"Tomadas = {tomadas_w} W")
print(f"Chuveiro = {chuveiro_kw} kW")
print(f"Lava-louça = {lava_louca_kw} kW")

print("\nCarga instalada:")

print(f"({iluminacao_w}+{tomadas_w})/1000 + {chuveiro_kw} + {lava_louca_kw}")

print(f"Carga instalada apartamento = {carga_instalada_apto:.2f} kW")

if carga_instalada_apto <= 25:

    print("\n✔ Carga ≤ 25 kW")
    print("Conforme GED119 não é necessário cálculo de demanda.")

else:

    print("\n✔ Carga > 25 kW")
    print("Necessário cálculo de demanda.")


# ---------------------------------------------------------
# 1 - ILUMINAÇÃO E TOMADAS
# ---------------------------------------------------------

print("\n1- Demanda Referente à Iluminação e Tomadas\n")

w_m2_apto = 5
w_m2_adm = 5
fp = 1

D1a = (area_apartamento_tipo_m2 * w_m2_apto * aptos) / 1000 * fp

print(f"D1a = {D1a:.2f} kVA (Apartamentos)")

D1b = (area_administracao_m2 * w_m2_adm) / 1000 * fp

print(f"D1b = {D1b:.2f} kVA (Administração)")

D1 = D1a + D1b

print(f"\nD1 = {D1:.2f} kVA")


# ---------------------------------------------------------
# 2 - APARELHOS
# ---------------------------------------------------------

print("\n2- Demanda Referente a Aparelhos\n")

FP = 1

f_chuveiro = fator_aparelho(cursor, "chuveiro_torneira_ferro", aptos)

f_lava = fator_aparelho(cursor, "maquinas_lavar_louca", aptos)

D2a = (aptos * chuveiro_kw * f_chuveiro) / FP

print(f"D2a = ({aptos} x {chuveiro_kw} x {f_chuveiro}) = {D2a:.2f} kVA")

D2b = (aptos * lava_louca_kw * f_lava) / FP

print(f"D2b = ({aptos} x {lava_louca_kw} x {f_lava}) = {D2b:.2f} kVA")

D2 = D2a + D2b

print(f"\nD2 = {D2:.2f} kVA")


# ---------------------------------------------------------
# 3 - MOTORES
# ---------------------------------------------------------

portao_hp = 2
bomba_piscina_hp = 2
elevador_hp = 10
bomba_recalque_hp = 10

qtd_elev = 4
qtd_recalque = 2

motores = [

    (portao_hp,1),
    (bomba_piscina_hp,1),
    (elevador_hp,qtd_elev),
    (bomba_recalque_hp,qtd_recalque)

]

D3 = demanda_motores(motores)


# ---------------------------------------------------------
# 4 - DEMANDA GERAL
# ---------------------------------------------------------

print("\n4- Demanda Geral da Entrada\n")

f_sim = fator_simultaneidade(aptos)

Dapt = (D1a + D2) * f_sim

Dadm = D1b + D3

print(f"Dapt = ({D1a:.2f} + {D2:.2f}) x {f_sim}")

print(f"Dapt = {Dapt:.2f} kVA")

print(f"\nDadm = {D1b:.2f} + {D3:.2f}")

print(f"Dadm = {Dadm:.2f} kVA")

Dg = Dapt + Dadm

print("\n--------------------------------")

print(f"DEMANDA GERAL = {Dg:.2f} kVA")

print("--------------------------------")

conn.close()