import csv
import os
import time
import serial
import configparser
from threading import Thread
from datetime import datetime

executando_automatico = False
executando_manual = False

# Caminho base para o diretório do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Caminho do arquivo atual (backend)
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, "..", ".."))  # Sai de src/backend
RESOURCES_DIR = os.path.join(PROJECT_DIR, "resources")  # Caminho do diretório resources

# Caminhos dos arquivos específicos
ARQUIVO_RESULTADOS = os.path.join(RESOURCES_DIR, "Resultados.csv")
CONFIG_FILE = os.path.join(RESOURCES_DIR, "config.ini")

# Função para verificar a existência dos arquivos e criar caso necessário
def inicializar_arquivos():
    """Verifica a existência dos arquivos necessários e cria-os, se necessário."""
    if not os.path.exists(RESOURCES_DIR):
        os.makedirs(RESOURCES_DIR)  # Cria o diretório resources, se não existir

    if not os.path.exists(ARQUIVO_RESULTADOS):
        with open(ARQUIVO_RESULTADOS, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=[
                "ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor", "Data e hora", "Quantidade de Álcool", "Status"
            ])
            writer.writeheader()
        print(f"Arquivo criado: {ARQUIVO_RESULTADOS}")

    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, mode="w", encoding="utf-8") as file:
            file.write("[Serial]\nporta=\n")
        print(f"Arquivo criado: {CONFIG_FILE}")

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

def inicializar_serial():
    """Inicializa a conexão serial com a porta configurada."""
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
    """Lê a resposta do dispositivo conectado via porta serial."""
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
        ids = [int(row["ID do teste"]) for row in reader if row["ID do teste"].isdigit()]
        return max(ids) + 1 if ids else 1

# Função para salvar resultados
def salvar_resultado(id_teste, id_usuario, nome, matricula, setor, data_hora, resultado):
    """Salva o resultado do teste no arquivo CSV."""
    quantidade, status = resultado.split("-")  # Exemplo: "0.000-OK" ou "1.125-HIGH"

    if status == "OK":
        status = "Aprovado"
    elif status == "HIGH":
        status = "Rejeitado"

    with open(ARQUIVO_RESULTADOS, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=[
            "ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor", "Data e hora", "Quantidade de Álcool", "Status"
        ])
        writer.writerow({
            "ID do teste": id_teste,
            "ID do usuário": id_usuario,
            "Nome": nome,
            "Matrícula": matricula,
            "Setor": setor,
            "Data e hora": data_hora,
            "Quantidade de Álcool": quantidade,
            "Status": status
        })

def executar_teste(id_usuario, nome, matricula, setor, automatico=False, callback=None):
    """Executa um teste (manual ou automático) em uma thread separada."""
    def executar():
        global executando_automatico, executando_manual

        if automatico:
            executando_automatico = True
        else:
            executando_manual = True

        try:
            while (executando_automatico if automatico else executando_manual):
                enviar_comando("$START")  # Envia o comando para iniciar o teste

                while (executando_automatico if automatico else executando_manual):
                    resposta = ler_resposta()  # Lê a resposta da porta serial

                    if resposta and resposta.startswith("$RESULT"):
                        # Extrai informações do resultado
                        id_teste = proximo_id_teste()  # Calcula o próximo ID de teste
                        data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        resultado = resposta.split(",")[1]  # Exemplo: "0.000-OK"
                        
                        if automatico:
                            # Salva o resultado como "Automático"
                            salvar_resultado(
                                id_teste=id_teste,
                                id_usuario=0,  # ID do usuário sempre 0
                                nome="Automático",
                                matricula="Automático",
                                setor="Automático",
                                data_hora=data_hora,
                                resultado=resultado
                            )
                        else:
                            # Salva o resultado do teste manual
                            salvar_resultado(
                                id_teste=id_teste,
                                id_usuario=id_usuario,
                                nome=nome,
                                matricula=matricula,
                                setor=setor,
                                data_hora=data_hora,
                                resultado=resultado
                            )

                        # Executa o callback com o resultado
                        if callback:
                            callback(resultado)

                        # Se for manual, encerra o teste após um único resultado
                        if not automatico:
                            return resultado

                        # Se for automático e o resultado for "HIGH", para o loop
                        if automatico and "HIGH" in resultado:
                            executando_automatico = False
                            break  # Sai do loop interno

                        # Se for automático e o resultado for "OK", continua
                        if automatico and "OK" in resultado:
                            print("Teste automático aprovado, continuando...")
                            break  # Sai do loop interno e volta ao início

                # Delay entre testes automáticos para evitar congestionamento
                if automatico:
                    time.sleep(1)

        except Exception as e:
            print(f"Erro durante o teste {'automático' if automatico else 'manual'}: {e}")
            raise
        finally:
            enviar_comando("$RESET")  # Garante que o dispositivo é resetado
            if automatico:
                executando_automatico = False
            else:
                executando_manual = False
            print(f"Teste {'automático' if automatico else 'manual'} interrompido.")

    # Inicia o teste em uma thread separada
    thread = Thread(target=executar, daemon=True)
    thread.start()

# Funções para iniciar e parar os testes
def iniciar_teste_manual(id_usuario, nome, matricula, setor):
    """Inicia o teste manual."""
    if executando_manual:
        print("Teste manual já está em execução.")
        return
    executar_teste(id_usuario, nome, matricula, setor, automatico=False)

def iniciar_teste_automatico():
    """Inicia o teste automático."""
    if executando_automatico:
        print("Teste automático já está em execução.")
        return
    executar_teste(None, None, None, None, automatico=True)

def parar_testes():
    """Para quaisquer testes em execução (manual ou automático)."""
    global executando_automatico, executando_manual
    executando_automatico = False
    executando_manual = False
    enviar_comando("$RESET")
    print("Todos os testes foram interrompidos.")