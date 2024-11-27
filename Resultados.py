import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog as fd
import csv
import pandas as pd
from datetime import datetime
from tkcalendar import DateEntry
import os

ARQUIVO_RESULTADOS = "Resultados.csv"

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

    # Função para ordenar colunas
    def ordenar_coluna(coluna, is_data):
        registros = [(tree.item(item)["values"], item) for item in tree.get_children()]
        if is_data:  # Ordena por data
            registros.sort(key=lambda x: datetime.strptime(str(x[0][5]), "%Y-%m-%d %H:%M:%S"))
        else:  # Ordena por texto ou número, convertendo para string para evitar erros
            registros.sort(key=lambda x: str(x[0][tree["columns"].index(coluna)]))

        # Reinsere os itens na nova ordem
        for i, (values, item) in enumerate(registros):
            tree.move(item, "", i)

    # Frame para os botões
    frame_esquerda = tk.Frame(resultados_root)
    frame_esquerda.pack(side="left", fill="y", padx=10, pady=10)

    tk.Button(frame_esquerda, text="Imprimir", command=lambda: messagebox.showinfo("Imprimir", "Funcionalidade de impressão em desenvolvimento!"), width=20).pack(pady=5)
    tk.Button(frame_esquerda, text="Salvar em Excel", command=lambda: salvar_excel(), width=20).pack(pady=5)
    tk.Button(frame_esquerda, text="Fechar", command=resultados_root.destroy, width=20).pack(pady=5)

    # Campos de pesquisa
    frame_pesquisa = tk.Frame(resultados_root)
    frame_pesquisa.pack(side="top", fill="x", padx=10, pady=10)

    # Período
    periodo_todos = tk.BooleanVar(value=True)
    tk.Checkbutton(frame_pesquisa, text="Todas as datas", variable=periodo_todos).grid(row=0, column=0, padx=5)
    tk.Label(frame_pesquisa, text="De:").grid(row=0, column=1)
    data_inicial = DateEntry(frame_pesquisa, width=12, state="disabled")
    data_inicial.grid(row=0, column=2)
    tk.Label(frame_pesquisa, text="Até:").grid(row=0, column=3)
    data_final = DateEntry(frame_pesquisa, width=12, state="disabled")
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
    tk.Label(frame_id, text="Usuário:").pack(side="left", padx=5)
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

    # Resultado
    frame_resultado = tk.Frame(frame_pesquisa)
    frame_resultado.grid(row=2, column=0, columnspan=5, pady=5)
    tk.Label(frame_resultado, text="Resultado:").pack(side="left", padx=5)
    resultado_opcoes = tk.StringVar(value="Todos")
    tk.Radiobutton(frame_resultado, text="Todos resultados", variable=resultado_opcoes, value="Todos").pack(side="left", padx=5)
    tk.Radiobutton(frame_resultado, text="Aprovados", variable=resultado_opcoes, value="Aprovados").pack(side="left", padx=5)
    tk.Radiobutton(frame_resultado, text="Reprovados", variable=resultado_opcoes, value="Reprovados").pack(side="left", padx=5)

    # Função para aplicar os filtros
    def aplicar_filtros():
        tree.delete(*tree.get_children())
        if not os.path.exists(ARQUIVO_RESULTADOS):
            return

        with open(ARQUIVO_RESULTADOS, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Filtro por data
                if not periodo_todos.get():
                    data_teste = datetime.strptime(row["Data e hora"], "%Y-%m-%d %H:%M:%S")
                    if data_inicial.get_date() > data_teste.date() or data_final.get_date() < data_teste.date():
                        continue

                # Filtro por usuário
                if lista_usuarios.get() and not lista_usuarios.get().startswith(row["ID do usuário"]):
                    continue

                # Filtro por resultado
                if resultado_opcoes.get() == "Aprovados" and "OK" not in row["Resultado do teste de álcool"]:
                    continue
                if resultado_opcoes.get() == "Reprovados" and "HIGH" not in row["Resultado do teste de álcool"]:
                    continue

                tree.insert("", "end", values=(row["ID do teste"], row["ID do usuário"], row["Nome"], row["Matrícula"], row["Setor"], row["Data e hora"]))

    tk.Button(frame_pesquisa, text="Pesquisar", command=aplicar_filtros).grid(row=3, column=0, columnspan=5, pady=10)

    # Função para salvar em Excel
    def salvar_excel():
        caminho_arquivo = fd.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Arquivos Excel", "*.xlsx")], title="Salvar em Excel")
        if not caminho_arquivo:
            return
        rows = [tree.item(item)["values"] for item in tree.get_children()]
        colunas = ["ID do teste", "ID do usuário", "Nome", "Matrícula", "Setor", "Data e hora"]
        df = pd.DataFrame(rows, columns=colunas)
        df.to_excel(caminho_arquivo, index=False)
        messagebox.showinfo("Sucesso", "Resultados salvos com sucesso!")

    resultados_root.mainloop()

# Para executar como standalone
if __name__ == "__main__":
    iniciar_resultados()
