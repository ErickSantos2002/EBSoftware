import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
import tkinter.filedialog as fd
import pandas as pd

# Nome do arquivo CSV
ARQUIVO_CSV = "registros.csv"
ordem_atual = {"coluna": None, "direcao": True}  # Por padrão, crescente (True

# Função para carregar os registros do CSV
def carregar_registros():
    if not os.path.exists(ARQUIVO_CSV):
        return []
    with open(ARQUIVO_CSV, mode="r", newline="") as file:
        reader = csv.DictReader(file)
        return list(reader)


# Função para salvar os registros no CSV
def salvar_registros(registros):
    with open(ARQUIVO_CSV, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["ID", "Nome", "Matricula", "Setor"])
        writer.writeheader()
        writer.writerows(registros)

# Função para iniciar a interface de registros
def iniciar_registros():
    registros_root = tk.Tk()
    registros_root.title("Cadastro de Registros")
    registros_root.geometry("1000x500")  # Tamanho da janela
    registros_root.resizable(False, False)

    # Lista de registros
    registros = carregar_registros()

    # Função para obter o próximo ID baseado no maior valor existente
    def proximo_id():
        if not registros:  # Se a lista estiver vazia, retorna 1
            return "1"
        maior_id = max(int(r["ID"]) for r in registros)  # Busca o maior ID existente
        return str(maior_id + 1)  # Incrementa o maior ID

    # Atualiza a lista exibida
    def atualizar_lista():
        tree.delete(*tree.get_children())
        for registro in registros:
            tree.insert("", "end", values=(registro["ID"], registro["Nome"], registro["Matricula"], registro["Setor"]))

    # Verifica se a matrícula é única
    def matricula_unica(matricula):
        return all(registro["Matricula"] != matricula for registro in registros)

    # Adiciona um novo registro
    def salvar_registro():
        nome = entrada_nome.get().strip()
        matricula = entrada_matricula.get().strip()
        setor = entrada_setor.get().strip()

        if not nome or not matricula:
            messagebox.showerror("Erro", "Os campos Nome e Matrícula são obrigatórios!")
            return

        if not matricula_unica(matricula):
            messagebox.showerror("Erro", "Matrícula já cadastrada!")
            return

        novo_registro = {
            "ID": proximo_id(),
            "Nome": nome,
            "Matricula": matricula,
            "Setor": setor
        }
        registros.append(novo_registro)
        salvar_registros(registros)
        atualizar_lista()

        entrada_nome.delete(0, tk.END)
        entrada_matricula.delete(0, tk.END)
        entrada_setor.delete(0, tk.END)

    # Remove os registros selecionados
    def apagar_registro():
        selecionados = tree.selection()
        if not selecionados:
            messagebox.showerror("Erro", "Nenhum registro selecionado!")
            return

        # Obtém os IDs dos registros selecionados e converte para strings
        ids_selecionados = [str(tree.item(item)["values"][0]) for item in selecionados]

        # Remove os registros correspondentes aos IDs selecionados
        nonlocal registros  # Permite modificar a lista de registros no escopo externo
        registros = [r for r in registros if str(r["ID"]) not in ids_selecionados]

        # Atualiza o arquivo CSV
        try:
            with open(ARQUIVO_CSV, mode="w", newline="") as file:
                writer = csv.DictWriter(file, fieldnames=["ID", "Nome", "Matricula", "Setor"])
                writer.writeheader()
                writer.writerows(registros)  # Escreve os registros restantes no arquivo
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível atualizar o arquivo CSV: {e}")
            return

        # Atualiza a exibição
        atualizar_lista()

        # Exibe mensagem de sucesso
        messagebox.showinfo("Sucesso", "Registros apagados com sucesso!")

    # Função para importar usuários de um arquivo Excel
    def importar_excel():
        # Abrir uma janela para selecionar o arquivo Excel
        caminho_arquivo = fd.askopenfilename(
            title="Selecione um arquivo Excel",
            filetypes=(("Arquivos Excel", "*.xlsx"), ("Todos os arquivos", "*.*"))
        )
        if not caminho_arquivo:
            return  # Caso o usuário cancele a seleção

        try:
            # Ler o arquivo Excel
            dados = pd.read_excel(caminho_arquivo, dtype=str)

            # Substituir valores NaN por strings vazias
            dados.fillna("", inplace=True)

            # Verificar se as colunas obrigatórias existem
            if not {"Nome", "Matricula", "Setor"}.issubset(dados.columns):
                messagebox.showerror("Erro", "O arquivo deve conter as colunas: Nome, Matricula e Setor!")
                return

            # Processar cada linha do Excel
            novos_registros = []
            erros = []
            for _, linha in dados.iterrows():
                nome = str(linha["Nome"]).strip()
                matricula = str(linha["Matricula"]).strip()
                setor = str(linha.get("Setor", "")).strip()  # Setor é opcional

                # Validar campos obrigatórios
                if not nome or not matricula:
                    erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Nome ou Matrícula ausente"})
                    continue

                # Verificar duplicidade de matrícula
                if not matricula_unica(matricula):
                    erros.append({"Nome": nome, "Matricula": matricula, "Setor": setor, "Erro": "Matrícula duplicada"})
                    continue

                # Criar um novo registro
                novo_registro = {
                    "ID": proximo_id(),
                    "Nome": nome,
                    "Matricula": matricula,
                    "Setor": setor
                }
                registros.append(novo_registro)
                novos_registros.append(novo_registro)

            # Salvar os novos registros no CSV
            salvar_registros(registros)

            # Atualizar a lista exibida
            atualizar_lista()

            # Gerar a planilha com erros (se existirem)
            if erros:
                df_erros = pd.DataFrame(erros)
                caminho_erros = "Erros_Importacao.xlsx"
                df_erros.to_excel(caminho_erros, index=False)

            # Exibir o erro_window com botão "Verificar Erros" se houver erros
            if erros:
                def abrir_erros():
                    os.startfile(caminho_erros)  # Abrir o arquivo Excel com os erros

                # Criar o messagebox personalizado
                erro_window = tk.Toplevel()
                erro_window.title("Resultado da Importação")
                if novos_registros:
                    tk.Label(erro_window, text=f"{len(novos_registros)} usuários foram importados com sucesso!").pack(pady=10)
                else:
                    tk.Label(erro_window, text="Nenhum usuário foi importado.").pack(pady=10)
                tk.Label(erro_window, text=f"{len(erros)} usuários não foram adicionados devido a erros.").pack(pady=10)
                tk.Button(erro_window, text="Verificar Erros", command=lambda: [abrir_erros(), erro_window.destroy()]).pack(pady=5)
                tk.Button(erro_window, text="OK", command=erro_window.destroy).pack(pady=5)
            else:
                # Apenas exibe o número de registros importados com sucesso, sem erros
                messagebox.showinfo("Sucesso", f"{len(novos_registros)} usuários foram importados com sucesso!")

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao importar o arquivo Excel: {e}")

    # Função para salvar o modelo de importação
    def salvar_modelo_excel():
        try:
            # Define os dados do modelo
            colunas = ["Nome", "Matricula", "Setor"]
            modelo_df = pd.DataFrame(columns=colunas)

            # Abrir janela para escolher o local de salvamento com nome padrão
            caminho_arquivo = fd.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Arquivos Excel", "*.xlsx")],
                title="Salvar modelo de importação",
                initialfile="Modelo_Cadastro_EBS.xlsx"  # Nome padrão do arquivo
            )

            if not caminho_arquivo:  # Se o usuário cancelar, não faz nada
                return

            # Salva o arquivo Excel
            modelo_df.to_excel(caminho_arquivo, index=False)

            # Exibe mensagem de sucesso
            messagebox.showinfo("Sucesso", f"O modelo foi salvo em '{caminho_arquivo}'.")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar o modelo: {e}")

    # Variável global para controle da ordenação

    # Função para atualizar a lista exibida
    def atualizar_lista():
        tree.delete(*tree.get_children())
        for registro in registros:
            tree.insert("", "end", values=(registro["ID"], registro["Nome"], registro["Matricula"], registro["Setor"]))

    # Função para ordenar colunas
    def ordenar_coluna(coluna):
        global ordem_atual

        # Alterna a direção da ordenação
        if ordem_atual["coluna"] == coluna:
            ordem_atual["direcao"] = not ordem_atual["direcao"]
        else:
            ordem_atual["coluna"] = coluna
            ordem_atual["direcao"] = True  # Começa sempre como crescente

        # Define o método de ordenação
        if coluna == "ID":
            registros.sort(key=lambda r: int(r["ID"]), reverse=not ordem_atual["direcao"])
        else:
            registros.sort(key=lambda r: r[coluna], reverse=not ordem_atual["direcao"])

        # Atualiza a exibição
        atualizar_lista()

        # Atualiza os cabeçalhos com a seta de ordenação
        for col in tree["columns"]:
            texto = col
            if col == coluna:
                texto += " ▲" if ordem_atual["direcao"] else " ▼"
            tree.heading(col, text=texto, command=lambda c=col: ordenar_coluna(c))

    # Função para pesquisar registros
    def pesquisar_registros(event=None):
        termo = entrada_pesquisa.get().strip().lower()
        if not termo:
            atualizar_lista()  # Se o campo de pesquisa estiver vazio, mostra todos os registros
            return

        # Filtra os registros com base no termo
        registros_filtrados = [
            r for r in registros if
            termo in r["ID"].lower() or
            termo in r["Nome"].lower() or
            termo in r["Matricula"].lower() or
            termo in r["Setor"].lower()
        ]

        # Atualiza a exibição com os registros filtrados
        tree.delete(*tree.get_children())
        for registro in registros_filtrados:
            tree.insert("", "end", values=(registro["ID"], registro["Nome"], registro["Matricula"], registro["Setor"]))


    # Layout do lado esquerdo
    frame_esquerdo = tk.Frame(registros_root)
    frame_esquerdo.pack(side="left", fill="y", padx=10, pady=10)

    # Adicionando a barra de rolagem
    scrollbar_vertical = ttk.Scrollbar(frame_esquerdo, orient="vertical")
    scrollbar_vertical.pack(side="right", fill="y")

    # Campo de pesquisa acima da lista
    frame_pesquisa = tk.Frame(registros_root)
    frame_pesquisa.pack(side="top", fill="x", padx=10, pady=5)

    tk.Label(frame_pesquisa, text="Pesquisar:").pack(side="left")
    entrada_pesquisa = tk.Entry(frame_pesquisa, width=30)
    entrada_pesquisa.pack(side="left", padx=5)
    entrada_pesquisa.bind("<KeyRelease>", pesquisar_registros)  # Atualiza a pesquisa enquanto o usuário digita

    # Configuração inicial da TreeView
    tree = ttk.Treeview(
        frame_esquerdo, 
        columns=("ID", "Nome", "Matricula", "Setor"), 
        show="headings", 
        yscrollcommand=scrollbar_vertical.set
    )
    tree.heading("ID", text="ID", command=lambda: ordenar_coluna("ID"))
    tree.heading("Nome", text="Nome", command=lambda: ordenar_coluna("Nome"))
    tree.heading("Matricula", text="Matricula", command=lambda: ordenar_coluna("Matricula"))
    tree.heading("Setor", text="Setor", command=lambda: ordenar_coluna("Setor"))
    tree.column("ID", width=50, anchor="center")
    tree.column("Nome", width=150)
    tree.column("Matricula", width=100)
    tree.column("Setor", width=100)
    tree.pack(side="left", fill="both", expand=True)

    # Configuração da barra de rolagem para controlar o Treeview
    scrollbar_vertical.config(command=tree.yview)

    # Layout do lado direito
    frame_direito = tk.Frame(registros_root)
    frame_direito.pack(side="right", fill="y", padx=10, pady=10)

    # Campo de Nome
    tk.Label(frame_direito, text="Nome:").pack(pady=5)
    entrada_nome = tk.Entry(frame_direito, width=30)
    entrada_nome.pack(pady=5)

    # Campo de Matrícula
    tk.Label(frame_direito, text="Matrícula:").pack(pady=5)
    entrada_matricula = tk.Entry(frame_direito, width=30)
    entrada_matricula.pack(pady=5)

    # Campo de Setor
    tk.Label(frame_direito, text="Setor (Opcional):").pack(pady=5)
    entrada_setor = tk.Entry(frame_direito, width=30)
    entrada_setor.pack(pady=5)

    # Botões
    tk.Button(frame_direito, text="Salvar", command=salvar_registro, width=20).pack(pady=10)
    tk.Button(frame_direito, text="Apagar", command=apagar_registro, width=20).pack(pady=10)
    tk.Button(frame_direito, text="Fechar", command=registros_root.destroy, width=20).pack(pady=10)
    tk.Button(frame_direito, text="Importar Excel", command=importar_excel, width=20).pack(pady=10)
    tk.Button(frame_direito, text="Salvar Modelo Excel", command=salvar_modelo_excel, width=20).pack(pady=10)

    # Atualiza a lista ao iniciar
    atualizar_lista()

    # Mantém a janela aberta
    registros_root.mainloop()

# Executa apenas se o arquivo for chamado diretamente
if __name__ == "__main__":
    iniciar_registros()
