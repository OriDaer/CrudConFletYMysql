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

class Herramienta_FichaTecnica:
    def __init__(self, page: ft.Page, main_menu_callback):
        self.page = page
        self.main_menu_callback = main_menu_callback
        self.connection = connect_to_db()
        self.cursor = self.connection.cursor() if self.connection else None
        self.mostrar_fichas()

    def mostrar_fichas(self):
        self.page.clean()
        if not self.cursor:
            self.page.add(ft.Text("No hay conexión a la base de datos"))
            return

        self.cursor.execute("""
            SELECT f.id, p.descripcion, per.nombre, per.apellido, v.marca, v.modelo, f.fecha, f.costo_mano_obra
            FROM ficha_tecnica f
            JOIN presupuesto p ON f.id_presupuesto = p.id
            JOIN cliente c ON p.id_cliente = c.id_persona
            JOIN persona per ON c.id_persona = per.id
            JOIN vehiculos v ON p.id_vehiculo = v.id
            ORDER BY f.fecha DESC
        """)
        datos = self.cursor.fetchall()

        rows = []
        for ficha in datos:
            eliminar_btn = ft.Container(
                content=ft.Image(src="iconos/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, f=ficha: self.eliminar_ficha(e, f),
                ink=True,
                padding=5
            )
            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(ficha[0]))),
                        ft.DataCell(ft.Text(ficha[1])),
                        ft.DataCell(ft.Text(f"{ficha[2]} {ficha[3]}")),
                        ft.DataCell(ft.Text(f"{ficha[4]} {ficha[5]}")),
                        ft.DataCell(ft.Text(str(ficha[6]))),
                        ft.DataCell(ft.Text(str(ficha[7]))),
                        ft.DataCell(eliminar_btn)
                    ]
                )
            )

        self.tabla_fichas = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Descripción")),
                ft.DataColumn(ft.Text("Cliente")),
                ft.DataColumn(ft.Text("Vehículo")),
                ft.DataColumn(ft.Text("Fecha")),
                ft.DataColumn(ft.Text("Costo Mano Obra")),
                ft.DataColumn(ft.Text("Acciones"))
            ],
            rows=rows
        )

        header = ft.Row(
            controls=[
                ft.Text("Gestión de Fichas Técnicas", size=20, weight="bold"),
                ft.ElevatedButton(text="Nueva Ficha Técnica", on_click=self.formulario_alta_ficha),
                ft.ElevatedButton(text="<-- Volver al Menú", on_click=self.volver_al_menu)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )

        self.page.add(ft.Column(controls=[header, self.tabla_fichas]))

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def eliminar_ficha(self, e, ficha):
        if not self.cursor:
            return
        self.cursor.execute("DELETE FROM ficha_tecnica WHERE id = %s", (ficha[0],))
        self.connection.commit()
        self.mostrar_fichas()

    def formulario_alta_ficha(self, e):
        self.page.clean()
        if not self.cursor:
            return

        # Selección del presupuesto
        self.cursor.execute("""
            SELECT p.id, per.nombre, per.apellido, v.marca, v.modelo
            FROM presupuesto p
            JOIN cliente c ON p.id_cliente = c.id_persona
            JOIN persona per ON c.id_persona = per.id
            JOIN vehiculos v ON p.id_vehiculo = v.id
        """)
        presupuestos = self.cursor.fetchall()
        self.dropdown_presupuesto = ft.Dropdown(
            label="Presupuesto",
            options=[ft.dropdown.Option(f"{p[0]} - {p[1]} {p[2]} - {p[3]} {p[4]}") for p in presupuestos],
            width=400
        )

        self.descripcion = ft.TextField(label="Descripción", width=400)
        self.costo_mano_obra = ft.TextField(label="Costo Mano de Obra", width=200)
        self.fecha = ft.DatePicker(label="Fecha", value=date.today())

        guardar_btn = ft.ElevatedButton(text="Guardar", on_click=self.guardar_nueva_ficha)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_fichas)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Nueva Ficha Técnica", size=24, weight="bold"),
                    self.dropdown_presupuesto,
                    self.descripcion,
                    self.costo_mano_obra,
                    self.fecha,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_nueva_ficha(self, e):
        if not self.cursor:
            return
        if not self.dropdown_presupuesto.value:
            return  # no se seleccionó presupuesto

        presupuesto_id = int(self.dropdown_presupuesto.value.split(" - ")[0])
        descripcion = self.descripcion.value.strip()
        try:
            costo = float(self.costo_mano_obra.value)
        except:
            costo = 0.0
        fecha_seleccionada = self.fecha.value if self.fecha.value else date.today()

        self.cursor.execute("""
            INSERT INTO ficha_tecnica (id_presupuesto, descripcion, fecha, costo_mano_obra)
            VALUES (%s, %s, %s, %s)
        """, (presupuesto_id, descripcion, fecha_seleccionada, costo))
        self.connection.commit()
        self.mostrar_fichas()
