import chardet
import os

ARQUIVO_CSV = r'C:\Users\pc\Documents\GitHub\SoftwareEBS\resources\registros.csv'

# Detectar o encoding do arquivo
with open(ARQUIVO_CSV, "rb") as file:
    raw_data = file.read()
    result = chardet.detect(raw_data)  # Detecta o encoding
    print(f"Encoding detectado: {result['encoding']}")
