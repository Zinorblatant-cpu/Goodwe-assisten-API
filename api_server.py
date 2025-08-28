# api_server.py
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from analysis import obter_dados, analisar_dia
from goodwe_client import client_from_env

# ================== Configurações ==================
ROOT = Path(__file__).parent
MOCK_PATH = ROOT / "data" / "mock_today.json"

app = FastAPI(title="GoodWe Assistant API", version="1.0")
acc = None
pwd = None

class Request(BaseModel):
    inverter_sn: str

# Habilita CORS (útil para testes em browser, não atrapalha Alexa)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================== Funções Auxiliares ==================
def carregar_mock(path: Path) -> pd.DataFrame:
    """Carrega dados mockados em formato DataFrame."""
    if not path.exists():
        return pd.DataFrame()
    with open(path, "r", encoding="utf-8") as f:
        payload = json.load(f)
    df = pd.DataFrame(payload["data"])
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"])
    return df


def resumo_dia(df: pd.DataFrame) -> dict:
    """Gera um resumo diário com métricas principais do inversor."""
    if df.empty:
        return {}

    # Energia do dia
    energia_dia = float(df["Eday"].dropna().iloc[-1]) if "Eday" in df else 0.0

    # Pico de potência
    if "Pac" in df and not df["Pac"].dropna().empty:
        idx_max = df["Pac"].idxmax()
        pico_p = float(df.loc[idx_max, "Pac"])
        hora_p = df.loc[idx_max, "time"] if "time" in df else None
    else:
        pico_p, hora_p = 0.0, None

    # SOC inicial/final
    soc_ini = int(df["Cbattery1"].dropna().iloc[0]) if "Cbattery1" in df else None
    soc_fim = int(df["Cbattery1"].dropna().iloc[-1]) if "Cbattery1" in df else None

    # Consumo do dia (checa várias colunas possíveis)
    consumo_cols = [
        "EloadDay", "LoadEday", "EhouseDay", "EHomeDay",
        "LoadEnergyDay", "LoadEnergy", "Eload"
    ]
    consumo_dia: Optional[float] = None
    for c in consumo_cols:
        if c in df and not df[c].dropna().empty:
            consumo_dia = float(df[c].dropna().iloc[-1])
            break

    # Status: ligado se potência atual > 5W
    status = "desligado"
    if "Pac" in df and not df["Pac"].dropna().empty:
        pac_now = float(df["Pac"].dropna().iloc[-1])
        status = "ligado" if pac_now > 5 else "desligado"

    return {
        "energia_dia": energia_dia,
        "consumo_dia": consumo_dia,
        "pico_potencia": pico_p,
        "hora_pico": hora_p.isoformat() if hora_p else None,
        "soc_ini": soc_ini,
        "soc_fim": soc_fim,
        "status": status,
        "atualizado_em": datetime.utcnow().isoformat() + "Z",
    }

# ================== Rotas ==================
@app.on_event("startup")
def load_envs():
    global acc, pwd
    acc = "demo@goodwe.com"
    pwd = "GoodweSems123!@#"
    # acc = client_from_env()["account"]
    # pwd = client_from_env()["password"]
    print(f"API iniciada em {datetime.utcnow().isoformat()}Z com conta '{acc}' e senha com {len(pwd)} caracteres.")

@app.get("/")
def read_root():
    return {"message": "API Goodwe rodando com sucesso 🚀"}


@app.post("/status")
def get_status(data: Request):
    dataframe = obter_dados(acc, pwd, data.inverter_sn, columns=["Pac"])

    response = analisar_dia(dataframe)
    response.pop("pico_potencia")
    response.pop("hora_pico")

    return response


@app.post("/potencia")
def get_potencia(data: Request):
    dataframe = obter_dados(acc, pwd, data.inverter_sn, columns=["Pac"])

    response = analisar_dia(dataframe)
    response.pop("status")

    return response


# @app.get("/tensao")
# def get_tensao():
#     """Exemplo de endpoint simples (mockado)."""
#     return {"tensao": "220V"}

@app.post("/bateria")
def get_soc(data: Request):
    dataframe = obter_dados(acc, pwd, data.inverter_sn, columns=["Cbattery1"])

    response = analisar_dia(dataframe)

    return response


@app.post("/energia-hoje")
def get_energia_hoje(data: Request):
    dataframe = obter_dados(acc, pwd, data.inverter_sn, columns=["Eday"])

    response = analisar_dia(dataframe)

    return response