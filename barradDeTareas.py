#crear un inicio y recien ahi te muetre todas las barras de tareas 
import flet as ft
import mysql.connector
from cliente import Herramienta_Cliente
from proveedores import Herramienta_Proveedor
# from producto import Herramienta_Producto

from usuario import Herramienta_Usuario
from cliente import Herramienta_Cliente
#from vehiculos import Herramienta_Vehiculo

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
def identificacion(page: ft.Page):
    page.clean()
    page.title="Login"
    page_bgcolor= ft.Colors.YELLOW_500
    page.windows.maximized=True
    page.window_resizable =False
    page.window_center=True #centra la ventana en la pantalla

    usuario=ft.TextField(label="Usuario", width=300)
    contraseña=ft.TextField(label="Contraseña", password=True, can_reveal_password=True,width=300) #can_reveal_password permite mostrar la contraseña al hacer clic en el icono de ojo

    formulario=ft.Column(
        controls=[
            ft.Text("iniciar sesión",size=35, weight=ft.FrontWeight.BOLD), #
            usuario,
            contraseña,
        ],alignment=ft.MainAxisAlignment.CENTER, # Alinea los controles al centro
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, # Alinea los controles horizontalmente al centro
        spacing=20 # Espacio entre los controles
    )
    def boton_login_click(e):
        consulta= '''
        select usuario,contraseña
        from detalle_usuario 
        where usuario=%s and contraseña=%s
        '''
        cursor.execute(consulta, (usuario.value, contraseña.value))
        datos_usuario = cursor.fetchone()
        if datos_usuario:
            print('usuario y contraseña correctos')
            page.clean()
            menu_principal(page)
        else:
            print('usuario o contraseña incorrectos')
            page.bgcolor=ft.Colors.BLUE_500
            page.add(
                ft.Text("Error:Usuario o contraseña incorrectos", color="red"),
                ft.ElevatedButton("Intentar nuevamente", on_click=lambda e: identificacion(page))
            )
            #btn de loogin
    boton_login = ft.ElevatedButton(text="Iniciar Sesión", on_click=boton_login_click, width=150)
    #contenedor p el formulario
    form_content=ft.Column(
        controls=[
            ft.Text("Iniciar Sesión", size=35, weight=ft.FontWeight.BOLD),
            usuario,
            contraseña,
            boton_login
        ],
        alignment=ft.MainAxisAlignment.CENTER, # Alinea los controles al centro
        horizontal_alignment=ft.CrossAxisAlignment.CENTER, # Alinea los controles horizontalmente al centro
        spacing=20 # Espacio entre los controles
    )
    #agregar el contenedor principal a la pg con alineación central
    page.add(
        ft.Container(
            content=form_content,
            alignment=ft.alignment.center, # Alinea el contenedor al centro de la
            width=400, # Ancho del contenedor
        ))
    
def menu_principal(page: ft.Page): #el page: sirve para que se pueda usar el page dentro de la función y el ft.Page es el tipo de dato que se espera 
    page.bgcolor = ft.Colors.PINK_50 # Color de fondo de la página
    page.window.maximized=True#maximiza la ventana
    page.title = "Administración de Taller Mecánico" # Título de la ventana
    # ----Iconos Personales--- 
    #se inicializan los iconos que se van a usar en la barra de tareas junto con su posicion
    # barra de tareas personalizada con iconos y texto("header")
    #  Crear un Row personalizado para el PopupMenuItem y barra de herramientas
    cliente_icono = ft.Image(src="iconos/usuario.png", width=28, height=28)
    cliente_item = ft.Row( # sirve
        controls=[
            cliente_icono, # Row sirve para crear una fila de controles 
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
    # -------------------Barra de Menú-------------------------------
    #--PopupMenuButton sirve para crear un botón que despliega un menú al hacer clic en él
    archivo_menu = ft.PopupMenuButton( #popupmenubutton sirve para crear un menú desplegable
        items=[
            ft.PopupMenuItem(text="Copiar", icon=ft.Icons.COPY),
            #ft.PopupMenuItem(text='Pegar', icon=ft.Icons.PASTE),
            ft.PopupMenuItem(text="Salir", icon=ft.Icons.EXIT_TO_APP),
        ],
        content=ft.Text("Archivo"), tooltip="Archivo"
    )
#se usa los icono inicializados anteriormente p usar en el header
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
    #------------------Barra de Herramientas----------------
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
    #iconbutton sirve para crear un botón con un icono
    #tooltip sirve para mostrar un texto al pasar el mouse por encima del botón
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
    Herramienta_Proveedor(page, menu_principal)
    
def producto(e, page: ft.Page):
    pass
def empleado(e, page: ft.Page):
    pass
#def usuario(e, page: ft.Page): #sirve basicamente para llamar a la clase Herramienta_Usuario y mostrar la ventana de gestión de usuarios
#   Herramienta_Usuario(page, menu_principal)# 

def main(page: ft.Page):
    page.window.maximized = True
    menu_principal(page)

ft.app(target=main) #sirve para ejecutar la aplicación y pasarle la función main como objetivo
#ft.app(main, view=ft.AppView.WEB_BROWSER) 

#login con los permisos de usuario y contraseña y recien se ve el menu principal