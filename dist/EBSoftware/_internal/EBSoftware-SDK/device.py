import os
import serial
from ebs010_sdk.config import ConfigManager

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")


class DeviceManager:
    def __init__(self):
        """Inicializa o gerenciador do dispositivo."""
        self.config_manager = ConfigManager()

    def _inicializar_serial(self):
        """Inicializa a comunicação serial usando a porta configurada."""
        porta = self.config_manager.get_serial_port()
        if not porta:
            raise RuntimeError("Porta serial não configurada.")
        try:
            ser = serial.Serial(
                port=porta,
                baudrate=4800,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1,
            )
            return ser
        except serial.SerialException as e:
            raise RuntimeError(f"Erro ao abrir porta serial: {e}")

    def get_device_info(self):
        """Obtém as informações do dispositivo enviando o comando $RECALL."""
        try:
            with self._inicializar_serial() as ser:
                ser.write(b"$RECALL\r\n")
                resposta = ser.readline().decode("ascii").strip()
                print(f"Resposta recebida: {resposta}")

                if resposta.startswith("$U/"):
                    dados = resposta.split(",")
                    unidade = dados[0].split("/")[1]
                    low = dados[1].split("/")[1]
                    high = dados[2].split("/")[1]
                    teste_num = dados[3].split("/")[1]

                    # Traduz a unidade para um formato amigável
                    unidade_traduzida = {"M": "mg/L", "B": "%BAC", "G": "g/L"}.get(unidade, unidade)
                    return {
                        "unit": unidade_traduzida,
                        "low_limit": low,
                        "high_limit": high,
                        "test_count": teste_num,
                    }
                else:
                    raise RuntimeError("Resposta inesperada do dispositivo.")
        except Exception as e:
            raise RuntimeError(f"Erro ao obter informações do dispositivo: {e}")
