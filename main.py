import sys
import os

# Adiciona o diretório "src" ao sys.path
base_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(base_dir, "src")
sys.path.append(src_dir)

from src.backend.Interface import iniciar_interface
if __name__ == "__main__":
    iniciar_interface()
