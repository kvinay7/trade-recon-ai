import pandas as pd

def normalize(df):
    df['trade_id'] = df['trade_id'].astype(str).str.strip()
    df['currency'] = df['currency'].astype(str).str.upper().str.strip()
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    df['trade_date'] = pd.to_datetime(df['trade_date'], errors='coerce')
    df['counterparty'] = df['counterparty'].astype(str).str.lower().str.strip()

    # instrument may not exist in some sources
    if 'instrument' not in df.columns:
        df['instrument'] = ""

    return df
