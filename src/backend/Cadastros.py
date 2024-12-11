import os
import csv
import pandas as pd
import sys
from PyQt5.QtCore import QObject, pyqtSignal

# Gerenciador de sinais
class SignalManager(QObject):
    registros_atualizados = pyqtSignal()

# Instância global do gerenciador de sinais
sinal_global = SignalManager()

# Diretórios e arquivos
BASE_DIR = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
ARQUIVO_CSV = os.path.join(RESOURCES_DIR, "registros.csv")

# ---------------------------------------
# Funções de Inicialização e Utilidades
# ---------------------------------------

def inicializar_arquivo_csv():
    """Verifica e cria o arquivo CSV de registros, se necessário."""
    if not os.path.exists(RESOURCES_DIR):
        os.makedirs(RESOURCES_DIR)
    if not os.path.exists(ARQUIVO_CSV):
        with open(ARQUIVO_CSV, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["ID", "Nome", "Matricula", "Setor"])
            writer.writeheader()

# ---------------------------------------
# Funções de Manipulação de Registros
# ---------------------------------------

def carregar_registros():
    """Carrega registros do arquivo CSV, removendo inconsistências e duplicados."""
    if not os.path.exists(ARQUIVO_CSV):
        return []

    with open(ARQUIVO_CSV, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        registros, ids_vistos = [], set()

        for row in reader:
            row["ID"] = str(row["ID"]).strip()
            if row["ID"] not in ids_vistos:
                ids_vistos.add(row["ID"])
                registros.append({k.strip(): v.strip() for k, v in row.items()})

        return registros

def salvar_registros(registros):
    """Salva a lista de registros no arquivo CSV."""
    with open(ARQUIVO_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Nome", "Matricula", "Setor"])
        writer.writeheader()
        writer.writerows(registros)

def adicionar_registro(nome, matricula, setor):
    """Adiciona um novo registro ao arquivo CSV."""
    registros = carregar_registros()

    if any(r["Matricula"] == matricula for r in registros):
        raise ValueError("Matrícula duplicada")

    # Calcula o próximo ID
    max_id = max((int(r["ID"]) for r in registros), default=0)
    novo_registro = {"ID": str(max_id + 1), "Nome": nome.strip(), "Matricula": matricula.strip(), "Setor": setor.strip()}
    registros.append(novo_registro)

    salvar_registros(registros)
    sinal_global.registros_atualizados.emit()  # Emite sinal de atualização
    return novo_registro

def apagar_registros(ids_para_apagar):
    """Remove registros pelo ID fornecido."""
    registros = carregar_registros()
    ids_para_apagar = set(map(str, ids_para_apagar))  # Converte IDs para strings
    registros_filtrados = [r for r in registros if r["ID"] not in ids_para_apagar]

    salvar_registros(registros_filtrados)
    sinal_global.registros_atualizados.emit()  # Emite sinal de atualização
    return registros_filtrados

# ---------------------------------------
# Funções de Importação e Exportação
# ---------------------------------------

def importar_excel(file_path):
    """Importa registros de um arquivo Excel, identificando erros."""
    registros = carregar_registros()
    erros = []

    # Calcula o próximo ID disponível com base no maior ID atual
    max_id = max((int(r["ID"]) for r in registros), default=0)

    try:
        df = pd.read_excel(file_path)

        for _, row in df.iterrows():
            # Extrai os valores das colunas e garante que são strings, mesmo para valores numéricos
            nome = str(row.get("Nome", "")).strip() if not pd.isna(row.get("Nome", "")) else ""
            matricula = str(row.get("Matricula", "")).strip() if not pd.isna(row.get("Matricula", "")) else ""
            setor = str(row.get("Setor", "")).strip() if not pd.isna(row.get("Setor", "")) else ""

            # Verifica se os campos obrigatórios estão preenchidos
            if not nome or not matricula:
                erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Nome ou Matrícula ausente"})
                continue

            # Verifica se a matrícula já existe
            if any(r["Matricula"] == matricula for r in registros):
                erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Matrícula duplicada"})
                continue

            # Adiciona o novo registro
            max_id += 1
            novo_registro = {"ID": str(max_id), "Nome": nome, "Matricula": matricula, "Setor": setor}
            registros.append(novo_registro)

        # Salva os registros válidos no arquivo CSV
        salvar_registros(registros)

        return registros, erros
    except Exception as e:
        raise Exception(f"Erro ao importar Excel: {e}")

def exportar_modelo(file_path):
    """Exporta um modelo de Excel para novos cadastros."""
    try:
        pd.DataFrame(columns=["Nome", "Matricula", "Setor"]).to_excel(file_path, index=False)
    except Exception as e:
        raise Exception(f"Erro ao exportar modelo: {e}")

def gerar_arquivo_erros(erros, file_path):
    """Gera um arquivo Excel contendo os erros de importação."""
    try:
        pd.DataFrame(erros).to_excel(file_path, index=False)
    except Exception as e:
        raise Exception(f"Erro ao gerar arquivo de erros: {e}")

# ---------------------------------------
# Funções de Teste
# ---------------------------------------

if __name__ == "__main__":
    inicializar_arquivo_csv()
    print("Registros carregados:")
    print(carregar_registros())
