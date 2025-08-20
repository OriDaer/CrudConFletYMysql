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
            print('Conexión exitosa')
            return connection
    except Exception as ex:
        print('Conexión errónea')
        print(ex)
        return None

class Herramienta_Cliente:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page #page sirve para acceder a la página y sus controles y ft es el objeto de la página 
        self.main_menu_callback = main_menu_callback # Callback para volver al menú principal
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None #el if self.connection es para verificar si la conexión a la base de datos fue exitosa 
        self.mostrar_cliente()
#self.cursor sirve para ejecutar consultas a la base de datos y obtener resultados
    def mostrar_cliente(self):
        self.page.clean() # Limpia la página antes de mostrar el cliente
        apellidos = []
        if self.cursor:
            self.cursor.execute("SELECT DISTINCT apellido FROM clientes ORDER BY apellido ASC")
            apellidos = [row[0] for row in self.cursor.fetchall()] #row es una tupla que contiene los resultados de la consulta y el [0] es para obtener el primer elemento de la tupla, que es el apellido 
#fetchall() sirve para obtener todos los resultados de la consulta y el [0] es para obtener el primer elemento de cada fila
        self.dropdown_busqueda = ft.Dropdown(
            label="Filtrar por Apellido",
            options=[ft.dropdown.Option(ap) for ap in apellidos],
            width=250,
            on_change=self.consulta_cliente # on_change es un evento que se dispara cuando se selecciona un elemento del dropdown
        )
        buscar_btn = ft.ElevatedButton(text="Consulta", on_click=self.consulta_cliente)
        header = ft.Row(
            controls=[
                ft.Text("Herramienta de Gestión de Clientes", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta_cliente),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.data_table = self.create_client_table()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.dropdown_busqueda,
                        buscar_btn,
                        header,
                        self.data_table
                    ],
                    alignment=ft.MainAxisAlignment.START, #
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER, 
                ),
                padding=20
            )
        )
    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)
    def create_client_table(self, filtro_apellido=None):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        if filtro_apellido:
            query = """
                SELECT apellido, nombre, email, dni, direccion, telefono, id
                FROM clientes 
                WHERE apellido = %s
                ORDER BY apellido
            """
            self.cursor.execute(query, (filtro_apellido,)) 
        else:
            query = """
                SELECT apellido, nombre, email, dni, direccion, telefono, id
                FROM clientes 
                ORDER BY apellido
            """
            self.cursor.execute(query)

        datos_clientes = self.cursor.fetchall() 
        if not datos_clientes:
            return ft.Text("No hay clientes registrados", size=16, color="red")
        rows = []
        for cliente in datos_clientes:
            #flecha-icon sirve para mostrar una flecha al lado del apellido del cliente
            flecha_icon = ft.Icon(name=ft.icons.ARROW_RIGHT, color="blue") if filtro_apellido and cliente[0] == filtro_apellido else ft.Container(width=24)
            eliminar_button = ft.Container(
                content=ft.Image(src="iconos/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, c=cliente: self.eliminar_cliente(e, c), 
                ink=True,
                padding=5
            )
            actualizar_button = ft.Container(
                content=ft.Image(src="iconos/modificar.png", width=28, height=28, tooltip="Modificar"),
                on_click=lambda e, c=cliente: self.actualizar_cliente(e, c),
                ink=True,
                padding=5
            )

            rows.append( # no uso add porque estoy creando una tabla
                #ft.DataRow sirve para crear una fila de datos en la tabla
                ft.DataRow(
                    cells=[
                        ft.DataCell(flecha_icon),
                        ft.DataCell(ft.Text(cliente[0])),  # Apellido
                        ft.DataCell(ft.Text(cliente[1])),  # Nombre
                        ft.DataCell(ft.Text(cliente[2])),  # Email
                        ft.DataCell(ft.Text(cliente[3])),  # DNI
                        ft.DataCell(ft.Text(cliente[4])),  # Dirección
                        ft.DataCell(ft.Text(cliente[5])),  # Teléfono
                        ft.DataCell(ft.Text(str(cliente[6]))),
                        ft.DataCell(ft.Row(controls=[eliminar_button, actualizar_button]))
                    ],
                ),
            )

        return ft.DataTable( # ft.datatable sirve para crear una tabla de datos y ft.datarow sirve para crear una fila de datos en la tabla
            columns=[
                ft.DataColumn(ft.Text(" ")),
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Código de Cliente")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
        )

    def eliminar_cliente(self, e, cliente):
        if not self.cursor:
            return
        try:
            consulta = "DELETE FROM clientes WHERE id = %s"
            self.cursor.execute(consulta, (cliente[6],))
            self.connection.commit()
            self.mostrar_cliente()
        except Exception as ex:
            print("Error al eliminar cliente:", ex)

    def actualizar_cliente(self, e, cliente):
        self.page.clean()
        self.cliente_a_modificar_id = cliente[6] 
        self.apellido = ft.TextField(label="Apellido", width=300, value=cliente[0])
        self.nombre = ft.TextField(label="Nombre", width=300, value=cliente[1])
        self.email = ft.TextField(label="Email", width=300, value=cliente[2])
        self.dni = ft.TextField(label="DNI", width=300, value=str(cliente[3]))
        self.direccion = ft.TextField(label="Dirección", width=300, value=cliente[4])
        self.telefono = ft.TextField(label="Teléfono", width=300, value=cliente[5])

        guardar_btn = ft.ElevatedButton(text="Guardar Cambios", on_click=self.guardar_modificacion_cliente)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_cliente)
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Modificar Cliente", size=24, weight="bold"),
                    self.apellido,
                    self.nombre,
                    self.email,
                    self.dni,
                    self.direccion,
                    self.telefono,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_modificacion_cliente(self, e):
        if not self.cursor:
            return
        try:
            consulta = """
                UPDATE clientes
                SET apellido = %s,
                    nombre = %s,
                    email = %s,
                    dni = %s,
                    direccion = %s,
                    telefono = %s
                WHERE id = %s
            """
            datos = (
                self.apellido.value.strip(), #strip() para eliminar los espacios en blanco al inicio y al final de la cadena
                self.nombre.value.strip(),
                self.email.value.strip(),
                self.dni.value.strip(),
                self.direccion.value.strip(),
                self.telefono.value.strip(),
                self.cliente_a_modificar_id
            )
            self.cursor.execute(consulta, datos)
            self.connection.commit()
            self.mostrar_cliente()
        except Exception as ex:
            print("Error al actualizar cliente:", ex)

    def formulario_alta_cliente(self, e):
        self.page.clean()
        self.apellido = ft.TextField(label="Apellido", width=300)
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.email = ft.TextField(label="Email", width=300)
        self.dni = ft.TextField(label="DNI", width=300)
        self.direccion = ft.TextField(label="Dirección", width=300)
        self.telefono = ft.TextField(label="Teléfono", width=300)

        guardar_btn = ft.ElevatedButton(text="Guardar", on_click=self.guardar_nuevo_cliente)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_cliente)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Alta de Nuevo Cliente", size=24, weight="bold"),
                    self.apellido,
                    self.nombre,
                    self.email,
                    self.dni,
                    self.direccion,
                    self.telefono,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_nuevo_cliente(self, e):
        if not self.cursor:
            return
        try:
            consulta = """
                INSERT INTO clientes (apellido, nombre, email, dni, direccion, telefono)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            datos = (
                self.apellido.value.strip(),
                self.nombre.value.strip(),
                self.email.value.strip(),
                self.dni.value.strip(),
                self.direccion.value.strip(),
                self.telefono.value.strip()
            )
            self.cursor.execute(consulta, datos)
            self.connection.commit() # sirve para guardar los cambios en la base de datos
            self.mostrar_cliente()
        except Exception as ex:
            print("Error al guardar cliente:", ex)

    def consulta_cliente(self, e): 
        apellido_seleccionado = self.dropdown_busqueda.value  #
        if apellido_seleccionado:
            self.data_table = self.create_client_table(filtro_apellido=apellido_seleccionado) 
        else:
            self.data_table = self.create_client_table() 
        # Actualizar la tabla en la página
        self.page.controls[0].content.controls[3] = self.data_table
        self.page.update()

def main_menu_callback(page: ft.Page):
    page.clean()
    page.add(ft.Text("Menú Principal"))

def main(page: ft.Page):
    Herramienta_Cliente(page, main_menu_callback)

# ft.app(target=main)
