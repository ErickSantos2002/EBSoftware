import sys
import os

# Adiciona o caminho do SDK ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ebs010_sdk.device import DeviceManager

device_manager = DeviceManager()

try:
    info = device_manager.get_device_info()
    print("Informações do dispositivo:", info)
except Exception as e:
    print("Erro:", e)

