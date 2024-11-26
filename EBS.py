import serial
import time
import csv
from datetime import datetime

# Configuração da porta serial
ser = serial.Serial(
    port="COM6",       # Substitua pela porta correta
    baudrate=4800,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1          # Timeout de 1 segundo
)

# Função para enviar comandos ao dispositivo
def enviar_comando(comando):
    comando_completo = f"{comando}\r\n"
    ser.write(comando_completo.encode('ascii'))
    print(f"Comando enviado: {comando_completo}")

# Função para ler resposta do dispositivo
def ler_resposta():
    resposta = ser.readline().decode('ascii').strip()
    print(f"Resposta recebida: {resposta}")
    return resposta

# Função para salvar resultados no CSV
def salvar_resultado(data_hora, resultado, valor, status):
    with open("resultados.csv", mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([data_hora, resultado, valor, status])
    print("Resultado salvo com sucesso!")

# Fluxo principal
try:
    # Envia comando para ligar o dispositivo
    enviar_comando("$START")

    while True:
        resposta = ler_resposta()

        if resposta == "$WAIT":
            print("Aquecendo o dispositivo, aguardando próximo estado...")
            time.sleep(1)

        elif resposta == "$STANBY":
            print("Dispositivo em standby, aguardando acionamento...")
            time.sleep(1)

        elif resposta == "$TRIGGER":
            print("Amostra de ar ativada, aguardando resultado...")
            time.sleep(1)

        elif resposta.startswith("$RESULT"):
            print("Resultado recebido!")
            # Processa o resultado
            resultado_bruto = resposta.split(",")[1]  # Exemplo: 0.000-OK
            valor, status = resultado_bruto.split("-")
            salvar_resultado(datetime.now(), resposta, valor, status)
            break

        elif resposta == "$BREATH":
            print("Coleta de ar concluída.")

        elif resposta == "$FLOW,ERR":
            print("Erro no fluxo de ar, tente novamente.")
            break

        elif resposta == "$BAT,LOW":
            print("Bateria baixa! Verifique o dispositivo.")
            break

        elif resposta == "$SENSOR,ERR":
            print("Erro no sensor, dispositivo pode precisar de manutenção.")
            break

        elif resposta == "$TIME,OUT":
            print("Tempo para o teste expirou.")
            break

        else:
            print(f"Resposta inesperada: {resposta}")
            time.sleep(1)

finally:
    ser.close()
