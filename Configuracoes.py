import serial
import serial.tools.list_ports
import configparser
from tkinter import messagebox

# Configuração do arquivo de configuração
CONFIG_FILE = "config.ini"
config = configparser.ConfigParser()

def salvar_porta_configurada(porta):
    """Salva a porta configurada no arquivo config.ini."""
    config["Serial"] = {"porta": porta}
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)
    print(f"Porta {porta} salva no arquivo de configuração.")

def carregar_porta_configurada():
    """Carrega a porta configurada no arquivo config.ini."""
    if not config.read(CONFIG_FILE):
        return None
    return config.get("Serial", "porta", fallback=None)

def buscar_porta_automatica():
    """Procura a porta correspondente automaticamente."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Silicon Labs" in port.description:
            return port.device
    return None

def abrir_porta_serial(porta):
    """Abre e retorna uma instância da porta serial."""
    try:
        ser = serial.Serial(
            port=porta,
            baudrate=4800,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        print(f"Porta {porta} aberta com sucesso.")
        return ser
    except Exception as e:
        print(f"Erro ao abrir porta {porta}: {e}")
        return None

def obter_serial_configurada():
    """Obtém uma instância da porta configurada."""
    porta_configurada = carregar_porta_configurada()
    if not porta_configurada:
        raise Exception("Nenhuma porta serial configurada.")
    ser = abrir_porta_serial(porta_configurada)
    if not ser:
        raise Exception(f"Falha ao abrir porta {porta_configurada}. Verifique as configurações.")
    return ser

def configurar_porta(porta):
    """Configura a porta serial."""
    if abrir_porta_serial(porta):
        salvar_porta_configurada(porta)
        messagebox.showinfo("Configuração", f"Porta {porta} configurada com sucesso!")
    else:
        messagebox.showerror("Erro", f"Falha ao configurar a porta {porta}.")
