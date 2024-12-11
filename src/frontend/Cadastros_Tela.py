import os
import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QApplication,
    QPushButton, QLineEdit, QFormLayout, QMessageBox, QHeaderView, QFrame, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from backend.Cadastros import (carregar_registros, adicionar_registro, 
    apagar_registros, importar_excel, exportar_modelo, exportar_modelo, gerar_arquivo_erros
)

if getattr(sys, 'frozen', False):
    # Diretório do executável (PyInstaller)
    BASE_DIR = sys._MEIPASS
else:
    # Diretório raiz do projeto (quando executado como script)
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)  # Adiciona src ao início do sys.path
    
estilo = """
            font-family: Arial; font-size: 12px;
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            padding: 5px;
            margin-top: 5px;
        """



class CustomTableWidgetItem(QTableWidgetItem):
    def __lt__(self, other):
        # Tenta comparar os dados internos (inteiros) em vez do texto
        try:
            return int(self.data(Qt.UserRole)) < int(other.data(Qt.UserRole))
        except (ValueError, TypeError):
            # Se a conversão falhar, usa a comparação padrão (strings)
            return super().__lt__(other)

class CadastrosTela(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Criação do frame principal com fundo branco
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: white; border: none;")
        main_layout = QVBoxLayout(self.frame)  # Define o layout dentro do frame

        # Painéis esquerdo (tabela) e direito (formulário/botões)
        inner_layout = QHBoxLayout()
        self.init_left_panel(inner_layout)
        self.init_right_panel(inner_layout)

        main_layout.addLayout(inner_layout)

        # Aplica padding para melhorar o visual
        inner_layout.setContentsMargins(10, 10, 10, 10)
        inner_layout.setSpacing(10)

        # Configura o layout principal do widget
        final_layout = QVBoxLayout(self)
        final_layout.addWidget(self.frame)

        # Carrega os dados iniciais
        self.carregar_dados()

    def init_left_panel(self, layout):
        """Configura a área da esquerda com a tabela e pesquisa."""
        left_panel = QVBoxLayout()

        # Título
        titulo = QLabel("Tabela de Cadastros")
        titulo.setAlignment(Qt.AlignCenter)
        titulo.setStyleSheet("font-family: Arial Black; font-size: 20px; background-color: #f0f0f0; margin-bottom: 10px;")
        left_panel.addWidget(titulo)
        # Campo de pesquisa
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Pesquisar por Nome, Matrícula ou Setor...")
        self.search_input.setStyleSheet(estilo)
        self.search_input.returnPressed.connect(self.pesquisar_registros)
        search_button = QPushButton("Pesquisar")
        search_button.setStyleSheet("""
            QPushButton {
                font-family: Arial; 
                font-size: 12px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 5px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;  /* Cor mais clara no hover */
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* Cor mais escura quando pressionado */
                border-style: inset;  /* Dá uma aparência de botão afundado */
            }
        """)
        search_button.clicked.connect(self.pesquisar_registros)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        left_panel.addLayout(search_layout)

        # Tabela para exibir os registros
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(4)
        self.tabela.setHorizontalHeaderLabels(["ID", "Nome", "Matrícula", "Setor"])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Faz os cabeçalhos ocuparem todo o espaço
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)
        self.tabela.setSortingEnabled(True)
        self.tabela.setStyleSheet("""
            font-family: Arial; font-size: 12px;
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
        """)
        left_panel.addWidget(self.tabela)

        layout.addLayout(left_panel, stretch=2)  # Painel da esquerda ocupa mais espaço

    def init_right_panel(self, layout):
        """Configura a área da direita com o formulário e botões."""
        right_panel = QVBoxLayout()

        # Título
        titulo = QLabel("Gerenciar Cadastros")
        titulo.setStyleSheet("font-family: Arial Black; font-size: 20px; background-color: #f0f0f0; margin-bottom: 10px;")
        titulo.setAlignment(Qt.AlignCenter)
        right_panel.addWidget(titulo)

        # Formulário de entrada
        form_layout = QVBoxLayout()  # Layout vertical para o formulário e botões
        form_fields = QFormLayout()
        form_fields.setLabelAlignment(Qt.AlignRight)  # Alinha os rótulos à direita
        form_fields.setContentsMargins(0, 0, 0, 0)  # Remove margens internas
        form_fields.setSpacing(5)  # Reduz o espaçamento entre os elementos

        # Campos de entrada
        self.nome_input = QLineEdit()
        self.matricula_input = QLineEdit()
        self.setor_input = QLineEdit()
        self.nome_input.setPlaceholderText("Nome")
        self.nome_input.returnPressed.connect(self.cadastrar_usuario)
        self.matricula_input.setPlaceholderText("Matricula")
        self.matricula_input.returnPressed.connect(self.cadastrar_usuario)
        self.setor_input.setPlaceholderText("Setor")
        self.setor_input.returnPressed.connect(self.cadastrar_usuario)
        estilo = """
            font-family: Arial; font-size: 12px;
            background-color: #f0f0f0;
            border: 1px solid #cccccc;
            padding: 5px;
        """
        self.nome_input.setStyleSheet(estilo)
        self.matricula_input.setStyleSheet(estilo)
        self.setor_input.setStyleSheet(estilo)
        form_fields.addRow("Nome:", self.nome_input)
        form_fields.addRow("Matricula:", self.matricula_input)
        form_fields.addRow("Setor:", self.setor_input)

        # Centralizar os rótulos no meio verticalmente
        for i in range(form_fields.rowCount()):
            label = form_fields.itemAt(i, QFormLayout.LabelRole).widget()
            if isinstance(label, QLabel):
                label.setStyleSheet("padding-top: 5px; font-family: Arial; font-size: 12px;")

        form_layout.addLayout(form_fields)

        # Botão de cadastrar
        cadastrar_btn = QPushButton("Cadastrar")
        cadastrar_btn.setStyleSheet("""
            QPushButton {
                font-family: Arial; 
                font-size: 12px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 5px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;  /* Cor mais clara no hover */
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* Cor mais escura quando pressionado */
                border-style: inset;  /* Dá uma aparência de botão afundado */
            }
        """)
        cadastrar_btn.clicked.connect(self.cadastrar_usuario)
        form_layout.addWidget(cadastrar_btn)

        # Adiciona o layout do formulário ao painel
        right_panel.addLayout(form_layout)

        # Botões adicionais
        self.add_right_buttons(right_panel)  # Adiciona os botões diretamente abaixo do formulário

        layout.addLayout(right_panel, stretch=1)


    def add_right_buttons(self, layout):
        """Adiciona os botões na área direita."""
        btn_apagar = QPushButton("Apagar Registro")
        btn_importar = QPushButton("Importar Excel")
        btn_exportar = QPushButton("Exportar Excel")
        btn_modelo = QPushButton("Baixar Modelo Base")

        # Estilo dos botões
        estilo_botao = """
            QPushButton {
                font-family: Arial; 
                font-size: 12px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 5px;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;  /* Cor mais clara no hover */
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* Cor mais escura quando pressionado */
                border-style: inset;  /* Dá uma aparência de botão afundado */
            }
        """
        for btn in [btn_apagar, btn_importar, btn_exportar, btn_modelo]:
            btn.setStyleSheet(estilo_botao)
            layout.addWidget(btn)

        # Conexões dos botões
        btn_apagar.clicked.connect(self.apagar_registro)
        btn_importar.clicked.connect(self.importar_cadastro)
        btn_exportar.clicked.connect(self.exportar_cadastro)
        btn_modelo.clicked.connect(self.baixar_modelo_base)

    def carregar_dados(self):
        """Carrega os dados do backend e exibe na tabela."""
        registros = carregar_registros()
        self.tabela.setRowCount(len(registros))

        for row, registro in enumerate(registros):
            # Converte o ID para inteiro, com tratamento de erro
            try:
                id_valor = int(registro["ID"])
            except ValueError:
                id_valor = 0  # Valor padrão caso a conversão falhe

            # Usa a nova classe CustomTableWidgetItem
            id_item = CustomTableWidgetItem(str(id_valor))
            id_item.setTextAlignment(Qt.AlignCenter)  # Centraliza o texto
            id_item.setData(Qt.UserRole, id_valor)  # Define o dado interno como inteiro
            self.tabela.setItem(row, 0, id_item)

            # Preenche os outros campos como texto
            self.tabela.setItem(row, 1, QTableWidgetItem(registro["Nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(registro["Matricula"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(registro["Setor"]))

        # Permite ordenação ao clicar nos cabeçalhos
        self.tabela.setSortingEnabled(True)

    def pesquisar_registros(self):
        """Filtra os registros na tabela com base na pesquisa."""
        termo = self.search_input.text().lower()
        registros = carregar_registros()
        registros_filtrados = [
            registro for registro in registros
            if termo in registro["Nome"].lower()
            or termo in registro["Matricula"].lower()
            or termo in registro["Setor"].lower()
        ]

        self.tabela.setRowCount(len(registros_filtrados))
        for row, registro in enumerate(registros_filtrados):
            # Configura o ID como CustomTableWidgetItem para manter a ordenação
            id_item = CustomTableWidgetItem(registro["ID"])
            id_item.setTextAlignment(Qt.AlignCenter)
            id_item.setData(Qt.UserRole, int(registro["ID"]))  # Define o dado interno para ordenação
            self.tabela.setItem(row, 0, id_item)

            # Preenche os outros campos como texto
            self.tabela.setItem(row, 1, QTableWidgetItem(registro["Nome"]))
            self.tabela.setItem(row, 2, QTableWidgetItem(registro["Matricula"]))
            self.tabela.setItem(row, 3, QTableWidgetItem(registro["Setor"]))

    def cadastrar_usuario(self):
        """Adiciona um novo registro."""
        nome = self.nome_input.text().strip()
        matricula = self.matricula_input.text().strip()
        setor = self.setor_input.text().strip()  # Setor pode ser opcional

        # Verifica apenas os campos obrigatórios
        if not nome or not matricula:
            QMessageBox.warning(self, "Erro", "Os campos Nome e Matrícula são obrigatórios.")
            return

        try:
            # Adiciona o registro ao backend
            novo_registro = adicionar_registro(nome, matricula, setor)
            QMessageBox.information(self, "Sucesso", f"Registro adicionado com sucesso: {novo_registro}")

            # Limpa os campos de entrada
            self.nome_input.clear()
            self.matricula_input.clear()
            self.setor_input.clear()

            # Atualiza os dados exibidos na tabela
            self.carregar_dados()
        except ValueError as e:
            QMessageBox.warning(self, "Erro", str(e))

    def apagar_registro(self):
        """Apaga o registro selecionado."""
        linhas_selecionadas = self.tabela.selectionModel().selectedRows()
        if not linhas_selecionadas:
            QMessageBox.warning(self, "Erro", "Selecione um registro para apagar.")
            return

        ids_para_apagar = [self.tabela.item(linha.row(), 0).text() for linha in linhas_selecionadas]
        print(f"IDs capturados para apagar: {ids_para_apagar}")

        try:
            apagar_registros(ids_para_apagar)
            QMessageBox.information(self, "Sucesso", "Registros apagados com sucesso.")
            self.carregar_dados()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao apagar registros: {e}")

    def importar_cadastro(self):
        """Importa registros a partir de um arquivo Excel."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar arquivo Excel para importar",
            "",
            "Arquivos Excel (*.xlsx);;Todos os Arquivos (*)",
            options=options
        )

        if file_path:
            try:
                # Carrega o arquivo Excel e calcula o total de registros tentados
                df = pd.read_excel(file_path)  # Lê o Excel para determinar o total de linhas
                total_tentados = len(df)

                # Importa os dados e coleta erros
                registros, erros = importar_excel(file_path)  # Importa registros válidos e coleta erros

                # Calcula o total de erros e sucesso
                total_erros = len(erros)
                total_sucesso = total_tentados - total_erros

                self.carregar_dados()  # Atualiza a tabela com os registros válidos

                if total_erros > 0:
                    # Gera o arquivo de erros
                    erros_path = os.path.join(os.path.dirname(file_path), "Erros_Importacao.xlsx")
                    gerar_arquivo_erros(erros, erros_path)  # Função no backend

                    # Mensagem customizada com dois botões
                    msg = QMessageBox(self)
                    msg.setIcon(QMessageBox.Warning)
                    msg.setWindowTitle("Importação Concluída com Erros")
                    msg.setText(f"""
                        <b>Importação concluída:</b><br>
                        - <b>{total_sucesso}</b> registros adicionados com sucesso.<br>
                        - <b>{total_erros}</b> registros apresentaram erros.<br>
                    """)
                    msg.setInformativeText("Deseja visualizar os detalhes dos erros?")
                    
                    # Botões personalizados
                    btn_abrir = msg.addButton("Abrir Erros", QMessageBox.AcceptRole)
                    btn_ok = msg.addButton("OK", QMessageBox.RejectRole)
                    
                    # Define a ação do botão "Abrir Erros"
                    def abrir_erros():
                        if os.path.exists(erros_path):
                            os.startfile(erros_path)  # Abre o arquivo no Excel

                    btn_abrir.clicked.connect(abrir_erros)
                    msg.exec_()
                else:
                    QMessageBox.information(self, "Sucesso", f"Todos os registros ({total_sucesso}) foram importados com sucesso!")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao importar registros: {e}")

    def exportar_cadastro(self):
        """Exporta os registros atuais para um arquivo Excel."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar registros como arquivo Excel",
            "Cadastros EBSoftware",
            "Arquivos Excel (*.xlsx);;Todos os Arquivos (*)",
            options=options
        )

        if file_path:
            try:
                registros = carregar_registros()
                df = pd.DataFrame(registros)
                df.to_excel(file_path, index=False)
                QMessageBox.information(self, "Sucesso", f"Registros exportados com sucesso para:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao exportar registros: {e}")

    def baixar_modelo_base(self):
        """Baixa um modelo base para cadastro em Excel."""
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar modelo base",
            "Modelo Base Para Cadastros",
            "Arquivos Excel (*.xlsx);;Todos os Arquivos (*)",
            options=options
        )

        if file_path:
            try:
                exportar_modelo(file_path)  # Função no backend que gera o modelo
                QMessageBox.information(self, "Sucesso", f"Modelo base salvo com sucesso em:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar modelo base: {e}")