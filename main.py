from fastapi import FastAPI, HTTPException
import json
from pathlib import Path

json_path = Path(__file__).parent / "municipios.json"

def cargar_datos():
    with open(json_path, 'r', encoding='utf-8') as file:
        datos = json.load(file)
    return datos

app = FastAPI()


#aca iria toda la data gral de la api
@app.get("/")
def read_root():
    return {"message": "API OK"}

# listado de todos los municipios
@app.get("/municipios")
def obtener_municipios():
    datos = cargar_datos()
    return datos

#buscar un municipio por su id
@app.get("/municipios/{id_municipio}")
def obtener_municipio(id_municipio: str):
    datos = cargar_datos()
    municipios = datos.get("municipios", [])

    for municipio in municipios:
        if municipio.get("id") == id_municipio:
            return municipio