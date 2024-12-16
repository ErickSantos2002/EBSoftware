from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QLabel, QComboBox, QDateEdit, QLineEdit, QMessageBox, QFrame, QHeaderView
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal

from src.backend.Resultados import carregar_resultados, salvar_em_excel, salvar_em_pdf

# Centralização de estilos
STYLES = {
    "input": "font-family: Arial; font-size: 12px; background-color: #f0f0f0; border: 1px solid #cccccc; padding: 5px;",
    "date_edit": """
        QDateEdit {
            font-family: Arial; font-size: 12px; background-color: #f0f0f0;
            border: 1px solid #cccccc; padding: 5px;
        }
        QDateEdit:hover { background-color: #e0e0e0; }
    """,
    "btn_filtros": """
        QPushButton {
            font-family: Arial; font-size: 12px; font-weight: bold; background-color: #0072B7; 
            color: white; border: 1px solid #005A9E; padding: 5px 10px;
        }
        QPushButton:hover { background-color: #005BB5; }
        QPushButton:pressed { background-color: #003F87; }
    """,
    "button": """
        QPushButton {
            font-family: Arial; font-size: 12px; background-color: #f0f0f0;
            border: 1px solid #cccccc; padding: 5px;
        }
        QPushButton:hover { background-color: #e0e0e0; }
        QPushButton:pressed {
            background-color: #d0d0d0; border-style: inset;
        }
    """,
    "combo_box": """
        QComboBox, QLineEdit {
            font-family: Arial; font-size: 12px; background-color: #f0f0f0;
            border: 1px solid #cccccc; padding: 5px;
        }
        QComboBox:hover, QLineEdit:hover { background-color: #e0e0e0; }
    """,
    "table": """
        font-family: Arial; font-size: 12px; background-color: #f0f0f0;
        border: 1px solid #cccccc;
    """
}

