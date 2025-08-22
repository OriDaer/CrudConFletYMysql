import flet as ft
import mysql.connector

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
            print('Conexión exitosa a la base de datos')
            return connection
    except Exception as ex:
        print('Error de conexión:', ex)
        return None

class Herramienta_Repuesto:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_repuestos()

    def mostrar_repuestos(self):
        self.page.clean()

        # Verificar conexión
        if not self.connection or not self.cursor:
            self.page.add(ft.Text("Error: No se pudo conectar a la base de datos.", color="red"))
            self.page.update()
            return

        # Obtener marcas
        marcas = []
        try:
            self.cursor.execute("SELECT DISTINCT marca FROM repuestos ORDER BY marca ASC")
            marcas = [row[0] for row in self.cursor.fetchall()]
        except Exception as ex:
            print("Error al obtener marcas:", ex)

        # Dropdown de marcas
        self.dropdown_busqueda = ft.Dropdown(
            label="Filtrar por Marca",
            options=[ft.dropdown.Option(m) for m in marcas],
            width=250,
            on_change=self.consulta_repuesto
        )

        # Botón de consulta
        buscar_btn = ft.ElevatedButton(text="Consultar", on_click=self.consulta_repuesto)

        # Header
        header = ft.Row(
            controls=[
                ft.Text("Gestión de Repuestos", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta_repuesto),
                ft.ElevatedButton(text="Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Tabla de repuestos
        self.data_table = self.create_repuesto_table()

        # Contenedor principal
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
        self.page.update()  # Asegurar que se actualice la interfaz

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def create_repuesto_table(self, filtro_marca=None):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos", color="red")

        try:
            if filtro_marca:
                query = """
                    SELECT nombre, marca, precio, stock, id
                    FROM repuestos
                    WHERE marca = %s
                    ORDER BY nombre
                """
                self.cursor.execute(query, (filtro_marca,))
            else:
                query = """
                    SELECT nombre, marca, precio, stock, id
                    FROM repuestos
                    ORDER BY nombre
                """
                self.cursor.execute(query)

            datos_repuestos = self.cursor.fetchall()

            if not datos_repuestos:
                return ft.Text("No hay repuestos registrados", size=16, color="red")

            rows = []
            for repuesto in datos_repuestos:
                eliminar_button = ft.IconButton(
                    ft.icons.DELETE,
                    tooltip="Borrar",
                    on_click=lambda e, r=repuesto: self.confirmar_eliminar_repuesto(e, r)
                )
                actualizar_button = ft.IconButton(
                    ft.icons.EDIT,
                    tooltip="Modificar",
                    on_click=lambda e, r=repuesto: self.actualizar_repuesto(e, r)
                )
                rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(repuesto[0])),
                            ft.DataCell(ft.Text(repuesto[1])),
                            ft.DataCell(ft.Text(f"${repuesto[2]:.2f}")),
                            ft.DataCell(ft.Text(str(repuesto[3]))),
                            ft.DataCell(ft.Text(str(repuesto[4]))),
                            ft.DataCell(ft.Row(controls=[eliminar_button, actualizar_button])),
                        ],
                    ),
                )

            return ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Nombre")),
                    ft.DataColumn(ft.Text("Marca")),
                    ft.DataColumn(ft.Text("Precio")),
                    ft.DataColumn(ft.Text("Stock")),
                    ft.DataColumn(ft.Text("Código")),
                    ft.DataColumn(ft.Text("Acciones")),
                ],
                rows=rows,
            )
        except Exception as ex:
            print("Error al crear la tabla:", ex)
            return ft.Text("Error al cargar los datos", color="red")

    def confirmar_eliminar_repuesto(self, e, repuesto):
        def confirmar_eliminar(e):
            try:
                consulta = "DELETE FROM repuestos WHERE id = %s"
                self.cursor.execute(consulta, (repuesto[4],))
                self.connection.commit()
                self.mostrar_repuestos()
                dialog.open = False
                self.page.update()
            except Exception as ex:
                self.page.add(ft.Text(f"Error al eliminar repuesto: {ex}", color="red"))
                self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Estás seguro de eliminar el repuesto {repuesto[0]}?"),
            actions=[
                ft.ElevatedButton("Sí", on_click=confirmar_eliminar),
                ft.ElevatedButton("No", on_click=lambda e: self.page.dialog.open(False)),
            ],
        )
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()

    def actualizar_repuesto(self, e, repuesto):
        self.page.clean()
        self.repuesto_a_modificar_id = repuesto[4]
        self.nombre = ft.TextField(label="Nombre", width=300, value=repuesto[0])
        self.marca = ft.TextField(label="Marca", width=300, value=repuesto[1])
        self.precio = ft.TextField(label="Precio", width=300, value=str(repuesto[2]))
        self.stock = ft.TextField(label="Stock", width=300, value=str(repuesto[3]))

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
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.update()

    def guardar_modificacion_repuesto(self, e):
        if not self.cursor:
            self.page.add(ft.Text("Error: No hay conexión a la base de datos.", color="red"))
            self.page.update()
            return

        try:
            nombre = self.nombre.value.strip()
            marca = self.marca.value.strip()
            precio = float(self.precio.value.strip())
            stock = int(self.stock.value.strip())

            if not all([nombre, marca]):
                raise ValueError("Nombre y marca son obligatorios.")

            consulta = """
                UPDATE repuestos
                SET nombre = %s,
                    marca = %s,
                    precio = %s,
                    stock = %s
                WHERE id = %s
            """
            datos = (nombre, marca, precio, stock, self.repuesto_a_modificar_id)
            self.cursor.execute(consulta, datos)
            self.connection.commit()
            self.mostrar_repuestos()
        except ValueError as ve:
            self.page.add(ft.Text(f"Error: {ve}", color="red"))
            self.page.update()
        except Exception as ex:
            self.page.add(ft.Text(f"Error al actualizar repuesto: {ex}", color="red"))
            self.page.update()

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
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )
        self.page.update()

    def guardar_nuevo_repuesto(self, e):
        if not self.cursor:
            self.page.add(ft.Text("Error: No hay conexión a la base de datos.", color="red"))
            self.page.update()
            return

        try:
            nombre = self.nombre.value.strip()
            marca = self.marca.value.strip()
            precio = float(self.precio.value.strip())
            stock = int(self.stock.value.strip())

            if not all([nombre, marca]):
                raise ValueError("Nombre y marca son obligatorios.")

            consulta = """
                INSERT INTO repuestos (nombre, marca, precio, stock)
                VALUES (%s, %s, %s, %s)
            """
            datos = (nombre, marca, precio, stock)
            self.cursor.execute(consulta, datos)
            self.connection.commit()
            self.mostrar_repuestos()
        except ValueError as ve:
            self.page.add(ft.Text(f"Error: {ve}", color="red"))
            self.page.update()
        except Exception as ex:
            self.page.add(ft.Text(f"Error al guardar repuesto: {ex}", color="red"))
            self.page.update()

    def consulta_repuesto(self, e):
        marca_seleccionada = self.dropdown_busqueda.value
        if marca_seleccionada:
            self.data_table = self.create_repuesto_table(filtro_marca=marca_seleccionada)
        else:
            self.data_table = self.create_repuesto_table()
        self.page.controls[0].content.controls[3] = self.data_table
        self.page.update()
