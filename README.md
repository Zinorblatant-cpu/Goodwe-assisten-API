# ⚡ GoodWe Assistant — Starter (Streamlit + SEMS + Mock)

> **Guia do projeto para você seguir em aula.**  
> Aqui está tudo que você precisa: o que é o SEMS, como funcionam os dados, como rodar o projeto em modo *mock* e em modo *real*, o que editar, como depurar, e quais evoluções fazer (IA e voz).

---

## 1) Objetivo do projeto

- Visualizar, de forma simples, os dados de um **inversor GoodWe** (potência, energia do dia, estado de carga da bateria).  
- Começar **com dados simulados (mock)** para entender a interface e os gráficos.  
- Trocar o *mock* por **dados reais do SEMS Portal** usando a API (com *login* e *token*).  
- Preparar terreno para evoluir: **IA** (texto explicativo) e **voz** (comandos por áudio).

---

## 2) Conceitos essenciais (GoodWe / SEMS)

Antes de ligar qualquer código, entenda estes termos. Eles vão aparecer no app e nas respostas da API.

### 2.1 SEMS Portal
- Plataforma web da **GoodWe** para monitorar plantas fotovoltaicas e dispositivos (inversores, baterias, medidores).  
- O SEMS exibe **plantas** (conjuntos) e, dentro delas, **dispositivos** (por ex. um inversor com um **Serial Number – SN**).

### 2.2 Identificadores
- **Plant ID**: identificador da planta no SEMS (aparece na URL depois que você entra na planta).  
- **Serial Number (SN)** do inversor: está na página de dispositivos/overview.  
- Em muitos endpoints, o parâmetro **`id`** é o **SN** do inversor.

### 2.3 Regiões (hosts)
- O login costuma ser feito em **US** (`https://us.semsportal.com`), mas o retorno pode apontar que os **dados** estão na **EU** (`https://eu.semsportal.com`).  
- No app, escolha **Região de login** (US/EU) e **Região de dados** (EU/US) conforme o seu caso.  
  - Com a conta **demo**, use normalmente **Login = US** e **Dados = EU**.

### 2.4 Autenticação (Token)
1. Envie um **Token inicial** no *header* (é um JSON simples encodado em **Base64**).  
2. Faça `POST /api/v2/common/crosslogin` com `account` e `pwd`.  
3. Na resposta, pegue o campo **`data`**, **encode em Base64** e use esse valor como **Token** em todas as chamadas seguintes.  
4. Chame os endpoints de dados (ex.: `GetInverterDataByColumn`) com esse Token “pós-login”.

### 2.5 Colunas e unidades (exemplos do projeto)
- **`Pac`** (kW): potência AC instantânea do inversor (varia ao longo do dia).  
- **`Eday`** (kWh): energia acumulada gerada no **dia** (cresce de 00:00 até o fim do dia).  
- **`Cbattery1`** (%): estado de carga da bateria (SOC).  
- Outras colunas possíveis em cenários reais: **`Temp`** (temperatura), **`Vac`** (tensão AC), etc.  
- O app já está preparado para receber séries “tempo → valor” e plotar.

### 2.6 Datas / Fuso horário
- O endpoint usado no exemplo aceita `date` no formato **`YYYY-MM-DD HH:MM:SS`**.  
- O SEMS frequentemente devolve horários no formato **`DD/MM/YYYY HH:MM:SS`**.  
- O app converte automaticamente e suporta ambos (usa `dayfirst=True` quando necessário).

---

## 3) Pré-requisitos

- **Python 3.10+**  
- **pip** atualizado  
- (Opcional) **VS Code** com extensão **Python**  
- Internet para usar o modo **Real (SEMS)**

---

## 4) Instalação (passo a passo)

1. Abra um terminal dentro da pasta do projeto `goodwe-assistant`.  
2. (Opcional) Crie e ative um **ambiente virtual**:

   **Windows (PowerShell)**
   ~~~bash
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ~~~

   **macOS / Linux**
   ~~~bash
   python3 -m venv .venv
   source .venv/bin/activate
   ~~~

3. Instale as dependências:
   ~~~bash
   pip install -r requirements.txt
   ~~~

4. Execute o app:
   ~~~bash
   streamlit run app.py
   ~~~
   O navegador abrirá em `http://localhost:8501`.

---

## 5) Estrutura do projeto (o que cada arquivo faz)


### 5.1 `app.py` (interface)
- Mostra os **KPIs**: Energia do dia, Pico de potência, Bateria (início → fim).  
- Exibe **gráficos** (linhas) de `Pac` e `Cbattery1` ao longo do tempo.  
- Alterna entre **Mock** e **Real (SEMS)** no **sidebar**.  
- Em **Real**, chama a API, **extrai série temporal** do JSON e faz **merge por tempo** quando há múltiplas colunas.  
- Se o formato do JSON vier diferente, o app abre um **expander** com a resposta bruta para depurar.

