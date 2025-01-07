import os
import sys

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QLineEdit, QFrame, QTabWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMovie

from backend.Cadastros import carregar_cadastros, sinal_global
from src.backend.Testes import executar_teste, parar_testes

# Determina o diretório base (suporta tanto execução normal quanto empacotamento com PyInstaller)
BASE_DIR = (
    sys._MEIPASS if getattr(sys, 'frozen', False) else os.path.abspath(os.path.dirname(__file__))
)
LOADING_GIF = os.path.join(BASE_DIR, "assets", "loading.gif")

def atualizar_status_spinner(status_code):
    """Mapeia os códigos de status do dispositivo para mensagens amigáveis."""
    status_map = {
        "T": "Inicializando teste...",
        "$WAIT": "Aguardando...",
        "$STANBY": "Pronto para o teste...",
        "$TRIGGER": "Assoprando no dispositivo...",
        "$BREATH": "Analisando o sopro...",
        "$RESULT": "Processando resultado...",
        "$END": "Teste concluído. Pronto para outro teste."
    }
    return status_map.get(status_code, "Teste em andamento...")

# Centralização de estilos
STYLES = {
    "input": "font-family: Arial; font-size: 12px; background-color: #f0f0f0; border: 1px solid #cccccc; padding: 5px;",
    "button_iniciar": """
        QPushButton {
            font-family: Arial; font-size: 12px; font-weight: bold; background-color: #0072B7; 
            color: white; border: 1px solid #005A9E; padding: 5px 10px;
        }
        QPushButton:hover { background-color: #005BB5; }
        QPushButton:pressed { background-color: #003F87; }
    """,
    "button_parar": """
        QPushButton {
            font-family: Arial; font-size: 12px; font-weight: bold; background-color: #FF0000; 
            color: white; border: 1px solid #CC0000; padding: 5px 10px;
        }
        QPushButton:hover { background-color: #CC0000; }
        QPushButton:pressed { background-color: #990000; }
    """,
    "label_status": """
        font-family: Arial; font-size: 12px; font-weight: bold; color: #0072B7;
        background-color: #f0f0f0; padding: 5px; border: 1px solid #cccccc;
    """,
    "table": """
        font-family: Arial; font-size: 12px; background-color: #f0f0f0; border: 1px solid #cccccc;
    """
}

