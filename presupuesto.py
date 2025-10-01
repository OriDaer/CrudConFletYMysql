import flet as ft
import mysql.connector
from datetime import date

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

class Herramienta_Presupuesto:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_presupuestos()

    def mostrar_presupuestos(self):
        self.page.clean()
        if not self.cursor:
            self.page.add(ft.Text("No hay conexión a la base de datos"))
            return

        self.cursor.execute("""
            SELECT p.id, per.nombre, per.apellido, v.marca, v.modelo, p.descripcion, p.costo_mano_obra, p.estado
            FROM presupuesto p
            JOIN cliente c ON p.id_cliente = c.id_persona
            JOIN persona per ON c.id_persona = per.id
            JOIN vehiculos v ON p.id_vehiculo = v.id
            ORDER BY p.fecha DESC
        """)
        datos = self.cursor.fetchall()

        rows = []
        for pres in datos:
            eliminar_btn = ft.Container(
                content=ft.Image(src="iconos/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, p=pres: self.eliminar_presupuesto(e, p),
                ink=True,
                padding=5
            )
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(pres[0]))),
                        ft.DataCell(ft.Text(f"{pres[1]} {pres[2]}")),
                        ft.DataCell(ft.Text(f"{pres[3]} {pres[4]}")),
                        ft.DataCell(ft.Text(pres[5])),
                        ft.DataCell(ft.Text(str(pres[6]))),
                        ft.DataCell(ft.Text(pres[7])),
                        ft.DataCell(eliminar_btn)
                    ]
                )
            )

        self.tabla_presupuestos = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Vehículo")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Costo Mano Obra")),
                ft.DataColumn(ft.Text("Estado")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=rows
        )

        header = ft.Row(
            controls=[
                ft.Text("Gestión de Presupuestos", size=20, weight="bold"),
                ft.ElevatedButton(text="Nuevo Presupuesto", on_click=self.formulario_alta_presupuesto),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.page.add(ft.Column(controls=[header, self.tabla_presupuestos]))

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def eliminar_presupuesto(self, e, pres):
        if not self.cursor:
            return
        self.cursor.execute("DELETE FROM presupuesto WHERE id = %s", (pres[0],))
        self.connection.commit()
        self.mostrar_presupuestos()

    def formulario_alta_presupuesto(self, e):
        self.page.clean()
        if not self.cursor:
            return

        # Dropdown clientes
        self.cursor.execute("SELECT c.id_persona, per.nombre, per.apellido FROM cliente c JOIN persona per ON c.id_persona = per.id")
        clientes = self.cursor.fetchall()
        self.dropdown_cliente = ft.Dropdown(
            label="Cliente",
            options=[ft.dropdown.Option(f"{c[0]} - {c[1]} {c[2]}") for c in clientes],
            width=400,
            on_change=self.cargar_vehiculos_cliente
        )

        # Dropdown vehículos
        self.dropdown_vehiculo = ft.Dropdown(label="Vehículo", width=400)

        # Dropdown empleados
        self.cursor.execute("SELECT e.id_persona, per.nombre, per.apellido FROM empleado e JOIN persona per ON e.id_persona = per.id")
        empleados = self.cursor.fetchall()
        self.dropdown_empleado = ft.Dropdown(
            label="Empleado",
            options=[ft.dropdown.Option(f"{em[0]} - {em[1]} {em[2]}") for em in empleados],
            width=400
        )

        self.descripcion = ft.TextField(label="Descripción", width=400)
        self.costo_mano_obra = ft.TextField(label="Costo Mano de Obra", width=200)
        self.estado = ft.Dropdown(
            label="Estado",
            options=[ft.dropdown.Option("pendiente"), ft.dropdown.Option("aceptado"), ft.dropdown.Option("rechazado")],
            value="pendiente",
            width=200
        )
        self.fecha = ft.DatePicker(value=date.today())

        guardar_btn = ft.ElevatedButton(text="Guardar", on_click=self.guardar_nuevo_presupuesto)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_presupuestos)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Nuevo Presupuesto", size=24, weight="bold"),
                    self.dropdown_cliente,
                    self.dropdown_vehiculo,
                    self.dropdown_empleado,
                    self.descripcion,
                    self.costo_mano_obra,
                    self.estado,
                    ft.Text("Fecha"),
                    self.fecha,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_nuevo_presupuesto(self, e):
        if not self.cursor:
            return
        if not self.dropdown_cliente.value or not self.dropdown_vehiculo.value or not self.dropdown_empleado.value:
            ft.alert("Selecciona cliente, vehículo y empleado")
            return

        id_cliente = int(self.dropdown_cliente.value.split(" - ")[0])
        id_vehiculo = int(self.dropdown_vehiculo.value.split(" - ")[0])
        id_empleado = int(self.dropdown_empleado.value.split(" - ")[0])
        descripcion = self.descripcion.value.strip()
        try:
            costo = float(self.costo_mano_obra.value)
        except:
            costo = 0.0
        estado = self.estado.value
        fecha_seleccionada = self.fecha.value if self.fecha.value else date.today()

        self.cursor.execute("""
            INSERT INTO presupuesto (id_cliente, id_vehiculo, id_empleado, fecha, descripcion, costo_mano_obra, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_cliente, id_vehiculo, id_empleado, fecha_seleccionada, descripcion, costo, estado))
        self.connection.commit()
        ft.alert("Presupuesto guardado correctamente")
        self.mostrar_presupuestos()

    def cargar_vehiculos_cliente(self, e):
        if not self.dropdown_cliente.value:
            return
        cliente_id = int(self.dropdown_cliente.value.split(" - ")[0])
        self.cursor.execute("SELECT id, marca, modelo FROM vehiculos WHERE id_cliente = %s", (cliente_id,))
        vehiculos = self.cursor.fetchall()
        self.dropdown_vehiculo.options.clear()
        for v in vehiculos:
            self.dropdown_vehiculo.options.append(ft.dropdown.Option(f"{v[0]} - {v[1]} {v[2]}"))
        self.dropdown_vehiculo.value = None
        self.page.update()