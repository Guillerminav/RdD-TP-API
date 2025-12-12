import requests
import time
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import os

app = FastAPI()
security = HTTPBasic()


#DATA_SERVER_URL = "http://127.0.0.1:8000"
DATA_SERVER_URL = "http://192.168.1.2:8000"

'''ACLARACION'''

# 1. Forzar a Python a NO usar proxies para direcciones locales
# (Reemplaza con la IP real del servidor de datos, la .2)
os.environ['NO_PROXY'] = '192.168.1.2' 

# 2. Opcional: Desactiva proxies globales por si acaso
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''


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
def obtener_municipios_inter(request: Request):

    verificar_limite(request)
    
    try:
        response = requests.get(f"{DATA_SERVER_URL}/municipios")
        return response.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="El servidor de datos no responde")

@app.get("/intermedio/municipios/{id_municipio}")
def obtener_municipio_inter(request: Request, id_municipio: str):
    verificar_limite(request)
    
    try:
        response = requests.get(f"{DATA_SERVER_URL}/municipios/{id_municipio}")

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get('detail'))
        return response.json()
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="El servidor de datos no responde")


@app.post("/intermedio/municipios")
def crear_municipio_inter(request: Request, datos: dict, cred: HTTPBasicCredentials = Depends(security)):
    verificar_limite(request)
    
    try:
        response = requests.post(
            f"{DATA_SERVER_URL}/municipios",
            json=datos,
            auth=(cred.username, cred.password)
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get('detail'))
        return response.json()
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="El servidor de datos no responde")


@app.delete("/intermedio/municipios/{id_municipio}")
def borrar_municipio_inter(request: Request, id_municipio: str, cred: HTTPBasicCredentials = Depends(security)):
    verificar_limite(request)
    
    try:
        response = requests.delete(
            f"{DATA_SERVER_URL}/municipios/{id_municipio}",
            auth=(cred.username, cred.password)
        )
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get('detail'))
        return response.json()
        
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="El servidor de datos no responde")
    
@app.get("/intermedio/distancia/{id1}/{id2}")
def get_distancia_intermedio(request: Request, id1: str, id2: str):
    verificar_limite(request)
    
    try:
        response = requests.get(f"{DATA_SERVER_URL}/distancia/{id1}/{id2}")
        if response.status_code != 200:
             raise HTTPException(status_code=response.status_code, detail=response.json().get('detail'))
        return response.json()
    
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="El servidor de datos no responde")
