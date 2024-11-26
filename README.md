# Integração do EBS-010 com Python

## Visão Geral
Este projeto demonstra um sistema de comunicação baseado em Python para o dispositivo bafômetro EBS-010. O sistema interage com o bafômetro via USB utilizando um protocolo de comunicação serial, permitindo o envio de comandos e o processamento de respostas para testes de níveis de álcool no sangue.

---

## Funcionalidades
- Envia comandos ao dispositivo EBS-010 para iniciar testes e obter resultados.
- Gerencia diferentes estados do dispositivo, como aquecimento, standby, ativação do gatilho e recuperação de resultados de testes.
- Processa e registra resultados de testes, incluindo níveis de álcool e status do teste (por exemplo, "OK", "HIGH").
- Salva resultados em um arquivo CSV para análise futura.
- Identifica e trata erros como problemas no sensor, erros de fluxo e avisos de bateria baixa.

---

## Requisitos
### Hardware
- **Dispositivo EBS-010**
- Conexão USB com o computador

### Software
- Python 3.8 ou superior
- Bibliotecas:
  - `pyserial`: Para comunicação serial
  - `datetime`: Para registro de data e hora dos resultados
  - `csv`: Para salvar os resultados em um arquivo CSV

Para instalar a biblioteca Python necessária:
```bash
pip install pyserial
```

---

## Protocolo de Comunicação
### Configuração da Porta Serial
| Parâmetro         | Valor           |
|-------------------|-----------------|
| Taxa de Baud      | 4800            |
| Bits de Dados     | 8               |
| Paridade          | Nenhuma         |
| Bits de Parada    | 1               |
| Timeout           | 1 segundo       |

### Comandos
#### Do Computador para o Bafômetro
| Comando          | Descrição                        |
|------------------|----------------------------------|
| `$START 0D 0A`   | Liga o dispositivo bafômetro     |
| `$RESET 0D 0A`   | Desliga o dispositivo bafômetro  |
| `$RECALL 0D 0A`  | Recupera configurações salvas    |

#### Do Bafômetro para o Computador
| Resposta          | Descrição                                      |
|-------------------|------------------------------------------------|
| `$WAIT`           | Dispositivo em aquecimento                    |
| `$STANBY`         | Dispositivo em modo standby                   |
| `$TRIGGER`        | Amostra de ar ativada                         |
| `$BREATH`         | Amostragem de ar correta                      |
| `$RESULT,x.xxx-STATUS` | Resultado do teste, onde `STATUS` é `OK` ou `HIGH` |
| `$FLOW,ERR`       | Erro de fluxo durante a amostragem            |
| `$BAT,LOW`        | Bateria baixa                                 |
| `$SENSOR,ERR`     | Erro no sensor detectado                      |

---

## Implementação Atual
### Funcionalidades
1. **Iniciando o Dispositivo**:
   - Envia o comando `$START` para ativar o bafômetro.
2. **Processando Respostas**:
   - Gerencia respostas como `$WAIT`, `$STANBY`, `$TRIGGER` e `$RESULT`.
   - Registra resultados para níveis de álcool `OK` ou `HIGH`.
3. **Salvando Resultados**:
   - Os resultados são salvos em um arquivo CSV (`resultados.csv`) no seguinte formato:
     ```csv
     Data e Hora, Resposta Bruta, Valor, Status
     2024-11-26 14:23, $RESULT,0.000-OK, 0.000, OK
     2024-11-26 15:01, $RESULT,0.610-HIGH, 0.610, HIGH
     ```
4. **Tratamento de Erros**:
   - Exibe mensagens de erro para problemas como erros de fluxo, bateria baixa ou falhas no sensor.

---

## Como Usar
### Executando o Script
1. Conecte o dispositivo EBS-010 ao computador via USB.
2. Configure a porta correta (por exemplo, `COM3` no Windows ou `/dev/ttyUSB0` no Linux).
3. Execute o script Python:
   ```bash
   python EBS.py
   ```
4. O script irá:
   - Enviar o comando `$START` para o dispositivo.
   - Aguardar as respostas e processar os resultados do teste.
   - Salvar os resultados no arquivo `resultados.csv`.

### Saída do CSV
Os resultados serão adicionados ao arquivo `resultados.csv` no mesmo diretório do script.

---

## Melhorias Futuras
1. **Interface Gráfica do Usuário (GUI):**
   - Criar uma interface amigável utilizando `tkinter` ou `PyQt`.
2. **Registros Aprimorados:**
   - Incluir logs mais detalhados para depuração e trilhas de auditoria.
3. **Integração com Nuvem:**
   - Enviar resultados para um banco de dados remoto ou plataforma para monitoramento centralizado.
4. **Suporte a Multi-Comandos:**
   - Adicionar suporte aos comandos `$RESET` e `$RECALL`.
5. **Configuração Dinâmica:**
   - Permitir que os usuários configurem limites (por exemplo, níveis de álcool pré-definidos) e ajustes de comunicação serial através de um arquivo de configuração.

---

## Contato
Para problemas ou contribuições, entre em contato com o responsável pelo projeto.

---

### Licença
Este projeto está licenciado sob a Licença MIT.

