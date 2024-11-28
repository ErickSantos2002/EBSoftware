import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk  # Biblioteca Pillow para redimensionar imagens
import subprocess  # Para executar o registros.py

def iniciar_interface():
    # Criação da janela principal
    root = tk.Tk()
    root.title("EBS-010 Interface")
    root.geometry("800x600")  # Tamanho da janela
    root.resizable(False, False)

    # Redimensionar a imagem de fundo
    original_image = Image.open("Logo.png")  # Carrega a imagem original
    resized_image = original_image.resize((800, 600))  # Redimensiona a imagem
    background_image = ImageTk.PhotoImage(resized_image)

    # Adiciona o fundo redimensionado
    background_label = tk.Label(root, image=background_image)
    background_label.place(relwidth=1, relheight=1)

    # Funções para os botões
    def abrir_registros():
        try:
            subprocess.Popen(["python", "registros.py"])  # Executa o arquivo registros.py
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir Registros.\n{e}")

    def abrir_testes():
        try:
            subprocess.Popen(["python", "Testes.py"])  # Executa o arquivo registros.py
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir Testes.\n{e}")

    def abrir_resultados():
        try:
            subprocess.Popen(["python", "Resultados.py"])  # Executa o arquivo Resultados.py
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir Resultados.\n{e}")

    def abrir_configuracoes():
        try:
            subprocess.Popen(["python", "Configuracoes.py"])  # Executa o arquivo Configurações.py
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir Configurações.\n{e}")

    def salvar_arquivo():
        messagebox.showinfo("Salvar", "Funcionalidade de Salvar!")

    # Criação dos botões na parte superior
    frame_top = tk.Frame(root, bg="#ccc", height=50)
    frame_top.pack(fill="x")

    botao_registros = tk.Button(frame_top, text="Registros", command=abrir_registros, width=15)
    botao_registros.pack(side="left", padx=5, pady=5)

    botao_testes = tk.Button(frame_top, text="Testes", command=abrir_testes, width=15)
    botao_testes.pack(side="left", padx=5, pady=5)

    botao_resultados = tk.Button(frame_top, text="Resultados", command=abrir_resultados, width=15)
    botao_resultados.pack(side="left", padx=5, pady=5)

    botao_configuracoes = tk.Button(frame_top, text="Configurações", command=abrir_configuracoes, width=15)
    botao_configuracoes.pack(side="left", padx=5, pady=5)

    botao_salvar = tk.Button(frame_top, text="Salvar", command=salvar_arquivo, width=15)
    botao_salvar.pack(side="left", padx=5, pady=5)

    # Mantém a janela aberta
    root.mainloop()
