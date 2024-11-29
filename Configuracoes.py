import tkinter as tk
from tkinter import ttk, messagebox
import serial.tools.list_ports
import configparser

# Caminho do arquivo de configuração
CONFIG_FILE = "config.ini"

# Função para salvar a porta no config.ini
def salvar_porta_configurada(porta):
    config = configparser.ConfigParser()
    config["Serial"] = {"porta": porta}
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)
    print(f"Porta {porta} salva no arquivo de configuração.")

# Função para buscar automaticamente a porta Silicon Labs
def buscar_porta_automatica():
    ports = serial.tools.list_ports.comports()
    for port in ports:
        if "Silicon Labs" in port.description:
            return port.device
    return None

# Função para carregar a porta configurada
def carregar_porta_configurada():
    config = configparser.ConfigParser()
    if config.read(CONFIG_FILE) and "Serial" in config and "porta" in config["Serial"]:
        return config["Serial"]["porta"]
    return None

# Função para iniciar a interface de configurações
def iniciar_configuracoes():
    root = tk.Tk()
    root.title("Configurações")
    root.geometry("400x300")
    root.resizable(False, False)

    # Frame principal
    frame_principal = tk.Frame(root, padx=10, pady=10)
    frame_principal.pack(fill="both", expand=True)

    # Label de título
    tk.Label(frame_principal, text="Configuração da Porta Serial", font=("Arial", 14, "bold")).pack(pady=10)

    # Combobox para portas disponíveis
    porta_var = tk.StringVar()
    portas_disponiveis = [port.device for port in serial.tools.list_ports.comports()]
    tk.Label(frame_principal, text="Selecione a porta:").pack(anchor="w", pady=5)
    combobox_portas = ttk.Combobox(frame_principal, textvariable=porta_var, values=portas_disponiveis, state="readonly")
    combobox_portas.pack(fill="x", pady=5)

    # Botão para buscar porta automaticamente
    def procurar_automatica():
        porta_auto = buscar_porta_automatica()
        if porta_auto:
            porta_var.set(porta_auto)
            salvar_porta_configurada(porta_auto)
            messagebox.showinfo("Configuração", f"Porta {porta_auto} configurada automaticamente.")
        else:
            messagebox.showerror("Erro", "Nenhuma porta Silicon Labs encontrada.")

    tk.Button(frame_principal, text="Buscar Porta Automática", command=procurar_automatica).pack(pady=5)

    # Botão para salvar a configuração manual
    def salvar_configuracao_manual():
        porta_selecionada = combobox_portas.get()
        if not porta_selecionada:
            messagebox.showerror("Erro", "Selecione uma porta para configurar.")
            return
        salvar_porta_configurada(porta_selecionada)
        messagebox.showinfo("Configuração", f"Porta {porta_selecionada} configurada com sucesso!")

    tk.Button(frame_principal, text="Salvar Configuração", command=salvar_configuracao_manual).pack(pady=5)

    # Exibe a porta configurada atualmente
    porta_configurada = carregar_porta_configurada()
    tk.Label(frame_principal, text=f"Porta Configurada: {porta_configurada or 'Nenhuma'}", font=("Arial", 10)).pack(pady=10)

    # Botão para fechar a janela
    tk.Button(frame_principal, text="Fechar", command=root.destroy).pack(side="bottom", pady=10)

    root.mainloop()

# Executar como standalone
if __name__ == "__main__":
    iniciar_configuracoes()
