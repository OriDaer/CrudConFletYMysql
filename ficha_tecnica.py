import flet as ft
import mysql.connector
from datetime import datetime

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

class Herramienta_FichaTecnica:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_fichas()

    def mostrar_fichas(self):
        self.page.clean()
        self.dropdown_cliente = ft.Dropdown(label="Filtrar por Cliente", width=250)
        self.dropdown_vehiculo = ft.Dropdown(label="Filtrar por Vehículo", width=250)
        self.cargar_clientes()
        self.cargar_vehiculos()

        buscar_btn = ft.ElevatedButton(text="Consulta", on_click=self.consulta_ficha)
        header = ft.Row(
            controls=[
                ft.Text("Herramienta de Gestión de Fichas Técnicas", size=20, weight="bold"),
                ft.ElevatedButton(text="Alta", on_click=self.formulario_alta_ficha),
                ft.ElevatedButton(text="Imprimir"),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER
        )

        self.data_table = self.create_ficha_table()
        self.page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        self.dropdown_cliente,
                        self.dropdown_vehiculo,
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

    def cargar_clientes(self):
        if self.cursor:
            self.cursor.execute("SELECT id, nombre, apellido FROM clientes ORDER BY apellido ASC")
            clientes = self.cursor.fetchall()
            self.dropdown_cliente.options = [ft.dropdown.Option(f"{c[1]} {c[2]}", key=str(c[0])) for c in clientes]
            self.page.update()

    def cargar_vehiculos(self):
        if self.cursor:
            self.cursor.execute("SELECT id, marca, modelo FROM vehiculos ORDER BY modelo ASC")
            vehiculos = self.cursor.fetchall()
            self.dropdown_vehiculo.options = [ft.dropdown.Option(f"{v[1]} {v[2]}", key=str(v[0])) for v in vehiculos]
            self.page.update()

    def create_ficha_table(self, id_cliente=None, id_vehiculo=None):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")
        if id_cliente and id_vehiculo:
            query = """
                SELECT ft.id, c.nombre, c.apellido, v.marca, v.modelo, ft.fecha, ft.costo_mano_obra
                FROM ficha_tecnica ft
                JOIN clientes c ON ft.id_cliente = c.id
                JOIN vehiculos v ON ft.id_vehiculo = v.id
                WHERE ft.id_cliente = %s AND ft.id_vehiculo = %s
                ORDER BY ft.fecha DESC
            """
            self.cursor.execute(query, (id_cliente, id_vehiculo))
        elif id_cliente:
            query = """
                SELECT ft.id, c.nombre, c.apellido, v.marca, v.modelo, ft.fecha, ft.costo_mano_obra
                FROM ficha_tecnica ft
                JOIN clientes c ON ft.id_cliente = c.id
                JOIN vehiculos v ON ft.id_vehiculo = v.id
                WHERE ft.id_cliente = %s
                ORDER BY ft.fecha DESC
            """
            self.cursor.execute(query, (id_cliente,))
        elif id_vehiculo:
            query = """
                SELECT ft.id, c.nombre, c.apellido, v.marca, v.modelo, ft.fecha, ft.costo_mano_obra
                FROM ficha_tecnica ft
                JOIN clientes c ON ft.id_cliente = c.id
                JOIN vehiculos v ON ft.id_vehiculo = v.id
                WHERE ft.id_vehiculo = %s
                ORDER BY ft.fecha DESC
            """
            self.cursor.execute(query, (id_vehiculo,))
        else:
            query = """
                SELECT ft.id, c.nombre, c.apellido, v.marca, v.modelo, ft.fecha, ft.costo_mano_obra
                FROM ficha_tecnica ft
                JOIN clientes c ON ft.id_cliente = c.id
                JOIN vehiculos v ON ft.id_vehiculo = v.id
                ORDER BY ft.fecha DESC
            """
            self.cursor.execute(query)

        datos_fichas = self.cursor.fetchall()
        if not datos_fichas:
            return ft.Text("No hay fichas técnicas registradas", size=16, color="red")
        rows = []
        for ficha in datos_fichas:
            ver_button = ft.Container(
                content=ft.Image(src="iconos/ver.png", width=28, height=28, tooltip="Ver Detalle"),
                on_click=lambda e, f=ficha: self.ver_detalle_ficha(e, f),
                ink=True,
                padding=5
            )
            eliminar_button = ft.Container(
                content=ft.Image(src="iconos/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, f=ficha: self.eliminar_ficha(e, f),
                ink=True,
                padding=5
            )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(ficha[0]))),  # ID
                        ft.DataCell(ft.Text(f"{ficha[1]} {ficha[2]}")),  # Cliente
                        ft.DataCell(ft.Text(f"{ficha[3]} {ficha[4]}")),  # Vehículo
                        ft.DataCell(ft.Text(ficha[5])),  # Fecha
                        ft.DataCell(ft.Text(f"${ficha[6]:.2f}")),  # Mano de Obra
                        ft.DataCell(ft.Row(controls=[ver_button, eliminar_button]))
                    ],
                ),
            )

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Vehículo")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Mano de Obra")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
        )

    def ver_detalle_ficha(self, e, ficha):
        self.page.clean()
        self.cursor.execute("""
            SELECT r.nombre, df.cantidad, df.precio_unitario, df.importe_total
            FROM detalle_ficha_tecnica df
            JOIN repuestos r ON df.id_repuesto = r.id
            WHERE df.id_ficha_tecnica = %s
        """, (ficha[0],))
        detalles = self.cursor.fetchall()
        rows = []
        subtotal = 0
        for detalle in detalles:
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(detalle[0])),  # Repuesto
                        ft.DataCell(ft.Text(str(detalle[1]))),  # Cantidad
                        ft.DataCell(ft.Text(f"${detalle[2]:.2f}")),  # Precio Unitario
                        ft.DataCell(ft.Text(f"${detalle[3]:.2f}")),  # Importe
                    ],
                ),
            )
            subtotal += detalle[3]

        total = subtotal + ficha[6]
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text(f"Detalle de Ficha Técnica #{ficha[0]}", size=24, weight="bold"),
                    ft.Text(f"Cliente: {ficha[1]} {ficha[2]}"),
                    ft.Text(f"Vehículo: {ficha[3]} {ficha[4]}"),
                    ft.Text(f"Fecha: {ficha[5]}"),
                    ft.DataTable(
                        columns=[
                            ft.DataColumn(ft.Text("Repuesto")),
                            ft.DataColumn(ft.Text("Cantidad")),
                            ft.DataColumn(ft.Text("Precio Unitario")),
                            ft.DataColumn(ft.Text("Importe")),
                        ],
                        rows=rows,
                    ),
                    ft.Text(f"Subtotal: ${subtotal:.2f}", size=16),
                    ft.Text(f"Mano de Obra: ${ficha[6]:.2f}", size=16),
                    ft.Text(f"Total: ${total:.2f}", size=16, weight="bold"),
                    ft.ElevatedButton("Volver", on_click=self.mostrar_fichas)
                ]
            )
        )

    def eliminar_ficha(self, e, ficha):
        if not self.cursor:
            return
        try:
            consulta = "DELETE FROM detalle_ficha_tecnica WHERE id_ficha_tecnica = %s"
            self.cursor.execute(consulta, (ficha[0],))
            consulta = "DELETE FROM ficha_tecnica WHERE id = %s"
            self.cursor.execute(consulta, (ficha[0],))
            self.connection.commit()
            self.mostrar_fichas()
        except Exception as ex:
            print("Error al eliminar ficha técnica:", ex)

    def formulario_alta_ficha(self, e):
        self.page.clean()
        self.dropdown_cliente_alta = ft.Dropdown(label="Cliente", width=300)
        self.dropdown_vehiculo_alta = ft.Dropdown(label="Vehículo", width=300)
        self.dropdown_empleado_alta = ft.Dropdown(label="Empleado", width=300)
        self.cargar_clientes_alta()
        self.cargar_vehiculos_alta()
        self.cargar_empleados_alta()
        self.fecha = ft.TextField(label="Fecha (YYYY-MM-DD)", width=300, value=datetime.now().strftime("%Y-%m-%d"))
        self.descripcion = ft.TextField(label="Descripción", width=300, multiline=True)
        self.mano_obra = ft.TextField(label="Costo de Mano de Obra", width=300)

        guardar_btn = ft.ElevatedButton(text="Guardar", on_click=self.guardar_nueva_ficha)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_fichas)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Alta de Nueva Ficha Técnica", size=24, weight="bold"),
                    self.dropdown_cliente_alta,
                    self.dropdown_vehiculo_alta,
                    self.dropdown_empleado_alta,
                    self.fecha,
                    self.descripcion,
                    self.mano_obra,
                    ft.ElevatedButton(text="Agregar Repuesto", on_click=self.agregar_repuesto),
                    ft.Column(id="repuestos_column"),
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def cargar_clientes_alta(self):
        if self.cursor:
            self.cursor.execute("SELECT id, nombre, apellido FROM clientes ORDER BY apellido ASC")
            clientes = self.cursor.fetchall()
            self.dropdown_cliente_alta.options = [ft.dropdown.Option(f"{c[1]} {c[2]}", key=str(c[0])) for c in clientes]

    def cargar_vehiculos_alta(self):
        if self.cursor:
            self.cursor.execute("SELECT id, marca, modelo FROM vehiculos ORDER BY modelo ASC")
            vehiculos = self.cursor.fetchall()
            self.dropdown_vehiculo_alta.options = [ft.dropdown.Option(f"{v[1]} {v[2]}", key=str(v[0])) for v in vehiculos]

    def cargar_empleados_alta(self):
        if self.cursor:
            self.cursor.execute("SELECT id, nombre, apellido FROM empleados ORDER BY apellido ASC")
            empleados = self.cursor.fetchall()
            self.dropdown_empleado_alta.options = [ft.dropdown.Option(f"{e[1]} {e[2]}", key=str(e[0])) for e in empleados]

    def agregar_repuesto(self, e):
        dropdown_repuesto = ft.Dropdown(label="Repuesto", width=250)
        self.cursor.execute("SELECT id, nombre FROM repuestos ORDER BY nombre ASC")
        repuestos = self.cursor.fetchall()
        dropdown_repuesto.options = [ft.dropdown.Option(r[1], key=str(r[0])) for r in repuestos]
        cantidad = ft.TextField(label="Cantidad", width=100)
        precio_unitario = ft.TextField(label="Precio Unitario", width=150)
        row = ft.Row(
            controls=[
                dropdown_repuesto,
                cantidad,
                precio_unitario,
                ft.IconButton(ft.icons.DELETE, on_click=lambda e: self.eliminar_fila_repuesto(e, row))
            ]
        )
        self.page.controls[0].content.controls[7].controls.append(row)
        self.page.update()

    def eliminar_fila_repuesto(self, e, row):
        self.page.controls[0].content.controls[7].controls.remove(row)
        self.page.update()

    def guardar_nueva_ficha(self, e):
        if not self.cursor:
            return
        try:
            consulta = """
                INSERT INTO ficha_tecnica (id_vehiculo, id_cliente, id_empleado, descripcion, fecha, costo_mano_obra)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            datos = (
                int(self.dropdown_vehiculo_alta.value),
                int(self.dropdown_cliente_alta.value),
                int(self.dropdown_empleado_alta.value),
                self.descripcion.value.strip(),
                self.fecha.value.strip(),
                float(self.mano_obra.value.strip())
            )
            self.cursor.execute(consulta, datos)
            id_ficha = self.cursor.lastrowid
            subtotal = 0
            for row in self.page.controls[0].content.controls[7].controls:
                dropdown = row.controls[0]
                cantidad = row.controls[1]
                precio = row.controls[2]
                consulta_detalle = """
                    INSERT INTO detalle_ficha_tecnica (id_ficha_tecnica, id_repuesto, cantidad, precio_unitario, importe_total)
                    VALUES (%s, %s, %s, %s, %s)
                """
                importe = int(cantidad.value) * float(precio.value)
                subtotal += importe
                self.cursor.execute(consulta_detalle, (id_ficha, int(dropdown.value), int(cantidad.value), float(precio.value), importe))
            self.connection.commit()
            self.mostrar_fichas()
        except Exception as ex:
            print("Error al guardar ficha técnica:", ex)

    def consulta_ficha(self, e):
        id_cliente = int(self.dropdown_cliente.value) if self.dropdown_cliente.value else None
        id_vehiculo = int(self.dropdown_vehiculo.value) if self.dropdown_vehiculo.value else None
        self.data_table = self.create_ficha_table(id_cliente=id_cliente, id_vehiculo=id_vehiculo)
        self.page.controls[0].content.controls[4] = self.data_table
        self.page.update()

def main_menu_callback(page: ft.Page):
    page.clean()
    page.add(ft.Text("Menú Principal"))


# ft.app(target=main)
