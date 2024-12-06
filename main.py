import sys
import os

# Determina o caminho base, considerando se está rodando como executável ou script
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)  # Diretório do executável
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Diretório do script
src_dir = os.path.join(BASE_DIR, "src")
sys.path.append(src_dir)

from src.frontend.Interface import MainWindow  # Importa a classe MainWindow da interface
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Cria e exibe a janela principal
    window = MainWindow()
    window.show()
    
    # Executa o loop do aplicativo
    sys.exit(app.exec_())
