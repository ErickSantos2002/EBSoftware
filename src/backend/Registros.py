import os
import csv
import pandas as pd
import sys
from PyQt5.QtCore import QObject, pyqtSignal

# Gerenciador de sinais
class SignalManager(QObject):
    registros_atualizados = pyqtSignal()

# Instância global
sinal_global = SignalManager()

if getattr(sys, 'frozen', False):
    # Diretório do executável (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Diretório raiz do projeto (quando executado como script)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # Sai de src/backend
RESOURCES_DIR = os.path.join(PROJECT_DIR, "resources")  # Caminho do diretório resources
ARQUIVO_CSV = os.path.join(RESOURCES_DIR, "registros.csv")  # Caminho completo do arquivo CSV

# Função para carregar os registros do CSV
def carregar_registros():
    """Carrega registros do arquivo CSV, remove inconsistências e duplicados."""
    if not os.path.exists(ARQUIVO_CSV):
        return []
    with open(ARQUIVO_CSV, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        registros = []
        ids_vistos = set()
        for row in reader:
            row["ID"] = str(row["ID"]).strip()
            if row["ID"] not in ids_vistos:  # Garante IDs únicos
                ids_vistos.add(row["ID"])
                registros.append({k.strip(): v.strip() for k, v in row.items()})
        return registros

# Função para salvar registros no CSV
def salvar_registros(registros):
    """Salva a lista de registros no arquivo CSV."""
    with open(ARQUIVO_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Nome", "Matricula", "Setor"])
        writer.writeheader()
        writer.writerows(registros)

def importar_excel(file_path):
    """Importa registros de um arquivo Excel."""
    registros = carregar_registros()
    erros = []

    # Calcula o próximo ID disponível com base no maior ID atual
    max_id = max((int(r["ID"]) for r in registros), default=0)

    try:
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            # Verifica se os valores são NaN ou None antes de converter para string
            nome = row.get("Nome", "")
            matricula = row.get("Matricula", "")
            setor = row.get("Setor", "")

            if pd.isna(nome) or pd.isna(matricula):  # Checa valores nulos ou NaN
                nome = nome if not pd.isna(nome) else ""  # Substitui NaN por string vazia
                matricula = matricula if not pd.isna(matricula) else ""
                erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Nome ou Matricula ausente"})
                continue

            # Converte valores válidos para string e remove espaços em branco
            nome = str(nome).strip()
            matricula = str(matricula).strip()
            setor = str(setor).strip() if not pd.isna(setor) else ""

            # Verifica se campos obrigatórios estão preenchidos
            if not nome or not matricula:
                erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Nome ou Matricula ausente"})
                continue

            # Verifica se matrícula já existe
            if any(r["Matricula"] == matricula for r in registros):
                erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Matricula duplicada"})
                continue

            # Calcula o próximo ID
            max_id += 1
            novo_registro = {"ID": str(max_id), "Nome": nome, "Matricula": matricula, "Setor": setor}
            registros.append(novo_registro)

        # Salva os registros válidos no arquivo CSV
        salvar_registros(registros)

        return registros, erros
    except Exception as e:
        raise Exception(f"Erro ao importar Excel: {e}")

# Função para exportar um modelo de Excel
def exportar_modelo(file_path):
    """Cria um modelo de Excel para cadastro."""
    df = pd.DataFrame(columns=["Nome", "Matricula", "Setor"])
    df.to_excel(file_path, index=False)

# Função para adicionar um novo registro
def adicionar_registro(nome, matricula, setor):
    """Adiciona um novo registro ao CSV."""
    registros = carregar_registros()

    if any(r["Matricula"] == matricula for r in registros):
        raise ValueError("Matrícula duplicada")

    # Calcula o próximo ID disponível com base no maior ID atual
    max_id = max((int(r["ID"]) for r in registros), default=0)
    novo_registro = {"ID": str(max_id + 1), "Nome": nome, "Matricula": matricula, "Setor": setor}

    registros.append(novo_registro)
    salvar_registros(registros)

    # Emite o sinal informando que os registros foram atualizados
    sinal_global.registros_atualizados.emit()

    return novo_registro

def apagar_registros(ids_para_apagar):
    """Apaga os registros com os IDs fornecidos."""
    registros = carregar_registros()
    print(f"Registros antes da exclusão: {registros}")
    print(f"IDs para apagar: {ids_para_apagar}")

    ids_para_apagar = set(str(id_) for id_ in ids_para_apagar)  # Converte IDs para strings
    registros_filtrados = [r for r in registros if r["ID"] not in ids_para_apagar]

    print(f"Registros restantes após exclusão: {registros_filtrados}")
    salvar_registros(registros_filtrados)

    return registros_filtrados

def gerar_arquivo_erros(erros, file_path):
    """Salva os registros com erro em um arquivo Excel."""
    try:
        # Cria um DataFrame com os erros
        df_erros = pd.DataFrame(erros)
        df_erros.to_excel(file_path, index=False)
    except Exception as e:
        raise Exception(f"Erro ao gerar arquivo de erros: {e}")

# Teste standalone
if __name__ == "__main__":
    # Exemplos de uso
    print("Carregando registros...")
    print(carregar_registros())
