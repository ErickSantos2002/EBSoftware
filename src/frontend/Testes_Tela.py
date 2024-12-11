from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QLineEdit, QFrame, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QMovie
from backend.Cadastros import carregar_registros, sinal_global
from src.backend.Testes import (
    iniciar_teste_manual, parar_testes,
    iniciar_teste_automatico, parar_testes, executar_teste
)
from threading import Thread
import os
import sys

# Define o diretório base (suporta tanto execução normal quanto empacotamento com PyInstaller)
if getattr(sys, 'frozen', False):  # Quando empacotado pelo PyInstaller
    BASE_DIR = sys._MEIPASS
else:  # Durante desenvolvimento
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
# Caminho correto para o arquivo GIF
LOADING_GIF = os.path.join(BASE_DIR, "assets", "loading.gif")
class TestesTela(QWidget):
    resultado_recebido = pyqtSignal(str)  # Sinal para transmitir resultados do backend
    erro_recebido = pyqtSignal(str)  # Novo sinal para erros
    def __init__(self, parent=None):
        super().__init__(parent)

        try:
            self.erro_recebido.disconnect(self.mostrar_erro)
        except TypeError:
            pass
        self.erro_recebido.connect(self.mostrar_erro)
        sinal_global.registros_atualizados.connect(self.carregar_registros)

        # Criação do frame principal com fundo branco
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: white; border: none;")
        main_layout = QVBoxLayout(self.frame)

        # Define o layout principal da janela
        final_layout = QVBoxLayout(self)
        final_layout.addWidget(self.frame)


        self.resultado_recebido.connect(self.mostrar_resultado)

        # Painel superior: barra de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar por Nome, Matrícula ou Setor...")
        self.search_input.setStyleSheet("""
            font-family: Arial; font-size: 12px;
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            padding: 5px;
        """)
        search_button = QPushButton("Pesquisar")
        search_button.setStyleSheet("""
            font-family: Arial; font-size: 12px;
            background-color: #0072B7;
            color: white;
            border: 1px solid #cccccc;
            padding: 5px;
        """)
        search_button.clicked.connect(self.pesquisar_registros)
        self.search_input.returnPressed.connect(self.pesquisar_registros)  # Permite pesquisar ao pressionar Enter
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        main_layout.addLayout(search_layout)

        # Tabela para exibir registros
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Matrícula", "Setor"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setStyleSheet("""
            font-family: Arial; font-size: 12px;
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
        """)
        main_layout.addWidget(self.tabela)

        # Painel de botões de teste
        botoes_layout = QVBoxLayout()
        botoes_layout.setSpacing(5)

        # Estilo dos botões de iniciar (azuis)
        estilo_botao_iniciar = """
            QPushButton {
                font-family: Arial;
                font-size: 12px;
                font-weight: bold;
                background-color: #0072B7; /* Azul padrão */
                color: white;
                border: 1px solid #005A9E; /* Azul escuro para borda */
                padding: 5px 10px; /* Ajuste do tamanho interno */
            }
            QPushButton:hover {
                background-color: #005BB5; /* Azul mais escuro no hover */
            }
            QPushButton:pressed {
                background-color: #003F87; /* Azul ainda mais escuro ao pressionar */
            }
        """

        # Estilo do botão parar (vermelho)
        estilo_botao_parar = """
            QPushButton {
                font-family: Arial;
                font-size: 12px;
                font-weight: bold;
                background-color: #FF0000; /* Vermelho padrão */
                color: white;
                border: 1px solid #CC0000; /* Vermelho escuro para borda */
                padding: 5px 10px; /* Ajuste do tamanho interno */
            }
            QPushButton:hover {
                background-color: #CC0000; /* Vermelho mais escuro no hover */
            }
            QPushButton:pressed {
                background-color: #990000; /* Vermelho ainda mais escuro ao pressionar */
            }
        """

        # Botão Manual
        btn_manual = QPushButton("Iniciar Teste Manual")
        btn_manual.setStyleSheet(estilo_botao_iniciar)
        btn_manual.clicked.connect(self.iniciar_teste_manual)
        btn_manual.adjustSize()  # Ajusta o tamanho do botão ao texto

        # Botão Automático
        btn_automatico = QPushButton("Iniciar Teste Automático")
        btn_automatico.setStyleSheet(estilo_botao_iniciar)
        btn_automatico.clicked.connect(self.iniciar_teste_automatico)
        btn_automatico.adjustSize()  # Ajusta o tamanho do botão ao texto

        # Botão Parar
        btn_parar = QPushButton("Parar Testes")
        btn_parar.setStyleSheet(estilo_botao_parar)
        btn_parar.clicked.connect(self.parar_testes)
        btn_parar.adjustSize()  # Ajusta o tamanho do botão ao texto

        # Carregar registros iniciais
        self.carregar_registros()

        # Layout principal para a área inferior
        inferior_layout = QHBoxLayout()

        # Espaço flexível à esquerda (mantém os botões centralizados)
        inferior_layout.addStretch()

        # Layout para os botões centralizados
        botoes_layout = QVBoxLayout()
        botoes_layout.addWidget(btn_manual, alignment=Qt.AlignCenter)
        botoes_layout.addWidget(btn_automatico, alignment=Qt.AlignCenter)
        botoes_layout.addWidget(btn_parar, alignment=Qt.AlignCenter)
        inferior_layout.addLayout(botoes_layout)

        # Espaço flexível entre os botões e o status/spinner
        inferior_layout.addStretch()

        # Adiciona o layout inferior ao layout principal
        main_layout.addLayout(inferior_layout)

        # Widget independente para status e spinner
        self.status_widget = QWidget(self)
        self.status_widget.setFixedSize(200, 50)  # Tamanho fixo para evitar impacto no layout principal
        self.status_widget.setStyleSheet("background-color: transparent;")

        # Layout interno para o status_widget
        status_layout = QHBoxLayout(self.status_widget)
        status_layout.setContentsMargins(0, 0, 0, 0)

        # Label para mensagens de status
        self.status_label = QLabel(self.status_widget)
        self.status_label.setStyleSheet("""
            font-family: Arial;
            font-size: 12px;
            font-weight: bold;
            color: #0072B7;
            background-color: #f0f0f0;
            padding: 5px;
            border: 1px solid #cccccc;
        """)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.status_label.setFixedSize(150, 30)
        self.status_label.setText("Status: Pronto")
        self.status_label.hide()  # Inicialmente escondido

        # Spinner
        self.spinner = QLabel(self.status_widget)
        self.spinner.setStyleSheet("background-color: transparent;")
        self.spinner.setFixedSize(32, 32)
        self.spinner.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.movie = QMovie(LOADING_GIF)  # Usa o caminho resolvido
        self.movie.setScaledSize(self.spinner.size())  # Escala o GIF para o tamanho do spinner
        self.spinner.setMovie(self.movie)
        self.spinner.hide()  # Inicialmente escondido

        # Adiciona ao layout do status_widget
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.spinner)

        # Reposiciona o status_widget dinamicamente
        self.reposicionar_status_widget()
        self.resizeEvent = self._handle_resize  # Conecta ao evento de redimensionamento

    def carregar_registros(self):
        """Carrega os registros do backend e exibe na tabela."""
        registros = carregar_registros()
        self.tabela.setRowCount(len(registros))
        for row, registro in enumerate(registros):
            self.tabela.setItem(row, 0, QTableWidgetItem(str(registro["ID"])))
            self.tabela.setItem(row, 1, QTableWidgetItem(registro["Nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(registro["Matricula"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(registro["Setor"]))

    def pesquisar_registros(self):
        """Filtra os registros na tabela com base na pesquisa."""
        termo = self.search_input.text().lower()
        registros = carregar_registros()
        registros_filtrados = [
            registro for registro in registros
            if termo in str(registro["Nome"]).lower()
            or termo in str(registro["Matricula"]).lower()
            or termo in str(registro["Setor"]).lower()
        ]
        self.tabela.setRowCount(len(registros_filtrados))
        for row, registro in enumerate(registros_filtrados):
            self.tabela.setItem(row, 0, QTableWidgetItem(str(registro["ID"])))
            self.tabela.setItem(row, 1, QTableWidgetItem(registro["Nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(registro["Matricula"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(registro["Setor"]))

    def iniciar_teste_manual(self):
        """Inicia um teste manual para o registro selecionado."""
        linhas_selecionadas = self.tabela.selectionModel().selectedRows()
        if not linhas_selecionadas:
            QMessageBox.warning(self, "Erro", "Selecione um registro para realizar o teste.")
            return

        linha = linhas_selecionadas[0].row()
        id_usuario = self.tabela.item(linha, 0).text()
        nome = self.tabela.item(linha, 1).text()
        matricula = self.tabela.item(linha, 2).text()
        setor = self.tabela.item(linha, 3).text()

        # Exibe o spinner e define o status inicial
        self.status_label.setText("Status: Teste iniciado...")
        self.spinner.show()
        self.movie.start()
        self.status_label.show()

        def callback(resultado):
            """Função chamada quando o backend envia uma resposta."""
            if resultado.startswith("ERRO"):
                erro_msg = resultado.split("-", 1)[1]
                self.erro_recebido.emit(erro_msg)
                self.status_label.setText("Status: Erro durante o teste.")
                self.spinner.hide()
                self.movie.stop()
            else:
                # Atualiza o status com base na resposta recebida
                self.atualizar_status(resultado)

                # Se o resultado final for recebido, para o spinner
                if resultado.startswith("$RESULT"):
                    self.spinner.hide()
                    self.movie.stop()

                # Emite o sinal com o resultado para outras partes da interface
                self.resultado_recebido.emit(resultado)

        try:
            from src.backend.Testes import executar_teste
            executar_teste(id_usuario, nome, matricula, setor, automatico=False, callback=callback)
        except Exception as e:
            self.spinner.hide()
            self.movie.stop()
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar o teste manual: {e}")

    def iniciar_teste_automatico(self):
        """Inicia testes automáticos e para ao encontrar um resultado reprovado (HIGH)."""
        self.iniciar_spinner()  # Inicia o spinner
        def callback(resultado):
            print(f"Resultado recebido: {resultado}")  # Verifica o texto recebido

            if resultado.startswith("ERRO"):
                erro_msg = resultado.split("-", 1)[1]
                self.erro_recebido.emit(erro_msg)
                self.status_label.setText("Status: Erro durante o teste.")
                self.spinner.hide()
                self.movie.stop()
            else:
                # Atualiza o status com base no resultado
                self.atualizar_status(resultado)

                # Finaliza o spinner para "$RESULT"
                if resultado.startswith("$RESULT"):
                    self.spinner.hide()
                    self.movie.stop()

                self.resultado_recebido.emit(resultado)

        try:
            from src.backend.Testes import executar_teste
            executar_teste(None, None, None, None, automatico=True, callback=callback)
        except Exception as e:
            self.parar_spinner()  # Para o spinner
            QMessageBox.critical(self, "Erro", f"Erro ao iniciar os testes automáticos: {e}")

    def mostrar_erro(self, mensagem):
        """Mostra mensagens de erro em um QMessageBox."""
        QMessageBox.critical(self, "Erro", mensagem)

    def mostrar_resultado(self, resultado):
        self.parar_spinner()  # Para o spinner
        """Mostra o resultado recebido do backend em um QMessageBox."""
        try:
            quantidade, status = resultado.split("-")  # Divide o resultado em quantidade e status

            if status == "HIGH":
                # Resultado reprovado com HIGH
                QMessageBox.warning(
                    self, "Resultado do Teste",
                    f"Teste reprovado, Quantidade do álcool: {quantidade}\n"
                    f"Recomenda-se aguardar 5 minutos antes de iniciar um novo teste."
                )
                return  # Evita mensagens adicionais após o HIGH

            if status == "OK":
                mensagem = f"Teste aprovado, quantidade do álcool: {quantidade}"
            else:
                mensagem = f"Resultado inesperado: {resultado}"  # Mensagem para casos não tratados

            QMessageBox.information(self, "Resultado do Teste", mensagem)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao processar o resultado: {e}")

    def parar_testes(self):
        self.parar_spinner()  # Para o spinner
        """Envia o comando $RESET para parar os testes."""
        try:
            parar_testes()
            QMessageBox.information(self, "Parado", "Testes interrompidos com sucesso.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao interromper os testes: {e}")

    def iniciar_spinner(self):
        """Inicia o spinner e exibe a mensagem de status."""
        self.spinner.show()
        self.movie.start()
        self.status_label.show()
        self.status_label.setText("Status: Teste iniciado...")

    def parar_spinner(self):
        """Para o spinner e oculta a mensagem de status."""
        self.spinner.hide()
        self.movie.stop()
        self.status_label.hide()

    def atualizar_status(self, resultado):
        """Atualiza a mensagem de status com base na resposta recebida."""
        status_map = {
            "$WAIT": "Aguardando início do teste...",
            "$STANBY": "Pronto para assoprar.",
            "$TRIGGER": "Assoprando no aparelho...",
            "$BREATH": "Analisando o sopro...",
            "$RESULT": "Teste finalizado.",
        }

        comando = resultado.split(",")[0]  # Extrai o comando principal
        print(f"Comando extraído: {comando}")  # Verifica qual comando foi recebido

        mensagem = status_map.get(comando, "Status desconhecido")
        self.status_label.setText(f"Status: {mensagem}")

        # Define a mensagem com base no mapa ou uma mensagem padrão
        mensagem = status_map.get(resultado.split(",")[0], "Status desconhecido")
        self.status_label.setText(f"Status: {mensagem}")
    
    def reposicionar_status_widget(self):
        """Reposiciona o status_widget no canto inferior direito."""
        margin = 20  # Margem em relação ao canto inferior direito
        self.status_widget.move(
            self.width() - self.status_widget.width() - margin,
            self.height() - self.status_widget.height() - margin
        )
    
    def _handle_resize(self, event):
        """Recalcula a posição do status_widget ao redimensionar a janela."""
        super(TestesTela, self).resizeEvent(event)
        self.reposicionar_status_widget()