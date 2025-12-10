import requests
import time
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials

app = FastAPI()
security = HTTPBasic()


DATA_SERVER_URL = "http://127.0.0.1:8000"


historial_peticiones = {}
LIMITE_PETICIONES = 10  
VENTANA_TIEMPO = 60     #segundos

def verificar_limite(request: Request):
    """
    Algoritmo para limitar peticiones por IP sin librerías externas.
    """
    cliente_ip = request.client.host
    tiempo_actual = time.time()

    if cliente_ip not in historial_peticiones:
        historial_peticiones[cliente_ip] = []

    historial_peticiones[cliente_ip] = [
        t for t in historial_peticiones[cliente_ip] 
        if t > (tiempo_actual - VENTANA_TIEMPO)
    ]

    if len(historial_peticiones[cliente_ip]) >= LIMITE_PETICIONES:
        raise HTTPException(
            status_code=429, 
            detail="Demasiadas solicitudes. Espere un momento."
        )

    historial_peticiones[cliente_ip].append(tiempo_actual)

# --- ENDPOINTS intermedio ---

@app.get("/")
def intermedio_root():
    return {"info": "Servidor Intermedio Activo. Use /intermedio/municipios"}

@app.get("/intermedio/municipios")
def get_municipios(request: Request):

    verificar_limite(request)
    
    try:
        response = requests.get(f"{DATA_SERVER_URL}/municipios")
        return response.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="El servidor de datos no responde")