class ResultadosTela(QWidget):
    atualizar_resultados_signal = pyqtSignal()  # Sinal para atualizar a tabela

    def __init__(self, parent=None):
        super().__init__(parent)

        self.resultados = carregar_resultados()  # Carrega os resultados inicialmente
        self.setup_ui()
        self.connect_signals()
        self.carregar_tabela(self.resultados)
        self.limite_exibicao = 100  # Começa exibindo os primeiros 100 registros

    def setup_ui(self):
        """Inicializa a interface do usuário."""
        self.setStyleSheet("background-color: white;")
        self.setWindowTitle("Resultados")
        self.setGeometry(100, 100, 1200, 600)

        # Layout principal
        self.frame = QFrame(self)
        self.frame.setStyleSheet("background-color: white; border: none;")
        main_layout = QVBoxLayout(self.frame)

        # Filtros
        self.init_filters(main_layout)

        # Tabela de resultados
        self.init_table(main_layout)

        # Botões para salvar
        self.init_save_buttons(main_layout)

        # Configura o layout principal da janela
        layout = QVBoxLayout(self)
        layout.addWidget(self.frame)

    def connect_signals(self):
        """Conecta sinais aos métodos apropriados."""
        self.atualizar_resultados_signal.connect(self.atualizar_tabela)

    def init_filters(self, layout):
        """Inicializa a barra de filtros."""
        filtros_layout = QHBoxLayout()

        # Filtros de data
        self.periodo_todos = self.create_button("Todas as Datas", checkable=True, checked=True, callback=self.toggle_datas)
        self.data_inicio = self.create_date_edit(enabled=False)
        self.data_fim = self.create_date_edit(enabled=False)

        # Filtro de usuário
        self.usuario_todos = self.create_button("Todos os Usuários", checkable=True, checked=True, callback=self.toggle_usuarios)
        self.input_usuario = self.create_line_edit("Digite o ID, Nome, Matrícula ou Setor do usuário...", enabled=False)

        # Conectar Enter do input_usuario ao botão "Aplicar Filtros"
        self.input_usuario.returnPressed.connect(self.aplicar_filtros)

        # Filtro de status
        self.combo_status = self.create_combo_box(["Todos", "Aprovados", "Rejeitados"])

        # Botão para aplicar filtros
        btn_aplicar_filtros = self.create_button("Aplicar Filtros", callback=self.aplicar_filtros)

        # Botão para carregar mais registros
        btn_carregar_mais = self.create_button(
            "Carregar Mais", callback=self.carregar_mais_registros
        )

        # Aplica o estilo azul diretamente
        btn_aplicar_filtros.setStyleSheet(STYLES["btn_filtros"])
        btn_carregar_mais.setStyleSheet(STYLES["btn_filtros"])

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
        filtros_layout.addWidget(btn_aplicar_filtros)
        filtros_layout.addWidget(btn_carregar_mais)

        layout.addLayout(filtros_layout)

    def init_table(self, layout):
        """Configura a tabela para exibição dos resultados."""
        self.tabela = QTableWidget()
        self.tabela.setColumnCount(8)  # Número de colunas da tabela
        self.tabela.setHorizontalHeaderLabels([
            "ID do Teste", "ID do Usuário", "Nome", "Matrícula", "Setor",
            "Data e Hora", "Quantidade de Álcool", "Status"
        ])
        
        # Ajusta o comportamento das colunas
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Ajusta o comportamento da seleção (linha inteira)
        self.tabela.setSelectionBehavior(QTableWidget.SelectRows)

        # Desativa a edição direta da tabela
        self.tabela.setEditTriggers(QTableWidget.NoEditTriggers)

        # Remove o cabeçalho vertical
        self.tabela.verticalHeader().setVisible(False)

        # Estilo da tabela
        self.tabela.setStyleSheet("""
            QTableWidget {
                font-family: Arial;
                font-size: 12px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
            }
            QTableWidget::item {
                padding: 5px;
            }
        """)

        # Adiciona a tabela ao layout
        layout.addWidget(self.tabela)

    def init_save_buttons(self, layout):
        """Inicializa os botões para salvar os resultados."""
        botoes_layout = QHBoxLayout()

        btn_salvar_excel = self.create_button("Salvar em Excel", callback=self.salvar_excel)
        btn_salvar_pdf = self.create_button("Salvar em PDF", callback=self.salvar_pdf)

        botoes_layout.addWidget(btn_salvar_excel)
        botoes_layout.addWidget(btn_salvar_pdf)

        layout.addLayout(botoes_layout)

    # Métodos utilitários para criação de widgets
    def create_button(self, text, checkable=False, checked=False, callback=None):
        """Cria e configura um botão."""
        button = QPushButton(text)
        button.setCheckable(checkable)
        button.setChecked(checked)
        button.setStyleSheet(STYLES["button"])
        if callback:
            button.clicked.connect(callback)
        return button

    def create_date_edit(self, enabled=True):
        """Cria e configura um campo de edição de data."""
        date_edit = QDateEdit()
        date_edit.setCalendarPopup(True)
        date_edit.setDate(QDate.currentDate())
        date_edit.setEnabled(enabled)
        date_edit.setStyleSheet(STYLES["date_edit"])
        return date_edit

    def create_line_edit(self, placeholder, enabled=True):
        """Cria e configura um campo de entrada de texto."""
        line_edit = QLineEdit()
        line_edit.setPlaceholderText(placeholder)
        line_edit.setEnabled(enabled)
        line_edit.setStyleSheet(STYLES["combo_box"])
        return line_edit

    def create_combo_box(self, items):
        """Cria e configura um campo de seleção (combo box)."""
        combo_box = QComboBox()
        combo_box.addItems(items)
        combo_box.setStyleSheet(STYLES["combo_box"])
        return combo_box

    # Métodos para manipulação de dados
    def carregar_tabela(self, resultados, limite=100):
        """Carrega os resultados na tabela, exibindo um número limitado de registros."""
        total_registros = len(resultados)
        registros_exibidos = resultados[:limite]  # Limita a quantidade exibida

        self.tabela.setRowCount(len(registros_exibidos))
        for row, resultado in enumerate(registros_exibidos):
            for col, key in enumerate(resultado.keys()):
                item = QTableWidgetItem(str(resultado[key]))
                item.setTextAlignment(Qt.AlignCenter)
                self.tabela.setItem(row, col, item)

        # Adiciona um aviso ao usuário sobre o limite
        if total_registros > limite:
            QMessageBox.information(
                self, 
                "Aviso", 
                f"Exibindo os primeiros {limite} registros de {total_registros}. "
                "Use os filtros para refinar a busca."
            )

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

        # Filtro de usuário (busca parcial por ID, Nome, Matrícula ou Setor)
        usuario_filtro = self.input_usuario.text().strip().lower() if not self.usuario_todos.isChecked() else None

        # Aplica os filtros usando o backend
        filtrados = []
        for resultado in self.resultados:
            # Filtra por período
            if periodo:
                try:
                    # Extrai e converte a data com validação
                    data_teste_str = resultado["Data e Hora"].split()[0]
                    data_teste = QDate.fromString(data_teste_str, "dd/MM/yyyy")  # Formato ajustado para PyQt5
                    if not data_teste.isValid():
                        print(f"Data inválida ignorada: {data_teste_str}")
                        continue  # Ignora entradas com datas inválidas

                    # Converte para tipo Python para comparação
                    data_teste = data_teste.toPyDate()
                    if not (periodo[0] <= data_teste <= periodo[1]):
                        continue
                except Exception as e:
                    print(f"Erro ao processar data: {resultado['Data e Hora']} - {e}")
                    continue

            # Filtra por status
            if status and resultado["Status"] != status:
                continue

            # Filtra por usuário (busca parcial em ID, Nome, Matrícula ou Setor)
            if usuario_filtro:
                if not (
                    usuario_filtro in str(resultado["ID do usuário"]).lower() or
                    usuario_filtro in str(resultado["Nome"]).lower() or
                    usuario_filtro in str(resultado["Matrícula"]).lower() or
                    usuario_filtro in str(resultado["Setor"]).lower()
                ):
                    continue

            filtrados.append(resultado)

        # Recarrega a tabela com os resultados filtrados
        self.carregar_tabela(filtrados)

    def salvar_excel(self):
        """Salva os resultados em Excel."""
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar em Excel", "", "Arquivos Excel (*.xlsx)")
        if caminho:
            try:
                salvar_em_excel(self.resultados, caminho)
                QMessageBox.information(self, "Sucesso", "Os dados foram salvos em Excel.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar em Excel: {e}")

    def salvar_pdf(self):
        """Salva os resultados em PDF."""
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar em PDF", "", "Arquivos PDF (*.pdf)")
        if caminho:
            try:
                salvar_em_pdf(self.resultados, caminho)
                QMessageBox.information(self, "Sucesso", "Os dados foram salvos em PDF.")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao salvar em PDF: {e}")

    # Métodos de alternância
    def toggle_datas(self):
        """Habilita/desabilita os campos de data e altera o texto do botão."""
        estado = not self.periodo_todos.isChecked()
        self.data_inicio.setEnabled(estado)
        self.data_fim.setEnabled(estado)
        self.periodo_todos.setText("Selecione uma Data" if estado else "Todas as Datas")

    def toggle_usuarios(self):
        """Habilita/desabilita o campo de entrada de usuário e altera o texto do botão."""
        estado = not self.usuario_todos.isChecked()
        self.input_usuario.setEnabled(estado)
        self.usuario_todos.setText("Digite o Usuário" if estado else "Todos os Usuários")

    def atualizar_tabela(self):
        """Recarrega os resultados e atualiza a tabela."""
        self.resultados = carregar_resultados()
        self.carregar_tabela(self.resultados)
    
    def carregar_mais_registros(self):
        """Aumenta o limite de registros exibidos na tabela."""
        self.limite_exibicao += 100  # Incrementa o limite em 100

        if self.limite_exibicao >= len(self.resultados):
            self.limite_exibicao = len(self.resultados)
            self.btn_carregar_mais.hide()  # Oculta o botão quando tudo for carregado

        self.carregar_tabela(self.resultados, self.limite_exibicao)