### 5.2 `goodwe_client.py` (API SEMS)
- `crosslogin(account, pwd, region)` → devolve o **Token** (Base64 do `data`).  
- `get_inverter_data_by_column(token, inv_id, column, date, region)` → devolve o **JSON** da coluna pedida (por exemplo `Cbattery1`) para a `date` informada.  
- Use o **SN** do inversor em `inv_id` (o parâmetro chama-se `id` na requisição).

### 5.3 `ai.py` (texto explicativo)
- Recebe os **agregados** (energia total, pico e horário do pico, SOC início e fim) e monta um **texto curto**.  
- Está sem LLM; serve para validar o fluxo. Depois troque por um modelo de IA (OpenAI/Ollama etc.).

### 5.4 `data/mock_today.json` (dados simulados)
- Contém amostras horárias de `Pac`, `Eday` e `Cbattery1` para um dia.  
- Use esse arquivo para praticar a interface sem depender de rede/credenciais.

---

## 6) Como rodar **Mock** (primeiro contato)

1. No **sidebar**, selecione **Modo de dados = Mock (recomendado para começar)**.  
2. Observe KPIs e gráficos.  
3. Clique em **“Analisar com IA (stub)”** para ver o texto gerado a partir dos agregados.  
4. Abra **“Ver tabela de dados”** para enxergar a série de tempo.  
5. Baixe **CSV**/JSON para conferir.

> Dica de estudo: edite `data/mock_today.json` (valores de `Pac`/`Cbattery1`) e recarregue para ver como KPIs e gráficos reagem.

---

## 7) Como rodar **Real (SEMS)**

1. No **sidebar**, selecione **Modo de dados = Real (SEMS)**.  
2. **Inverter SN**: informe o SN (ex.: `5010KETU229W6177`).  
3. **Data**: selecione a data de interesse (o app monta `YYYY-MM-DD 00:00:00`).  
4. **Login SEMS**  
   - **Região de login**: escolha **US** (para a conta demo).  
   - **Região de dados**: escolha **EU** (com a demo, o retorno costuma indicar dados na EU).  
   - **SEMS_ACCOUNT**: `demo@goodwe.com` (ou sua conta).  
   - **SEMS_PASSWORD**: `GoodweSems123!@#` (ou sua senha).  
5. **Colunas**: deixe, para começar, `Cbattery1`. Depois adicione `Pac` e `Eday`.  
6. Aguarde o carregamento.  
   - Se aparecer aviso **“Não consegui parsear a coluna…”**, clique em **“Ver resposta JSON”** e observe:
     - Onde está a **lista** de pontos (`data.column1`, `items`, `list`…);  
     - Qual é o **campo de tempo** (`date`, `time`, `tm`…) e qual é o **campo do valor** (`column`, `value`, `v`, `val`…).

> Exemplo real comum:  
> A resposta vem como  
> `{"data":{"column1":[{"date":"08/12/2025 00:00:00", "column":88.0}, ...]}}`.  
> O app já mapeia `date` → **time** e `column` → **valor**.

---

## 8) O que editar para **personalizar**

### 8.1 Editar **KPIs** (em `app.py`)
- Abra a função `resumo_dia(df)`.  
- Calcule novos indicadores (ex.: **média de potência**, **hora de início da geração**).  
- Exiba em novos `st.metric(...)` no topo, como já é feito com Energia do dia/Pico/SOC.

### 8.2 Editar **gráficos** (em `app.py`)
- Procure onde `px.line(...)` é chamado para `Pac` e `Cbattery1`.  
- Troque títulos, adicione/remova `markers=True`, crie **abas** (`st.tabs`) para organizar.

### 8.3 Adicionar **novas colunas** (em `app.py`)
- No **sidebar**, inclua a nova coluna na lista de seleção (ex.: `Temp`).  
- O `fetch_realtime_df(...)` já busca **várias colunas** e as combina por tempo.  
- Se o JSON vier em outro formato, ajuste a função `parse_column_timeseries(...)` mapeando as chaves corretas.

### 8.4 Ajustar **parser** (se necessário)
- Abra o **JSON** no expander.  
- Verifique:
  - Onde está a **lista** (ex.: `data.column1`).  
  - Qual é o **campo de tempo** (`date`, `time`, `tm`…)  
  - Qual é o **campo de valor** (`column`, `value`, `v`, `val` ou a própria `coluna` pelo nome).  
- Altere o trecho correspondente em `parse_column_timeseries(...)`.

### 8.5 Alterar **regiões** (em `goodwe_client.py`)
- Edite o dicionário `BASE = {"us": "...", "eu": "..."}` se precisar apontar para outro host.  
- Ajuste `timeout` das requisições se a rede estiver lenta.

---

## 9) Como o fluxo funciona (por baixo dos panos)

