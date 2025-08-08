#crear un inicio y recien ahi te muetre todas las barras de tareas 
import flet as ft
import mysql.connector
from cliente import Herramienta_Cliente
# from proveedor import Herramienta_Proveedor
# from producto import Herramienta_Producto

#from usuario import Herramienta_Usuario
from cliente import Herramienta_Cliente
def connect_to_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port='3306',
            user='root',
            password='root',
            database='taller_mecanico',
            ssl_disabled=True
        )
        if connection.is_connected():
            print('Conexión exitosa')
            return connection
    except Exception as ex:
        print('Conexión errónea')
        print(ex)
        return None
connection = connect_to_db()

def menu_principal(page: ft.Page): #el page: sirve para que se pueda usar el page dentro de la función y el ft.Page es el tipo de dato que se espera 
    page.bgcolor = ft.Colors.PINK_50 # Color de fondo de la página
    page.window.maximized=True#maximiza la ventana
    page.title = "Administración de Taller Mecánico" # Título de la ventana
    # ----Iconos Personales--- 
    #  Crear un Row personalizado para el PopupMenuItem y barra de herramientas
    cliente_icono = ft.Image(src="iconos/usuario.png", width=28, height=28)
    cliente_item = ft.Row(
        controls=[
            cliente_icono,
            ft.Text("Cliente"),
        ],
        alignment=ft.MainAxisAlignment.START, # Alinea el texto y el icono a la izquierda
        spacing=8
    )
    
    proveedor_icono = ft.Image(src="iconos/proveedor.png", width=28, height=28)
    proveedor_item = ft.Row(
        controls=[
            proveedor_icono,
            ft.Text("Proveedor"),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=8
    )

    repuesto_icono = ft.Image(src="iconos/caja-de-cambios.png", width=28, height=28)  
    repuesto_item = ft.Row(
        controls=[
            repuesto_icono,
            ft.Text("Repuesto"),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=8
    )
    producto_icono= ft.Image(src="iconos/producto.png", width=28, height=28)
    producto_item =ft.Row(
        controls=[
            producto_icono,
            ft.Text("Producto"),
        ],
        alignment=ft.MainAxisAlignment.START,#mainaxizalignment sirve para alinear los controles en la fila y el start es para alinear a la izquierda
        spacing=8 #sirve para separar los controles dentro de la fila
    )
    empleado_icono = ft.Image(src="iconos/empleado.png", width=28, height=28)  
    empleado_item = ft.Row(
        controls=[
            empleado_icono,
            ft.Text("Empleado"),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=8
    ) 
    
    usuario_icono = ft.Image(src="iconos/usuarios.png", width=28, height=28)  
    usuario_item = ft.Row(
        controls=[
            usuario_icono,
            ft.Text("Usuario"),
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=8
    )
    
    ficha_tecnica_icono=ft.Image(src="iconos/auto.png", width=28, height=28)
    ficha_tecnica_item=ft.Row(
        controls=[
            ficha_tecnica_icono,
            ft.Text("Ficha Técnica")
        ],
        alignment=ft.MainAxisAlignment.START,
        spacing=8
    )
    
    presupuesto_icono=ft.Image(src="./iconos/presupuesto.png", width=28, height=28)
    presupuesto_icono_item=ft.Row(
        controls=[
            presupuesto_icono,
            ft.Text("Presupuesto")
        ]
    )
    # ---Barra de Menú---
    archivo_menu = ft.PopupMenuButton( #popupmenubutton sirve para crear un menú desplegable
        items=[
            ft.PopupMenuItem(text="Copiar", icon=ft.Icons.COPY),
            #ft.PopupMenuItem(text='Pegar', icon=ft.Icons.PASTE),
            ft.PopupMenuItem(text="Salir", icon=ft.Icons.EXIT_TO_APP),
        ],
        content=ft.Text("Archivo"), tooltip="Archivo"
    )

    herramientas_menu = ft.PopupMenuButton(
        #--PopupMenuItem sirve para crear un elemento del menú desplegable
        #--content es el contenido que se muestra en el elemento del menú
        #--on_click es la función que se ejecuta cuando se hace clic en el elemento del menú
        #--lambda e: cliente(e, page) es una función anónima que se ejecuta cuando se hace clic en el elemento del menú
        #se estructura de la siguiente manera:
        #e es el evento que se genera al hacer clic en el elemento del menú , los : indica el inicio de la función anónima 
        # cliente es el nombre de la función que se ejecuta al hacer clic en el elemento del menú
        #(e, page) son los parámetros que se pasan a la función cliente, donde e es el evento y page es la página actual
        #en resumen , al hacer clic en el elemento del menú se ejecuta la función cliente y se le pasan los parámetros e y page para que pueda acceder a la página actual y al evento que se generó al hacer clic en el elemento del menú
        # mosrara 
        items=[
            ft.PopupMenuItem(content=cliente_item, on_click=lambda e: cliente(e, page)),
            ft.PopupMenuItem(content=proveedor_item, on_click=lambda e:proveedor(e, page)),
            ft.PopupMenuItem(content=producto_item,on_click=lambda e: producto(e, page)), 
            ft.PopupMenuItem(content=repuesto_item, on_click=lambda e: producto(e, page)),
            ft.PopupMenuItem(content=empleado_item, on_click=lambda e: empleado(e, page)),
            #ft.PopupMenuItem(content=usuario_item, on_click=lambda e: usuario(e, page)),
        ],
        #--content es el contenido que se muestra en el elemento del menú
        #--tooltip es el texto que se muestra al pasar el mouse por encima del elemento del menú
        content=ft.Text("Herramientas"), tooltip="Administrador de archivos maestros"
    )
    
    administracion = ft.PopupMenuButton(
        items=[
            ft.PopupMenuItem(content=ficha_tecnica_item),#, on_click=lambda e: cliente(e, page)),
            ft.PopupMenuItem(content=presupuesto_icono_item),#, on_click=lambda e:proveedor(e, page)),
        ],
        content=ft.Text("Administración"), tooltip="Administración de presupuesto y ficha técnica"
    )
    #--Barra de Herramientas--
    #--Cliente
    boton_cliente_item=ft.Row(
        controls=[
            cliente_icono,
        ],
    )
    boton_cliente = ft.IconButton(content=boton_cliente_item, tooltip="Cliente")
    #--Repuesto
    boton_repuesto_item=ft.Row(
        controls=[
            repuesto_icono,
        ],
    )
    boton_producto = ft.IconButton(content=boton_repuesto_item, tooltip="Repuesto")
    #--Ficha Técnica
    boton_ficha_tecnica_item=ft.Row(
        controls=[
                ficha_tecnica_icono,
        ]
    )
    boton_ficha_tecnica = ft.IconButton(content=boton_ficha_tecnica_item,tooltip="Ficha Técnica")
    
    #--Presupuesto
    boton_presupuesto_item=ft.Row(
        controls=[
            presupuesto_icono,
        ]
    )
    boton_presupuesto=ft.IconButton(content=boton_presupuesto_item,tooltip="Presupuesto")
    
    page.add(
        ft.Row(
            controls=[
                archivo_menu,
                administracion,
                herramientas_menu
            ],
            spacing=10,
        ),
        
        ft.Row(
            controls=[
                boton_cliente,
                boton_producto,
                boton_ficha_tecnica,
                boton_presupuesto
            ]
        )
    
    )

def cliente(e, page: ft.Page):
    Herramienta_Cliente(page, menu_principal)
def proveedor(e, page: ft.Page):
    pass
def producto(e, page: ft.Page):
    pass
def empleado(e, page: ft.Page):
    pass
#def usuario(e, page: ft.Page): #sirve basicamente para llamar a la clase Herramienta_Usuario y mostrar la ventana de gestión de usuarios
 #   Herramienta_Usuario(page, menu_principal)# 

def main(page: ft.Page):
    page.window.maximized = True
    menu_principal(page)

ft.app(target=main)
#ft.app(main, view=ft.AppView.WEB_BROWSER) 

#login con los permisos de usuario y contraseña y recien se ve el menu principal