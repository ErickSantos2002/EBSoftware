import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt

if getattr(sys, 'frozen', False):
    # Diretório do executável (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Diretório raiz do projeto (quando executado como script)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BACKEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", "backend"))
sys.path.append(BACKEND_DIR)

from src.backend.Configuracoes import salvar_porta_configurada, buscar_porta_automatica, carregar_porta_configurada
import serial.tools.list_ports

class ConfiguracoesTela(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Configurações")
        self.setGeometry(100, 100, 400, 300)

        # Criação do frame principal com fundo branco
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: white; border: none;")
        main_layout = QVBoxLayout(self.frame)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Estilo dos widgets
        estilo_label = "font-size: 14px; font-family: Arial; color: black;"
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
        estilo_combobox = """
            QComboBox {
                font-family: Arial;
                font-size: 14px;
                background-color: #f0f0f0; /* Cinza claro */
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QComboBox:hover {
                background-color: #e0e0e0; /* Cinza mais claro no hover */
            }
        """

        # Título
        titulo = QLabel("Configuração da Porta Serial")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-size: 16px; font-weight: bold; color: black; background-color: #f0f0f0; padding: 5px;")
        main_layout.addWidget(titulo)

        # ComboBox para seleção de porta
        self.combo_portas = QComboBox()
        self.combo_portas.setStyleSheet(estilo_combobox)
        self.combo_portas.addItems([port.device for port in serial.tools.list_ports.comports()])
        main_layout.addWidget(QLabel("Selecione a porta:").setStyleSheet(estilo_label))
        main_layout.addWidget(self.combo_portas)

        # Botão para buscar porta automática
        btn_automatica = QPushButton("Buscar Porta Automática")
        btn_automatica.setStyleSheet(estilo_botao)
        btn_automatica.clicked.connect(self.buscar_automatica)
        main_layout.addWidget(btn_automatica)

        # Botão para salvar configuração manual
        btn_salvar = QPushButton("Salvar Configuração")
        btn_salvar.setStyleSheet(estilo_botao)
        btn_salvar.clicked.connect(self.salvar_configuracao_manual)
        main_layout.addWidget(btn_salvar)

        # Exibe a porta configurada atualmente
        self.label_porta_configurada = QLabel(f"Porta Configurada: {carregar_porta_configurada() or 'Nenhuma'}")
        self.label_porta_configurada.setStyleSheet("font-size: 14px; font-family: Arial; color: black; background-color: #f0f0f0; padding: 5px;")
        self.label_porta_configurada.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.label_porta_configurada)

        # Configura o layout principal da janela
        final_layout = QVBoxLayout(self)
        final_layout.addWidget(self.frame)

    def buscar_automatica(self):
        """Busca e configura automaticamente a porta Silicon Labs."""
        porta_auto = buscar_porta_automatica()
        if porta_auto:
            salvar_porta_configurada(porta_auto)
            self.label_porta_configurada.setText(f"Porta Configurada: {porta_auto}")
            QMessageBox.information(self, "Configuração", f"Porta {porta_auto} configurada automaticamente.")
        else:
            QMessageBox.warning(self, "Erro", "Nenhuma porta Silicon Labs encontrada.")

    def salvar_configuracao_manual(self):
        """Salva a configuração da porta selecionada manualmente."""
        porta_selecionada = self.combo_portas.currentText()
        if not porta_selecionada:
            QMessageBox.warning(self, "Erro", "Selecione uma porta para configurar.")
            return
        salvar_porta_configurada(porta_selecionada)
        self.label_porta_configurada.setText(f"Porta Configurada: {porta_selecionada}")
        QMessageBox.information(self, "Configuração", f"Porta {porta_selecionada} configurada com sucesso!")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = ConfiguracoesTela()
    window.show()
    sys.exit(app.exec_())