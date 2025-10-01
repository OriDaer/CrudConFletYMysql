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
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_cliente()

    def mostrar_cliente(self, e=None):
        self.page.clean()
        self.caja_busqueda = ft.TextField(label="Buscar por Apellido", width=300)

        buscar_btn = ft.ElevatedButton(text="Buscar", on_click=lambda e: self.consulta_cliente(e,self.caja_busqueda.value))
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

        self.tabla_De_Datos = self.crear_tablaCliente()

        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.caja_busqueda,
                        buscar_btn,
                        header,
                        self.tabla_De_Datos
                    ],
                    alignment=ft.MainAxisAlignment.START,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                padding=20
            )
        )

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def crear_tablaCliente(self, filtro_apellido=None):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")

        if filtro_apellido:
            consulta = """
                SELECT p.apellido, p.nombre, p.email, c.dni, p.direccion, p.telefono, p.id
                FROM persona p
                JOIN cliente c ON c.id_persona = p.id
                WHERE p.apellido = %s
                ORDER BY p.apellido
            """
            self.cursor.execute(consulta, (filtro_apellido,))
        else:
            consulta = """
                SELECT p.apellido, p.nombre, p.email, c.dni, p.direccion, p.telefono, p.id
                FROM persona p
                JOIN cliente c ON c.id_persona = p.id
                ORDER BY p.apellido
            """
            self.cursor.execute(consulta)

        datos_clientes = self.cursor.fetchall()
        if not datos_clientes:
            return ft.Text("No hay clientes registrados", size=16, color="red")

        rows = []
        for cliente in datos_clientes:
            flecha_icon = ft.Icon(name=ft.Icons.ARROW_RIGHT, color="blue") if filtro_apellido and cliente[0] == filtro_apellido else ft.Container(width=24)
            
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

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(flecha_icon),
                        ft.DataCell(ft.Text(cliente[0])),
                        ft.DataCell(ft.Text(cliente[1])),
                        ft.DataCell(ft.Text(cliente[2])),
                        ft.DataCell(ft.Text(cliente[3])),
                        ft.DataCell(ft.Text(cliente[4])),
                        ft.DataCell(ft.Text(cliente[5])),
                        ft.DataCell(ft.Text(str(cliente[6]))),
                        ft.DataCell(ft.Row(controls=[eliminar_button, actualizar_button]))
                    ],
                ),
            )

        return ft.DataTable(
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
        cliente_id = cliente[6]  # id de persona
        apellido = cliente[0]
        nombre = cliente[1]
    
        # Creamos el diálogo de confirmación
        dialogo_confirmar = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Desea eliminar al cliente {apellido} {nombre}?"),
            actions=[
                ft.TextButton("Sí", on_click=lambda e: self.confirmar_eliminar(dialogo_confirmar, cliente_id)),
                ft.TextButton("No", on_click=lambda e: self.cancelar_eliminar(dialogo_confirmar))
            ],
            modal=True
        )
    
        self.page.dialog = dialogo_confirmar
        self.page.update()



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
                UPDATE persona p
                JOIN cliente c ON c.id_persona = p.id
                SET p.apellido = %s,
                    p.nombre = %s,
                    p.email = %s,
                    c.dni = %s,
                    p.direccion = %s,
                    p.telefono = %s
                WHERE p.id = %s
            """
            datos = (
                self.apellido.value.strip(),
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
            # Insertar en persona
            consulta_persona = """
                INSERT INTO persona (apellido, nombre, email, telefono, direccion)
                VALUES (%s, %s, %s, %s, %s)
            """
            datos_persona = (
                self.apellido.value.strip(),
                self.nombre.value.strip(),
                self.email.value.strip(),
                self.telefono.value.strip(),
                self.direccion.value.strip()
            )
            self.cursor.execute(consulta_persona, datos_persona)
            id_nueva_persona = self.cursor.lastrowid

            # Insertar en cliente
            consulta_cliente = "INSERT INTO cliente (id_persona, dni) VALUES (%s, %s)"
            self.cursor.execute(consulta_cliente, (id_nueva_persona, self.dni.value.strip()))
            self.connection.commit()
            self.mostrar_cliente()
        except Exception as ex:
            print("Error al guardar cliente:", ex)

    def consulta_cliente(self, e, apellido_buscado):
        if apellido_buscado:
            self.tabla_De_Datos= self.crear_tablaCliente(filtro_apellido=apellido_buscado)
        else:
            self.tabla_De_Datos = self.crear_tablaCliente()
        
        self.page.controls[0].content.controls[3] = self.tabla_De_Datos 
        self.page.update()  

def main_menu_callback(page: ft.Page):
    page.clean()
    page.add(ft.Text("Menú Principal"))

def main(page: ft.Page):
    Herramienta_Cliente(page, main_menu_callback)

# ft.app(target=main)
