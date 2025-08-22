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
class Herramienta_Proveedor:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_proveedor()
    def mostrar_proveedor(self):
        self.page.clean()
        nombres = []
        if self.cursor:
            self.cursor.execute("SELECT DISTINCT nombre FROM proveedores ORDER BY nombre ASC")
            nombres = [row[0] for row in self.cursor.fetchall()]
        self.dropdown_busqueda = ft.Dropdown(
            label="Filtrar por Nombre",
            options=[ft.dropdown.Option(n) for n in nombres],
            width=250,
            on_change=self.consulta_proveedor
        )
        buscar_btn = ft.ElevatedButton(text="Consulta", on_click=self.consulta_proveedor)
        header = ft.Row(
            controls=[
                ft.Text("Herramienta de Gestión de Proveedores", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta_proveedor),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )
        self.data_table = self.create_proveedor_table()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.dropdown_busqueda,
                        buscar_btn,
                        header,
                        self.data_table
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
    def create_proveedor_table(self, filtro_nombre=None):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        if filtro_nombre:
            query = """
                SELECT nombre, email, telefono, direccion, id
                FROM proveedores
                WHERE nombre = %s
                ORDER BY nombre
            """
            self.cursor.execute(query, (filtro_nombre,))
        else:
            query = """
                SELECT nombre, email, telefono, direccion, id
                FROM proveedores
                ORDER BY nombre
            """
            self.cursor.execute(query)
        datos_proveedores = self.cursor.fetchall()
        if not datos_proveedores:
            return ft.Text("No hay proveedores registrados", size=16, color="red")
        rows = []
        for proveedor in datos_proveedores:
            flecha_icon = ft.Icon(name=ft.icons.ARROW_RIGHT, color="blue") if filtro_nombre and proveedor[0] == filtro_nombre else ft.Container(width=24)
            eliminar_button = ft.Container(
                content=ft.Image(src="iconos/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, p=proveedor: self.eliminar_proveedor(e, p),
                ink=True,
                padding=5
            )
            actualizar_button = ft.Container(
                content=ft.Image(src="iconos/modificar.png", width=28, height=28, tooltip="Modificar"),
                on_click=lambda e, p=proveedor: self.actualizar_proveedor(e, p),
                ink=True,
                padding=5
            )
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(flecha_icon),
                        ft.DataCell(ft.Text(proveedor[0])),  # Nombre
                        ft.DataCell(ft.Text(proveedor[1])),  # Email
                        ft.DataCell(ft.Text(proveedor[2])),  # Teléfono
                        ft.DataCell(ft.Text(proveedor[3])),  # Dirección
                        ft.DataCell(ft.Text(str(proveedor[4]))),  # ID
                        ft.DataCell(ft.Row(controls=[eliminar_button, actualizar_button]))
                    ],
                ),
            )
        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(" ")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
        )
    def eliminar_proveedor(self, e, proveedor):
        if not self.cursor:
            return
        try:
            consulta = "DELETE FROM proveedores WHERE id = %s"
            self.cursor.execute(consulta, (proveedor[4],))
            self.connection.commit()
            self.mostrar_proveedor()
        except Exception as ex:
            print("Error al eliminar proveedor:", ex)
    def actualizar_proveedor(self, e, proveedor):
        self.page.clean()
        self.proveedor_a_modificar_id = proveedor[4]
        self.nombre = ft.TextField(label="Nombre", width=300, value=proveedor[0])
        self.email = ft.TextField(label="Email", width=300, value=proveedor[1])
        self.telefono = ft.TextField(label="Teléfono", width=300, value=proveedor[2])
        self.direccion = ft.TextField(label="Dirección", width=300, value=proveedor[3])
        guardar_btn = ft.ElevatedButton(text="Guardar Cambios", on_click=self.guardar_modificacion_proveedor)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_proveedor)
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Modificar Proveedor", size=24, weight="bold"),
                    self.nombre,
                    self.email,
                    self.telefono,
                    self.direccion,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
    def guardar_modificacion_proveedor(self, e):
        if not self.cursor:
            return
        try:
            consulta = """
                UPDATE proveedores
                SET nombre = %s,
                    email = %s,
                    telefono = %s,
                    direccion = %s
                WHERE id = %s
            """
            datos = (
                self.nombre.value.strip(),
                self.email.value.strip(),
                self.telefono.value.strip(),
                self.direccion.value.strip(),
                self.proveedor_a_modificar_id
            )
            self.cursor.execute(consulta, datos)
            self.connection.commit()
            self.mostrar_proveedor()
        except Exception as ex:
            print("Error al actualizar proveedor:", ex)
    def formulario_alta_proveedor(self, e):
        self.page.clean()
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.email = ft.TextField(label="Email", width=300)
        self.telefono = ft.TextField(label="Teléfono", width=300)
        self.direccion = ft.TextField(label="Dirección", width=300)
        guardar_btn = ft.ElevatedButton(text="Guardar", on_click=self.guardar_nuevo_proveedor)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_proveedor)
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Alta de Nuevo Proveedor", size=24, weight="bold"),
                    self.nombre,
                    self.email,
                    self.telefono,
                    self.direccion,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
    def guardar_nuevo_proveedor(self, e):
        if not self.cursor:
            return
        try:
            consulta = """
                INSERT INTO proveedores (nombre, email, telefono, direccion)
                VALUES (%s, %s, %s, %s)
            """
            datos = (
                self.nombre.value.strip(),
                self.email.value.strip(),
                self.telefono.value.strip(),
                self.direccion.value.strip()
            )
            self.cursor.execute(consulta, datos)
            self.connection.commit()
            self.mostrar_proveedor()
        except Exception as ex:
            print("Error al guardar proveedor:", ex)
    def consulta_proveedor(self, e):
        nombre_seleccionado = self.dropdown_busqueda.value
        if nombre_seleccionado:
            self.data_table = self.create_proveedor_table(filtro_nombre=nombre_seleccionado)
        else:
            self.data_table = self.create_proveedor_table()
        self.page.controls[0].content.controls[3] = self.data_table
        self.page.update()
def main_menu_callback(page: ft.Page):
    page.clean()
    page.add(ft.Text("Menú Principal"))
def main(page: ft.Page):
    Herramienta_Proveedor(page, main_menu_callback)
# ft.app(target=main) 