import os
import sys
import csv
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas

if getattr(sys, 'frozen', False):
    # Diretório do executável (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Diretório raiz do projeto (quando executado como script)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")  # Caminho do diretório resources

# Caminho do arquivo específico
ARQUIVO_RESULTADOS = os.path.join(RESOURCES_DIR, "Resultados.csv")

def carregar_resultados():
    """Carrega os resultados do arquivo CSV."""
    if not os.path.exists(ARQUIVO_RESULTADOS):
        return []
    with open(ARQUIVO_RESULTADOS, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [row for row in reader]


def filtrar_resultados(resultados, periodo=None, usuario=None, status=None):
    """Filtra os resultados com base nos parâmetros fornecidos."""
    filtrados = []

    for resultado in resultados:
        # Filtro por período
        if periodo:
            data_teste = datetime.strptime(resultado["Data e hora"], "%Y-%m-%d %H:%M:%S").date()
            if not (periodo[0] <= data_teste <= periodo[1]):
                continue

        # Filtro por usuário
        if usuario and resultado["Nome"] != usuario:
            continue

        # Filtro por status
        if status and resultado["Status"] != status:
            continue

        filtrados.append(resultado)

    return filtrados

def salvar_em_excel(resultados, caminho_arquivo):
    """Salva os resultados em um arquivo Excel."""
    df = pd.DataFrame(resultados)

    # Formata a coluna de Data e Hora, se existir
    if "Data e hora" in df.columns:
        df["Data e hora"] = pd.to_datetime(df["Data e hora"]).dt.strftime("%d/%m/%y %H:%M:%S")

    with pd.ExcelWriter(caminho_arquivo, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
        worksheet = writer.sheets["Resultados"]

        # Ajusta a largura das colunas no Excel
        for col_idx, column_cells in enumerate(worksheet.iter_cols()):
            max_length = max(len(str(cell.value)) for cell in column_cells if cell.value)
            col_letter = worksheet.cell(row=1, column=col_idx + 1).column_letter
            worksheet.column_dimensions[col_letter].width = max_length + 2

def salvar_em_pdf(resultados, caminho_arquivo):
    """Salva os resultados em um arquivo PDF."""
    c = canvas.Canvas(caminho_arquivo, pagesize=landscape(letter))
    largura, altura = landscape(letter)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(30, altura - 40, "Registros de Resultados EBS010")

    # Cabeçalhos
    colunas = ["ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor", "Data e hora", "Qtd. Álcool", "Status"]
    larguras_colunas = [60, 80, 100, 90, 90, 160, 90, 80]
    c.setFont("Helvetica-Bold", 10)
    y = altura - 70
    x_inicial = 30
    for i, coluna in enumerate(colunas):
        c.drawString(x_inicial, y, coluna)
        x_inicial += larguras_colunas[i]

    # Dados
    c.setFont("Helvetica", 10)
    y -= 20
    for row in resultados:
        x_inicial = 30
        for i, coluna in enumerate(colunas):
            c.drawString(x_inicial, y, str(row[coluna]))
            x_inicial += larguras_colunas[i]
        y -= 20
        if y < 50:
            c.showPage()
            y = altura - 70
            c.setFont("Helvetica-Bold", 10)
            for i, coluna in enumerate(colunas):
                c.drawString(x_inicial, y, coluna)
                x_inicial += larguras_colunas[i]
            c.setFont("Helvetica", 10)
            y -= 20

    c.save()
