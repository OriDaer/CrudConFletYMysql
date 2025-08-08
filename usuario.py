import flet as ft

def botonGuardar(e, nombre_usuario,gmail_usuario, contraseña_usuario):
    print(f"Nombre: {nombre_usuario.value}, Gmail: {gmail_usuario.value}, Contraseña: {contraseña_usuario.value}")
    nombre_usuario.value = ""
    gmail_usuario.value = ""
    contraseña_usuario.value = ""
    nombre_usuario.update()
    gmail_usuario.update()
    contraseña_usuario.update()

def Herramienta_Usuario(page: ft.Page):
    page.title = "Herramienta de usuario"
    nombre_usuario= ft.TextField(label="Nombre de usuario", width=300)
    gmail_usuario= ft.TextField(label="Gmail", width=300)
    contraseña_usuario = ft.TextField(label="Contraseña", password=True, width=300)
    boton_guardar =ft.ElevatedButton(text="Guardar",on_click= lambda e: botonGuardar(e,nombre_usuario,gmail_usuario,contraseña_usuario),width=150)

    page.add(nombre_usuario, gmail_usuario, contraseña_usuario, boton_guardar)

ft.app(target=Herramienta_Usuario)
#un brouse con todos los clientes y botones para cada uno y para retroceder 
#usa clasessss no metodos:)
#listado d lientes cargados, datacell y datarow,datatable