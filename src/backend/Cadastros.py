import os
import csv
import pandas as pd
import sys
from PyQt5.QtCore import QObject, pyqtSignal
import sqlite3
from src.backend.db import conectar

# Gerenciador de sinais
class SignalManager(QObject):
    cadastros_atualizados = pyqtSignal()

# Instância global do gerenciador de sinais
sinal_global = SignalManager()

# Diretórios e arquivos
BASE_DIR = sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
ARQUIVO_CSV = os.path.join(RESOURCES_DIR, "cadastros.csv")

# ---------------------------------------
# Funções de Inicialização e Utilidades
# ---------------------------------------

def inicializar_arquivo_csv():
    """Verifica e cria o arquivo CSV de cadastros, se necessário."""
    if not os.path.exists(RESOURCES_DIR):
        os.makedirs(RESOURCES_DIR)
    if not os.path.exists(ARQUIVO_CSV):
        with open(ARQUIVO_CSV, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["ID", "Nome", "Matricula", "Setor"])
            writer.writeheader()

# ---------------------------------------
# Funções de Manipulação de cadastros
# ---------------------------------------

def atualizar_cadastro(id_usuario, nome, matricula, setor):
    """Atualiza os dados de um cadastro no banco de dados."""
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE cadastros
                SET nome = ?, matricula = ?, setor = ?
                WHERE id = ?
            """, (nome, matricula, setor, id_usuario))
            conn.commit()
            sinal_global.cadastros_atualizados.emit()  # Notifica a interface
        except sqlite3.IntegrityError:
            raise ValueError("Matrícula duplicada.")
        
def carregar_cadastros():
    """Carrega cadastros do banco de dados."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, matricula, setor FROM cadastros")
        cadastros = [{"ID": str(row[0]), "Nome": row[1], "Matricula": row[2], "Setor": row[3]} for row in cursor.fetchall()]
    return cadastros

def salvar_cadastros(cadastros):
    """Salva a lista de cadastros no arquivo CSV."""
    with open(ARQUIVO_CSV, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Nome", "Matricula", "Setor"])
        writer.writeheader()
        writer.writerows(cadastros)

def adicionar_registro(nome, matricula, setor):
    """Adiciona um novo registro ao banco de dados."""
    with conectar() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
            INSERT INTO cadastros (nome, matricula, setor)
            VALUES (?, ?, ?)""", (nome, matricula, setor))
            conn.commit()
            sinal_global.cadastros_atualizados.emit()  # Notifica a interface
        except sqlite3.IntegrityError:
            raise ValueError("Matrícula duplicada")

def apagar_cadastros(ids_para_apagar):
    """Remove cadastros do banco de dados pelo ID."""
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cadastros WHERE id IN ({})".format(", ".join("?" * len(ids_para_apagar))), ids_para_apagar)
        conn.commit()
        sinal_global.cadastros_atualizados.emit()

# ---------------------------------------
# Funções de Importação e Exportação
# ---------------------------------------

def importar_excel(file_path):
    """Importa cadastros de um arquivo Excel, identificando erros."""
    cadastros = carregar_cadastros()
    erros = []

    # Calcula o próximo ID disponível com base no maior ID atual
    max_id = max((int(r["ID"]) for r in cadastros), default=0)

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
            if any(r["Matricula"] == matricula for r in cadastros):
                erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Matrícula duplicada"})
                continue

            # Adiciona o novo registro
            max_id += 1
            novo_registro = {"ID": str(max_id), "Nome": nome, "Matricula": matricula, "Setor": setor}
            cadastros.append(novo_registro)

        # Salva os cadastros válidos no arquivo CSV
        salvar_cadastros(cadastros)

        return cadastros, erros
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
    print("cadastros carregados:")
    print(carregar_cadastros())
