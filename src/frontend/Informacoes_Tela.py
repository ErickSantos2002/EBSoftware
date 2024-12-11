import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt

# Configuração do diretório base (suporte a PyInstaller e script normal)
BASE_DIR = getattr(sys, 'frozen', False) and sys._MEIPASS or os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Importa funções do backend
from src.backend.Informacoes import enviar_comando_recall, carregar_informacoes

class InformacoesTela(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Configuração inicial da janela
        self.setWindowTitle("Informações do Aparelho")
        self.setGeometry(100, 100, 400, 300)

        # Criação do layout principal
        self.init_ui()

        # Carregar informações do arquivo ao abrir
        self.carregar_informacoes_salvas()

    def init_ui(self):
        """Inicializa a interface da tela."""
        # Criação do frame principal com fundo branco
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: white; border: none;")
        
        main_layout = QVBoxLayout(self.frame)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Estilo centralizado
        estilo_label = "font-size: 14px; font-family: Arial; color: black; padding: 5px; background-color: #f0f0f0;"
        estilo_botao = """
            QPushButton {
                font-family: Arial;
                font-size: 14px;
                font-weight: bold;
                color: white;
                background-color: #0072B7; /* Azul padrão */
                border: none;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #005BB5; /* Azul mais escuro no hover */
            }
            QPushButton:pressed {
                background-color: #003F87; /* Azul ainda mais escuro ao pressionar */
            }
        """

        # Título
        titulo = QLabel("Informações do Aparelho")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: black; padding: 10px;")
        main_layout.addWidget(titulo)

        # Campos para exibir informações
        self.campo_unidade = QLabel("Unidade: Carregando...")
        self.campo_unidade.setStyleSheet(estilo_label)
        main_layout.addWidget(self.campo_unidade)

        self.campo_low = QLabel("Limite Baixo: Carregando...")
        self.campo_low.setStyleSheet(estilo_label)
        main_layout.addWidget(self.campo_low)

        self.campo_high = QLabel("Limite Alto: Carregando...")
        self.campo_high.setStyleSheet(estilo_label)
        main_layout.addWidget(self.campo_high)

        self.campo_teste = QLabel("Nº Testes: Carregando...")
        self.campo_teste.setStyleSheet(estilo_label)
        main_layout.addWidget(self.campo_teste)

        # Botão para atualizar informações
        btn_atualizar = QPushButton("Atualizar Informações")
        btn_atualizar.setStyleSheet(estilo_botao)
        btn_atualizar.clicked.connect(self.atualizar_informacoes)
        main_layout.addWidget(btn_atualizar)

        # Configuração do layout principal
        final_layout = QVBoxLayout(self)
        final_layout.addWidget(self.frame)

    def atualizar_informacoes(self):
        """Atualiza as informações enviando o comando $RECALL ao dispositivo."""
        try:
            # Envia comando para obter informações do dispositivo
            unidade, low, high, teste_num = enviar_comando_recall()

            # Atualiza os campos com os valores retornados
            self.campo_unidade.setText(f"Unidade: {unidade}")
            self.campo_low.setText(f"Limite Baixo: {low}")
            self.campo_high.setText(f"Limite Alto: {high}")
            self.campo_teste.setText(f"Nº Testes: {teste_num}")
        except Exception as e:
            # Mostra uma mensagem de erro caso falhe
            QMessageBox.critical(self, "Erro", f"Erro ao atualizar informações: {e}")

    def carregar_informacoes_salvas(self):
        """Carrega as informações salvas no arquivo info.ini ao abrir a tela."""
        try:
            informacoes = carregar_informacoes()

            if informacoes:
                self.campo_unidade.setText(f"Unidade: {informacoes['Unidade']}")
                self.campo_low.setText(f"Limite Baixo: {informacoes['Limite_Baixo']}")
                self.campo_high.setText(f"Limite Alto: {informacoes['Limite_Alto']}")
                self.campo_teste.setText(f"Nº Testes: {informacoes['Numero_Teste']}")
            else:
                QMessageBox.warning(self, "Aviso", "Não há informações salvas para carregar.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar informações salvas: {e}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = InformacoesTela()
    window.show()
    sys.exit(app.exec_())
