# analysis.py
from datetime import date
from app import fetch_realtime_df, resumo_dia
import pandas as pd

def obter_dados(account, password, inverter_sn, req_date=date.today(), columns=None):
    if columns is None:
        columns = ["Pac", "Eday", "Cbattery1"]

    df = fetch_realtime_df(account, password, inverter_sn, req_date, columns)
    return df

def analisar_dia(df: pd.DataFrame) -> dict:
    return resumo_dia(df)

if __name__ == "__main__":
    # Exemplo: usar credenciais reais ou demo
    account = "chellengegoodwe@gmail.com"
    password = "Goodwe2018"
    inverter_sn = "53600ERN238W0001"

    df = obter_dados(account, password, inverter_sn)
    print("DataFrame bruto:")
    print(df.head())

    resumo = analisar_dia(df)
    print("\nResumo do dia:")
    print(resumo)
