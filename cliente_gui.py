import tkinter as tk
from tkinter import simpledialog, messagebox, scrolledtext
import requests
from requests.auth import HTTPBasicAuth
import json
import webbrowser

# Configuración
intermedio_URL = "http://127.0.0.1:8001"
#intermedio_URL = "http://192.168.1.5:8001"

class AppMunicipios:
    def __init__(self, root):
        self.root = root
        self.root.title("Cliente API - Municipios")
        self.root.geometry("500x600")

        # TITULO
        tk.Label(root, text="CONTROL DE MUNICIPIOS", font=("Arial", 16, "bold")).pack(pady=10)

        # --- BOTONERA ---
        
        # Botón 1: Ver todos
        tk.Button(root, text="1. Ver todos los municipios", font=("Arial", 12), 
                  command=self.obtener_municipios, bg="#e1f5fe", height=2, width=30).pack(pady=5)

        # Botón 2: Buscar
        tk.Button(root, text="2. Buscar por ID", font=("Arial", 12), 
                  command=self.obtener_municipio, bg="#e1f5fe", height=2, width=30).pack(pady=5)

        # Botón 3: Agregar
        tk.Button(root, text="3. Agregar Municipio (Admin)", font=("Arial", 12), 
                  command=self.agregar_municipio, bg="#fff9c4", height=2, width=30).pack(pady=5)

        # Botón 4: Eliminar
        tk.Button(root, text="4. Eliminar Municipio (Admin)", font=("Arial", 12), 
                  command=self.eliminar_municipio, bg="#ffcdd2", height=2, width=30).pack(pady=5)
        
        # Botón 5: Calcular distancia
        tk.Button(root, text="5. Calcular Distancia (KM)", font=("Arial", 12), 
                  command=self.calcular_distancia, bg="#dcedc8", height=2, width=30).pack(pady=5)
        
        # Botón 6: Ver en google maps
        tk.Button(root, text="6. Ver Municipio en Mapa", font=("Arial", 12), 
                  command=self.ver_mapa, bg="#b3e5fc", height=2, width=30).pack(pady=5)

        # --- PANTALLA DE SALIDA ---
        tk.Label(root, text="Respuesta del Servidor:", font=("Arial", 10, "bold")).pack(pady=(20, 0))
        
        self.pantalla = scrolledtext.ScrolledText(root, width=55, height=15, font=("Consolas", 9))
        self.pantalla.pack(padx=10, pady=10)

    # --- FUNCIONES LÓGICAS ---

    def mostrar_salida(self, contenido):
        self.pantalla.delete(1.0, tk.END)
        if isinstance(contenido, (dict, list)):
            texto = json.dumps(contenido, indent=4, ensure_ascii=False)
        else:
            texto = str(contenido)
        self.pantalla.insert(tk.END, texto)

    def obtener_municipios(self):
        try:
            self.mostrar_salida("Consultando al servidor...")
            # forzamos actualización de la ventana antes de pedir datos
            self.root.update()
            
            resp = requests.get(f"{intermedio_URL}/intermedio/municipios")
            if resp.status_code == 200:
                self.mostrar_salida(resp.json())
            elif resp.status_code == 429:
                messagebox.showerror("Rate Limit", "⛔ Vas muy rápido.", parent=self.root)
            else:
                self.mostrar_salida(f"Error {resp.status_code}: {resp.text}")
        except:
            messagebox.showerror("Error", "No se puede conectar al intermedio", parent=self.root)

    def obtener_municipio(self):
        # el parametro parent=self.root fuerza al popup a estar encima
        id_buscado = simpledialog.askstring("Buscar", "Ingrese el ID del Municipio:", parent=self.root)
        
        if id_buscado:
            try:
                resp = requests.get(f"{intermedio_URL}/intermedio/municipios/{id_buscado}")
                if resp.status_code == 200:
                    self.mostrar_salida(resp.json())
                elif resp.status_code == 404:
                    self.mostrar_salida("❌ Municipio NO encontrado.")
                else:
                    self.mostrar_salida(f"Error {resp.status_code}: {resp.text}")
            except:
                messagebox.showerror("Error", "Error de conexión", parent=self.root)

    def agregar_municipio(self):
        nuevo_id = simpledialog.askstring("Nuevo", "ID del Municipio:", parent=self.root)
        
        nuevo_nombre = simpledialog.askstring("Nuevo", "Nombre del Municipio:", parent=self.root)
        
        nueva_prov = simpledialog.askstring("Nuevo", "Provincia (Dejar vacio para Default):", parent=self.root)

        # Pedir credenciales (ahora con asteriscos en la contraseña)
        user = simpledialog.askstring("Seguridad", "Usuario Administrador:", parent=self.root)
        
        # show='*' oculta los caracteres
        pwd = simpledialog.askstring("Seguridad", "Contraseña:", parent=self.root, show='*') 

        datos = {"id": nuevo_id, "nombre": nuevo_nombre}
        # Opcional
        if nueva_prov: datos["provincia"] = nueva_prov

        try:
            resp = requests.post(
                f"{intermedio_URL}/intermedio/municipios",
                json=datos,
                auth=HTTPBasicAuth(user, pwd)
            )
            self.mostrar_salida(resp.json())
            
            if resp.status_code == 200:
                messagebox.showinfo("Éxito", "Municipio Agregado Correctamente", parent=self.root)
            elif resp.status_code == 401:
                messagebox.showerror("Error", "Credenciales Incorrectas", parent=self.root)
            elif resp.status_code == 400:
                messagebox.showerror("Error","⚠️ ERROR: " + resp.json().get('detail', 'Datos inválidos'), parent=self.root)
        except:
            messagebox.showerror("Error", "Error de conexión", parent=self.root)

    def eliminar_municipio(self):
        id_borrar = simpledialog.askstring("Eliminar", "Ingrese el ID a eliminar:", parent=self.root)
        if not id_borrar: return

        user = simpledialog.askstring("Seguridad", "Usuario Administrador:", parent=self.root)
    
        pwd = simpledialog.askstring("Seguridad", "Contraseña:", parent=self.root, show='*')

        if messagebox.askyesno("Confirmar", "¿Está seguro?", parent=self.root):
            try:
                resp = requests.delete(
                    f"{intermedio_URL}/intermedio/municipios/{id_borrar}",
                    auth=HTTPBasicAuth(user, pwd)
                )
                self.mostrar_salida(resp.json())
                if resp.status_code == 200:
                    messagebox.showinfo("Éxito", "Municipio Eliminado", parent=self.root)
                elif resp.status_code == 401:
                    messagebox.showerror("Error", "Credenciales Incorrectas", parent=self.root)
                elif resp.status_code == 404:
                    messagebox.showerror("Error","❌ No se encontró ese municipio.", parent=self.root)
            except Exception as e:
                self.mostrar_salida(f"Error: {e}")
    
    def calcular_distancia(self):
        id_origen = simpledialog.askstring("Distancia", "ID del Origen:", parent=self.root)
        if not id_origen: return
        
        id_destino = simpledialog.askstring("Distancia", "ID del Destino:", parent=self.root)
        if not id_destino: return
        
        try:
            self.mostrar_salida(f"Calculando distancia de {id_origen} a {id_destino}...")
            self.root.update()
            
            resp = requests.get(f"{intermedio_URL}/intermedio/distancia/{id_origen}/{id_destino}")
            self.mostrar_salida(resp.json())
            
        except Exception as e:
            self.mostrar_salida(f"Error: {e}")

    def ver_mapa(self):
        id_mapa = simpledialog.askstring("Mapa", "ID del Municipio a ver:", parent=self.root)
        if not id_mapa: return
        
        try:
            
            resp = requests.get(f"{intermedio_URL}/intermedio/municipios/{id_mapa}")
            
            if resp.status_code == 200:
                data = resp.json()
                self.mostrar_salida(data)
                
                
                if "centroide" in data:
                    centroide = data["centroide"]
                    lat = centroide["lat"]
                    lon = centroide["lon"]
                    
                    # URL de google maps
                    # api=1&query=lat,lon abre un marcador en ese punto
                    url = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
                    
                    self.mostrar_salida(f"🌍 Abriendo navegador en: {lat}, {lon}")
                    webbrowser.open(url)
                else:
                    messagebox.showwarning("Faltan Datos", "Este municipio no tiene coordenadas (lat/lon) cargadas.", parent=self.root)
            elif resp.status_code == 404:
                messagebox.showerror("Error", "Municipio no encontrado", parent=self.root)
            else:
                self.mostrar_salida(f"Error {resp.status_code}: {resp.text}")
                
        except Exception as e:
            self.mostrar_salida(f"Error: {e}")
    

# Ejecutar aplicación
if __name__ == "__main__":
    ventana = tk.Tk()
    app = AppMunicipios(ventana)
    ventana.mainloop()