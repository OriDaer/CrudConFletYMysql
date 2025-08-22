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

class Herramienta_Empleado:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_empleados()

    def mostrar_empleados(self):
        self.page.clean()
        apellidos = []
        if self.cursor:
            self.cursor.execute("SELECT DISTINCT apellido FROM empleados ORDER BY apellido ASC")
            apellidos = [row[0] for row in self.cursor.fetchall()]

        self.dropdown_busqueda = ft.Dropdown(
            label="Filtrar por Apellido",
            options=[ft.dropdown.Option(ap) for ap in apellidos],
            width=250,
            on_change=self.consulta_empleado
        )
        buscar_btn = ft.ElevatedButton(text="Consulta", on_click=self.consulta_empleado)
        header = ft.Row(
            controls=[
                ft.Text("Herramienta de Gestión de Empleados", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta_empleado),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.data_table = self.create_empleado_table()
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

    def create_empleado_table(self, filtro_apellido=None):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        if filtro_apellido:
            query = """
                SELECT nombre, apellido, dni, puesto, telefono, id
                FROM empleados
                WHERE apellido = %s
                ORDER BY apellido
            """
            self.cursor.execute(query, (filtro_apellido,))
        else:
            query = """
                SELECT nombre, apellido, dni, puesto, telefono, id
                FROM empleados
                ORDER BY apellido
            """
            self.cursor.execute(query)

        datos_empleados = self.cursor.fetchall()
        if not datos_empleados:
            return ft.Text("No hay empleados registrados", size=16, color="red")
        rows = []
        for empleado in datos_empleados:
            flecha_icon = ft.Icon(name=ft.icons.ARROW_RIGHT, color="blue") if filtro_apellido and empleado[1] == filtro_apellido else ft.Container(width=24)
            eliminar_button = ft.Container(
                content=ft.Image(src="iconos/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, emp=empleado: self.eliminar_empleado(e, emp),
                ink=True,
                padding=5
            )
            actualizar_button = ft.Container(
                content=ft.Image(src="iconos/modificar.png", width=28, height=28, tooltip="Modificar"),
                on_click=lambda e, emp=empleado: self.actualizar_empleado(e, emp),
                ink=True,
                padding=5
            )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(flecha_icon),
                        ft.DataCell(ft.Text(empleado[0])),  # Nombre
                        ft.DataCell(ft.Text(empleado[1])),  # Apellido
                        ft.DataCell(ft.Text(empleado[2])),  # DNI
                        ft.DataCell(ft.Text(empleado[3])),  # Puesto
                        ft.DataCell(ft.Text(empleado[4])),  # Teléfono
                        ft.DataCell(ft.Text(str(empleado[5]))),  # ID
                        ft.DataCell(ft.Row(controls=[eliminar_button, actualizar_button]))
                    ],
                ),
            )

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text(" ")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("DNI")),
                ft.DataColumn(ft.Text("Puesto")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Código")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
        )

    def eliminar_empleado(self, e, empleado):
        if not self.cursor:
            return
        try:
            consulta = "DELETE FROM empleados WHERE id = %s"
            self.cursor.execute(consulta, (empleado[5],))
            self.connection.commit()
            self.mostrar_empleados()
        except Exception as ex:
            print("Error al eliminar empleado:", ex)

    def actualizar_empleado(self, e, empleado):
        self.page.clean()
        self.empleado_a_modificar_id = empleado[5]
        self.nombre = ft.TextField(label="Nombre", width=300, value=empleado[0])
        self.apellido = ft.TextField(label="Apellido", width=300, value=empleado[1])
        self.dni = ft.TextField(label="DNI", width=300, value=empleado[2])
        self.puesto = ft.TextField(label="Puesto", width=300, value=empleado[3])
        self.telefono = ft.TextField(label="Teléfono", width=300, value=empleado[4])

        guardar_btn = ft.ElevatedButton(text="Guardar Cambios", on_click=self.guardar_modificacion_empleado)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_empleados)
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Modificar Empleado", size=24, weight="bold"),
                    self.nombre,
                    self.apellido,
                    self.dni,
                    self.puesto,
                    self.telefono,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_modificacion_empleado(self, e):
        if not self.cursor:
            return
        try:
            consulta = """
                UPDATE empleados
                SET nombre = %s,
                    apellido = %s,
                    dni = %s,
                    puesto = %s,
                    telefono = %s
                WHERE id = %s
            """
            datos = (
                self.nombre.value.strip(),
                self.apellido.value.strip(),
                self.dni.value.strip(),
                self.puesto.value.strip(),
                self.telefono.value.strip(),
                self.empleado_a_modificar_id
            )
            self.cursor.execute(consulta, datos)
            self.connection.commit()
            self.mostrar_empleados()
        except Exception as ex:
            print("Error al actualizar empleado:", ex)

    def formulario_alta_empleado(self, e):
        self.page.clean()
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.apellido = ft.TextField(label="Apellido", width=300)
        self.dni = ft.TextField(label="DNI", width=300)
        self.puesto = ft.TextField(label="Puesto", width=300)
        self.telefono = ft.TextField(label="Teléfono", width=300)

        guardar_btn = ft.ElevatedButton(text="Guardar", on_click=self.guardar_nuevo_empleado)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_empleados)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Alta de Nuevo Empleado", size=24, weight="bold"),
                    self.nombre,
                    self.apellido,
                    self.dni,
                    self.puesto,
                    self.telefono,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_nuevo_empleado(self, e):
        if not self.cursor:
            return
        try:
            consulta = """
                INSERT INTO empleados (nombre, apellido, dni, puesto, telefono)
                VALUES (%s, %s, %s, %s, %s)
            """
            datos = (
                self.nombre.value.strip(),
                self.apellido.value.strip(),
                self.dni.value.strip(),
                self.puesto.value.strip(),
                self.telefono.value.strip()
            )
            self.cursor.execute(consulta, datos)
            self.connection.commit()
            self.mostrar_empleados()
        except Exception as ex:
            print("Error al guardar empleado:", ex)

    def consulta_empleado(self, e):
        apellido_seleccionado = self.dropdown_busqueda.value
        if apellido_seleccionado:
            self.data_table = self.create_empleado_table(filtro_apellido=apellido_seleccionado)
        else:
            self.data_table = self.create_empleado_table()
        self.page.controls[0].content.controls[3] = self.data_table
        self.page.update()

def main_menu_callback(page: ft.Page):
    page.clean()
    page.add(ft.Text("Menú Principal"))

def main(page: ft.Page):
    Herramienta_Empleado(page, main_menu_callback)

# ft.app(target=main)
