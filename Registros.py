import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os

# Nome do arquivo CSV
ARQUIVO_CSV = "registros.csv"

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
    registros_root.geometry("800x400")  # Tamanho da janela
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

    # Layout do lado esquerdo
    frame_esquerdo = tk.Frame(registros_root)
    frame_esquerdo.pack(side="left", fill="y", padx=10, pady=10)

    # Tabela para exibir os registros
    tree = ttk.Treeview(frame_esquerdo, columns=("ID", "Nome", "Matricula", "Setor"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Nome", text="Nome")
    tree.heading("Matricula", text="Matrícula")
    tree.heading("Setor", text="Setor")
    tree.column("ID", width=50)
    tree.column("Nome", width=150)
    tree.column("Matricula", width=100)
    tree.column("Setor", width=100)
    tree.pack(fill="both", expand=True)

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

    # Atualiza a lista ao iniciar
    atualizar_lista()

    # Mantém a janela aberta
    registros_root.mainloop()

# Executa apenas se o arquivo for chamado diretamente
if __name__ == "__main__":
    iniciar_registros()
