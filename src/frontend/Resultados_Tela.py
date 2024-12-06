from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QLabel, QComboBox, QDateEdit, QFrame, QLineEdit, QMessageBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QObject
from src.backend.Resultados import carregar_resultados, filtrar_resultados, salvar_em_excel, salvar_em_pdf
from src.backend.Testes import sinal_global  # Importa o gerenciador de sinais


class ResultadosTela(QWidget):
    # Sinal para atualizar os resultados
    atualizar_resultados_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        sinal_global.resultado_atualizado.connect(self.atualizar_tabela)
        self.setStyleSheet("background-color: white;")
        self.setWindowTitle("Resultados")
        self.setGeometry(100, 100, 1200, 600)

        # Inicializar componentes
        self.resultados = carregar_resultados()  # Carrega resultados inicialmente

        # Conecta o sinal de atualização
        self.atualizar_resultados_signal.connect(self.atualizar_tabela)

        # Criação do frame principal com fundo branco
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: white; border: none;")
        main_layout = QVBoxLayout(self.frame)

        # Define o layout principal da janela
        final_layout = QVBoxLayout(self)
        final_layout.addWidget(self.frame)

        # Estilo para os campos de data
        estilo_dateedit = """
            QDateEdit {
                font-family: Arial;
                font-size: 12px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QDateEdit::drop-down {
                border: none;
            }
            QDateEdit:hover {
                background-color: #e0e0e0;  /* Cinza mais claro no hover */
            }
        """

        # Estilo para os botões
        estilo_botao = """
            QPushButton {
                font-family: Arial;
                font-size: 12px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;  /* Cinza mais claro no hover */
            }
            QPushButton:pressed {
                background-color: #d0d0d0;  /* Cinza mais escuro ao pressionar */
                border-style: inset;
            }
        """

        # Estilo para combobox e campo de digitação
        estilo_combobox = """
            QComboBox, QLineEdit {
                font-family: Arial;
                font-size: 12px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                padding: 5px;
            }
            QComboBox:hover, QLineEdit:hover {
                background-color: #e0e0e0;  /* Cinza mais claro no hover */
            }
        """

        # Filtros
        filtros_layout = QHBoxLayout()

        # Configuração de "Todas as Datas"
        self.periodo_todos = QPushButton("Todas as Datas")
        self.periodo_todos.setCheckable(True)
        self.periodo_todos.setChecked(True)  # Por padrão, habilitado para "Todas as datas"
        self.periodo_todos.setStyleSheet(estilo_botao)
        self.periodo_todos.clicked.connect(self.toggle_datas)

        self.data_inicio = QDateEdit()
        self.data_inicio.setCalendarPopup(True)
        self.data_inicio.setDate(QDate.currentDate())
        self.data_inicio.setEnabled(False)  # Desabilitado quando "Todas as Datas" está selecionado
        self.data_inicio.setStyleSheet(estilo_dateedit)

        self.data_fim = QDateEdit()
        self.data_fim.setCalendarPopup(True)
        self.data_fim.setDate(QDate.currentDate())
        self.data_fim.setEnabled(False)  # Desabilitado quando "Todas as Datas" está selecionado
        self.data_fim.setStyleSheet(estilo_dateedit)

        # Configuração de "Todos os Usuários" e campo de entrada
        self.usuario_todos = QPushButton("Todos os Usuários")
        self.usuario_todos.setCheckable(True)
        self.usuario_todos.setChecked(True)  # Padrão: "Todos os Usuários"
        self.usuario_todos.setStyleSheet(estilo_botao)
        self.usuario_todos.clicked.connect(self.toggle_usuarios)

        self.input_usuario = QLineEdit()
        self.input_usuario.setPlaceholderText("Digite o nome do usuário...")
        self.input_usuario.setEnabled(False)  # Desabilitado se "Todos os Usuários" estiver selecionado
        self.input_usuario.setStyleSheet(estilo_combobox)

        # Configuração de Status
        self.combo_status = QComboBox()
        self.combo_status.addItems(["Todos", "Aprovados", "Rejeitados"])
        self.combo_status.setStyleSheet(estilo_combobox)

        # Adiciona widgets ao layout de filtros
        filtros_layout.addWidget(self.periodo_todos)
        filtros_layout.addWidget(QLabel("De:"))
        filtros_layout.addWidget(self.data_inicio)
        filtros_layout.addWidget(QLabel("Até:"))
        filtros_layout.addWidget(self.data_fim)
        filtros_layout.addWidget(self.usuario_todos)
        filtros_layout.addWidget(QLabel("Usuário:"))
        filtros_layout.addWidget(self.input_usuario)
        filtros_layout.addWidget(QLabel("Status:"))
        filtros_layout.addWidget(self.combo_status)

        btn_aplicar_filtros = QPushButton("Aplicar Filtros")
        btn_aplicar_filtros.clicked.connect(self.aplicar_filtros)
        btn_aplicar_filtros.setStyleSheet(estilo_botao)
        filtros_layout.addWidget(btn_aplicar_filtros)

        # Adiciona o layout de filtros ao layout principal
        main_layout.addLayout(filtros_layout)

        # Tabela de resultados
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)
        self.tabela.setHorizontalHeaderLabels([
            "ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor",
            "Data e hora", "Qtd. Álcool", "Status"
        ])
        self.tabela.horizontalHeader().setStretchLastSection(True)
        main_layout.addWidget(self.tabela)

        # Botões para salvar
        botoes_layout = QHBoxLayout()
        btn_salvar_excel = QPushButton("Salvar em Excel")
        btn_salvar_excel.clicked.connect(self.salvar_excel)
        btn_salvar_excel.setStyleSheet(estilo_botao)
        botoes_layout.addWidget(btn_salvar_excel)

        btn_salvar_pdf = QPushButton("Salvar em PDF")
        btn_salvar_pdf.clicked.connect(self.salvar_pdf)
        btn_salvar_pdf.setStyleSheet(estilo_botao)
        botoes_layout.addWidget(btn_salvar_pdf)

        main_layout.addLayout(botoes_layout)

        # Carregar resultados iniciais
        self.resultados = carregar_resultados()
        self.carregar_tabela(self.resultados)

    def carregar_tabela(self, resultados):
        """Carrega os resultados na tabela."""
        self.tabela.setRowCount(len(resultados))
        for row, resultado in enumerate(resultados):
            for col, key in enumerate(resultado.keys()):
                item = QTableWidgetItem(str(resultado[key]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(row, col, item)

    def aplicar_filtros(self):
        """Aplica filtros aos resultados e recarrega a tabela."""
        # Verifica se deve filtrar por período
        if self.periodo_todos.isChecked():
            periodo = None
        else:
            periodo = (
                self.data_inicio.date().toPyDate(),
                self.data_fim.date().toPyDate()
            )

        # Corrige o valor do status para bater com os dados da planilha
        status = self.combo_status.currentText()
        if status == "Todos":
            status = None  # Não aplica filtro
        elif status == "Aprovados":
            status = "Aprovado"
        elif status == "Rejeitados":
            status = "Rejeitado"

        # Filtro de usuário (busca parcial no nome)
        usuario_filtro = self.input_usuario.text().strip().lower() if not self.usuario_todos.isChecked() else None

        # Aplica os filtros usando o backend
        filtrados = []
        for resultado in self.resultados:
            # Filtra por período
            if periodo:
                data_teste = QDate.fromString(resultado["Data e hora"].split()[0], "yyyy-MM-dd").toPyDate()
                if not (periodo[0] <= data_teste <= periodo[1]):
                    continue

            # Filtra por status
            if status and resultado["Status"] != status:
                continue

            # Filtra por usuário (busca parcial)
            if usuario_filtro and usuario_filtro not in resultado["Nome"].lower():
                continue

            filtrados.append(resultado)

        # Recarrega a tabela com os resultados filtrados
        self.carregar_tabela(filtrados)

    def salvar_excel(self): 
        """Salva os resultados filtrados atualmente exibidos na tabela em um arquivo Excel."""
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar em Excel", "", "Arquivos Excel (*.xlsx)")
        if not caminho:
            return  # O usuário cancelou a ação

        # Obtém os dados exibidos na tabela
        dados = []
        for row in range(self.tabela.rowCount()):
            linha = []
            for col in range(self.tabela.columnCount()):
                item = self.tabela.item(row, col)
                linha.append(item.text() if item else "")
            dados.append(linha)

        # Cabeçalhos da tabela
        colunas = [self.tabela.horizontalHeaderItem(i).text() for i in range(self.tabela.columnCount())]

        # Salva os dados em um arquivo Excel usando a função do backend
        try:
            from src.backend.Resultados import salvar_em_excel
            salvar_em_excel([dict(zip(colunas, linha)) for linha in dados], caminho)
            QMessageBox.information(self, "Sucesso", "Os dados foram salvos com sucesso em Excel.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar em Excel: {e}")

    def salvar_pdf(self):
        """Salva os resultados filtrados atualmente exibidos na tabela em um arquivo PDF."""
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar em PDF", "", "Arquivos PDF (*.pdf)")
        if not caminho:
            return  # O usuário cancelou a ação

        # Obtém os dados exibidos na tabela
        dados = []
        for row in range(self.tabela.rowCount()):
            linha = []
            for col in range(self.tabela.columnCount()):
                item = self.tabela.item(row, col)
                linha.append(item.text() if item else "")
            dados.append(linha)

        # Cabeçalhos da tabela
        colunas = [self.tabela.horizontalHeaderItem(i).text() for i in range(self.tabela.columnCount())]

        # Salva os dados em um PDF
        try:
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(caminho, pagesize=landscape(letter))
            largura, altura = landscape(letter)

            # Define o título do PDF
            c.setFont("Helvetica-Bold", 14)
            c.drawString(30, altura - 30, "Relatório de Resultados")

            # Cabeçalhos
            c.setFont("Helvetica-Bold", 10)
            x_inicial = 30
            y = altura - 50
            largura_colunas = largura / len(colunas)  # Divide igualmente as colunas

            for coluna in colunas:
                c.drawString(x_inicial, y, coluna)
                x_inicial += largura_colunas

            # Dados
            c.setFont("Helvetica", 10)
            y -= 20  # Ajusta para a primeira linha dos dados
            for linha in dados:
                x_inicial = 30
                for valor in linha:
                    # Ajusta texto com encoding UTF-8 para evitar problemas
                    c.drawString(x_inicial, y, valor.encode('utf-8', 'replace').decode('utf-8'))
                    x_inicial += largura_colunas
                y -= 20

                # Adiciona uma nova página se acabar o espaço
                if y < 30:
                    c.showPage()
                    c.setFont("Helvetica-Bold", 10)
                    y = altura - 50
                    for coluna in colunas:
                        c.drawString(x_inicial, y, coluna)
                        x_inicial += largura_colunas
                    y -= 20

            c.save()
            QMessageBox.information(self, "Sucesso", "Os dados foram salvos com sucesso em PDF.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar em PDF: {e}")

    def toggle_datas(self):
        """Habilita/desabilita os campos de data e altera o texto do botão."""
        estado = not self.periodo_todos.isChecked()
        self.data_inicio.setEnabled(estado)
        self.data_fim.setEnabled(estado)

        # Altera o texto do botão
        if estado:
            self.periodo_todos.setText("Selecionar Datas")
        else:
            self.periodo_todos.setText("Todas as Datas")

    def toggle_usuarios(self):
        """Habilita/desabilita o campo de entrada de usuário e altera o texto do botão."""
        estado = not self.usuario_todos.isChecked()
        self.input_usuario.setEnabled(estado)

        # Altera o texto do botão
        if estado:
            self.usuario_todos.setText("Selecionar Usuários")
        else:
            self.usuario_todos.setText("Todos os Usuários")

    def atualizar_tabela(self):
        """Recarrega os resultados do backend e os exibe na tabela."""
        self.resultados = carregar_resultados()  # Recarrega resultados do backend
        self.carregar_tabela(self.resultados)   # Atualiza a tabela com os novos dados