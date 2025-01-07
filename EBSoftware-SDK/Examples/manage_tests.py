import sys
import os

# Adiciona o caminho do SDK ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ebs010_sdk.tests import TestsManager
import time

def callback(result):
    print(f"Resultado do teste: {result}")

manager = TestsManager()

# Teste manual
try:
    print("Iniciando teste manual...")
    manager.start_manual_test(user_id=1, name="João Silva", registration="12345", department="TI", callback=callback)
    time.sleep(10)  # Simula tempo de execução
    manager.stop_tests()
except RuntimeError as e:
    print(f"Erro: {e}")

# Testes automáticos
try:
    print("Iniciando testes automáticos...")
    manager.start_auto_test(callback=callback)
    time.sleep(15)  # Simula tempo de execução
    manager.stop_tests()
except RuntimeError as e:
    print(f"Erro: {e}")
