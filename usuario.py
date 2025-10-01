import flet as ft
import mysql.connector

def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='root',
            database='taller_mecanico',
            ssl_disabled=True
        )
        if connection.is_connected():
            print('Conexión exitosa a la base de datos')
            return connection
    except Exception as ex:
        print('Error de conexión:', ex)
        return None

class Herramienta_Usuario:
    def __init__(self, page: ft.Page): #self sirve 
        self.page = page
        page.title = "Herramienta de usuario"
        self.nombre_usuario= ft.TextField(label="Nombre de usuario", width=300)
        self.contraseña_usuario = ft.TextField(label="Contraseña", password=True, width=300)
        
        self.boton_guardar =ft.ElevatedButton(
            text="Guardar",
            on_click= self.botonGuardar,
            width=150)

        self.page.add(
            self.nombre_usuario,
            self.contraseña_usuario,
            self.boton_guardar)

    def botonGuardar(self, e):
        print(
            f"""Nombre: {self.nombre_usuario.value}, 
            Contraseña: {self.contraseña_usuario.value}""")
        self.nombre_usuario.value = ""
        self.contraseña_usuario.value = ""
        self.nombre_usuario.update()
        self.contraseña_usuario.update()
def main(page: ft.Page):
    Herramienta_Usuario(page)

ft.app(target=main)
#un brouse con todos los clientes y botones para cada uno y para retroceder 
#usa clasessss no metodos:)
#listado d lientes cargados, datacell y datarow,datatable