from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import json
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
    if "id" not in nuevo_muni or "nombre" not in nuevo_muni:
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