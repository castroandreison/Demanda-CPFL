# -*- coding: utf-8 -*-
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

# ---------------------------------
# CONEXÃO COM BANCO
# ---------------------------------

banco = r"C:\Users\an053116\Documents\01 - Códigos python\Demanda CPFL GED119\database\databaseCPFLGed119.db"

conn = sqlite3.connect(banco)
cursor = conn.cursor()

# ---------------------------------
# NORMALIZAÇÃO DE CV
# ---------------------------------

def normalizar_cv(cv):

    cv = str(cv).replace(",", ".").strip()

    mapa = {
        "0.33": "1/3",
        "0.5": "1/2",
        "0.75": "3/4",
        "1": "1",
        "1.5": "1 1/2",
        "2": "2",
        "3": "3",
        "4": "4",
        "5": "5",
        "7.5": "7 1/2",
        "10": "10",
        "12.5": "12 1/2",
        "15": "15",
        "20": "20",
        "25": "25",
        "30": "30",
        "40": "40",
        "50": "50",
        "60": "60",
        "75": "75",
        "100": "100",
        "125": "125",
        "150": "150",
        "200": "200"
    }

    return mapa.get(cv, cv)


# ---------------------------------
# BUSCAR kVA DO MOTOR
# ---------------------------------

def cv_para_kva(cv):

    chave = normalizar_cv(cv)

    cursor.execute("""
        SELECT potencia_kva
        FROM TABELA_4
        WHERE potencia_cv_hp = ?
    """, (chave,))

    r = cursor.fetchone()

    if r:
        return r[0]

    print(f"⚠ Motor {cv} CV não encontrado na tabela")
    return 0


# ---------------------------------
# DEMANDA MOTORES
# ---------------------------------

def demanda_motores(motores):

    print("\n3- Demanda Referente a Motores\n")

    total = 0
    maior = 0

    for cv, qtd in motores:

        kva = cv_para_kva(cv)
        total_kva = kva * qtd

        print(f"{cv} CV x {qtd} = {kva:.2f} kVA x {qtd} = {total_kva:.2f} kVA")

        total += total_kva
        maior = max(maior, kva)

    restantes = total - maior

    D3 = (maior * 1.0) + (restantes * 0.5)

    print(f"\nTotal: {total:.2f} kVA")
    print(f"Maior Motor: {maior:.2f} kVA")
    print(f"Demais motores: {restantes:.2f} kVA")
    print(f"D3 = {D3:.2f} kVA")

    return D3


# ---------------------------------
# FATOR DEMANDA APARELHOS
# ---------------------------------

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


# ---------------------------------
# FATOR SIMULTANEIDADE
# ---------------------------------

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


# ---------------------------------
# DADOS DO EMPREENDIMENTO
# ---------------------------------

aptos = 20

area_apto_m2 = 160
area_adm_m2 = 2884

w_m2 = 5

# cargas apartamento exemplo GED119

iluminacao_w = 3130
tomadas_w = 1800

chuveiro_kw = 5.4
lavar_louca_kw = 2.5
secar_kw = 2.5

# administração

chuveiros_admin = 5
torneiras_admin = 2

# ---------------------------------
# 0 - CARGA INSTALADA APARTAMENTO
# ---------------------------------

print("\n0- Carga Instalada do Apartamento (Item 15.2.1 GED119)\n")

carga_ilum_tom = (iluminacao_w + tomadas_w) / 1000

carga_instalada_apto = (
    carga_ilum_tom +
    chuveiro_kw +
    lavar_louca_kw +
    secar_kw
)

print(f"Iluminação = {iluminacao_w} W")
print(f"Tomadas = {tomadas_w} W")
print(f"Chuveiro = {chuveiro_kw} kW")
print(f"Lava-louça = {lavar_louca_kw} kW")
print(f"Secadora = {secar_kw} kW")

print("\nCálculo:")

print(f"({iluminacao_w}+{tomadas_w})/1000 + "
      f"{chuveiro_kw} + {lavar_louca_kw} + {secar_kw}")

print(f"\nCarga instalada apartamento = {carga_instalada_apto:.2f} kW")

if carga_instalada_apto <= 25:

    print("\n✔ Carga ≤ 25 kW")
    print("Não necessita cálculo de demanda individual.")

else:

    print("\n✔ Carga > 25 kW")
    print("Necessário cálculo de demanda.")

# ---------------------------------
# 1 - ILUMINAÇÃO E TOMADAS
# ---------------------------------

print("\n1- Demanda Referente à Iluminação e Tomadas de Uso Geral\n")

D1a = (area_apto_m2 * aptos * w_m2) / 1000
D1b = (area_adm_m2 * w_m2) / 1000

print(f"D1a = {D1a:.2f} kVA")
print(f"D1b = {D1b:.2f} kVA")

D1 = D1a + D1b

print(f"D1 = {D1:.2f} kVA")

# ---------------------------------
# 2 - APARELHOS
# ---------------------------------

print("\n2- Demanda Referente a Aparelhos\n")

total_chuveiros = aptos + chuveiros_admin + torneiras_admin
total_lava = aptos
total_sec = aptos

f_ch = fator_aparelho("chuveiro_torneira_ferro", total_chuveiros)
f_lava = fator_aparelho("maquinas_lavar_louca", total_lava)
f_sec = fator_aparelho("maquina_secar_roupa", total_sec)

D2a_apt = aptos * chuveiro_kw * f_ch
D2b = aptos * lavar_louca_kw * f_lava
D2c = aptos * secar_kw * f_sec

D2a_admin_ch = chuveiros_admin * chuveiro_kw * f_ch
D2a_admin_tor = torneiras_admin * 3.0 * f_ch

D2_admin = D2a_admin_ch + D2a_admin_tor

D2 = D2a_apt + D2b + D2c + D2_admin

print(f"D2a apartamentos = {D2a_apt:.2f} kVA")
print(f"D2 administração = {D2_admin:.2f} kVA")
print(f"D2b = {D2b:.2f} kVA")
print(f"D2c = {D2c:.2f} kVA")

print(f"\nD2 = {D2:.2f} kVA")

# ---------------------------------
# 3 - MOTORES
# ---------------------------------

motores = [
    (1,1),
    (10,1),
    (5,1),
    (10,2),
    (7.5,1)
]

D3 = demanda_motores(motores)

# ---------------------------------
# 4 - DEMANDA FINAL
# ---------------------------------

print("\n4- Demanda Geral da Entrada\n")

f_sim = fator_simultaneidade(aptos)

D2_apt = D2a_apt + D2b + D2c

Dapt = (D1a + D2_apt) * f_sim

Dadm = D1b + D2_admin + D3

Dg = Dapt + Dadm

print(f"Dapt = {Dapt:.2f} kVA")
print(f"Dadm = {Dadm:.2f} kVA")

print("\n--------------------------------")
print(f"DEMANDA GERAL = {Dg:.2f} kVA")
print("--------------------------------")

conn.close()