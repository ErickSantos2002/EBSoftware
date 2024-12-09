import os
import serial
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
INFO_FILE = os.path.join(RESOURCES_DIR, "info.ini")

# Função para inicializar o serial com base no config.ini
def inicializar_serial():
    """Inicializa a comunicação serial com base na porta configurada."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        raise Exception("Arquivo config.ini não encontrado. Configure a porta primeiro.")
    
    config.read(CONFIG_FILE)
    porta = config.get("Serial", "porta", fallback=None)
    
    if not porta:
        raise Exception("Nenhuma porta configurada em config.ini.")
    
    try:
        ser = serial.Serial(
            port=porta,
            baudrate=4800,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        return ser
    except Exception as e:
        raise Exception(f"Erro ao inicializar a porta serial: {e}")

# Função para enviar o comando $RECALL e salvar as informações em info.ini
def enviar_comando_recall():
    """Envia o comando $RECALL ao dispositivo e salva as informações em info.ini."""
    try:
        with inicializar_serial() as ser:
            ser.write(b"$RECALL\r\n")
            resposta = ser.readline().decode('ascii').strip()
            print(f"Resposta recebida: {resposta}")
            
            if resposta.startswith("$U/"):
                dados = resposta.split(",")
                unidade = dados[0].split("/")[1]
                low = dados[1].split("/")[1]
                high = dados[2].split("/")[1]
                teste_num = dados[3].split("/")[1]

                # Traduzir unidade
                unidade_traduzida = {"M": "Mg/L", "B": "%BAC", "G": "g/L"}.get(unidade, unidade)

                # Salvar as informações em info.ini
                info_config = configparser.ConfigParser()
                info_config["Info"] = {
                    "Unidade": unidade_traduzida,
                    "Limite_Baixo": low,
                    "Limite_Alto": high,
                    "Numero_Teste": teste_num,
                }
                if not os.path.exists(RESOURCES_DIR):
                    os.makedirs(RESOURCES_DIR)
                with open(INFO_FILE, "w") as infofile:
                    info_config.write(infofile)
                return unidade_traduzida, low, high, teste_num
            else:
                raise Exception("Resposta inesperada do dispositivo.")
    except Exception as e:
        raise Exception(f"Erro ao enviar comando $RECALL: {e}")

# Função para carregar as informações do arquivo info.ini
def carregar_informacoes():
    """Carrega as informações salvas no arquivo info.ini."""
    info_config = configparser.ConfigParser()
    if not os.path.exists(INFO_FILE):
        return None
    info_config.read(INFO_FILE)
    return {
        "Unidade": info_config.get("Info", "Unidade", fallback="Não disponível"),
        "Limite_Baixo": info_config.get("Info", "Limite_Baixo", fallback="Não disponível"),
        "Limite_Alto": info_config.get("Info", "Limite_Alto", fallback="Não disponível"),
        "Numero_Teste": info_config.get("Info", "Numero_Teste", fallback="Não disponível"),
    }
