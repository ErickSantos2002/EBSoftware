# EBSoftware SDK

O **EBSoftware SDK** foi desenvolvido para facilitar a integração com o software EBS-010. Este SDK permite que os usuários interajam diretamente com o banco de dados local, executem testes, configurem dispositivos, gerenciem cadastros e obtenham resultados de forma eficiente.

## Estrutura do SDK

### Módulos Principais

#### 1. `cadastros`
Gerenciamento de cadastros de usuários.

- **Métodos**:
  - `add_record(name, registration, department)`: Adiciona um novo cadastro.
  - `get_all_records()`: Retorna todos os cadastros.
  - `delete_record(record_id)`: Remove um cadastro pelo ID.
  - `import_from_excel(file_path)`: Importa cadastros de um arquivo Excel.
  - `export_to_excel(file_path)`: Exporta cadastros para um arquivo Excel.

#### 2. `config`
Configuração do dispositivo.

- **Métodos**:
  - `set_serial_port(port)`: Define manualmente a porta serial.
  - `get_serial_port()`: Obtém a porta serial configurada.
  - `auto_detect_port()`: Detecta automaticamente a porta do dispositivo.

#### 3. `device`
Interação direta com o dispositivo.

- **Métodos**:
  - `get_device_info()`: Obtém informações do dispositivo.

#### 4. `results`
Gerenciamento de resultados armazenados.

- **Métodos**:
  - `get_all_results()`: Retorna todos os resultados.
  - `get_results_by_date(start_date, end_date)`: Retorna resultados filtrados por data.
  - `export_to_excel(file_path)`: Exporta resultados para um arquivo Excel.
  - `export_to_pdf(file_path)`: Exporta resultados para um arquivo PDF.
  - `save_result(user_id, name, registration, department, alcohol_level, status)`: Salva um novo resultado no banco de dados.

#### 5. `tests`
Execução de testes automáticos ou manuais.

- **Métodos**:
  - `start_manual_test(user_id, name, registration, department, callback)`: Inicia um teste manual.
  - `start_auto_test(callback)`: Inicia testes automáticos.
  - `stop_tests()`: Interrompe os testes em execução.

## Exemplo de Uso

O SDK acompanha exemplos na pasta `Examples`. Abaixo estão alguns exemplos de utilização.

### Gerenciamento de Cadastros
Arquivo: `manage_cadastros.py`
```python
from ebs010_sdk.cadastros import CadastrosManager

manager = CadastrosManager()

# Adiciona um novo registro
record_id = manager.add_record("João Silva", "12345", "RH")
print(f"Registro adicionado com ID: {record_id}")

# Lista todos os cadastros
records = manager.get_all_records()
print("Cadastros:", records)

# Exporta cadastros para Excel
manager.export_to_excel("cadastros_export.xlsx")

# Importa cadastros de um arquivo Excel
manager.import_from_excel("cadastros_import.xlsx")

# Remove um cadastro
manager.delete_record(record_id)
```

### Configuração do Dispositivo
Arquivo: `manage_config.py`
```python
from ebs010_sdk.config import ConfigManager

manager = ConfigManager()

# Define a porta serial manualmente
manager.set_serial_port("COM3")

# Obtém a porta configurada
print(manager.get_serial_port())

# Detecta a porta automaticamente
manager.auto_detect_port()
```

### Interação com o Dispositivo
Arquivo: `manage_device.py`
```python
from ebs010_sdk.device import DeviceManager

device_manager = DeviceManager()

# Obtém informações do dispositivo
info = device_manager.get_device_info()
print("Informações do dispositivo:", info)
```

### Gerenciamento de Resultados
Arquivo: `manage_results.py`
```python
from ebs010_sdk.results import ResultsManager

manager = ResultsManager()

# Obtém todos os resultados
all_results = manager.get_all_results()
print(all_results)

# Filtra resultados por data
filtered_results = manager.get_results_by_date("2024-01-01", "2025-01-06")
print(filtered_results)

# Exporta resultados
manager.export_to_excel("resultados.xlsx")
manager.export_to_pdf("resultados.pdf")
```

### Execução de Testes
Arquivo: `manage_tests.py`
```python
from ebs010_sdk.tests import TestsManager
import time

def callback(result):
    print(f"Resultado do teste: {result}")

manager = TestsManager()

# Teste manual
manager.start_manual_test(user_id=1, name="João Silva", registration="12345", department="TI", callback=callback)
time.sleep(10)  # Simula tempo de execução
manager.stop_tests()

# Testes automáticos
manager.start_auto_test(callback=callback)
time.sleep(15)  # Simula tempo de execução
manager.stop_tests()
```

## Requisitos

Crie um arquivo `requirements.txt` com as seguintes dependências:
```
openpyxl
pandas
PyQt5
pyserial
reportlab
```

Instale-as utilizando:
```bash
pip install -r requirements.txt
```

## Observações
- O SDK só funcionará se estiver na mesma estrutura de pastas do software principal, onde a pasta `resources` e o banco de dados local estão localizados.
- Certifique-se de que todas as dependências estão instaladas e que a porta serial esteja corretamente configurada.

## Licença
Consulte o arquivo LICENSE para mais informações.
