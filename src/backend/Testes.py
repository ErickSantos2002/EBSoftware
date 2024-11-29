import tkinter as tk
from tkinter import messagebox, ttk
import csv
from datetime import datetime
import serial
import time
import os
from threading import Thread
import configparser

# Nome do arquivo CSV para resultados
ARQUIVO_RESULTADOS = "Resultados.csv"
CONFIG_FILE = "config.ini"

# Variável global para controlar o estado do teste
teste_em_execucao = False

# Variável global para controle do modo manual
executando_manual = False

# Função para carregar a porta configurada
def carregar_porta_configurada():
    """Carrega a porta configurada do arquivo config.ini."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE) or not config.read(CONFIG_FILE):
        raise Exception("Arquivo de configuração não encontrado ou inválido.")
    porta = config.get("Serial", "porta", fallback=None)
    if not porta:
        raise Exception("Nenhuma porta configurada no arquivo.")
    return porta

import time

def inicializar_serial():
    """Inicializa a conexão serial com a porta configurada, com tentativas de re-tentativa."""
    tentativa = 0
    max_tentativas = 3
    while tentativa < max_tentativas:
        try:
            porta = carregar_porta_configurada()
            ser = serial.Serial(
                port=porta,
                baudrate=4800,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1
            )
            return ser
        except serial.SerialException as e:
            print(f"Tentativa {tentativa + 1}/{max_tentativas}: Erro ao abrir a porta {porta} - {e}")
            tentativa += 1
            time.sleep(1)  # Aguarda 1 segundo antes de tentar novamente
        except Exception as e:
            raise Exception(f"Erro ao inicializar a porta serial: {e}")
    raise Exception("Falha ao inicializar a porta serial após múltiplas tentativas.")

# Função para enviar comandos ao dispositivo
def enviar_comando(comando):
    """Envia um comando ao dispositivo conectado via porta serial."""
    try:
        with inicializar_serial() as ser:
            comando_completo = f"{comando}\r\n"
            ser.write(comando_completo.encode('ascii'))
            print(f"Comando enviado: {comando_completo}")
    except Exception as e:
        print(f"Erro ao enviar comando: {e}")
        raise Exception("Porta serial não está configurada ou aberta.")

# Função para ler resposta do dispositivo
def ler_resposta():
    try:
        with inicializar_serial() as ser:
            resposta = ser.readline().decode('ascii').strip()
            print(f"Resposta recebida: {resposta}")
            return resposta
    except Exception as e:
        print(f"Erro ao ler resposta: {e}")
        return None

# Função para obter o próximo ID de teste
def proximo_id_teste():
    """Calcula o próximo ID de teste com base no arquivo CSV."""
    if not os.path.exists(ARQUIVO_RESULTADOS):
        with open(ARQUIVO_RESULTADOS, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=[
                "ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor", "Data e hora", "Quantidade de Álcool", "Status"
            ])
            writer.writeheader()
        return 1  # Primeiro ID

    with open(ARQUIVO_RESULTADOS, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        try:
            ids = [int(row["ID do teste"]) for row in reader if row["ID do teste"].isdigit()]
            return max(ids) + 1 if ids else 1
        except KeyError:
            with open(ARQUIVO_RESULTADOS, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=[
                    "ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor", "Data e hora", "Quantidade de Álcool", "Status"
                ])
                writer.writeheader()
            return 1

# Função para salvar resultados
def salvar_resultado(id_teste, id_usuario, nome, matricula, setor, data_hora, resultado):
    # Extrai quantidade e status do resultado
    quantidade, status = resultado.split("-")  # Exemplo: "0.000-OK" ou "1.125-HIGH"

    # Substitui o status para "Aprovado" ou "Rejeitado"
    if status == "OK":
        status = "Aprovado"
    elif status == "HIGH":
        status = "Rejeitado"

    # Salva no CSV com os valores ajustados
    with open("Resultados.csv", mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([id_teste, id_usuario, nome, matricula, setor, data_hora, quantidade, status])
    print("Resultado salvo com sucesso!")

# Variável global para controle do modo automático
executando_automatico = False

# Função para iniciar a janela de testes
def iniciar_testes():
    global executando_automatico

    # Função para iniciar o teste manual
    def iniciar_manual():
        """Inicia o teste manual em uma thread separada."""
        global executando_manual
        if executando_manual:
            messagebox.showerror("Erro", "Um teste manual já está em execução!")
            return

        selecionado = tree.selection()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um usuário para realizar o teste!")
            return

        usuario = tree.item(selecionado)["values"]
        id_usuario, nome, matricula, setor = usuario

        id_teste = proximo_id_teste()
        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        executando_manual = True  # Sinaliza que o teste manual está em execução

        def executar_teste():
            global executando_manual
            try:
                enviar_comando("$START")
                while executando_manual:
                    resposta = ler_resposta()
                    if resposta and resposta.startswith("$RESULT"):
                        resultado = resposta.split(",")[1]  # Exemplo: "0.000-OK" ou "1.125-HIGH"
                        quantidade, status = resultado.split("-")

                        # Ajusta o status para os termos "Aprovado" ou "Rejeitado"
                        status = "Aprovado" if status == "OK" else "Rejeitado"

                        salvar_resultado(id_teste, id_usuario, nome, matricula, setor, data_hora, resultado)

                        messagebox.showinfo(
                            "Sucesso",
                            f"Teste realizado com sucesso!\n\nResultado: {status}\nQuantidade de Álcool: {quantidade}",
                        )

                        # Se o resultado for "Rejeitado", exibe o aviso
                        if "HIGH" in resultado:
                            messagebox.showwarning(
                                "Aviso de Segurança",
                                f"Teste com álcool detectado ({quantidade}).\nAguarde 5 minutos antes de retomar."
                            )
                        break
            except Exception as e:
                messagebox.showerror("Erro", f"Erro durante o teste: {e}")
            finally:
                executando_manual = False  # Finaliza o estado do teste manual

        # Inicia o teste em uma thread separada
        Thread(target=executar_teste, daemon=True).start()

    def iniciar_automatico():
        global executando_automatico
        executando_automatico = True

        def loop_automatico():
            while executando_automatico:
                id_teste = proximo_id_teste()
                data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                enviar_comando("$START")
                while executando_automatico:
                    resposta = ler_resposta()
                    if resposta.startswith("$RESULT"):
                        resultado = resposta.split(",")[1]  # Exemplo: "0.000-OK" ou "1.125-HIGH"
                        quantidade, status = resultado.split("-")  # Separa a quantidade e o status (OK/HIGH)

                        # Ajusta o status para os termos "Aprovado" ou "Rejeitado"
                        if status == "OK":
                            status = "Aprovado"
                        elif status == "HIGH":
                            status = "Rejeitado"

                        salvar_resultado(id_teste, 0, "Automático", "Automático", "Automático", data_hora, resultado)
                        print("Teste automático realizado com sucesso!")

                        # Verifica se o resultado foi "HIGH" e exibe o aviso apropriado
                        if "HIGH" in resultado:
                            parar_automatico()
                            messagebox.showwarning(
                                "Aviso de Segurança",
                                f"Teste com álcool detectado ({quantidade}).\nAguarde 5 minutos antes de retomar."
                            )
                            return
                        break
                    elif not executando_automatico:
                        break
                time.sleep(1)

        Thread(target=loop_automatico, daemon=True).start()

    def parar_automatico():
        try:
            global executando_automatico
            executando_automatico = False
            enviar_comando("$RESET")
            print("Teste automático interrompido.")
            messagebox.showinfo("Parado", "O teste automatico foi interrompido.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao parar o teste: {e}")
        

    # Função para parar o teste manual
    def parar_manual():
        """Interrompe o teste manual enviando `$RESET`."""
        global executando_manual
        if not executando_manual:
            messagebox.showwarning("Atenção", "Nenhum teste manual está em execução para ser interrompido.")
            return

        try:
            executando_manual = False  # Interrompe o loop do teste manual
            enviar_comando("$RESET")
            print("Teste manual interrompido.")
            messagebox.showinfo("Parado", "O teste manual foi interrompido.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao parar o teste manual: {e}")

    # Interface
    testes_root = tk.Tk()
    testes_root.title("Realizar Testes")
    testes_root.geometry("1000x400")
    testes_root.resizable(False, False)

    # Tipo de teste
    frame_tipo = tk.Frame(testes_root)
    frame_tipo.pack(side="top", fill="x", padx=10, pady=10)
    tk.Label(frame_tipo, text="Selecione o tipo de teste:").pack(side="left", padx=5)
    tk.Button(frame_tipo, text="Manual", command=lambda: mostrar_manual()).pack(side="left", padx=5)
    tk.Button(frame_tipo, text="Automático", command=lambda: mostrar_automatico()).pack(side="left", padx=5)

    # Modos Manual e Automático
    frame_manual = tk.Frame(testes_root)
    frame_automatico = tk.Frame(testes_root)

    def mostrar_manual():
        frame_automatico.pack_forget()
        frame_manual.pack(fill="both", expand=True)

    def mostrar_automatico():
        frame_manual.pack_forget()
        frame_automatico.pack(fill="both", expand=True)

    # Configurações do modo Manual
    tk.Label(frame_manual, text="Selecione um usuário:").pack(pady=5)
    tree = ttk.Treeview(frame_manual, columns=("ID", "Nome", "Matrícula", "Setor"), show="headings", selectmode="browse")
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Matrícula", text="Matrícula")
    tree.heading("Setor", text="Setor")
    tree.pack(fill="both", expand=True)

    def carregar_usuarios():
        if not os.path.exists("registros.csv"):
            return
        with open("registros.csv", mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                tree.insert("", "end", values=(row["ID"], row["Nome"], row["Matricula"], row["Setor"]))

    carregar_usuarios()
    # Botões "Iniciar Teste" e "Parar Teste" no modo Manual
    frame_botoes = tk.Frame(frame_manual)
    frame_botoes.pack(pady=10)

    tk.Button(frame_botoes, text="Iniciar Teste", command=iniciar_manual).pack(side="left", padx=10)
    tk.Button(frame_botoes, text="Parar Teste", command=parar_manual).pack(side="left", padx=10)


    tk.Button(frame_automatico, text="Iniciar Testes Automáticos", command=iniciar_automatico).pack(pady=10)
    tk.Button(frame_automatico, text="Parar Testes Automáticos", command=parar_automatico).pack(pady=10)

    testes_root.mainloop()

# Para executar
if __name__ == "__main__":
    iniciar_testes()