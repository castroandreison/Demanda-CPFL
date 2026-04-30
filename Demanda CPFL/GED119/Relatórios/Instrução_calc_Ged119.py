import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


def gerar_relatorio_pdf():

    # =========================
    # CAMINHO DO ARQUIVO
    # =========================
    pasta = r"C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\GED119\Relatórios"
    
    os.makedirs(pasta, exist_ok=True)

    caminho_pdf = os.path.join(pasta, "Memorial_Calculo_Demanda_GED119.pdf")

    doc = SimpleDocTemplate(caminho_pdf, pagesize=A4)

    styles = getSampleStyleSheet()

    titulo = ParagraphStyle(
        "titulo",
        parent=styles["Heading1"],
        fontSize=16,
        alignment=1,
        spaceAfter=12
    )

    subtitulo = ParagraphStyle(
        "subtitulo",
        parent=styles["Heading2"],
        fontSize=12,
        textColor=colors.darkblue,
        spaceBefore=10,
        spaceAfter=6
    )

    normal = ParagraphStyle(
        "normal",
        parent=styles["Normal"],
        fontSize=10,
        leading=12
    )

    elementos = []

    # =========================
    # TÍTULO
    # =========================
    elementos.append(Paragraph("MEMORIAL DE CÁLCULO DE DEMANDA - GED119", titulo))
    elementos.append(Spacer(1, 12))

    # =========================
    # 15.1
    # =========================
    elementos.append(Paragraph("15.1 Definições Gerais", subtitulo))

    elementos.append(Paragraph(
        "<b>Área útil do apartamento:</b> área privativa excluindo paredes e pilares.<br/>"
        "<b>Área útil da administração:</b> áreas comuns como corredores, salão de festas, casa de máquinas.<br/>"
        "<b>Área útil da edificação:</b> soma das áreas dos apartamentos e administração.",
        normal
    ))

    # =========================
    # 15.2
    # =========================
    elementos.append(Paragraph("15.2 Tipo de Fornecimento", subtitulo))

    elementos.append(Paragraph(
        "O tipo de fornecimento deve ser definido após o cálculo da carga instalada ou demanda, conforme Tabelas 13 e 14.",
        normal
    ))

    # =========================
    # 15.2.1
    # =========================
    elementos.append(Paragraph("15.2.1 Cálculo da Carga Instalada", subtitulo))

    elementos.append(Paragraph(
        "Se a carga instalada for ≤ 25 kW, não é necessário calcular demanda.<br/>"
        "Se for > 25 kW, deve-se aplicar o cálculo de demanda conforme GED13.",
        normal
    ))

    elementos.append(Paragraph("<b>a) Iluminação</b>", normal))
    elementos.append(Paragraph(
        "Devem ser informados tipo, quantidade e potência dos pontos de luz.",
        normal
    ))

    elementos.append(Paragraph("<b>b) Tomadas</b>", normal))
    elementos.append(Paragraph(
        "- Cozinhas e áreas de serviço: até 3 tomadas = 600 W cada<br/>"
        "- Excedentes = 100 W<br/>"
        "- Uso geral = 100 W por tomada",
        normal
    ))

    elementos.append(Paragraph("<b>c) Eletrodomésticos</b>", normal))
    elementos.append(Paragraph(
        "Utilizar potências da Tabela 3 ou valores do fabricante quando superiores.<br/>"
        "Ex: boiler, fogão elétrico, ar-condicionado, hidromassagem.",
        normal
    ))

    elementos.append(Paragraph("<b>d) Motores</b>", normal))
    elementos.append(Paragraph(
        "Informar potência, quantidade, fases, corrente de partida e tipo de acionamento.",
        normal
    ))

    # =========================
    # 15.3
    # =========================
    elementos.append(Paragraph("15.3 Iluminação e Tomadas", subtitulo))

    elementos.append(Paragraph(
        "Para edificações residenciais, considerar 5 W/m² sobre a área útil.",
        normal
    ))

    # =========================
    # 15.4
    # =========================
    elementos.append(Paragraph("15.4 Aparelhos", subtitulo))

    elementos.append(Paragraph(
        "Aplicar fatores de demanda conforme Tabela 2.<br/>"
        "Somar quantidade de aparelhos e aplicar fator correspondente.",
        normal
    ))

    elementos.append(Paragraph(
        "Chuveiros e torneiras devem ser somados e aplicados ao fator correspondente.",
        normal
    ))

    # =========================
    # 15.5
    # =========================
    elementos.append(Paragraph("15.5 Motores Elétricos", subtitulo))

    elementos.append(Paragraph(
        "Converter CV para kVA conforme tabelas.<br/>"
        "Maior motor = 100%<br/>"
        "Demais motores = 50%",
        normal
    ))

    # =========================
    # 15.6
    # =========================
    elementos.append(Paragraph("15.6 Ar Condicionado", subtitulo))

    elementos.append(Paragraph(
        "Tipo central: 100% da carga.<br/>"
        "Fan-coil: 75%.<br/>"
        "Tipo janela: conforme tabela.",
        normal
    ))

    # =========================
    # 15.7
    # =========================
    elementos.append(Paragraph("15.7 Equipamentos Especiais", subtitulo))

    elementos.append(Paragraph(
        "Maior equipamento: 100%<br/>"
        "Demais: 60%",
        normal
    ))

    # =========================
    # 15.8
    # =========================
    elementos.append(Paragraph("15.8 Simultaneidade", subtitulo))

    elementos.append(Paragraph(
        "Aplicar coeficiente conforme número de apartamentos (Tabela 7).",
        normal
    ))

    # =========================
    # GERAR PDF
    # =========================
    doc.build(elementos)

    print("\n========================================")
    print("RELATÓRIO GERADO COM SUCESSO")
    print("Arquivo:", caminho_pdf)
    print("========================================\n")


# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    gerar_relatorio_pdf()