1. **Token inicial (pré-login)**  
   - Envie um *header* `Token` com um JSON simples (uid vazio, client “web”, etc.) **encodado em Base64**.
2. **Crosslogin**  
   - `POST /api/v2/common/crosslogin` com `account` e `pwd`.  
   - Resposta traz `data` com `uid`, `timestamp`, `token`, etc.  
   - **Encode `data` em Base64** → isso vira o **Token “pós-login”** para as próximas chamadas.
3. **Dados de coluna**  
   - `POST /api/PowerStationMonitor/GetInverterDataByColumn` com:
     ~~~json
     {
       "date": "YYYY-MM-DD 00:00:00",
       "column": "Cbattery1",
       "id": "SEU_SN_AQUI"
     }
     ~~~
   - O JSON comum traz `{"data":{"column1":[{"date":"...", "column":<valor>}, ...]}}`.
4. **Parser**  
   - Extrai pares **tempo → valor** independente do campo exato (`date/time/tm`, `column/value/v/val`).  
   - Converte datas `DD/MM` ↔ `MM/DD` automaticamente.  
5. **Merge de colunas**  
   - Busca várias colunas e usa `merge_asof` por `time` para juntar na mesma tabela.  
6. **KPIs e gráficos**  
   - Calcula agregados (energia, pico, SOC) e mostra linhas no tempo.

---

## 10) Boas práticas de **credenciais**

- Não deixe `account` e `pwd` no código fonte.  
- Use **variáveis de ambiente** (o app já lê se existirem).  
- Se quiser um `.env` local (sem subir para o Git):
  1. Instale `python-dotenv`: `pip install python-dotenv`  
  2. No topo do `app.py`, adicione:
     ~~~python
     from dotenv import load_dotenv
     load_dotenv()
     ~~~
  3. Crie um `.env` com:
     ~~~
     SEMS_ACCOUNT=seu_email
     SEMS_PASSWORD=sua_senha
     SEMS_REGION=us
     ~~~

---

## 11) Depuração (erros comuns e como resolver)

- **“Não consegui parsear a coluna …”**  
  - Abra “Ver resposta JSON” e confirme:  
    - onde está a lista (`data.column1`/`items`/`list`/`datas`/`result`);  
    - qual é o campo de tempo (`date`/`time`/`tm`/`collectTime`/`cTime`);  
    - qual é o campo de valor (`column`/`value`/`v`/`val`/`nome da coluna`).  
  - Ajuste `parse_column_timeseries(...)`.

- **HTTP 200 mas sem dados**  
  - Confira o **SN** informado.  
  - Ajuste **Região de login** e **Região de dados** (com a demo, use Login=US e Dados=EU).  
  - Tente outra **data**.

- **401/403 (não autorizado)**  
  - Refazer o **crosslogin** para obter **novo Token** (ele pode expirar).  
  - Conferir se o **Token** no header é o **Base64 do `data`** da última resposta de login.

- **Timeout / rede lenta**  
  - Aumentar o `timeout` nas chamadas no `goodwe_client.py`.  
  - Testar conectividade/hosts.

- **Datas mal interpretadas**  
  - O parser tenta `dayfirst=True`. Se ainda assim falhar, ajuste a conversão manualmente.

---

## 12) Roteiro de estudo (entregas)

**Etapa 1 — UI + Mock**  
- Rode o app em modo Mock.  
- Edite o `mock_today.json` e mostre que KPIs e gráficos mudam.  
- Grave um vídeo curto explicando o dashboard.

**Etapa 2 — Dados reais (SEMS)**  
- Faça login, busque `Cbattery1`, depois `Pac` e `Eday`.  
- Mostre o expander com o JSON e explique como o parser funciona.

**Etapa 3 — Explicação automática (IA)**  
- Substitua o `ai.py` por uma chamada de LLM (envie apenas os agregados numéricos).  
- Gere 1–2 parágrafos sobre o “comportamento do dia” (picos/vales/SOC).

**Etapa 4 — Voz**  
- Integre captura de áudio (navegador) + STT (Whisper/local) + TTS.  
- Faça perguntas como “Qual a energia do dia?” e responda por voz.

---

## 13) Próximas evoluções

- **Mais colunas** (temperatura, tensão, etc.) e novos KPIs.  
- **Períodos maiores** (semana/mês): repita consultas por dia e *concatene* resultados.  
- **Histórico local**: botão para salvar o JSON/CSV de cada dia em `data/real/AAAA-MM-DD.json`.  
- **Deploy**: publicar no Streamlit Cloud para demonstração (atenção a credenciais).  
- **Alexa Skill**: modelar intents (“energia de hoje”, “status da bateria”) e chamar a mesma lógica do `goodwe_client`.

---

> Siga este README passo a passo. Comece em **Mock**, entenda a **interface**, depois ligue o **Real**, ajuste o **parser** quando necessário e avance para **IA** e **voz**.
