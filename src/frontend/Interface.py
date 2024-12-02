import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QSize


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

        # Configurações de estilo geral
        self.setStyleSheet(f"background-color: {COR_CINZA};")

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
        self.main_area.setStyleSheet(f"background-color: {COR_CINZA};")
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
        """Adiciona os botões com ícones e a logo na barra superior."""
        ICONES = {
            "Registros": "assets/Registros.png",
            "Testes": "assets/Testes.png",
            "Resultados": "assets/Resultados.png",
            "Configurações": "assets/Configuracoes.png",
            "Informações": "assets/Informacoes.png",
        }

        for nome, icone in ICONES.items():
            botao = QPushButton()
            botao.setText(nome)
            botao.setIcon(QIcon(icone))
            botao.setIconSize(QSize(50, 50))  # Ajuste do tamanho do ícone
            botao.setFont(QFont("Arial", 12, QFont.Bold))
            botao.setStyleSheet(f"""
                QPushButton {{
                    border: none;  /* Sem borda */
                    background: transparent;  /* Sem fundo */
                    color: {COR_PRETO};  /* Texto na cor preta */
                }}
                QPushButton:hover {{
                    color: {COR_AZUL};  /* Texto azul ao passar o mouse */
                }}
            """)
            botao.clicked.connect(lambda checked, n=nome: self.botao_clicado(n))
            layout.addWidget(botao)

        # Adiciona a logo como último elemento do layout
        logo_button = QPushButton()
        logo_button.setIcon(QIcon("assets/Logo.png"))
        logo_button.setIconSize(QSize(160, 120))  # Ajuste do tamanho da logo
        logo_button.setStyleSheet("border: none; background: transparent;")  # Sem borda e fundo
        logo_button.clicked.connect(self.logo_clicada)
        layout.addWidget(logo_button, alignment=Qt.AlignRight)

    def botao_clicado(self, nome):
        """Função chamada ao clicar nos botões."""
        print(f"Botão {nome} clicado!")

    def logo_clicada(self):
        """Função chamada ao clicar na logo."""
        print("Logo clicada! Redirecionando para a tela inicial...")
        # Aqui você pode implementar a lógica de redirecionamento para a tela inicial


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
