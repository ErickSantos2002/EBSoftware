import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QFormLayout, QMessageBox, QHeaderView, QFrame, QFileDialog
)
from PyQt5.QtCore import Qt
from backend.Cadastros import (
    carregar_registros, adicionar_registro, apagar_registros, importar_excel,
    exportar_modelo, gerar_arquivo_erros
)

# Determina o diretório base
BASE_DIR = (
    os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

# Estilos centralizados
STYLES = {
    "input": "font-family: Arial; font-size: 12px; background-color: #f0f0f0; border: 1px solid #cccccc; padding: 5px;",
    "button": """
        QPushButton {
            font-family: Arial; font-size: 12px; background-color: #f0f0f0;
            border: 1px solid #cccccc; padding: 5px; margin-top: 5px;
        }
        QPushButton:hover { background-color: #e0e0e0; }
        QPushButton:pressed { background-color: #d0d0d0; border-style: inset; }
    """,
    "label_title": "font-family: Arial Black; font-size: 20px; background-color: #f0f0f0; margin-bottom: 10px;",
    "table": "font-family: Arial; font-size: 12px; background-color: #f0f0f0; border: 1px solid #cccccc;",
}

class CustomTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        """Permite ordenação baseada em valores inteiros quando possível."""
        try:
            return int(self.data(Qt.UserRole)) < int(other.data(Qt.UserRole))
        except (ValueError, TypeError):
            return super().__lt__(other)

class CadastrosTela(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.carregar_dados()

    def setup_ui(self):
        """Configura o layout principal e os painéis."""
        # Frame principal
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: white; border: none;")
        main_layout = QVBoxLayout(self.frame)

        # Layout interno
        inner_layout = QHBoxLayout()
        self.init_left_panel(inner_layout)
        self.init_right_panel(inner_layout)

        main_layout.addLayout(inner_layout)
        inner_layout.setContentsMargins(10, 10, 10, 10)
        inner_layout.setSpacing(10)

        # Configuração do layout principal do widget
        final_layout = QVBoxLayout(self)
        final_layout.addWidget(self.frame)

    def init_left_panel(self, layout):
        """Cria o painel esquerdo com tabela e campo de pesquisa."""
        left_panel = QVBoxLayout()

        # Título
        titulo = QLabel("Tabela de Cadastros")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(STYLES["label_title"])
        left_panel.addWidget(titulo)

        # Campo de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar por Nome, Matrícula ou Setor...")
        self.search_input.setStyleSheet(STYLES["input"])
        self.search_input.returnPressed.connect(self.pesquisar_registros)
        search_button = QPushButton("Pesquisar")
        search_button.setStyleSheet(STYLES["button"])
        search_button.clicked.connect(self.pesquisar_registros)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        left_panel.addLayout(search_layout)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Matrícula", "Setor"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSortingEnabled(True)
        self.tabela.setStyleSheet(STYLES["table"])
        left_panel.addWidget(self.tabela)

        layout.addLayout(left_panel, stretch=2)

    def init_right_panel(self, layout):
        """Cria o painel direito com formulário e botões."""
        right_panel = QVBoxLayout()

        # Título
        titulo = QLabel("Gerenciar Cadastros")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet(STYLES["label_title"])
        right_panel.addWidget(titulo)

        # Formulário
        form_layout = QVBoxLayout()
        form_fields = QFormLayout()
        self.nome_input = self.create_input_field("Nome", form_fields)
        self.matricula_input = self.create_input_field("Matrícula", form_fields)
        self.setor_input = self.create_input_field("Setor", form_fields)
        form_layout.addLayout(form_fields)

        # Botão cadastrar
        cadastrar_btn = QPushButton("Cadastrar")
        cadastrar_btn.setStyleSheet(STYLES["button"])
        cadastrar_btn.clicked.connect(self.cadastrar_usuario)
        form_layout.addWidget(cadastrar_btn)

        right_panel.addLayout(form_layout)
        self.add_right_buttons(right_panel)
        layout.addLayout(right_panel, stretch=1)

    def create_input_field(self, placeholder, layout):
        """Cria um campo de entrada e adiciona ao layout do formulário."""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet(STYLES["input"])
        layout.addRow(f"{placeholder}:", input_field)
        return input_field

    def add_right_buttons(self, layout):
        """Cria os botões na área direita."""
        buttons = [
            ("Apagar Registro", self.apagar_registro),
            ("Importar Excel", self.importar_cadastro),
            ("Exportar Excel", self.exportar_cadastro),
            ("Baixar Modelo Base", self.baixar_modelo_base),
        ]
        for text, func in buttons:
            button = QPushButton(text)
            button.setStyleSheet(STYLES["button"])
            button.clicked.connect(func)
            layout.addWidget(button)

    # Funções para manipular a tabela e registros
    def carregar_dados(self):
        """Carrega os registros e preenche a tabela."""
        registros = carregar_registros()
        self.tabela.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            id_item = CustomTableWidgetItem(str(registro["ID"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setData(Qt.UserRole, int(registro["ID"]))
            self.tabela.setItem(row, 0, id_item)
            self.tabela.setItem(row, 1, QTableWidgetItem(registro["Nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(registro["Matricula"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(registro["Setor"]))

    def pesquisar_registros(self):
        """Filtra os registros com base no termo pesquisado."""
        termo = self.search_input.text().lower()
        registros = carregar_registros()
        registros_filtrados = [
            registro for registro in registros
            if termo in registro["Nome"].lower() or termo in registro["Matricula"].lower() or termo in registro["Setor"].lower()
        ]
        self.carregar_dados_filtrados(registros_filtrados)

    def carregar_dados_filtrados(self, registros):
        """Popula a tabela com registros filtrados."""
        self.tabela.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            id_item = CustomTableWidgetItem(str(registro["ID"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setData(Qt.UserRole, int(registro["ID"]))
            self.tabela.setItem(row, 0, id_item)
            self.tabela.setItem(row, 1, QTableWidgetItem(registro["Nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(registro["Matricula"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(registro["Setor"]))

    def cadastrar_usuario(self):
        """Adiciona um novo registro ao sistema."""
        nome = self.nome_input.text().strip()
        matricula = self.matricula_input.text().strip()
        setor = self.setor_input.text().strip()
        if not nome or not matricula:
            QMessageBox.warning(self, "Erro", "Os campos Nome e Matrícula são obrigatórios.")
            return
        try:
            adicionar_registro(nome, matricula, setor)
            QMessageBox.information(self, "Sucesso", "Registro adicionado com sucesso!")
            self.carregar_dados()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))

    def apagar_registro(self):
        """Remove os registros selecionados."""
        linhas_selecionadas = self.tabela.selectionModel().selectedRows()
        if not linhas_selecionadas:
            QMessageBox.warning(self, "Erro", "Selecione um registro para apagar.")
            return
        ids_para_apagar = [self.tabela.item(linha.row(), 0).text() for linha in linhas_selecionadas]
        apagar_registros(ids_para_apagar)
        QMessageBox.information(self, "Sucesso", "Registros apagados com sucesso.")
        self.carregar_dados()

    def importar_cadastro(self):
        """Importa registros de um arquivo Excel."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo Excel", "", "Arquivos Excel (*.xlsx)")
        if file_path:
            try:
                registros, erros = importar_excel(file_path)
                self.carregar_dados()
                if erros:
                    erro_path = os.path.join(os.path.dirname(file_path), "Erros_Importacao.xlsx")
                    gerar_arquivo_erros(erros, erro_path)
                    QMessageBox.warning(self, "Aviso", f"Alguns registros apresentaram erros. Detalhes salvos em: {erro_path}")
                else:
                    QMessageBox.information(self, "Sucesso", "Todos os registros foram importados com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar registros: {e}")

    def exportar_cadastro(self):
        """Exporta os registros para um arquivo Excel."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar registros", "Cadastros", "Arquivos Excel (*.xlsx)")
        if file_path:
            try:
                registros = carregar_registros()
                df = pd.DataFrame(registros)
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Sucesso", f"Registros exportados para {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar registros: {e}")

    def baixar_modelo_base(self):
        """Salva um modelo de cadastro em Excel."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar modelo", "Modelo Base", "Arquivos Excel (*.xlsx)")
        if file_path:
            try:
                exportar_modelo(file_path)
                QMessageBox.information(self, "Sucesso", f"Modelo base salvo em {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar modelo base: {e}")
