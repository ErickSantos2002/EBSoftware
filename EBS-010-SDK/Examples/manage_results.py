import sys
import os

# Adiciona o caminho base do SDK
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ebs010_sdk.results import ResultsManager

# Inicializa o gerenciador
manager = ResultsManager()

# Obtém todos os resultados
all_results = manager.get_all_results()
print(all_results)

# Filtra resultados por data
filtered_results = manager.get_results_by_date("2024-01-01", "2025-01-06")
print(filtered_results)

# Exporta para Excel
manager.export_to_excel("resultados.xlsx")

# Exporta para PDF
manager.export_to_pdf("resultados.pdf")