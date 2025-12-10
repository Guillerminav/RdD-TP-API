import requests
from requests.auth import HTTPBasicAuth
import json

# IMPORTANTE: Apuntamos al intermedio (Puerto 8001), NO al servidor de datos.
intermedio_URL = "http://127.0.0.1:8001"

def mostrar_menu():
    print("\n" + "="*40)
    print("   CLIENTE GESTIÓN MUNICIPIOS ") #(Vía intermedio)
    print("="*40)
    print("1. Ver todos los municipios (GET)")
    print("2. Buscar municipio por ID (GET)")
    print("3. Agregar municipio (POST - Requiere Admin)")
    print("4. Eliminar municipio (DELETE - Requiere Admin)")
    print("5. Salir")
    print("-" * 40)

def imprimir_en_consola(datos):
    """Ayuda a leer mejor el JSON en la consola"""
    print(json.dumps(datos, indent=4, ensure_ascii=False))
    
while True:
    mostrar_menu()
    opcion = input(">> Seleccione una opción: ")

    if opcion == "5":
        print("Cerrando aplicación...")
        break

    try:
        # --- OPCIÓN 1: LISTAR (Público) ---
        if opcion == "1":
            print(f"Consultando a {intermedio_URL}...")
            resp = requests.get(f"{intermedio_URL}/intermedio/municipios")
            
            if resp.status_code == 200:
                datos = resp.json()
                print(f"¡Éxito! Se encontraron {len(datos)} municipios.")
                # Mostramos solo los primeros 3 para no llenar la pantalla
                imprimir_en_consola(datos[:3])
                if len(datos) > 3:
                    print("... (y más municipios) ...")
            elif resp.status_code == 429:
                print("⛔ BLOQUEADO POR EL intermedio: Demasiadas solicitudes. Espere un minuto.")
            else:
                print(f"Error {resp.status_code}: {resp.text}")
                
# --- OPCIÓN 2: BUSCAR (Público) ---
        elif opcion == "2":
            id_buscado = input("Ingrese el ID del municipio: ")
            resp = requests.get(f"{intermedio_URL}/intermedio/municipios/{id_buscado}")
            
            if resp.status_code == 200:
                imprimir_en_consola(resp.json())
            elif resp.status_code == 404:
                print("❌ El municipio no existe.")
            elif resp.status_code == 429:
                print("⛔ BLOQUEADO POR EL intermedio: Calma, vas muy rápido.")
            else:
                print(f"Error {resp.status_code}: {resp.text}")

        # --- OPCIÓN 3: AGREGAR (Privado - Requiere Auth) ---
        elif opcion == "3":
            print("\n--- NUEVO MUNICIPIO ---")
            m_id = input("ID (ej: 123): ")
            m_nombre = input("Nombre (ej: Rosario): ")
            m_prov = input("Provincia (Enter para default): ")
            
            nuevo_dato = {"id": m_id, "nombre": m_nombre}
            if m_prov:
                nuevo_dato["provincia"] = m_prov

            print("\n🔒 Esta acción requiere permisos de Administrador.")
            user = input("Usuario: ")
            pwd = input("Contraseña: ")

            resp = requests.post(
                f"{intermedio_URL}/intermedio/municipios",
                json=nuevo_dato,
                auth=HTTPBasicAuth(user, pwd)
            )

            if resp.status_code == 200:
                print("✅ ¡Municipio Creado!")
                imprimir_en_consola(resp.json())
            elif resp.status_code == 401:
                print("🚫 ACCESO DENEGADO: Credenciales incorrectas.")
            elif resp.status_code == 400:
                print("⚠️ ERROR: " + resp.json().get('detail', 'Datos inválidos'))
            else:
                print(f"Error {resp.status_code}: {resp.text}")

        # --- OPCIÓN 4: BORRAR (Privado - Requiere Auth) ---
        elif opcion == "4":
            m_id = input("ID del municipio a borrar: ")
            
            print("\n🔒 Esta acción requiere permisos de Administrador.")
            user = input("Usuario: ")
            pwd = input("Contraseña: ")

            resp = requests.delete(
                f"{intermedio_URL}/intermedio/municipios/{m_id}",
                auth=HTTPBasicAuth(user, pwd)
            )

            if resp.status_code == 200:
                print("✅ ¡Municipio Eliminado!")
                print(resp.json())
            elif resp.status_code == 401:
                print("🚫 ACCESO DENEGADO: Credenciales incorrectas.")
            elif resp.status_code == 404:
                print("❌ No se encontró ese municipio.")
            else:
                print(f"Error {resp.status_code}: {resp.text}")

    except requests.exceptions.ConnectionError:
        print("\n🔥 ERROR CRÍTICO: No se puede conectar con el intermedio.")
        print("Asegúrate de que 'intermedio_server.py' esté corriendo en el puerto 8001.")