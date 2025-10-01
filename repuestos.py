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

class Herramienta_Repuesto:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_repuestos()

    def mostrar_repuestos(self, e=None):
        self.page.clean()
        marcas = []
        if self.cursor:
            self.cursor.execute("SELECT DISTINCT marca FROM repuestos ORDER BY marca ASC")
            marcas = [row[0] for row in self.cursor.fetchall()]

        self.dropdown_busqueda = ft.Dropdown(
            label="Filtrar por Marca",
            options=[ft.dropdown.Option(m) for m in marcas],
            width=250,
            on_change=self.consulta_repuesto
        )
        buscar_btn = ft.ElevatedButton(text="Consulta", on_click=self.consulta_repuesto)
        header = ft.Row(
            controls=[
                ft.Text("Herramienta de Gestión de Repuestos", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta_repuesto),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.tabla_De_Datos = self.create_repuestos_table()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.dropdown_busqueda,
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

    def create_repuestos_table(self, filtro_marca=None):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")

        if filtro_marca:
            consulta = "SELECT id, nombre, marca, precio, stock FROM repuestos WHERE marca = %s ORDER BY nombre"
            self.cursor.execute(consulta, (filtro_marca,))
        else:
            consulta = "SELECT id, nombre, marca, precio, stock FROM repuestos ORDER BY nombre"
            self.cursor.execute(consulta)

        datos = self.cursor.fetchall()
        if not datos:
            return ft.Text("No hay repuestos registrados", size=16, color="red")

        rows = []
        for repuesto in datos:
            eliminar_button = ft.Container(
                content=ft.Image(src="iconos/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, r=repuesto: self.eliminar_repuesto(e, r),
                ink=True,
                padding=5
            )
            actualizar_button = ft.Container(
                content=ft.Image(src="iconos/modificar.png", width=28, height=28, tooltip="Modificar"),
                on_click=lambda e, r=repuesto: self.actualizar_repuesto(e, r),
                ink=True,
                padding=5
            )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(repuesto[0]))),
                        ft.DataCell(ft.Text(repuesto[1])),
                        ft.DataCell(ft.Text(repuesto[2])),
                        ft.DataCell(ft.Text(str(repuesto[3]))),
                        ft.DataCell(ft.Text(str(repuesto[4]))),
                        ft.DataCell(ft.Row(controls=[eliminar_button, actualizar_button]))
                    ]
                )
            )

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Marca")),
                ft.DataColumn(ft.Text("Precio")),
                ft.DataColumn(ft.Text("Stock")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
        )

    def eliminar_repuesto(self, e, repuesto):
        if not self.cursor:
            return
        try:
            repuesto_id = repuesto[0]
            self.cursor.execute("DELETE FROM repuestos WHERE id = %s", (repuesto_id,))
            self.connection.commit()
            self.mostrar_repuestos()
        except Exception as ex:
            print("Error al eliminar repuesto:", ex)

    def actualizar_repuesto(self, e, repuesto):
        self.page.clean()
        self.repuesto_a_modificar_id = repuesto[0]
        self.nombre = ft.TextField(label="Nombre", width=300, value=repuesto[1])
        self.marca = ft.TextField(label="Marca", width=300, value=repuesto[2])
        self.precio = ft.TextField(label="Precio", width=300, value=str(repuesto[3]))
        self.stock = ft.TextField(label="Stock", width=300, value=str(repuesto[4]))

        guardar_btn = ft.ElevatedButton(text="Guardar Cambios", on_click=self.guardar_modificacion_repuesto)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_repuestos)
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Modificar Repuesto", size=24, weight="bold"),
                    self.nombre,
                    self.marca,
                    self.precio,
                    self.stock,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_modificacion_repuesto(self, e):
        if not self.cursor:
            return
        try:
            consulta = """
                UPDATE repuestos
                SET nombre = %s,
                    marca = %s,
                    precio = %s,
                    stock = %s
                WHERE id = %s
            """
            datos = (
                self.nombre.value.strip(),
                self.marca.value.strip(),
                float(self.precio.value.strip()),
                int(self.stock.value.strip()),
                self.repuesto_a_modificar_id
            )
            self.cursor.execute(consulta, datos)
            self.connection.commit()
            self.mostrar_repuestos()
        except Exception as ex:
            print("Error al actualizar repuesto:", ex)

    def formulario_alta_repuesto(self, e):
        self.page.clean()
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.marca = ft.TextField(label="Marca", width=300)
        self.precio = ft.TextField(label="Precio", width=300)
        self.stock = ft.TextField(label="Stock", width=300)

        guardar_btn = ft.ElevatedButton(text="Guardar", on_click=self.guardar_nuevo_repuesto)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_repuestos)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Alta de Nuevo Repuesto", size=24, weight="bold"),
                    self.nombre,
                    self.marca,
                    self.precio,
                    self.stock,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_nuevo_repuesto(self, e):
        if not self.cursor:
            return
        try:
            consulta = "INSERT INTO repuestos (nombre, marca, precio, stock) VALUES (%s, %s, %s, %s)"
            datos = (
                self.nombre.value.strip(),
                self.marca.value.strip(),
                float(self.precio.value.strip()),
                int(self.stock.value.strip())
            )
            self.cursor.execute(consulta, datos)
            self.connection.commit()
            self.mostrar_repuestos()
        except Exception as ex:
            print("Error al guardar repuesto:", ex)

    def consulta_repuesto(self, e):
        marca_seleccionada = self.dropdown_busqueda.value
        if marca_seleccionada:
            self.tabla_De_Datos = self.create_repuestos_table(filtro_marca=marca_seleccionada)
        else:
            self.tabla_De_Datos = self.create_repuestos_table()
        self.page.controls[0].content.controls[3] = self.tabla_De_Datos
        self.page.update()

def main_menu_callback(page: ft.Page):
    page.clean()
    page.add(ft.Text("Menú Principal"))

def main(page: ft.Page):
    Herramienta_Repuesto(page, main_menu_callback)

# ft.app(target=main)
