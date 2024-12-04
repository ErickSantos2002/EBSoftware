from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem,
    QPushButton, QMessageBox, QHeaderView, QLineEdit
)
from PyQt5.QtCore import Qt
from src.backend.Registros import carregar_registros
from src.backend.Testes import (
    iniciar_teste_manual, parar_testes,
    iniciar_teste_automatico, parar_testes
)
from threading import Thread

class TestesTela(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Layout principal
        main_layout = QVBoxLayout(self)

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

        # Adiciona os botões ao layout
        botoes_layout.addWidget(btn_manual, alignment=Qt.AlignCenter)
        botoes_layout.addWidget(btn_automatico, alignment=Qt.AlignCenter)
        botoes_layout.addWidget(btn_parar, alignment=Qt.AlignCenter)
        main_layout.addLayout(botoes_layout)

        # Carregar registros iniciais
        self.carregar_registros()

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

        def executar_teste():
            try:
                resultado = iniciar_teste_manual(id_usuario, nome, matricula, setor)
                if resultado.startswith("0.000-OK"):
                    self.exibir_messagebox("sucesso", f"Teste realizado com sucesso!\nResultado: {resultado}")
                else:
                    self.exibir_messagebox("erro", f"Teste retornou um resultado inesperado: {resultado}")
            except Exception as e:
                self.exibir_messagebox("erro", f"Erro ao realizar o teste: {e}")

        # Inicia a execução do teste em uma thread separada
        thread = Thread(target=executar_teste, daemon=True)
        thread.start()

    def exibir_messagebox(self, tipo, mensagem):
        """Exibe uma mensagem dependendo do tipo."""
        if tipo == "sucesso":
            QMessageBox.information(self, "Resultado do Teste", mensagem)
        elif tipo == "erro":
            QMessageBox.critical(self, "Erro", mensagem)

    def iniciar_teste_automatico(self):
        """Inicia testes automáticos."""
        try:
            resultado = iniciar_teste_automatico()
            QMessageBox.information(self, "Resultado do Teste Automático", f"Teste realizado com sucesso!\nResultado: {resultado}")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao realizar o teste automático: {e}")

    def parar_testes(self):
        """Envia o comando $RESET para parar os testes."""
        try:
            parar_testes()
            QMessageBox.information(self, "Parado", "Testes interrompidos com sucesso.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao interromper os testes: {e}")