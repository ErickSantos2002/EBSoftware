import os
import csv
import pandas as pd

# Caminho base para o diretório do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Caminho do arquivo atual (backend)
PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # Sai de src/backend
RESOURCES_DIR = os.path.join(PROJECT_DIR, "resources")  # Caminho do diretório resources
ARQUIVO_CSV = os.path.join(RESOURCES_DIR, "registros.csv")  # Caminho completo do arquivo CSV

# Função para carregar os registros do CSV
def carregar_registros():
    """Carrega registros do arquivo CSV e remove inconsistências."""
    if not os.path.exists(ARQUIVO_CSV):
        return []  # Retorna uma lista vazia se o arquivo não existir
    with open(ARQUIVO_CSV, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        registros = []
        for row in reader:
            # Limpa chaves e valores (remover espaços, caracteres inválidos, etc.)
            registros.append({k.strip(): v.strip() for k, v in row.items()})
        return registros

# Função para salvar registros no CSV
def salvar_registros(registros):
    """Salva a lista de registros no arquivo CSV."""
    with open(ARQUIVO_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Nome", "Matricula", "Setor"])
        writer.writeheader()
        writer.writerows(registros)

# Função para importar registros de um arquivo Excel
def importar_excel(file_path):
    """Importa registros de um arquivo Excel."""
    registros = carregar_registros()
    erros = []

    try:
        df = pd.read_excel(file_path)
        for _, row in df.iterrows():
            nome = row.get("Nome", "").strip()
            matricula = row.get("Matricula", "").strip()
            setor = row.get("Setor", "").strip()

            # Verifica se campos obrigatórios estão preenchidos
            if not nome or not matricula:
                erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Nome ou Matricula ausente"})
                continue

            # Verifica se matrícula já existe
            if any(r["Matricula"] == matricula for r in registros):
                erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Matricula duplicada"})
                continue

            # Adiciona registro válido
            novo_registro = {"ID": str(len(registros) + 1), "Nome": nome, "Matricula": matricula, "Setor": setor}
            registros.append(novo_registro)

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

    novo_registro = {"ID": str(len(registros) + 1), "Nome": nome, "Matricula": matricula, "Setor": setor}
    registros.append(novo_registro)
    salvar_registros(registros)

    return novo_registro

# Função para apagar registros
def apagar_registros(ids_para_apagar):
    """Apaga os registros com os IDs fornecidos."""
    registros = carregar_registros()
    registros_filtrados = [r for r in registros if r["ID"] not in ids_para_apagar]
    salvar_registros(registros_filtrados)
    return registros_filtrados

# Teste standalone
if __name__ == "__main__":
    # Exemplos de uso
    print("Carregando registros...")
    print(carregar_registros())
