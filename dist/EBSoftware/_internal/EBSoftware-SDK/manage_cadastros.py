import sys
import os

# Adiciona o caminho do SDK ao PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ebs010_sdk.cadastros import CadastrosManager

# Inicializa o gerenciador de cadastros
manager = CadastrosManager()

# Adiciona um novo registro
record_id = manager.add_record("João Silva", "12345", "RH")
print(f"Registro adicionado com ID: {record_id}")

# Lista todos os cadastros
records = manager.get_all_records()
print("Cadastros:", records)

# Exporta para Excel
export_path = os.path.join(os.getcwd(), "cadastros_export.xlsx")
manager.export_to_excel(export_path)
print(f"Cadastros exportados para: {export_path}")

# Importa de um Excel
imported_records = manager.import_from_excel("cadastros_import.xlsx")
print(f"Registros importados: {imported_records}")

# Remove um registro
manager.delete_record(record_id)
print(f"Registro com ID {record_id} excluído.")
