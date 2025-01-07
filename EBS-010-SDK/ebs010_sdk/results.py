import sqlite3
import os
import json
from datetime import datetime
from typing import List

# Diretório base do SDK
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "resources", "database.db")


class ResultsManager:
    def __init__(self, db_path=DB_PATH):
        """Inicializa o gerenciador de resultados."""
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Banco de dados não encontrado em: {self.db_path}")

    def _connect_db(self):
        """Cria uma conexão com o banco de dados."""
        return sqlite3.connect(self.db_path)

    def get_all_results(self) -> List[dict]:
        """Retorna todos os resultados armazenados no banco de dados em formato JSON."""
        with self._connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, id_usuario, nome, matricula, setor, data_hora, quantidade_alcool, status
                FROM resultados
            """)
            results = cursor.fetchall()

        # Converte para JSON
        return [
            {
                "id": row[0],
                "user_id": row[1],
                "name": row[2],
                "registration": row[3],
                "department": row[4],
                "timestamp": row[5],
                "alcohol_level": row[6],
                "status": row[7],
            }
            for row in results
        ]

    def get_results_by_date(self, start_date: str, end_date: str) -> List[dict]:
        """
        Retorna os resultados entre duas datas fornecidas.
        :param start_date: Data de início no formato 'YYYY-MM-DD'.
        :param end_date: Data de fim no formato 'YYYY-MM-DD'.
        """
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        with self._connect_db() as conn:
            cursor = conn.cursor()

            # Ajusta a consulta para lidar com o formato "DD/MM/YYYY HH:MM:SS"
            cursor.execute("""
                SELECT id, id_usuario, nome, matricula, setor, data_hora, quantidade_alcool, status
                FROM resultados
                WHERE DATE(substr(data_hora, 7, 4) || '-' || substr(data_hora, 4, 2) || '-' || substr(data_hora, 1, 2)) 
                BETWEEN ? AND ?
            """, (start.date(), end.date()))
            results = cursor.fetchall()

        # Retorna os resultados no formato JSON
        return [
            {
                "id": row[0],
                "user_id": row[1],
                "name": row[2],
                "registration": row[3],
                "department": row[4],
                "timestamp": row[5],
                "alcohol_level": row[6],
                "status": row[7],
            }
            for row in results
        ]

    def export_to_excel(self, file_path: str):
        """
        Exporta os resultados para um arquivo Excel.
        :param file_path: Caminho para salvar o arquivo Excel.
        """
        import pandas as pd

        results = self.get_all_results()
        df = pd.DataFrame(results)
        df.to_excel(file_path, index=False)
        print(f"Resultados exportados para {file_path}")

    def export_to_pdf(self, file_path: str):
        """
        Exporta os resultados para um arquivo PDF.
        :param file_path: Caminho para salvar o arquivo PDF.
        """
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.pdfgen import canvas

        results = self.get_all_results()
        c = canvas.Canvas(file_path, pagesize=landscape(letter))

        # Cabeçalho
        c.setFont("Helvetica-Bold", 12)
        c.drawString(30, 550, "Resultados de Testes - EBS-010 SDK")

        # Dados
        y = 500
        for result in results:
            c.drawString(30, y, f"ID: {result['id']}, Usuário: {result['name']}, Álcool: {result['alcohol_level']}%, Status: {result['status']}")
            y -= 20
            if y < 50:
                c.showPage()
                y = 500

        c.save()
        print(f"Resultados exportados para {file_path}")

    def save_result(self, user_id: int, name: str, registration: str, department: str, alcohol_level: float, status: str):
        """
        Salva um novo resultado no banco de dados.
        :param user_id: ID do usuário.
        :param name: Nome do usuário.
        :param registration: Matrícula do usuário.
        :param department: Setor do usuário.
        :param alcohol_level: Quantidade de álcool detectada.
        :param status: Status do teste (Aprovado/Rejeitado).
        """
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        with self._connect_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resultados (id_usuario, nome, matricula, setor, data_hora, quantidade_alcool, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, name, registration, department, timestamp, alcohol_level, status))
            conn.commit()

        print("Resultado salvo com sucesso!")
