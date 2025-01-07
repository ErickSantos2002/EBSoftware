import sqlite3
import os
import pandas as pd
from typing import List, Optional

# Diretório base do SDK
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "resources", "database.db")


class CadastrosManager:
    def __init__(self, db_path=DB_PATH):
        """Inicializa o gerenciador de cadastros."""
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Banco de dados não encontrado em: {self.db_path}")

    def _connect_db(self):
        """Cria uma conexão com o banco de dados."""
        return sqlite3.connect(self.db_path)

    def add_record(self, name: str, registration: str, department: Optional[str] = None) -> int:
        """
        Adiciona um novo registro de cadastro.
        :param name: Nome do usuário.
        :param registration: Matrícula do usuário (única).
        :param department: Setor do usuário (opcional).
        :return: ID do registro inserido.
        """
        with self._connect_db() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO cadastros (nome, matricula, setor)
                    VALUES (?, ?, ?)
                """, (name, registration, department))
                conn.commit()
                return cursor.lastrowid
            except sqlite3.IntegrityError:
                raise ValueError("Matrícula duplicada. Não foi possível adicionar o registro.")

    def get_all_records(self) -> List[dict]:
        """
        Retorna todos os registros de cadastro em formato JSON.
        :return: Lista de dicionários contendo os cadastros.
        """
        with self._connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nome, matricula, setor FROM cadastros")
            records = cursor.fetchall()

        return [
            {"id": row[0], "name": row[1], "registration": row[2], "department": row[3]}
            for row in records
        ]

    def delete_record(self, record_id: int):
        """
        Remove um registro de cadastro pelo ID.
        :param record_id: ID do registro a ser excluído.
        """
        with self._connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM cadastros WHERE id = ?", (record_id,))
            if cursor.rowcount == 0:
                raise ValueError(f"Registro com ID {record_id} não encontrado.")
            conn.commit()

    def import_from_excel(self, file_path: str) -> List[dict]:
        """
        Importa registros de um arquivo Excel e adiciona ao banco de dados.
        :param file_path: Caminho do arquivo Excel.
        :return: Lista de registros adicionados com sucesso.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Arquivo Excel não encontrado: {file_path}")

        # Lê o Excel e converte para DataFrame
        df = pd.read_excel(file_path)
        added_records = []

        with self._connect_db() as conn:
            cursor = conn.cursor()
            for _, row in df.iterrows():
                name = row.get("Nome", "").strip()
                registration = row.get("Matrícula", "").strip()
                department = row.get("Setor", "").strip()

                if not name or not registration:
                    continue  # Ignora registros inválidos

                try:
                    cursor.execute("""
                        INSERT INTO cadastros (nome, matricula, setor)
                        VALUES (?, ?, ?)
                    """, (name, registration, department))
                    added_records.append({
                        "id": cursor.lastrowid,
                        "name": name,
                        "registration": registration,
                        "department": department,
                    })
                except sqlite3.IntegrityError:
                    continue  # Ignora registros duplicados
            conn.commit()

        return added_records

    def export_to_excel(self, file_path: str):
        """
        Exporta os cadastros para um arquivo Excel.
        :param file_path: Caminho para salvar o arquivo Excel.
        """
        records = self.get_all_records()
        df = pd.DataFrame(records)
        df.to_excel(file_path, index=False)
        print(f"Cadastros exportados para {file_path}")
