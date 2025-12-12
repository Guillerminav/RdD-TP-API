from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
import math
from pathlib import Path

json_path = Path(__file__).parent / "municipios.json"

app = FastAPI()
security = HTTPBasic()

def cargar_datos():
    if not json_path.exists():
        return {"municipios": []}
    
    with open(json_path, 'r', encoding='utf-8') as file:  
        return json.load(file)

def guardar_datos(datos):
    with open(json_path, 'w', encoding='utf-8') as file:
        json.dump(datos, file, indent=4, ensure_ascii=False)

def verificar_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verifica usuario y contraseña"""
    user = "admin"
    password = "admin"
    
    if credentials.username != user or credentials.password != password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return credentials.username

def calcular_distancia_h(lat1, lon1, lat2, lon2):
    """Calcula la distancia entre dos coordenadas"""
    R = 6371  # radio del planeta en km
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    
    return round(distance, 2)


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

@app.post("/municipios", dependencies=[Depends(verificar_admin)])
def crear_municipio(nuevo_muni: dict):
    if "id" not in nuevo_muni or "nombre" not in nuevo_muni or (nuevo_muni["nombre"] == "") or (nuevo_muni["id"] == ""):
        raise HTTPException(status_code=400, detail="Faltan datos obligatorios (id, nombre)")

    datos = cargar_datos()
    lista_municipios = datos.get("municipios", [])
    
    # Validar que el ID no exista ya
    for m in lista_municipios:
        if m['id'] == nuevo_muni['id']:
            raise HTTPException(status_code=400, detail=f"El ID {m['id']} pertenece al municipio {m['nombre']}")
    
    lista_municipios.append(nuevo_muni)
    datos["municipios"] = lista_municipios
    
    guardar_datos(datos)
    return {"mensaje": "Municipio creado exitosamente", "municipio": nuevo_muni}

@app.delete("/municipios/{id_municipio}", dependencies=[Depends(verificar_admin)])
def borrar_municipio(id_municipio: str):
    datos = cargar_datos()
    lista_municipios = datos.get("municipios", [])
    
    nueva_lista = [m for m in lista_municipios if m['id'] != id_municipio]
    
    if len(lista_municipios) == len(nueva_lista):
        raise HTTPException(status_code=404, detail="Municipio no encontrado para eliminar")
        
    datos["municipios"] = nueva_lista
    guardar_datos(datos)
    return {"mensaje": f"Municipio {id_municipio} eliminado"}

@app.get("/distancia/{id1}/{id2}")
def get_distancia(id1: str, id2: str):
    datos = cargar_datos()
    muni1 = None
    muni2 = None
    
    # buscamos los municipios
    for m in datos.get("municipios", []):
        if m["id"] == id1:
            muni1 = m
        if m["id"] == id2:
            muni2 = m
        if muni1 and muni2:
            break
            
    if not muni1 or not muni2:
        raise HTTPException(status_code=404, detail="Uno o ambos municipios no existen")
        
    # chequeamos que tengan coordenadas
    if "centroide" not in muni1 or "centroide" not in muni2:
        raise HTTPException(status_code=400, detail="Faltan coordenadas en los municipios")  
    else:
        muni1_centroide = muni1["centroide"]  
        muni2_centroide = muni2["centroide"]  
        
    km = calcular_distancia_h(
        muni1_centroide["lat"], muni1_centroide["lon"],
        muni2_centroide["lat"], muni2_centroide["lon"]
    )
    
    return {
        "origen": muni1["nombre"],
        "destino": muni2["nombre"],
        "distancia_km": km
    }