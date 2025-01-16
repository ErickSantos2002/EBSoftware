import sys
import os

# Adiciona o caminho do SDK ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ebs010_sdk.config import ConfigManager

manager = ConfigManager()

# Testando configuração manual da porta
try:
    print("Definindo porta manualmente para COM3...")
    manager.set_serial_port("COM3")
    print("Porta configurada com sucesso.")
except Exception as e:
    print(f"Erro ao configurar porta: {e}")

# Testando recuperação da porta configurada
try:
    print("Obtendo porta configurada...")
    port = manager.get_serial_port()
    print(f"Porta configurada: {port}")
except Exception as e:
    print(f"Erro ao obter porta: {e}")

# Testando detecção automática
try:
    print("Detectando porta automaticamente...")
    port = manager.auto_detect_port()
    print(f"Porta detectada automaticamente: {port}")
except Exception as e:
    print(f"Erro na detecção automática: {e}")
