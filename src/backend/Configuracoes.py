import os
import serial.tools.list_ports
import configparser
import sys

if getattr(sys, 'frozen', False):
    # Diretório do executável (PyInstaller)
    BASE_DIR = os.path.join(sys._MEIPASS)
else:
    # Diretório base para execução no modo script
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Diretório resources no local correto
RESOURCES_DIR = os.path.join(BASE_DIR, "resources")
CONFIG_FILE = os.path.join(RESOURCES_DIR, "config.ini")

print("Diretorio base: " + BASE_DIR)
print("Diretorios resources: " + RESOURCES_DIR)


def salvar_porta_configurada(porta):
    """Salva a porta no arquivo de configuração."""
    # Garante que o diretório resources existe
    if not os.path.exists(RESOURCES_DIR):
        os.makedirs(RESOURCES_DIR)
    
    config = configparser.ConfigParser()
    config["Serial"] = {"porta": porta}
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)
    print(f"Porta {porta} salva no arquivo de configuração.")


def buscar_porta_automatica():
    """Busca automaticamente a porta Silicon Labs."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Silicon Labs" in port.description:
            print(f"Porta automática encontrada: {port.device}")
            return port.device
    print("Nenhuma porta Silicon Labs encontrada.")
    return None


def carregar_porta_configurada():
    """Carrega a porta configurada a partir do arquivo de configuração."""
    config = configparser.ConfigParser()
    if config.read(CONFIG_FILE) and "Serial" in config and "porta" in config["Serial"]:
        porta = config["Serial"]["porta"]
        print(f"Porta configurada carregada: {porta}")
        return porta
    print("Nenhuma porta configurada encontrada.")
    return None


# Exemplo de uso
if __name__ == "__main__":
    # Buscar porta automaticamente
    porta_automatica = buscar_porta_automatica()
    if porta_automatica:
        salvar_porta_configurada(porta_automatica)
    else:
        # Carregar porta previamente configurada
        porta_configurada = carregar_porta_configurada()
