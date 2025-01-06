import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton,
    QLineEdit, QFormLayout, QMessageBox, QHeaderView, QFrame, QFileDialog, QInputDialog
)
from PyQt5.QtCore import Qt
from backend.Cadastros import (
    carregar_cadastros, adicionar_registro, apagar_cadastros, importar_excel,
    exportar_modelo, gerar_arquivo_erros, atualizar_cadastro
)

# Determina o diretório base
BASE_DIR = (
    os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

# Estilos centralizados
STYLES = {
    "input": "font-family: Arial; font-size: 12px; background-color: #f0f0f0; border: 1px solid #cccccc; padding: 5px;",
    "btn_pesquisar": """
        QPushButton {
            font-family: Arial; font-size: 12px; font-weight: bold; background-color: #0072B7; 
            color: white; border: 1px solid #005A9E; padding: 5px 10px;
        }
        QPushButton:hover { background-color: #005BB5; }
        QPushButton:pressed { background-color: #003F87; }
    """,
    "button": """
        QPushButton {
            font-family: Arial; font-size: 12px; background-color: #f0f0f0;
            border: 1px solid #cccccc; padding: 5px;  /* Alinha padding com input */
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
        self.search_input.setPlaceholderText("Pesquisar por ID, Nome, Matrícula ou Setor...")
        self.search_input.setStyleSheet(STYLES["input"])
        self.search_input.returnPressed.connect(self.pesquisar_cadastros)

        search_button = QPushButton("Pesquisar")
        search_button.setStyleSheet(STYLES["btn_pesquisar"])
        search_button.setMinimumHeight(self.search_input.sizeHint().height())  # Ajusta a altura mínima do botão
        search_button.clicked.connect(self.pesquisar_cadastros)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        left_panel.addLayout(search_layout)

        # Botões acima da tabela
        top_buttons_layout = QHBoxLayout()
        importar_btn = QPushButton("Importar Excel")
        importar_btn.setStyleSheet(STYLES["button"])
        importar_btn.clicked.connect(self.importar_cadastro)

        exportar_btn = QPushButton("Exportar Excel")
        exportar_btn.setStyleSheet(STYLES["button"])
        exportar_btn.clicked.connect(self.exportar_cadastro)

        modelo_btn = QPushButton("Baixar Modelo Base")
        modelo_btn.setStyleSheet(STYLES["button"])
        modelo_btn.clicked.connect(self.baixar_modelo_base)

        top_buttons_layout.addWidget(importar_btn)
        top_buttons_layout.addWidget(exportar_btn)
        top_buttons_layout.addWidget(modelo_btn)
        left_panel.addLayout(top_buttons_layout)

        # Tabela
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)  # Define 4 colunas
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Matrícula", "Setor"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSortingEnabled(True)
        self.tabela.setStyleSheet(STYLES["table"])

        # Desabilita a edição direta na tabela
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)

        self.tabela.verticalHeader().setVisible(False)

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
        form_layout = QFormLayout()  # Use QFormLayout diretamente para o formulário
        self.nome_input = self.create_input_field("Nome")
        self.matricula_input = self.create_input_field("Matrícula")
        self.setor_input = self.create_input_field("Setor")

        # Adiciona os campos ao formulário
        form_layout.addRow("Nome:", self.nome_input)
        form_layout.addRow("Matrícula:", self.matricula_input)
        form_layout.addRow("Setor:", self.setor_input)

        # Adiciona o formulário ao painel direito
        right_panel.addLayout(form_layout)

        # Botão cadastrar
        cadastrar_btn = QPushButton("Cadastrar")
        cadastrar_btn.setStyleSheet(STYLES["button"])
        cadastrar_btn.clicked.connect(self.cadastrar_usuario)
        right_panel.addWidget(cadastrar_btn)

        # Botão apagar cadastro
        apagar_btn = QPushButton("Apagar Cadastro")
        apagar_btn.setStyleSheet(STYLES["button"])
        apagar_btn.clicked.connect(self.apagar_registro)
        right_panel.addWidget(apagar_btn)

        # Botão editar cadastro
        editar_btn = QPushButton("Editar Cadastro")
        editar_btn.setStyleSheet(STYLES["button"])
        editar_btn.clicked.connect(self.editar_cadastro)
        right_panel.addWidget(editar_btn)

        # Adiciona o painel direito ao layout principal
        layout.addLayout(right_panel, stretch=1)

    def create_input_field(self, placeholder):
        """Cria e retorna um campo de entrada com um placeholder."""
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder)
        input_field.setStyleSheet(STYLES["input"])
        return input_field

    # Funções para manipular a tabela e cadastros
    def carregar_dados(self):
        """Carrega os cadastros do banco de dados e preenche a tabela."""
        cadastros = carregar_cadastros()
        self.tabela.setRowCount(len(cadastros))
        for row, registro in enumerate(cadastros):
            self.tabela.setItem(row, 0, QTableWidgetItem(registro["ID"]))
            self.tabela.setItem(row, 1, QTableWidgetItem(registro["Nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(registro["Matricula"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(registro["Setor"]))

    def pesquisar_cadastros(self):
        """Filtra os cadastros com base no termo pesquisado."""
        termo = self.search_input.text().lower()
        cadastros = carregar_cadastros()
        cadastros_filtrados = [
            registro for registro in cadastros
            if termo in registro["ID"].lower() or termo in registro["Nome"].lower() or termo in registro["Matricula"].lower() or termo in registro["Setor"].lower()
        ]
        self.carregar_dados_filtrados(cadastros_filtrados)

    def carregar_dados_filtrados(self, cadastros):
        """Popula a tabela com cadastros filtrados."""
        self.tabela.setRowCount(len(cadastros))
        for row, registro in enumerate(cadastros):
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
        """Remove os cadastros selecionados."""
        linhas_selecionadas = self.tabela.selectionModel().selectedRows()
        if not linhas_selecionadas:
            QMessageBox.warning(self, "Erro", "Selecione um registro para apagar.")
            return
        ids_para_apagar = [self.tabela.item(linha.row(), 0).text() for linha in linhas_selecionadas]
        apagar_cadastros(ids_para_apagar)
        QMessageBox.information(self, "Sucesso", "cadastros apagados com sucesso.")
        self.carregar_dados()

    def importar_cadastro(self):
        """Importa cadastros de um arquivo Excel."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo Excel", "", "Arquivos Excel (*.xlsx)")
        if file_path:
            try:
                cadastros, erros = importar_excel(file_path)
                self.carregar_dados()
                if erros:
                    erro_path = os.path.join(os.path.dirname(file_path), "Erros_Importacao.xlsx")
                    gerar_arquivo_erros(erros, erro_path)
                    QMessageBox.warning(self, "Aviso", f"Alguns cadastros apresentaram erros. Detalhes salvos em: {erro_path}")
                else:
                    QMessageBox.information(self, "Sucesso", "Todos os cadastros foram importados com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar cadastros: {e}")

    def exportar_cadastro(self):
        """Exporta os cadastros para um arquivo Excel."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar cadastros", "Cadastros", "Arquivos Excel (*.xlsx)")
        if file_path:
            try:
                cadastros = carregar_cadastros()
                df = pd.DataFrame(cadastros)
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Sucesso", f"cadastros exportados para {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar cadastros: {e}")

    def baixar_modelo_base(self):
        """Salva um modelo de cadastro em Excel."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Salvar modelo", "Modelo Base", "Arquivos Excel (*.xlsx)")
        if file_path:
            try:
                exportar_modelo(file_path)
                QMessageBox.information(self, "Sucesso", f"Modelo base salvo em {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar modelo base: {e}")

    def editar_cadastro(self):
        """Edita os campos Nome, Matrícula ou Setor de um usuário selecionado."""
        linhas_selecionadas = self.tabela.selectionModel().selectedRows()
        if not linhas_selecionadas:
            QMessageBox.warning(self, "Erro", "Selecione um registro para editar.")
            return

        linha = linhas_selecionadas[0].row()
        id_usuario = self.tabela.item(linha, 0).text()  # ID do usuário

        # Solicitar o novo nome
        nome_atual = self.tabela.item(linha, 1).text()
        novo_nome, ok_nome = QInputDialog.getText(self, "Editar Nome", "Digite o novo nome:", QLineEdit.Normal, nome_atual)
        if not ok_nome:  # Usuário cancelou a edição do nome
            return
        if not novo_nome.strip():
            QMessageBox.warning(self, "Aviso", "Nome não pode estar vazio.")
            return

        # Solicitar a nova matrícula
        matricula_atual = self.tabela.item(linha, 2).text()
        nova_matricula, ok_matricula = QInputDialog.getText(self, "Editar Matrícula", "Digite a nova matrícula:", QLineEdit.Normal, matricula_atual)
        if not ok_matricula:  # Usuário cancelou a edição da matrícula
            return
        if not nova_matricula.strip():
            QMessageBox.warning(self, "Aviso", "Matrícula não pode estar vazia.")
            return

        # Solicitar o novo setor
        setor_atual = self.tabela.item(linha, 3).text()
        novo_setor, ok_setor = QInputDialog.getText(self, "Editar Setor", "Digite o novo setor:", QLineEdit.Normal, setor_atual)
        if not ok_setor:  # Usuário cancelou a edição do setor
            return
        if not novo_setor.strip():
            QMessageBox.warning(self, "Aviso", "Setor não pode estar vazio.")
            return

        # Atualizar os campos no banco de dados
        try:
            atualizar_cadastro(id_usuario, novo_nome.strip(), nova_matricula.strip(), novo_setor.strip())
            QMessageBox.information(self, "Sucesso", "Cadastro atualizado com sucesso!")
            self.carregar_dados()  # Recarrega os dados para refletir a atualização
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))