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

    def mostrar_cliente(self):
        self.page.clean()
        self.text_busqueda = ft.TextField(label="Buscar por ID o Apellido", width=250)
        buscar_btn=ft.ElevatedButton(text="Consulta", on_click=self.consulta_cliente)
        header = ft.Row(
            controls=[
                ft.Text("Herramienta de Gestión de Clientes", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta_cliente),
                #ft.ElevatedButton(text="Consulta", on_click=self.consulta_cliente),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        data_table = self.create_client_table()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.text_busqueda,
                        buscar_btn,
                        header,
                        data_table
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

    def create_client_table(self):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")

        query = """
            SELECT apellido, nombre, email, dni, direccion, telefono, id
            FROM clientes 
            ORDER BY apellido
        """
        self.cursor.execute(query)
        datos_clientes = self.cursor.fetchall()
        rows = []

        for cliente in datos_clientes:
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

        data_table = ft.DataTable(
            columns=[
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
        return data_table

    def eliminar_cliente(self, e, cliente):
        if not self.cursor:
            return
        try:
            consulta = "DELETE FROM clientes WHERE id = %s"
            self.cursor.execute(consulta, (cliente[6],))
            self.connection.commit()
            print(f"Cliente {cliente[0]} eliminado exitosamente")
            self.mostrar_cliente()
        except Exception as ex:
            print("Error al eliminar cliente:", ex)

    def actualizar_cliente(self, e, cliente):
        self.page.clean()
        self.cliente_a_modificar_id = cliente[6]

        self.apellido = ft.TextField(label="Apellido", width=300, value=cliente[2])
        self.nombre = ft.TextField(label="Nombre", width=300, value=cliente[1])
        self.email = ft.TextField(label="Email", width=300, value=cliente[3])
        self.dni = ft.TextField(label="DNI", width=300, value=str(cliente[4]))
        self.direccion = ft.TextField(label="Dirección", width=300, value=cliente[6])
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
                SET nombre = %s,
                    apellido = %s,
                    email = %s,
                    dni = %s,
                    telefono= %s,
                    direccion = %s
                WHERE id = %s
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
            print("Cliente actualizado exitosamente.")
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
            self.connection.commit()
            print("Cliente agregado exitosamente")
            self.mostrar_cliente()
        except Exception as ex:
            print("Error al guardar cliente:", ex)
    def consulta_cliente(self, e):
        if not self.cursor:
            self.page.add(ft.Text("No hay conexión a la base de datos"))
            return

        texto_busqueda = self.text_busqueda.value.strip()

        if texto_busqueda == "":
            self.mostrar_cliente()
            return

        try:
            # Intentar convertir a entero para buscar por ID
            id_busqueda = int(texto_busqueda)
            consulta = """
                SELECT apellido, nombre, email, dni, direccion, telefono, id
                FROM clientes 
                WHERE id = %s
            """
            self.cursor.execute(consulta, (id_busqueda,))
        except ValueError:
            # No es número: buscar por apellido parcial (LIKE)
            consulta = """
                SELECT apellido, nombre, email, dni, direccion, telefono, id
                FROM clientes 
                WHERE apellido LIKE %s
                ORDER BY apellido
            """
            self.cursor.execute(consulta, ('%' + texto_busqueda + '%',))

        datos_filtrados = self.cursor.fetchall()

        if not datos_filtrados:
            self.page.snack_bar = ft.SnackBar(ft.Text("No se encontraron clientes con ese criterio"))
            self.page.snack_bar.open = True
            self.page.update()
            return

        rows = []
        for cliente in datos_filtrados:
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
                        ft.DataCell(ft.Text(cliente[0])),  # apellido
                        ft.DataCell(ft.Text(cliente[1])),  # nombre
                        ft.DataCell(ft.Text(cliente[2])),  # email
                        ft.DataCell(ft.Text(cliente[3])),  # dni
                        ft.DataCell(ft.Text(cliente[4])),  # direccion
                        ft.DataCell(ft.Text(cliente[5])),  # telefono
                        ft.DataCell(ft.Text(str(cliente[6]))),  # id
                        ft.DataCell(ft.Row(controls=[eliminar_button, actualizar_button]))
                    ],
                ),
            )

        data_table = ft.DataTable(
            columns=[
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

        # Reemplazamos la tabla en la UI para que se muestre el resultado filtrado
        self.page.controls[0].content.controls[1] = data_table
        self.page.update()

def main_menu_callback(page: ft.Page):
    page.clean()
    page.add(ft.Text("Menú Principal"))

def main(page: ft.Page):
    Herramienta_Cliente(page, main_menu_callback)

#ft.app(target=main)
 