# vigia.py - El Cerebro de El Vigía
import time
import pandas as pd
import requests
import ta
from ta.volatility import AverageTrueRange
from ta.trend import EMAIndicator
from ta.momentum import RSIIndicator
import requests
import json

# ===================== CONFIGURACIÓN =====================
TWELVEDATA_API_KEY = "https://twelvedata.com/account/api-keysda05fdce2dca49a9ac3f0d9a46dbccae"  # <--- ¡CAMBIA ESTO!
ACTIVOS = [
    {"nombre": "ORO", "simbolo": "XAUUSD"},
    {"nombre": "PETRÓLEO", "simbolo": "WTI"},
    {"nombre": "NASDAQ", "simbolo": "US100"}
]
INTERVALO = "5min"
TIEMPO_ENTRE_ANALISIS = 60  # Segundos (análisis cada minuto para pruebas)

# ===================== FUNCIONES DE ESTRATEGIA (Tuyas) =====================
def calcular_indicadores(df):
    if df is None or len(df) < 20: return None
    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    df['ema_20'] = ta.trend.EMAIndicator(df['close'], window=20).ema_indicator()
    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=14)
    df['atr'] = atr.average_true_range()
    df['atr_pct'] = (df['atr'] / df['close']) * 100
    return df

def detectar_senal_apalancamiento(df):
    if df is None: return None
    ultimo = df.iloc[-1]
    if 30 <= ultimo['rsi'] <= 45 and ultimo['close'] > ultimo['ema_20'] and ultimo['atr_pct'] > 0.5:
        return {'tipo': 'CALL', 'precio': round(ultimo['close'], 2), 'tp1': round(ultimo['close']*1.02,2), 'tp2': round(ultimo['close']*1.04,2), 'confianza': 'ALTA'}
    if 55 <= ultimo['rsi'] <= 70 and ultimo['close'] < ultimo['ema_20'] and ultimo['atr_pct'] > 0.5:
        return {'tipo': 'PUT', 'precio': round(ultimo['close'], 2), 'tp1': round(ultimo['close']*0.98,2), 'tp2': round(ultimo['close']*0.96,2), 'confianza': 'ALTA'}
    return None

def detectar_senal_binarias(df):
    if df is None: return None
    ultimo = df.iloc[-1]
    if 40 <= ultimo['rsi'] <= 60 and ultimo['close'] > ultimo['ema_20']:
        return {'tipo': 'CALL', 'precio': round(ultimo['close'], 2), 'duracion': '5-15 min'}
    if 40 <= ultimo['rsi'] <= 60 and ultimo['close'] < ultimo['ema_20']:
        return {'tipo': 'PUT', 'precio': round(ultimo['close'], 2), 'duracion': '5-15 min'}
    return None

# ===================== FUNCIÓN PARA OBTENER DATOS (Twelve Data) =====================
def obtener_datos_twelvedata(simbolo):
    url = "https://api.twelvedata.com/time_series"
    params = {
        "apikey": TWELVEDATA_API_KEY,
        "symbol": simbolo,
        "interval": INTERVALO,
        "outputsize": 50,
        "format": "JSON"
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        if "values" not in data: return None
        df = pd.DataFrame(data["values"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")
        df[["open", "high", "low", "close"]] = df[["open", "high", "low", "close"]].astype(float)
        df.columns = [c.lower() for c in df.columns]
        return df
    except: return None

# ===================== ENVÍO A LA API LOCAL (El Correo) =====================
def enviar_senal_a_web(senal):
    try:
        requests.post("http://localhost:8000/nueva-senal", json=senal, timeout=1)
    except: pass  # Si la web no está abierta, no pasa nada

# ===================== BUCLE PRINCIPAL =====================
if __name__ == "__main__":
    print("🤖 El Vigía (Cerebro) iniciado. Vigilando el mercado...")
    while True:
        for activo in ACTIVOS:
            df = obtener_datos_twelvedata(activo["simbolo"])
            if df is not None:
                df_indicadores = calcular_indicadores(df)
                if df_indicadores is not None:
                    senal_ap = detectar_senal_apalancamiento(df_indicadores)
                    senal_bin = detectar_senal_binarias(df_indicadores)
                    if senal_ap or senal_bin:
                        mensaje = {
                            "activo": activo["nombre"],
                            "apalancamiento": senal_ap,
                            "binarias": senal_bin
                        }
                        enviar_senal_a_web(mensaje)
                        print(f"🔔 Señal enviada para {activo['nombre']}")
            time.sleep(2)  # Pequeña pausa entre activos
        time.sleep(TIEMPO_ENTRE_ANALISIS)