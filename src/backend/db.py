import sqlite3
import os

# Diretório do banco de dados
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DB_PATH = os.path.join(BASE_DIR, "resources", "database.db")

def conectar():
    """Conecta ao banco de dados SQLite."""
    return sqlite3.connect(DB_PATH)

def inicializar_db():
    """Inicializa o banco de dados criando tabelas se necessário."""
    with conectar() as conn:
        cursor = conn.cursor()
        
        # Tabela de Cadastros
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cadastros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            matricula TEXT UNIQUE NOT NULL,
            setor TEXT
        )
        """)
        
        # Tabela de Resultados
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS resultados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_usuario INTEGER,
            nome TEXT,
            matricula TEXT,
            setor TEXT,
            data_hora TEXT NOT NULL,
            quantidade_alcool REAL,
            status TEXT,
            FOREIGN KEY (id_usuario) REFERENCES registros (id)
        )
        """)
        conn.commit()

# Inicializa o banco de dados automaticamente ao carregar o módulo
if not os.path.exists(DB_PATH):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    inicializar_db()
