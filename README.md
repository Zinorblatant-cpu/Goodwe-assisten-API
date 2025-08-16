# ⚡ GoodWe Assistant — Starter (Streamlit + SEMS + Mock)

Projeto **didático** para alunos do 1º ano de Ciência da Computação: uma interface simples em **Streamlit** que lê dados do **SEMS Portal (GoodWe)**, mostra **KPIs e gráficos**, e prepara o terreno para **IA** (explicação dos dados) e **voz** (perguntas por áudio).

> **Ideia pedagógica:** começar com dados **mock**, entender a estrutura do código, **substituir** por dados reais do SEMS e, por fim, evoluir para IA e voz. Tudo com passos curtos e objetivos.

---

## 🧭 Sumário

- [Objetivos do Starter](#objetivos-do-starter)
- [Pré‑requisitos](#pré-requisitos)
- [Instalação (passo a passo)](#instalação-passo-a-passo)
- [Como rodar (modo Mock)](#como-rodar-modo-mock)
- [Como rodar (modo Real SEMS)](#como-rodar-modo-real-sems)
- [Estrutura de Pastas e Arquivos](#estrutura-de-pastas-e-arquivos)
  - [app.py](#apppy)
  - [goodwe_client.py](#goodwe_clientpy)
  - [ai.py](#aipy)
  - [data/mock_today.json](#datamock_todayjson)
  - [requirements.txt e .gitignore](#requirementstxt-e-gitignore)
- [Personalizações (o que o aluno pode mudar)](#personalizações-o-que-o-aluno-pode-mudar)
- [Como adicionar novas colunas/endereços de API](#como-adicionar-novas-colunasendereços-de-api)
- [Boas práticas de credenciais](#boas-práticas-de-credenciais)
- [Debug e resolução de problemas](#debug-e-resolução-de-problemas)
- [Roteiro sugerido de Sprints](#roteiro-sugerido-de-sprints)
- [Próximos passos (IA, Voz, Deploy)](#próximos-passos-ia-voz-deploy)
- [FAQ — Erros comuns](#faq--erros-comuns)

---

## 🎯 Objetivos do Starter

1. **Visualizar** dados de um inversor/planta GoodWe (potência, energia do dia, SOC de bateria).  
2. **Desacoplar** UI de coleta: a UI funciona com **mock** (sem internet) e depois com **SEMS** (real).  
3. **Padronizar** a análise: calcular agregados (pico, energia do dia, SOC início/fim) e **explicar** com texto.  
4. **Preparar** a turma para evoluir: IA de verdade (LLM), Voz no navegador e Alexa Skill em sprints posteriores.

---

## 🧰 Pré‑requisitos

- **Python 3.10+** (Windows, macOS ou Linux).  
- **pip** atualizado.  
- (Opcional) **VS Code** + extensão **Python**.  
- Acesso à internet (para usar o modo **Real SEMS**).

> Se for usar dados reais do SEMS, você precisa de um **account/senha** e do **Serial Number (SN)** do inversor (ou o ID correto dependendo do endpoint).

---

## ⚙️ Instalação (passo a passo)

1) **Crie** e ative um ambiente virtual (opcional, mas recomendado):

```bash
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

2) **Instale** as dependências:

```bash
pip install -r requirements.txt
```

3) **Rode** o app:

```bash
streamlit run app.py
```

> Abrirá no navegador (geralmente em `http://localhost:8501`).

---

## ▶️ Como rodar (modo Mock)

No **sidebar**, deixe **Modo de dados = Mock (recomendado para começar)**.  
Esse modo usa apenas o arquivo `data/mock_today.json` para alimentar gráficos e KPIs. É ideal para:

- rodar **offline**;
- manter a turma no **fluxo de UI/plot** antes de APIs;
- simular rapidamente um “dia típico” de geração e bateria.

---

## 🌐 Como rodar (modo Real SEMS)

1) No **sidebar**, escolha **Modo de dados = Real (SEMS)**.  
2) Informe:
   - **Inverter SN** (ex.: `5010KETU229W6177`).  
   - **Data** (o endpoint do exemplo usa uma data com hora interna `00:00:00`).  
   - **Região de login**: geralmente **US** (funciona com a conta de demo).  
   - **Região de dados**: geralmente **EU** (o próprio `crosslogin` costuma apontar para `eu.semsportal.com`).
   - **SEMS_ACCOUNT** e **SEMS_PASSWORD** (para DEMO já ficam preenchidos).  

3) Escolha as **colunas** (comece com `Cbattery1`; depois teste `Pac` e `Eday`).  
4) Clique fora dos campos e aguarde o carregamento. Se algo não vier, um **expander** mostrará o **JSON bruto** da resposta para debug.

> O fluxo é o mesmo que o script `requests` do professor: `crosslogin` → gera **Token** (Base64 do `data`) → `GetInverterDataByColumn` com `id` (SN), `column` (`Cbattery1`) e `date` (`YYYY-MM-DD HH:MM:SS`).

---

## 🗂️ Estrutura de Pastas e Arquivos

```
goodwe-assistant/
├─ app.py                 # UI Streamlit: gráficos, KPIs, modo Mock/Real, parser e merge
├─ goodwe_client.py       # Login (crosslogin) + chamada GetInverterDataByColumn
├─ ai.py                  # "explicação" de dados (stub, sem LLM ainda)
├─ data/
│  └─ mock_today.json     # amostra de dados para um dia (Pac, Eday, Cbattery1)
├─ requirements.txt       # dependências
└─ .gitignore
```

### `app.py`

- **O que faz**: toda a interface em **Streamlit**. Mostra KPIs (Energia do dia, Pico de potência, SOC início→fim), gráficos e tabela.  
- **Partes-chave**:
  - `carregar_mock(...)`: lê o JSON de mock e devolve um `DataFrame` com a coluna `time`.  
  - `resumo_dia(df)`: calcula **agregados** (energia, pico, horários, SOC).  
  - `parse_column_timeseries(resp_json, column_name)`: **interpreta** a resposta do SEMS e extrai série temporal.  
    - Suporta o formato `data.column1 = [{ "date": "...", "column": 88.0 }, ...]` (caso real).  
    - Também tenta outras variações (`time`, `value`, `v`, `val` etc.).  
    - Converte automaticamente datas no padrão **DD/MM/YYYY** ou **MM/DD/YYYY**.  
  - `fetch_realtime_df(...)`: faz `crosslogin`, busca **várias colunas** e faz um **merge_asof** por tempo.  
  - Sidebar: alterna **Mock**/ **Real (SEMS)** e configura colunas, regiões e credenciais.
- **O que você pode mudar**:
  - **KPIs**: adicione novas métricas usando colunas adicionais (ex.: `Temp`).  
  - **Gráficos**: mude títulos, eixos, `markers=True/False`.  
  - **Colunas**: mude a lista-padrão na sidebar.  
  - **Parser**: se o endpoint voltar em outro formato, ajuste as chaves no `parse_column_timeseries`.

### `goodwe_client.py`

- **O que faz**: encapsula chamadas HTTP ao SEMS.
  - `crosslogin(account, pwd, region) -> token`: faz POST para `/api/v2/common/crosslogin`, e devolve o **Token** (Base64 do `data`).  
  - `get_inverter_data_by_column(token, inv_id, column, date, region)`: chama `/api/PowerStationMonitor/GetInverterDataByColumn`.
- **O que você pode mudar**:
  - **Regiões**: dicionário `BASE = {"us": "...", "eu": "..."}`. Adapte se o seu ambiente usar outro host.  
  - **Timeouts**: altere `timeout=20`.  
  - **Novos endpoints**: crie novas funções seguindo o mesmo padrão (headers com `Token`, payloads JSON e `raise_for_status()`).

### `ai.py`

- **O que faz**: gera um texto simples a partir do `resumo_dia` (**sem LLM**). Serve para validar a “narrativa” antes de gastar tokens em IA.  
- **O que você pode mudar**:
  - Trocar por chamada a um **LLM** (OpenAI/Azure/Ollama). **Dica didática**: **não** envie o `df` inteiro; envie **agregados** (números) e peça para o modelo **explicar**.

### `data/mock_today.json`

- **O que é**: uma amostra para um dia (horas do dia com `Pac`, `Eday`, `Cbattery1`).  
- **O que você pode mudar**:
  - Substitua os valores para simular outros dias.  
  - Adicione novas chaves/colunas e ajuste o `app.py` para plotá-las.

### `requirements.txt` e `.gitignore`

- **requirements**: lista de pacotes (Streamlit/Pandas/Plotly/Requests).  
- **.gitignore**: evita subir `__pycache__`, `.env` e configurações locais.

---

## 🎛️ Personalizações (o que o aluno **pode** mudar)

- **Tema/cores** (Streamlit): crie `.streamlit/config.toml` e personalize o tema do app.  
- **Colunas exibidas**: adicione/remova opções na sidebar e nos gráficos (ex.: `Temp`, `Vac`, etc.).  
- **KPIs extra**: exibir **média** de potência, **hora de início** da geração, **tempo acima de X kW**, etc.  
- **Período**: hoje o exemplo usa **um dia**. Você pode repetir consultas por datas distintas e **concatenar** resultados para mostrar **semana/mês**.  
- **Layout**: reorganizar colunas, usar `st.tabs`, inserir explicações com Markdown para “guiar” o usuário final.

---

## ➕ Como adicionar novas colunas/endereços de API

1) **No app (modo Real)**, inclua a coluna na seleção da sidebar (ex.: `Temp`).  
2) O `fetch_realtime_df(...)` chamará `GetInverterDataByColumn` para cada coluna.  
3) Se a resposta tiver **outro formato**, ajuste o `parse_column_timeseries(...)`. Ex.:

```python
# Exemplo: o endpoint devolve {"data":{"column1":[{"date":"08/12/2025 00:00:00","column":88.0}, ...]}}
# Já suportado. Se vier, por exemplo, {"result":[{"tm":"...", "val":"..."}]}, mapeie 'tm' e 'val' nas linhas do parser.
```

4) Para **novos endpoints** (ex.: totais diários, status do inversor etc.), crie uma função em `goodwe_client.py` com:
   - Montagem do **header** `{"Token": <token>, "Content-Type": "application/json"}`  
   - Montagem do **payload** (veja no seu inspetor/SDKs)  
   - `requests.post(...)`/`get(...)` + `r.raise_for_status()`  
   - Retorne o `r.json()`; **parseie** no `app.py` para `DataFrame` e plote.

---

## 🔐 Boas práticas de credenciais

- **Nunca** comite `SEMS_ACCOUNT`/`SEMS_PASSWORD`.  
- Prefira **variáveis de ambiente** (já suportadas).  
- (Opcional) Use `python-dotenv` para um arquivo `.env` **local** (não comite):
  ```bash
  pip install python-dotenv
  ```
  ```python
  # no início do app.py
  from dotenv import load_dotenv; load_dotenv()
  ```
- **Desative**/remova credenciais de **demo** em produção.

---

## 🩺 Debug e resolução de problemas

- **“Não consegui parsear a coluna…”**  
  - Abra o **“Ver resposta JSON (coluna)”** e verifique onde está a lista (ex.: `data.column1`).  
  - Ajuste o parser mapeando **chaves de tempo** (`time`, `date`, `tm`...) e **valor** (`value`, `v`, `val`, `column`...).  
- **200 OK mas sem dados**  
  - `SN/ID` incorreto para o endpoint escolhido.  
  - **Região** incorreta (tente **login US** + **dados EU** como no exemplo).  
  - Data fora de cobertura (tente outro dia).  
- **401/403**  
  - Token inválido/expirado → garanta que o **Token** usado é o **Base64 do `data`** do `crosslogin` mais recente.  
- **Timeouts**  
  - Links/hosts lentos → ajuste `timeout=20` no `goodwe_client.py` e repita.  
- **Formato de data**  
  - O SEMS às vezes retorna `DD/MM/YYYY`. O app tenta as duas formas (`dayfirst=True`).

---

## 🗓️ Roteiro sugerido de Sprints

**Sprint 1 (UI + Mock)**  
- Rodar app, entender gráficos e KPIs.  
- Alterar o mock, recalcular KPIs.  
- **Entrega**: vídeo curto mostrando dashboard + explicando os números.

**Sprint 2 (Real SEMS)**  
- Conectar com `crosslogin`, buscar `Cbattery1` e `Pac`.  
- Ajustar parser se necessário.  
- **Entrega**: dashboard com dados reais de 1 dia.

**Sprint 3 (IA explicativa)**  
- Calcular agregados e gerar texto com LLM (substituir `ai.py`).  
- **Entrega**: botão “Explicar o dia” gerando 1–2 parágrafos objetivos.

**Sprint 4 (Voz → Navegador ou Alexa)**  
- Navegador: gravação + STT (Whisper/Local) + TTS.  
- Opcional: **Alexa Skill** (ASK + Lambda) chamando a mesma lógica de dados.

---

## 🚀 Próximos passos (IA, Voz, Deploy)

- **IA real (LLM)**: substituir `ai.py` para usar OpenAI/Azure/Local (Ollama), sempre enviando **agregados** (não a tabela inteira).  
- **Voz**:
  - Navegador: integrar **Web Speech API** (STT/TTS) via componente Streamlit (p.ex. `streamlit-webrtc`).  
  - Alexa: criar **Skill** com intents “energia de hoje”, “status da bateria”; a Lambda chama o mesmo `goodwe_client`.  
- **Deploy**:
  - **Streamlit Community Cloud** (UI) + **Render/Railway/Cloud Run** (se separar backend).  
  - Para MVP, dá para hospedar tudo no próprio Streamlit Cloud (modo Mock/Real com cautela).

---

## ❓ FAQ — Erros comuns

**1) “Login OK, mas os gráficos não aparecem.”**  
Verifique **Região de dados** (muitas vezes **EU**), **SN** correto e **data**. Veja o JSON exposto.

**2) “Parser não achou `time`.”**  
Mapeie `date`, `tm`, `collectTime` etc. no `parse_column_timeseries` (já há exemplos no código).

**3) “Quero 7 dias de dados.”**  
Faça um loop de datas chamando a função por dia e `concat` os `DataFrames`. Depois plote barra/linha semanal.

**4) “Como troco idioma/formato?”**  
Os textos estão em PT‑BR; altere strings na UI. O parser detecta `DD/MM` (dayfirst).

**5) “Como guardo histórico?”**  
Salve CSV/JSON diários em uma pasta (`data/real/YYYY-MM-DD.json`). Dá pra criar um botão “Salvar histórico”.

---

> **Dica final para apresentar em sala**: começar **mock** (segurança/confiança), ligar **Real**, abrir um **JSON** e mostrar como a gente “descobre” as chaves certas. Em seguida, pedir que cada grupo **personalize** 1 KPI e 1 gráfico.

Bom estudo! ✨
