import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog as fd
import csv
import pandas as pd
from datetime import datetime
from tkcalendar import DateEntry
import os
import subprocess
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
import win32print
import win32api
import win32ui

ARQUIVO_RESULTADOS = "Resultados.csv"
# Variável global para armazenar o estado da ordenação
ordem_atual = {"coluna": None, "direcao": True}  # Por padrão, crescente (True)

def iniciar_resultados():
    resultados_root = tk.Tk()
    resultados_root.title("Resultados")
    resultados_root.geometry("1800x500")
    resultados_root.resizable(False, False)

    # Lista de resultados
    frame_direita = tk.Frame(resultados_root)
    frame_direita.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # Frame para conter o Treeview e as barras de rolagem
    frame_tree = tk.Frame(frame_direita)
    frame_tree.pack_propagate(False)  # Impede expansão automática do frame
    frame_tree.pack(fill="both", expand=True, padx=10, pady=10)

    # Scrollbars para Treeview
    scrollbar_x = ttk.Scrollbar(frame_tree, orient="horizontal")
    scrollbar_y = ttk.Scrollbar(frame_tree, orient="vertical")

    # Configuração do Treeview
    tree = ttk.Treeview(
        frame_tree,
        columns=("ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor", "Data e hora", "Quantidade de Álcool", "Status"),
        show="headings",
        height=20,
        xscrollcommand=scrollbar_x.set,
        yscrollcommand=scrollbar_y.set
    )

    # Configuração dos cabeçalhos e colunas
    tree.heading("ID do teste", text="ID do teste", command=lambda: ordenar_coluna("ID do teste", False))
    tree.heading("ID do usuário", text="ID do usuário", command=lambda: ordenar_coluna("ID do usuário", False))
    tree.heading("Nome", text="Nome", command=lambda: ordenar_coluna("Nome", False))
    tree.heading("Matrícula", text="Matrícula", command=lambda: ordenar_coluna("Matrícula", False))
    tree.heading("Setor", text="Setor", command=lambda: ordenar_coluna("Setor", False))
    tree.heading("Data e hora", text="Data e hora", command=lambda: ordenar_coluna("Data e hora", True))
    tree.heading("Quantidade de Álcool", text="Qtd. Álcool", command=lambda: ordenar_coluna("Quantidade de Álcool", False))
    tree.heading("Status", text="Status", command=lambda: ordenar_coluna("Status", False))

    # Ajustar larguras das colunas
    tree.column("ID do teste", width=70, minwidth=70)
    tree.column("ID do usuário", width=100, minwidth=100)
    tree.column("Nome", width=120, minwidth=120)
    tree.column("Matrícula", width=100, minwidth=100)
    tree.column("Setor", width=100, minwidth=100)
    tree.column("Data e hora", width=140, minwidth=140)
    tree.column("Quantidade de Álcool", width=100, minwidth=100)
    tree.column("Status", width=80, minwidth=80)

    # Configuração do Scrollbar Vertical
    scrollbar_y.config(command=tree.yview)
    scrollbar_y.pack(side="right", fill="y")

    # Configuração do Scrollbar Horizontal
    scrollbar_x.config(command=tree.xview)
    scrollbar_x.pack(side="bottom", fill="x")

    # Adicionar Treeview
    tree.pack(fill="both", expand=True)

    def carregar_resultados():
        tree.delete(*tree.get_children())  # Limpa a lista
        if not os.path.exists(ARQUIVO_RESULTADOS):
            return
        with open(ARQUIVO_RESULTADOS, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Adiciona à lista com as colunas separadas
                tree.insert(
                    "", "end",
                    values=(
                        row["ID do teste"],
                        row["ID do usuário"],
                        row["Nome"],
                        row["Matrícula"],
                        row["Setor"],
                        row["Data e hora"],
                        row["Quantidade de Álcool"],
                        row["Status"],
                    )
                )

    carregar_resultados()

    

    def ordenar_coluna(coluna, numerica=False):
        global ordem_atual

        # Alterna a direção da ordenação
        if ordem_atual["coluna"] == coluna:
            ordem_atual["direcao"] = not ordem_atual["direcao"]
        else:
            ordem_atual["coluna"] = coluna
            ordem_atual["direcao"] = True  # Começa sempre como crescente

        # Ordena os dados
        dados = [(tree.set(k, coluna), k) for k in tree.get_children("")]
        if numerica:
            dados.sort(key=lambda t: int(t[0]) if t[0].isdigit() else 0, reverse=not ordem_atual["direcao"])
        else:
            dados.sort(key=lambda t: t[0], reverse=not ordem_atual["direcao"])

        # Reorganiza as linhas
        for index, (_, k) in enumerate(dados):
            tree.move(k, "", index)

        # Atualiza os cabeçalhos com a seta de ordenação
        for col in tree["columns"]:
            texto = col
            if col == coluna:
                texto += " ▲" if ordem_atual["direcao"] else " ▼"
            tree.heading(col, text=texto, command=lambda c=col: ordenar_coluna(c, c in ["ID do teste", "ID do usuário"]))

    # Frame para os botões
    frame_esquerda = tk.Frame(resultados_root)
    frame_esquerda.pack(side="left", fill="y", padx=10, pady=10)
    
    def salvar_lista_como_pdf(tree):
        try:
            # Obter o caminho para salvar o arquivo
            caminho_arquivo = fd.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")],
                title="Salvar como PDF",
                initialfile="Registros EBS010"
            )
            if not caminho_arquivo:
                return  # O usuário cancelou a ação

            # Configuração do PDF (paisagem para mais espaço horizontal)
            c = canvas.Canvas(caminho_arquivo, pagesize=landscape(letter))
            largura, altura = landscape(letter)

            # Título do PDF
            c.setFont("Helvetica-Bold", 16)
            c.drawString(30, altura - 40, "Registros de Resultados EBS010")

            # Cabeçalhos das colunas
            colunas = ["ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor", "Data e hora", "Qtd. Álcool", "Status"]
            larguras_colunas = [60, 80, 100, 90, 90, 160, 90, 80]  # Ajustar tamanhos das colunas
            c.setFont("Helvetica-Bold", 10)
            y = altura - 70  # Início da tabela
            x_inicial = 30

            for i, coluna in enumerate(colunas):
                c.drawString(x_inicial, y, coluna)
                x_inicial += larguras_colunas[i]

            # Dados do Treeview
            c.setFont("Helvetica", 10)
            y -= 20  # Ajusta a posição inicial para os dados
            for item in tree.get_children():
                valores = tree.item(item)["values"]
                x_inicial = 30  # Reinicia a posição X para cada linha
                for i, valor in enumerate(valores):
                    c.drawString(x_inicial, y, str(valor))
                    x_inicial += larguras_colunas[i]
                y -= 20  # Move para a próxima linha

                # Adiciona uma nova página se o espaço acabar
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica-Bold", 10)
                    y = altura - 70
                    x_inicial = 30
                    for i, coluna in enumerate(colunas):
                        c.drawString(x_inicial, y, coluna)
                        x_inicial += larguras_colunas[i]
                    c.setFont("Helvetica", 10)
                    y -= 20

            # Salvar e fechar o PDF
            c.save()
            messagebox.showinfo("Sucesso", "O arquivo PDF foi salvo com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o PDF: {e}")
    
    # Função para salvar em Excel
    def salvar_excel():
        caminho_arquivo = fd.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Arquivos Excel", "*.xlsx")],
            title="Salvar em Excel",
            initialfile="Registros EBS010"
        )
        if not caminho_arquivo:
            return  # O usuário cancelou a ação

        # Coletar dados do Treeview
        rows = [tree.item(item)["values"] for item in tree.get_children()]
        colunas = [
            "ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor", "Data e hora", "Qtd. Álcool", "Status"
        ]

        # Criar o DataFrame
        df = pd.DataFrame(rows, columns=colunas)

        # Alterar a formatação da coluna "Data e hora"
        if "Data e hora" in df.columns:
            df["Data e hora"] = df["Data e hora"].apply(
                lambda x: datetime.strptime(x, "%Y-%m-%d %H:%M:%S").strftime("%d/%m/%y %H:%M:%S") if isinstance(x, str) else x
            )

        # Salvar o DataFrame em Excel com ajuste de largura
        try:
            with pd.ExcelWriter(caminho_arquivo, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Resultados")
                worksheet = writer.sheets["Resultados"]

                # Auto ajustar as colunas no Excel
                for column_cells in worksheet.columns:
                    max_length = 0
                    column = column_cells[0].column_letter  # Letra da coluna no Excel
                    for cell in column_cells:
                        try:
                            if cell.value:
                                max_length = max(max_length, len(str(cell.value)))
                        except:
                            pass
                    adjusted_width = max_length + 2  # Espaço extra para melhor visualização
                    worksheet.column_dimensions[column].width = adjusted_width

            messagebox.showinfo("Sucesso", "Resultados salvos com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar o Excel: {e}")

    tk.Button(frame_esquerda, text="Salvar em PDF", command=lambda: salvar_lista_como_pdf(tree), width=20).pack(pady=5)
    tk.Button(frame_esquerda, text="Salvar em Excel", command=lambda: salvar_excel(), width=20).pack(pady=5)
    tk.Button(frame_esquerda, text="Fechar", command=resultados_root.destroy, width=20).pack(pady=5)

    # Campos de pesquisa
    frame_pesquisa = tk.Frame(resultados_root)
    frame_pesquisa.pack(side="top", fill="x", padx=10, pady=10)

    # Período
    periodo_todos = tk.BooleanVar(value=True)
    tk.Checkbutton(frame_pesquisa, text="Todas as datas", variable=periodo_todos).grid(row=0, column=0, padx=5)
    tk.Label(frame_pesquisa, text="De:").grid(row=0, column=1)

    # Configuração para exibir DD/MM/YY
    data_inicial = DateEntry(frame_pesquisa, width=12, state="disabled", date_pattern="dd/MM/yyyy")
    data_inicial.grid(row=0, column=2)

    tk.Label(frame_pesquisa, text="Até:").grid(row=0, column=3)
    data_final = DateEntry(frame_pesquisa, width=12, state="disabled", date_pattern="dd/MM/yyyy")
    data_final.grid(row=0, column=4)

    # Ativar/desativar campos de data
    def toggle_datas():
        estado = "normal" if not periodo_todos.get() else "disabled"
        data_inicial.configure(state=estado)
        data_final.configure(state=estado)

    periodo_todos.trace_add("write", lambda *args: toggle_datas())
    
    # ID do usuário
    frame_id = tk.Frame(frame_pesquisa)
    frame_id.grid(row=1, column=0, columnspan=5, pady=5)
    tk.Label(frame_id, text="Usuário (ID):").pack(side="left", padx=5)
    lista_usuarios = ttk.Combobox(frame_id, values=[], state="readonly", width=20)
    lista_usuarios.pack(side="left", padx=5)

    def carregar_usuarios():
        if not os.path.exists("registros.csv"):
            return
        with open("registros.csv", mode="r", newline="") as file:
            reader = csv.DictReader(file)
            usuarios = [f"{row['ID']} - {row['Nome']}" for row in reader]
            lista_usuarios["values"] = usuarios

    carregar_usuarios()

    # Checkbox para "Todos os Usuários"
    todos_usuarios = tk.BooleanVar(value=True)

    # Função para habilitar/desabilitar o Combobox de usuários
    def toggle_usuarios():
        if todos_usuarios.get():
            lista_usuarios.set("")  # Limpa a seleção
            lista_usuarios.configure(state="disabled")  # Desabilita o Combobox
        else:
            lista_usuarios.configure(state="normal")  # Habilita o Combobox

    # Atualiza o estado inicial do Combobox de usuários
    toggle_usuarios()

    
    tk.Checkbutton(frame_id, text="Todos os usuários", variable=todos_usuarios, command=toggle_usuarios).pack(side="left", padx=5)

    # Resultado
    frame_resultado = tk.Frame(frame_pesquisa)
    frame_resultado.grid(row=2, column=0, columnspan=5, pady=5)
    tk.Label(frame_resultado, text="Resultado:").pack(side="left", padx=5)
    resultado_opcoes = tk.StringVar(value="Todos")
    tk.Radiobutton(frame_resultado, text="Todos resultados", variable=resultado_opcoes, value="Todos").pack(side="left", padx=5)
    tk.Radiobutton(frame_resultado, text="Aprovados", variable=resultado_opcoes, value="Aprovados").pack(side="left", padx=5)
    tk.Radiobutton(frame_resultado, text="Rejeitados", variable=resultado_opcoes, value="Rejeitados").pack(side="left", padx=5)

    def aplicar_filtros():
        tree.delete(*tree.get_children())  # Limpa o Treeview
        if not os.path.exists(ARQUIVO_RESULTADOS):
            return

        with open(ARQUIVO_RESULTADOS, mode="r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Filtro por data
                if not periodo_todos.get():
                    data_teste = datetime.strptime(row["Data e hora"], "%Y-%m-%d %H:%M:%S")
                    if data_inicial.get_date() > data_teste.date() or data_final.get_date() < data_teste.date():
                        continue

                # Filtro por usuário
                if not todos_usuarios.get() and lista_usuarios.get() and not lista_usuarios.get().startswith(row["ID do usuário"]):
                    continue

                # Filtro por resultado
                if resultado_opcoes.get() == "Aprovados" and row["Status"] != "Aprovado":
                    continue
                if resultado_opcoes.get() == "Rejeitados" and row["Status"] != "Rejeitado":
                    continue

                # Adiciona o resultado ao Treeview
                tree.insert(
                    "",
                    "end",
                    values=(
                        row["ID do teste"],
                        row["ID do usuário"],
                        row["Nome"],
                        row["Matrícula"],
                        row["Setor"],
                        row["Data e hora"],
                        row["Quantidade de Álcool"],
                        row["Status"],
                    )
                )

    tk.Button(frame_pesquisa, text="Pesquisar", command=aplicar_filtros).grid(row=3, column=0, columnspan=5, pady=10)

    resultados_root.mainloop()

    

# Para executar como standalone
if __name__ == "__main__":
    iniciar_resultados()
