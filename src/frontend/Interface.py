import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QStackedLayout, QPushButton,
    QMessageBox, QToolButton
)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize


# Configuração do diretório base
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.append(os.path.join(BASE_DIR, "src"))

# Cores
COR_AZUL = "#0072B7"
COR_CINZA = "#969595"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EBS-010 Interface")
        self.setGeometry(100, 100, 1200, 800)
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "assets", "HS2.ico")))

        # Inicializa o mapeamento dos módulos
        self.mapeamento_modulos = {
            "Cadastros": "frontend.Cadastros_Tela.CadastrosTela",
            "Testes": "frontend.Testes_Tela.TestesTela",
            "Resultados": "frontend.Resultados_Tela.ResultadosTela",
            "Configurações": "frontend.Configuracoes_Tela.ConfiguracoesTela",
            "Informações": "frontend.Informacoes_Tela.InformacoesTela",
        }

        # Inicializa os módulos carregados
        self.modulos_carregados = {}

        # Layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Barra superior
        self.create_top_bar(main_layout)

        # Área principal com QStackedLayout
        self.main_area = QWidget()
        self.stacked_layout = QStackedLayout(self.main_area)
        main_layout.addWidget(self.main_area)

        # Dicionário de módulos
        self.modulos = {}

    def create_top_bar(self, layout):
        """Cria a barra superior com botões para os módulos e adiciona a logo."""
        self.top_bar_buttons = {}  # Dicionário para armazenar os botões e associá-los aos módulos

        top_bar = QWidget()
        top_bar.setFixedHeight(100)  # Ajusta para comportar ícones e texto
        top_bar.setStyleSheet(f"""
            background: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
            stop:0 {COR_AZUL}, stop:1 white);
        """)

        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(10, 0, 10, 0)
        top_layout.setSpacing(15)  # Espaçamento entre os botões

        # Botões com ícone acima do texto
        for nome in self.mapeamento_modulos.keys():
            botao = QToolButton()
            botao.setText(nome)
            botao.setIcon(QIcon(os.path.join(BASE_DIR, "assets", f"{nome}.png")))
            botao.setIconSize(QSize(40, 40))
            botao.setStyleSheet("""
                QToolButton {
                    background: transparent;
                    border: 2px solid transparent;  /* Contorno invisível por padrão */
                    font-size: 14px;
                    font-weight: bold;
                    color: black;
                }
                QToolButton:hover {
                    color: white;  /* Texto branco no hover */
                    border: 2px solid #969595;  /* Borda cinza no hover */
                    border-radius: 8px;
                }
                QToolButton[selected="true"] {
                    border: 2px solid #969595;  /* Contorno cinza para botão selecionado */
                    border-radius: 8px;
                    color: white;  /* Mantém o texto branco quando selecionado */
                }
            """)
            botao.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)  # Coloca o texto abaixo do ícone
            botao.clicked.connect(lambda checked, nome=nome: self.abrir_modulo(nome))
            self.top_bar_buttons[nome] = botao  # Armazena o botão associado ao módulo
            top_layout.addWidget(botao)

        # Adiciona a logo no final da barra
        logo_button = QPushButton()
        logo_button.setIcon(QIcon(os.path.join(BASE_DIR, "assets", "Logo.png")))
        logo_button.setIconSize(QSize(140, 80))
        logo_button.setStyleSheet("border: none; background: transparent;")
        logo_button.clicked.connect(self.mostrar_logo_info)  # Exemplo de função, caso necessário
        top_layout.addWidget(logo_button, alignment=Qt.AlignRight)

        layout.addWidget(top_bar)

    def criar_conexao(self, nome):
        """Cria uma conexão para abrir o módulo especificado."""
        def on_click():
            self.abrir_modulo(nome)
        return on_click

    def abrir_modulo(self, modulo):
        """Carrega o módulo especificado na área principal e atualiza o botão selecionado."""
        if not hasattr(self, "stacked_layout"):
            # Cria o QStackedLayout apenas uma vez
            self.stacked_layout = QStackedLayout()
            self.main_area.setLayout(self.stacked_layout)
            self.modulos_carregados = {}  # Dicionário para armazenar os widgets carregados

        if modulo not in self.modulos_carregados:
            try:
                # Importa o módulo dinamicamente a partir do mapeamento
                modulo_path = self.mapeamento_modulos[modulo]
                module_name, class_name = modulo_path.rsplit(".", 1)
                imported_module = __import__(module_name, fromlist=[class_name])
                widget_class = getattr(imported_module, class_name)

                # Instancia o widget e adiciona ao QStackedLayout
                widget_instance = widget_class(self)
                self.stacked_layout.addWidget(widget_instance)
                self.modulos_carregados[modulo] = widget_instance
            except (ImportError, AttributeError) as e:
                print(f"Erro ao carregar o módulo {modulo}: {e}")
                return

        # Alterna para o módulo apropriado
        self.stacked_layout.setCurrentWidget(self.modulos_carregados[modulo])
        self.atualizar_estilo_botoes(modulo)  # Atualiza o estilo dos botões
    
    def atualizar_estilo_botoes(self, modulo_selecionado):
        """Atualiza o estilo dos botões da barra superior com base no módulo selecionado."""
        for nome, botao in self.top_bar_buttons.items():
            if nome == modulo_selecionado:
                botao.setProperty("selected", True)
                botao.style().unpolish(botao)
                botao.style().polish(botao)
            else:
                botao.setProperty("selected", False)
                botao.style().unpolish(botao)
                botao.style().polish(botao)

    def mostrar_erro(self, mensagem):
        """Exibe uma mensagem de erro na área principal."""
        erro_widget = QWidget()
        layout = QVBoxLayout(erro_widget)
        label = QLabel(f"Erro: {mensagem}")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 16, QFont.Bold))
        layout.addWidget(label)

        self.stacked_layout.addWidget(erro_widget)
        self.stacked_layout.setCurrentWidget(erro_widget)
    
    def mostrar_logo_info(self):
        QMessageBox.information(self, "Sobre", "Software EBS-010\nVersão 1.0")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
