import sys
import os

# Adiciona o diretório "src" ao sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, "src")
sys.path.append(src_dir)

from frontend.Interface import MainWindow  # Importa a classe MainWindow da interface
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Cria e exibe a janela principal
    window = MainWindow()
    window.show()
    
    # Executa o loop do aplicativo
    sys.exit(app.exec_())
