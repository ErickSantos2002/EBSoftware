import os
import time
from threading import Thread
from datetime import datetime
import serial
from ebs010_sdk.config import ConfigManager
from ebs010_sdk.results import ResultsManager


class TestsManager:
    def __init__(self):
        self.executando_manual = False
        self.executando_automatico = False
        self.results_manager = ResultsManager()
        self.config_manager = ConfigManager()

    def _inicializar_serial(self):
        """Inicializa a comunicação serial usando a porta configurada."""
        porta = self.config_manager.get_serial_port()
        if not porta:
            raise RuntimeError("Porta serial não configurada.")
        try:
            ser = serial.Serial(
                port=porta,
                baudrate=4800,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1,
            )
            return ser
        except serial.SerialException as e:
            raise RuntimeError(f"Erro ao abrir porta serial: {e}")

    def _enviar_comando(self, comando):
        """Envia um comando para o dispositivo."""
        with self._inicializar_serial() as ser:
            comando_completo = f"{comando}\r\n"
            ser.write(comando_completo.encode('ascii'))
            print(f"Comando enviado: {comando_completo}")

    def _ler_resposta(self):
        """Lê a resposta do dispositivo."""
        with self._inicializar_serial() as ser:
            resposta = ser.readline().decode('ascii').strip()
            print(f"Resposta recebida: {resposta}")
            return resposta

    def _executar_teste(self, id_usuario, nome, matricula, setor, automatico, callback):
        """Executa um teste manual ou automático."""
        def executar():
            if automatico:
                self.executando_automatico = True
            else:
                self.executando_manual = True

            try:
                while (self.executando_automatico if automatico else self.executando_manual):
                    self._enviar_comando("$START")
                    print(f"Teste {'automático' if automatico else 'manual'} iniciado.")

                    while (self.executando_automatico if automatico else self.executando_manual):
                        resposta = self._ler_resposta()
                        if not resposta:
                            continue

                        if resposta.startswith("$RESULT"):
                            resultado = resposta.split(",")[1]  # Exemplo: "0.000-OK"
                            quantidade, status = resultado.split("-")
                            status_traduzido = "Aprovado" if status == "OK" else "Rejeitado"

                            # Salva o resultado no banco de dados
                            self.results_manager.save_result(
                                id_usuario if not automatico else None,
                                nome if not automatico else "Automático",
                                matricula if not automatico else "Automático",
                                setor if not automatico else "Automático",
                                float(quantidade),
                                status_traduzido,
                            )

                            # Callback para fornecer feedback ao usuário
                            if callback:
                                callback({
                                    "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                                    "alcohol_level": quantidade,
                                    "status": status_traduzido,
                                })

                            if automatico and status == "HIGH":
                                print("Resultado crítico encontrado. Parando teste automático.")
                                self.executando_automatico = False
                                break

                            if not automatico:
                                self.executando_manual = False
                                break

                        elif resposta.startswith("$END"):
                            print("Teste encerrado, enviando novo comando para continuidade.")
                            break  # Sai do loop interno para reiniciar o teste

                        time.sleep(1)

            finally:
                self._enviar_comando("$RESET")
                self.executando_automatico = False
                self.executando_manual = False
                print("Teste encerrado.")

        thread = Thread(target=executar, daemon=True)
        thread.start()

    def start_manual_test(self, user_id, name, registration, department, callback=None):
        """Inicia um teste manual."""
        if self.executando_manual:
            raise RuntimeError("Um teste manual já está em execução.")
        self._executar_teste(user_id, name, registration, department, automatico=False, callback=callback)

    def start_auto_test(self, callback=None):
        """Inicia testes automáticos."""
        if self.executando_automatico:
            raise RuntimeError("Testes automáticos já estão em execução.")
        self._executar_teste(None, None, None, None, automatico=True, callback=callback)

    def stop_tests(self):
        """Para qualquer teste em execução."""
        self.executando_manual = False
        self.executando_automatico = False
        self._enviar_comando("$RESET")
        print("Testes interrompidos.")
