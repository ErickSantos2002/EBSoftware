import tkinter as tk
from tkinter import messagebox
import serial
import configparser
import os

# Caminhos dos arquivos de configuração
CONFIG_FILE = "config.ini"
INFO_FILE = "info.ini"

# Função para inicializar o serial com base no config.ini
def inicializar_serial():
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
                with open(INFO_FILE, "w") as infofile:
                    info_config.write(infofile)
                return unidade_traduzida, low, high, teste_num
            else:
                raise Exception("Resposta inesperada do dispositivo.")
    except Exception as e:
        raise Exception(f"Erro ao enviar comando $RECALL: {e}")

# Função para carregar as informações do arquivo info.ini
def carregar_informacoes():
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

# Interface principal
def iniciar_informacoes():
    root = tk.Tk()
    root.title("Informações do Aparelho")
    root.geometry("400x300")
    root.resizable(False, False)

    frame_info = tk.Frame(root, bd=2, relief="groove", padx=10, pady=10)
    frame_info.pack(fill="both", expand=True, padx=10, pady=10)

    tk.Label(frame_info, text="Informações do Aparelho", font=("Arial", 12, "bold")).pack(pady=5)

    # Campos de informação
    campo_unidade = tk.Label(frame_info, text="Unidade: Carregando...", anchor="w")
    campo_unidade.pack(fill="x")

    campo_low = tk.Label(frame_info, text="Limite Baixo: Carregando...", anchor="w")
    campo_low.pack(fill="x")

    campo_high = tk.Label(frame_info, text="Limite Alto: Carregando...", anchor="w")
    campo_high.pack(fill="x")

    campo_teste = tk.Label(frame_info, text="Nº Teste: Carregando...", anchor="w")
    campo_teste.pack(fill="x")

    def atualizar_informacoes():
        try:
            unidade, low, high, teste_num = enviar_comando_recall()
            campo_unidade.config(text=f"Unidade: {unidade}")
            campo_low.config(text=f"Limite Baixo: {low}")
            campo_high.config(text=f"Limite Alto: {high}")
            campo_teste.config(text=f"Nº Teste: {teste_num}")
        except Exception as e:
            messagebox.showerror("Erro", str(e))

    # Carregar informações do info.ini ao abrir
    informacoes_salvas = carregar_informacoes()
    if informacoes_salvas:
        campo_unidade.config(text=f"Unidade: {informacoes_salvas['Unidade']}")
        campo_low.config(text=f"Limite Baixo: {informacoes_salvas['Limite_Baixo']}")
        campo_high.config(text=f"Limite Alto: {informacoes_salvas['Limite_Alto']}")
        campo_teste.config(text=f"Nº Teste: {informacoes_salvas['Numero_Teste']}")

    # Botões
    frame_botoes = tk.Frame(root)
    frame_botoes.pack(fill="x", padx=10, pady=10)

    tk.Button(frame_botoes, text="Atualizar Informações", command=atualizar_informacoes).pack(side="left", padx=5)
    tk.Button(frame_botoes, text="Fechar", command=root.destroy).pack(side="right", padx=5)

    root.mainloop()

# Para execução standalone
if __name__ == "__main__":
    iniciar_informacoes()
