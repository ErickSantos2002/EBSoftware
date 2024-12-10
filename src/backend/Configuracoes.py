import os
import serial
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
    """Busca automaticamente a porta Silicon Labs e ajusta o baudrate para 4800."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Silicon Labs" in port.description:
            # Ajusta o baudrate da porta detectada
            try:
                configurar_baudrate(port.device, 4800)
                return port.device
            except Exception as e:
                print(f"Erro ao configurar a porta {port.device}: {e}")
    return None

def configurar_baudrate(porta, baudrate):
    """Configura o baudrate da porta especificada."""
    try:
        with serial.Serial(port=porta, baudrate=baudrate) as ser:
            print(f"Baudrate configurado para {baudrate} na porta {porta}.")
    except Exception as e:
        print(f"Erro ao configurar baudrate na porta {porta}: {e}")
        raise

def carregar_porta_configurada():
    """Carrega a porta configurada a partir do arquivo de configuração."""
    config = configparser.ConfigParser()
    if config.read(CONFIG_FILE) and "Serial" in config and "porta" in config["Serial"]:
        porta = config["Serial"]["porta"]
        try:
            # Configura o baudrate para 4800 na porta carregada
            configurar_baudrate(porta, 4800)
            return porta
        except Exception as e:
            print(f"Erro ao configurar baudrate na porta {porta}: {e}")
            return None
    return None
