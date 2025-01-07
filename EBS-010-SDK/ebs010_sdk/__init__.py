import sys
import os
import time

# Adiciona o caminho do SDK ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ebs010_sdk.cadastros import CadastrosManager
from ebs010_sdk.config import ConfigManager
from ebs010_sdk.device import DeviceManager
from ebs010_sdk.results import ResultsManager
from ebs010_sdk.tests import TestsManager

def callback(result):
    print(f"Resultado do teste: {result}")

# Inicializa o gerenciador
cadastros_manager = CadastrosManager()
Config_manager = ConfigManager()
device_manager = DeviceManager()
Results_manager = ResultsManager()
Tests_manager = TestsManager()