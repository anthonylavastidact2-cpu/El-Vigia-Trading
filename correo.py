# correo.py - El Cartero de El Vigía
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Permitir que cualquier página web (la tuya) se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Senal(BaseModel):
    activo: str
    apalancamiento: dict | None = None
    binarias: dict | None = None

# Base de datos simple (en memoria, para guardar las últimas señales)
ultimas_senales = []

@app.post("/nueva-senal")
async def recibir_senal(senal: Senal):
    ultimas_senales.append(senal.dict())
    if len(ultimas_senales) > 100:  # Guarda solo las últimas 100
        ultimas_senales.pop(0)
    return {"mensaje": "Señal recibida"}

@app.get("/ultimas-senales")
async def obtener_senales():
    return ultimas_senales

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)