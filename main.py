from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
from pathlib import Path

json_path = Path(__file__).parent / "municipios.json"

def cargar_datos():
    if not json_path.exists():
        return {"municipios": []}
    
    with open(json_path, 'r', encoding='utf-8') as file:  
        return json.load(file)

def guardar_datos(datos):
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(datos, file, indent=4, ensure_ascii=False)
        
app = FastAPI()
security = HTTPBasic()

#aca iria toda la data gral de la api
@app.get("/")
def read_root():
    return {"message": "API OK"}

# listado de todos los municipios
@app.get("/municipios")
def obtener_municipios():
    datos = cargar_datos()
    return datos.get("municipios", [])

#buscar un municipio por su id
@app.get("/municipios/{id_municipio}")
def obtener_municipio(id_municipio: str):
    datos = cargar_datos()
    municipios = datos.get("municipios", [])

    for municipio in municipios:
        if municipio.get("id") == id_municipio:
            return municipio
    
    raise HTTPException(status_code=404, detail="Municipio no encontrado")