class TestesTela(QWidget):
    resultado_recebido = pyqtSignal(str)
    erro_recebido = pyqtSignal(str)
    exibir_resultado = pyqtSignal(str)  # Novo sinal
    atualizar_spinner = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()
        self.connect_signals()
        self.carregar_cadastros()

    def setup_ui(self):
        """Configura o layout principal e os componentes da tela."""
        # Tab Widget
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("background-color: white;")

        # Aba Teste Manual
        self.tab_manual = QWidget()
        self.setup_tab_manual()

        # Aba Teste Automático
        self.tab_automatico = QWidget()
        self.setup_tab_automatico()

        # Adiciona as abas ao QTabWidget
        self.tabs.addTab(self.tab_manual, "Testes Manuais")
        self.tabs.addTab(self.tab_automatico, "Testes Automáticos")

        # Inicializa o widget de status
        self.init_status_widget()

        # Layout principal
        layout = QVBoxLayout(self)
        layout.addWidget(self.tabs)
        layout.addWidget(self.status_widget)  # Adiciona o widget de status ao layout principal

    def setup_tab_manual(self):
        """Configura a aba de Testes Manuais."""
        layout = QVBoxLayout(self.tab_manual)

        # Barra de pesquisa
        self.init_search_bar(layout)

        # Tabela de cadastros
        self.init_table(layout)

        # Botões específicos para teste manual
        btn_manual = self.create_button("Iniciar Teste Manual", STYLES["button_iniciar"], self.iniciar_teste_manual)
        layout.addWidget(btn_manual, alignment=Qt.AlignCenter)

        # Botão para parar testes
        btn_parar_manual = self.create_button("Parar Testes", STYLES["button_parar"], self.parar_testes)
        layout.addWidget(btn_parar_manual, alignment=Qt.AlignCenter)

        self.tab_manual.setLayout(layout)

    def setup_tab_automatico(self):
        """Configura a aba de Testes Automáticos."""
        layout = QVBoxLayout(self.tab_automatico)

        # Botão para iniciar testes automáticos
        btn_automatico = self.create_button("Iniciar Teste Automático", STYLES["button_iniciar"], self.iniciar_teste_automatico)
        layout.addWidget(btn_automatico, alignment=Qt.AlignCenter)

        # Botão para parar testes
        btn_parar_automatico = self.create_button("Parar Testes", STYLES["button_parar"], self.parar_testes)
        layout.addWidget(btn_parar_automatico, alignment=Qt.AlignCenter)

        self.tab_automatico.setLayout(layout)

    def connect_signals(self):
        """Conecta sinais aos respectivos slots."""
        sinal_global.cadastros_atualizados.connect(self.carregar_cadastros)
        self.resultado_recebido.connect(self.mostrar_resultado)
        self.erro_recebido.connect(self.mostrar_erro)
        self.exibir_resultado.connect(self.mostrar_resultado)
        self.atualizar_spinner.connect(self.start_spinner)

    def init_search_bar(self, layout):
        """Cria a barra de pesquisa."""
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar por Nome, Matrícula ou Setor...")
        self.search_input.setStyleSheet(STYLES["input"])
        self.search_input.returnPressed.connect(self.pesquisar_cadastros)

        search_button = QPushButton("Pesquisar")
        search_button.setStyleSheet(STYLES["button_iniciar"])
        search_button.clicked.connect(self.pesquisar_cadastros)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

    def init_table(self, layout):
        """Configura a tabela para exibição dos cadastros."""
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Matrícula", "Setor"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSelectionMode(QTableWidget.SingleSelection)  # Proibir seleção múltipla
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)  # Proibir edição por duplo clique
        self.tabela.verticalHeader().setVisible(False)  # Remover o VerticalHeader
        self.tabela.setStyleSheet(STYLES["table"])  # Aplicar estilo à tabela
        layout.addWidget(self.tabela)

    def init_status_widget(self):
        """Configura o widget de status e spinner."""
        self.status_widget = QWidget(self)
        self.status_widget.setFixedSize(300, 50)  # Aumenta o tamanho para melhor visibilidade
        self.status_widget.setStyleSheet("background-color: transparent;")
        self.status_widget.hide()

        status_layout = QHBoxLayout(self.status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)

        self.status_label = QLabel("Status: Pronto", self.status_widget)
        self.status_label.setStyleSheet(STYLES["label_status"])
        self.status_label.setFixedSize(200, 30)  # Ajusta o tamanho da label

        self.spinner = QLabel(self.status_widget)
        self.spinner.setFixedSize(32, 32)
        self.spinner.setStyleSheet("background-color: transparent;")
        self.movie = QMovie(LOADING_GIF)
        self.movie.setScaledSize(self.spinner.size())
        self.spinner.setMovie(self.movie)

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.spinner)

    def create_button(self, text, style, callback):
        """Cria um botão configurado."""
        button = QPushButton(text)
        button.setStyleSheet(style)
        button.clicked.connect(callback)
        return button

    # Métodos de controle de cadastros
    def carregar_cadastros(self):
        """Carrega os cadastros e exibe na tabela."""
        cadastros = carregar_cadastros()
        self.populate_table(cadastros)

    def pesquisar_cadastros(self):
        """Filtra cadastros com base no termo pesquisado."""
        termo = self.search_input.text().lower()
        cadastros = carregar_cadastros()
        cadastros_filtrados = [
            registro for registro in cadastros
            if termo in str(registro["Nome"]).lower()
            or termo in str(registro["Matricula"]).lower()
            or termo in str(registro["Setor"]).lower()
        ]
        self.populate_table(cadastros_filtrados)

    def populate_table(self, cadastros):
        """Popula a tabela com os cadastros fornecidos."""
        self.tabela.setRowCount(len(cadastros))
        for row, registro in enumerate(cadastros):
            self.tabela.setItem(row, 0, QTableWidgetItem(str(registro["ID"])))
            self.tabela.setItem(row, 1, QTableWidgetItem(registro["Nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(registro["Matricula"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(registro["Setor"]))

    # Métodos para testes
    def iniciar_teste_manual(self):
        """Inicia um teste manual."""
        self.execute_test(automatico=False)

    def iniciar_teste_automatico(self):
        """Inicia testes automáticos."""
        self.execute_test(automatico=True)

    def execute_test(self, automatico):
        """Executa o teste manual ou automático."""
        linhas_selecionadas = self.tabela.selectionModel().selectedRows()
        if not linhas_selecionadas and not automatico:
            QMessageBox.warning(self, "Erro", "Selecione um registro para realizar o teste.")
            return

        if automatico:
            params = (None, None, None, None)
        else:
            linha = linhas_selecionadas[0].row()
            params = (
                self.tabela.item(linha, 0).text(),
                self.tabela.item(linha, 1).text(),
                self.tabela.item(linha, 2).text(),
                self.tabela.item(linha, 3).text(),
            )

        self.start_spinner("Teste iniciado...")
        try:
            executar_teste(*params, automatico=automatico, callback=self.handle_test_result)
        except Exception as e:
            self.stop_spinner()
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar o teste: {e}")

    def handle_test_result(self, resultado):
        """Processa o resultado do teste ou atualiza o spinner."""
        if resultado.startswith("ERRO"):
            self.erro_recebido.emit(resultado.split("-", 1)[1])
        elif resultado.startswith("$"):
            # Atualiza o spinner com base no status intermediário
            status_text = atualizar_status_spinner(resultado)
            self.start_spinner(status_text)  # Chamada direta ao spinner na thread principal
        else:
            # Exibe o resultado apenas em testes manuais
            if not self.tabs.currentIndex():  # Verifica se está na aba de Testes Manuais
                self.exibir_resultado.emit(resultado)

        # Limpa a seleção após o teste
        self.tabela.clearSelection()

    def parar_testes(self):
        """Para os testes em execução."""
        try:
            parar_testes()
            QMessageBox.information(self, "Parado", "Testes interrompidos com sucesso.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao parar os testes: {e}")
        finally:
            self.stop_spinner()

    # Métodos para spinner e status
    def start_spinner(self, status_text):
        """Inicia o spinner e exibe o status dinamicamente."""
        self.status_label.setText(f"Status: {status_text}")
        self.spinner.show()
        self.movie.start()
        self.status_widget.show()

    def stop_spinner(self):
        """Para o spinner e oculta o status."""
        self.spinner.hide()
        self.movie.stop()
        self.status_widget.hide()

    def mostrar_erro(self, mensagem):
        """Exibe mensagens de erro."""
        QMessageBox.critical(self, "Erro", mensagem)

    def mostrar_resultado(self, resultado):
        """Exibe o resultado final do teste."""
        self.stop_spinner()
        try:
            quantidade, status = resultado.split("-")
            if status == "HIGH":
                QMessageBox.warning(self, "Resultado do Teste", f"Reprovado: {quantidade}")
            else:
                QMessageBox.information(self, "Resultado do Teste", f"Aprovado: {quantidade}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar o resultado: {e}")