import os
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors


def gerar_relatorio_pdf():

    # =========================
    # CAMINHO DO ARQUIVO
    # =========================
    pasta = r"C:\Users\an053116\Documents\01 - Códigos python\35 - Demanda CPFL GED119\Demanda CPFL\Ged13\Relatórios"
    
    os.makedirs(pasta, exist_ok=True)

    caminho_pdf = os.path.join(pasta, "Descrição Cálculo Demanda Ged13.pdf")

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
    elementos.append(Paragraph("RELATÓRIO DE CÁLCULO DE CARGA INSTALADA E DEMANDA", titulo))
    elementos.append(Spacer(1, 12))

    # =========================
    # 6.17
    # =========================
    elementos.append(Paragraph("6.17 Cálculo da Carga Instalada", subtitulo))
    elementos.append(Paragraph(
        "Determina o tipo de atendimento e fornecimento. Define categoria do cliente e padrão de entrada.",
        normal
    ))

    # =========================
    # 6.18
    # =========================
    elementos.append(Paragraph("6.18 Iluminação e Tomadas", subtitulo))

    elementos.append(Paragraph("<b>a) Residencial</b>", normal))
    elementos.append(Paragraph(
        "- 100 W por tomada<br/>"
        "- 1 ponto de luz por cômodo (100 W)<br/>"
        "- Acima de 250 m²: declarar tomadas",
        normal
    ))

    elementos.append(Spacer(1, 6))

    elementos.append(Paragraph("<b>b) Outros tipos</b>", normal))
    elementos.append(Paragraph(
        "Hotéis, hospitais, comércios, indústrias, bancos, igrejas etc. conforme Tabela 15.",
        normal
    ))

    elementos.append(Spacer(1, 6))

    elementos.append(Paragraph("<b>c) Eletrodomésticos</b>", normal))
    elementos.append(Paragraph(
        "Considerar ≥ 1000 W ou soma equivalente.",
        normal
    ))

    elementos.append(Paragraph(
        "- Chuveiro: 6500 W<br/>"
        "- Torneira elétrica: 5500 W<br/>"
        "- Micro-ondas: 1400 W<br/>"
        "- Forno elétrico: 1500 W<br/>"
        "- Secadora: 2500 W<br/>"
        "- Ferro elétrico: 1000 W",
        normal
    ))

    # =========================
    # 6.19
    # =========================
    elementos.append(Paragraph("6.19 Motores e Equipamentos Especiais", subtitulo))
    elementos.append(Paragraph(
        "Motores conforme placa do fabricante (Tabelas 13 e 14).",
        normal
    ))

    elementos.append(Paragraph(
        "Equipamentos especiais: raio X, fornos elétricos, indução, solda, eletrólise, retificadores.",
        normal
    ))

    # =========================
    # 6.20
    # =========================
    elementos.append(Paragraph("6.20 Partida de Motores", subtitulo))
    elementos.append(Paragraph(
        "Proteção conforme NBR 5410. Uso de dispositivos de partida reduzida conforme Tabela 12.",
        normal
    ))

    elementos.append(Paragraph(
        "Utilizar soft starter quando potência ultrapassar limites.",
        normal
    ))

    # =========================
    # 6.21
    # =========================
    elementos.append(Paragraph("6.21 Recarga de Veículos Elétricos", subtitulo))
    elementos.append(Paragraph(
        "Seguir CPFL nº 150030. Potência e FP conforme fabricante. Fator de demanda = 1.",
        normal
    ))

    # =========================
    # 6.22
    # =========================
    elementos.append(Paragraph("6.22 Dimensionamento do Padrão de Entrada", subtitulo))

    elementos.append(Paragraph(
        "Demanda total: D = a + b + c + d + e + f + g + h + i",
        normal
    ))

    elementos.append(Paragraph(
        "<b>Componentes:</b><br/>"
        "a) Iluminação e tomadas<br/>"
        "b) Chuveiros e aquecedores<br/>"
        "c) Boiler<br/>"
        "d) Secadora, forno, micro-ondas<br/>"
        "e) Fogões elétricos<br/>"
        "f) Ar-condicionado<br/>"
        "g) Motores<br/>"
        "h) Equipamentos especiais<br/>"
        "i) Hidromassagem",
        normal
    ))

    # =========================
    # GERAR PDF
    # =========================
    doc.build(elementos)

    print(f"Relatório gerado com sucesso em:\n{caminho_pdf}")


# =========================
# EXECUÇÃO
# =========================
if __name__ == "__main__":
    gerar_relatorio_pdf()