import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget, 
    QVBoxLayout, QHBoxLayout, QLabel, QGraphicsDropShadowEffect, QStackedLayout, QMessageBox
)
from PyQt5.QtGui import QIcon, QFont, QColor
from PyQt5.QtCore import Qt, QSize, QPropertyAnimation

if getattr(sys, 'frozen', False):
    # Diretório do executável (quando empacotado com PyInstaller)
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # Diretório raiz do projeto (quando executado como script)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
src_dir = os.path.join(BASE_DIR, "src")
sys.path.append(src_dir)

# Cores e Estilos
COR_CINZA = "#969595"  # Cinza
COR_AZUL = "#0072B7"   # Azul
COR_PRETO = "#0C0C0E"  # Preto
COR_BRANCA = "#FFFFFF"  # Branco


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EBS-010 Interface")
        self.setGeometry(100, 100, 1200, 800)

        # Define o ícone da janela
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "assets", "HS2.ico")))

        # Configurações de estilo geral
        self.setStyleSheet("""
            QMainWindow {
                background-color: white; /* Ou use COR_BRANCA */
            }
            QWidget#main_area {
                background-color: #969595; /* Ou use COR_CINZA */
            }
        """)

        # Layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Barra superior
        self.create_top_bar(main_layout)

        # Área principal
        self.main_area = QWidget()
        self.main_area.setObjectName("main_area")  # Identificador CSS para aplicar estilo
        main_layout.addWidget(self.main_area)

    def create_top_bar(self, layout):
        """Cria a barra superior com gradiente e insere os botões e a logo."""
        # Widget da barra superior com gradiente
        top_bar = QWidget()
        top_bar.setFixedHeight(80)
        top_bar.setStyleSheet("""
            background: qlineargradient(
                spread:pad,
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #0072B7, stop:1 #FFFFFF
            );
        """)

        # Layout interno do top_bar
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(10, 0, 10, 0)
        top_layout.setSpacing(20)

        # Widget para os botões e a logo (sem gradiente)
        inner_widget = QWidget()
        inner_layout = QHBoxLayout(inner_widget)
        inner_layout.setContentsMargins(0, 0, 0, 0)
        inner_layout.setSpacing(20)

        # Adiciona os botões e a logo
        self.add_buttons_with_icons(inner_layout)

        # Adiciona o inner_widget ao top_layout
        top_layout.addWidget(inner_widget)

        # Adiciona a barra ao layout principal
        layout.addWidget(top_bar)

    def add_buttons_with_icons(self, layout):
        """Adiciona os botões com ícones e textos abaixo na barra superior, com hover para o texto."""
        ICONES = {
            "Registros": os.path.join("assets", "Registros.png"),
            "Testes": os.path.join("assets", "Testes.png"),
            "Resultados": os.path.join("assets", "Resultados.png"),
            "Configurações": os.path.join("assets", "Configuracoes.png"),
            "Informações": os.path.join("assets", "Informacoes.png"),
        }

        for nome, icone in ICONES.items():
            # Caminho completo do ícone
            caminho_completo = os.path.join(BASE_DIR, icone)
            print(f"Carregando ícone para '{nome}': {caminho_completo}")  # Adicionado para debug

            # Cria o widget para organizar ícone e texto verticalmente
            botao_widget = QWidget()
            botao_widget.setStyleSheet("background: transparent;")  # Garante que o widget é transparente

            botao_layout = QVBoxLayout(botao_widget)
            botao_layout.setContentsMargins(0, 0, 0, 0)  # Remove margens internas
            botao_layout.setSpacing(5)  # Espaçamento entre ícone e texto

            # Cria o botão com o ícone
            botao = QPushButton()
            botao.setIcon(QIcon(caminho_completo))
            botao.setIconSize(QSize(35, 35))  # Ajusta o tamanho do ícone
            botao.setStyleSheet("border: none; background: transparent;")

            # Conecta o botão à funcionalidade correspondente
            botao.clicked.connect(self.criar_conexao(nome))

            # Cria o rótulo do texto abaixo do ícone
            rotulo = QLabel(nome)
            rotulo.setAlignment(Qt.AlignCenter)
            rotulo.setStyleSheet(f"""
                font-family: ArialBlack;
                font-size: 14px;
                font-weight: bold;  /* Negrito no texto */
                color: black;  /* Preto padrão */
                background: transparent;  /* Sem fundo */
            """)

            # Adiciona o botão e o rótulo ao layout vertical
            botao_layout.addWidget(botao, alignment=Qt.AlignCenter)
            botao_layout.addWidget(rotulo)

            # Adiciona o widget completo ao layout horizontal
            layout.addWidget(botao_widget, alignment=Qt.AlignCenter)

        # Adiciona a logo como um botão clicável, sem fundo
        logo_path = os.path.join(BASE_DIR, "assets", "Logo.png")
        logo_button = QPushButton()
        logo_button.setIcon(QIcon(logo_path))
        logo_button.setIconSize(QSize(140, 80))  # Ajuste do tamanho da logo
        logo_button.setStyleSheet("border: none; background: transparent;")  # Remove fundo e borda
        layout.addWidget(logo_button, alignment=Qt.AlignRight)  # Alinha a logo à direita
    
    def criar_conexao(self, nome):
        """Cria uma conexão para o botão com o nome especificado."""
        def on_click():
            if nome == "Registros":
                self.abrir_modulo("Registros_Tela")
            elif nome == "Testes":
                self.abrir_modulo("Testes_Tela")
            elif nome == "Resultados":
                self.abrir_modulo("Resultados_Tela")
            elif nome == "Configurações":
                self.abrir_modulo("Configuracoes_Tela")
            elif nome == "Informações":
                self.abrir_modulo("Informacoes_Tela")
        return on_click
    
    def abrir_modulo(self, modulo):
        """Carrega o módulo especificado na área principal usando QStackedLayout."""
        if not hasattr(self, "stacked_layout"):
            # Cria o QStackedLayout apenas uma vez
            self.stacked_layout = QStackedLayout()
            self.main_area.setLayout(self.stacked_layout)
            
            # Adiciona os módulos ao layout empilhado
            from src.frontend.Registros_Tela import RegistrosTela
            self.tela_registros = RegistrosTela(self)
            self.stacked_layout.addWidget(self.tela_registros)

            from src.frontend.Testes_Tela import TestesTela
            self.tela_testes = TestesTela(self)
            self.stacked_layout.addWidget(self.tela_testes)

            from src.frontend.Resultados_Tela import ResultadosTela
            self.tela_resultados = ResultadosTela(self)
            self.stacked_layout.addWidget(self.tela_resultados)

            from src.frontend.Configuracoes_Tela import ConfiguracoesTela
            self.tela_configuracoes = ConfiguracoesTela(self)
            self.stacked_layout.addWidget(self.tela_configuracoes)

            from src.frontend.Informacoes_Tela import  InformacoesTela
            self.tela_informacoes = InformacoesTela(self)
            self.stacked_layout.addWidget(self.tela_informacoes)

        # Alterna para o módulo apropriado
        if modulo == "Registros_Tela":
            self.stacked_layout.setCurrentWidget(self.tela_registros)
        elif modulo == "Testes_Tela":
            self.stacked_layout.setCurrentWidget(self.tela_testes)
        elif modulo == "Resultados_Tela":
            self.stacked_layout.setCurrentWidget(self.tela_resultados)
        elif modulo == "Configuracoes_Tela":
            self.stacked_layout.setCurrentWidget(self.tela_configuracoes)
        elif modulo == "Informacoes_Tela":
            self.stacked_layout.setCurrentWidget(self.tela_informacoes)
        else:
            print(f"Módulo {modulo} não encontrado.")

    def carregar_registros(self, layout):
        """Carrega a tela de Registros_Tela na área principal."""
        from src.frontend.Registros_Tela import RegistrosTela  # Importa o widget da tela de registros
        
        # Limpa widgets anteriores da área principal
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        # Adiciona a tela de registros à área principal
        registros_tela = RegistrosTela(parent=self)
        layout.addWidget(registros_tela)

    def carregar_testes(self, layout):
        """Carrega o módulo de Testes na área principal."""
        label = QLabel("Módulo: Testes")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)

    def carregar_resultados(self, layout):
        """Carrega o módulo de Resultados na área principal."""
        label = QLabel("Módulo: Resultados")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)

    def carregar_configuracoes(self, layout):
        """Carrega o módulo de Configurações na área principal."""
        label = QLabel("Módulo: Configurações")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)

    def carregar_informacoes(self, layout):
        """Carrega o módulo de Informações na área principal."""
        label = QLabel("Módulo: Informações")
        label.setAlignment(Qt.AlignCenter)
        label.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(label)


    # Criação da área central
        self.central_area = QWidget()
        self.central_layout = QVBoxLayout()
        self.central_area.setLayout(self.central_layout)
        self.setCentralWidget(self.central_area)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
