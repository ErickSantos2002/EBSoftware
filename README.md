# EBS-010 Software

## Descrição
O EBS-010 é um software desenvolvido para gerenciar dispositivos de teste de álcool com foco em segurança no trabalho. Ele utiliza comunicação serial para se conectar a dispositivos de medição, gerencia cadastros e resultados, e oferece uma interface gráfica amigável construída com PyQt5.

## Funcionalidades

### Principais Recursos:
1. **Gestão de Cadastros**:
   - Cadastrar, editar e apagar usuários.
   - Importar e exportar cadastros em formato Excel.
   - Interface intuitiva para gerenciamento.

2. **Execução de Testes**:
   - Testes manuais e automáticos com suporte a conexão serial.
   - Controle de execução e interrupção de testes.
   - Armazenamento de resultados no banco de dados SQLite.

3. **Gestão de Resultados**:
   - Visualização de resultados com filtros por data, usuário e status.
   - Exportação dos resultados em formatos Excel e PDF.

4. **Configurações**:
   - Configuração da porta serial utilizada pelo dispositivo.
   - Detecção automática de portas compatíveis.

5. **Informações do Aparelho**:
   - Consulta e armazenamento de limites e informações do dispositivo.

## Requisitos

### Sistema Operacional
- Windows, macOS ou Linux.

### Dependências
- Python 3.8+
- PyQt5
- pandas
- openpyxl
- reportlab
- sqlite3
- pyserial

### Instalação de Dependências
Instale as dependências utilizando o comando:
```bash
pip install -r requirements.txt
```

## Estrutura do Projeto

```
EBS-010
├── main.py                # Ponto de entrada principal.
├── src/
│   ├── backend/
│   │   ├── Cadastros.py  # Lógica de gestão de cadastros.
│   │   ├── Configuracoes.py # Configuração da porta serial.
│   │   ├── db.py         # Inicialização e conexão com SQLite.
│   │   ├── Informacoes.py # Consulta e armazenamento de informações do dispositivo.
│   │   ├── Resultados.py # Manipulação e exportação de resultados.
│   │   └── Teste.py      # Execução de testes e comunicação serial.
│   ├── frontend/
│       ├── Cadastros_Tela.py # Interface de gestão de cadastros.
│       ├── Configuracoes_Tela.py # Interface de configuração.
│       ├── Informacoes_Tela.py # Interface de informações do aparelho.
│       ├── Resultados_Tela.py # Interface de visualização de resultados.
│       ├── Testes_Tela.py # Interface de execução de testes.
│       └── Interface.py  # Janela principal do aplicativo.
├── resources/            # Diretório de recursos (imagens, banco de dados, etc).
│   ├── database.db       # Arquivo SQLite.
│   ├── config.ini        # Configurações de porta serial.
│   └── info.ini          # Informações do dispositivo.
├── requirements.txt      # Lista de dependências.
└── README.md             # Documentação.
```

## Uso

### Executando o Software
1. Clone este repositório:
   ```bash
   git clone <repository-url>
   cd EBS-010
   ```

2. Certifique-se de que o Python está instalado e as dependências configuradas.

3. Execute o programa:
   ```bash
   python main.py
   ```

### Configuração da Porta Serial
1. Acesse o menu de configurações no software.
2. Selecione uma porta manualmente ou utilize a busca automática.

### Execução de Testes
1. Escolha entre teste manual ou automático na interface principal.
2. Acompanhe os resultados em tempo real.

### Exportação de Resultados
1. Use a interface de resultados para filtrar e visualizar os registros.
2. Exporte os resultados em formato Excel ou PDF conforme necessário.

## Contribuindo
Contribuições são bem-vindas! Siga os passos abaixo:
1. Faça um fork deste repositório.
2. Crie uma branch para sua feature ou correção de bug:
   ```bash
   git checkout -b minha-branch
   ```
3. Envie suas alterações:
   ```bash
   git commit -m "Minha contribuição"
   git push origin minha-branch
   ```
4. Abra um Pull Request no GitHub.

## Licença
Este projeto é licenciado sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
