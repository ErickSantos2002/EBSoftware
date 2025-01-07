import os
import configparser
import serial.tools.list_ports


class ConfigManager:
    def __init__(self):
        self.base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        self.resources_dir = os.path.join(self.base_dir, "resources")
        self.config_file = os.path.join(self.resources_dir, "config.ini")

        # Garante que o diretório de recursos existe
        if not os.path.exists(self.resources_dir):
            os.makedirs(self.resources_dir)

    def _write_config(self, port):
        """Escreve a porta no arquivo de configuração."""
        config = configparser.ConfigParser()
        config["Serial"] = {"port": port}
        with open(self.config_file, "w") as file:
            config.write(file)

    def set_serial_port(self, port: str):
        """
        Define e salva a porta serial no arquivo de configuração.
        :param port: Porta serial a ser configurada.
        """
        self._write_config(port)
        print(f"Porta serial '{port}' configurada com sucesso.")

    def get_serial_port(self) -> str:
        """
        Retorna a porta serial configurada.
        :return: Porta serial configurada ou None, se não configurada.
        """
        if not os.path.exists(self.config_file):
            raise FileNotFoundError("Arquivo de configuração não encontrado.")
        
        config = configparser.ConfigParser()
        config.read(self.config_file)

        return config.get("Serial", "port", fallback=None)

    def auto_detect_port(self) -> str:
        """
        Detecta automaticamente a porta de dispositivos "Silicon Labs".
        :return: Porta detectada ou None, se nenhuma encontrada.
        """
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if "Silicon Labs" in port.description:
                self.set_serial_port(port.device)
                print(f"Porta '{port.device}' detectada automaticamente.")
                return port.device

        raise RuntimeError("Nenhum dispositivo 'Silicon Labs' detectado.")
