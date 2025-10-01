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

    def mostrar_proveedor(self, e=None):
        self.page.clean()
        self.caja_busqueda = ft.TextField(label="Buscar por Empresa", width=300)

        buscar_btn = ft.ElevatedButton(
            text="Buscar",
            on_click=lambda e: self.consulta_proveedor(e, self.caja_busqueda.value)
        )

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

        self.tabla_De_Datos = self.crear_tablaProveedor()

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

    def crear_tablaProveedor(self, filtro_empresa=None):
        if not self.cursor:
            return ft.Text("No hay conexión a la base de datos")

        if filtro_empresa:
            consulta = """
                SELECT p.apellido, p.nombre, p.email, pr.empresa, p.direccion, p.telefono, p.id
                FROM persona p
                JOIN proveedor pr ON pr.id_persona = p.id
                WHERE pr.empresa = %s
                ORDER BY pr.empresa
            """
            self.cursor.execute(consulta, (filtro_empresa,))
        else:
            consulta = """
                SELECT p.apellido, p.nombre, p.email, pr.empresa, p.direccion, p.telefono, p.id
                FROM persona p
                JOIN proveedor pr ON pr.id_persona = p.id
                ORDER BY pr.empresa
            """
            self.cursor.execute(consulta)

        datos_proveedores = self.cursor.fetchall()
        if not datos_proveedores:
            return ft.Text("No hay proveedores registrados", size=16, color="red")

        rows = []
        for proveedor in datos_proveedores:
            eliminar_button = ft.Container(
                content=ft.Image(src="iconos/bote-de-basura.png", width=28, height=28, tooltip="Borrar"),
                on_click=lambda e, c=proveedor: self.eliminar_proveedor(e, c),
                ink=True,
                padding=5
            )

            actualizar_button = ft.Container(
                content=ft.Image(src="iconos/modificar.png", width=28, height=28, tooltip="Modificar"),
                on_click=lambda e, c=proveedor: self.actualizar_proveedor(e, c),
                ink=True,
                padding=5
            )

            rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(proveedor[0])),  # Apellido
                        ft.DataCell(ft.Text(proveedor[1])),  # Nombre
                        ft.DataCell(ft.Text(proveedor[2])),  # Email
                        ft.DataCell(ft.Text(proveedor[3])),  # Empresa
                        ft.DataCell(ft.Text(proveedor[4])),  # Dirección
                        ft.DataCell(ft.Text(proveedor[5])),  # Teléfono
                        ft.DataCell(ft.Text(str(proveedor[6]))),  # ID Persona
                        ft.DataCell(ft.Row(controls=[eliminar_button, actualizar_button]))
                    ],
                ),
            )

        return ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("Apellido")),
                ft.DataColumn(ft.Text("Nombre")),
                ft.DataColumn(ft.Text("Email")),
                ft.DataColumn(ft.Text("Empresa")),
                ft.DataColumn(ft.Text("Dirección")),
                ft.DataColumn(ft.Text("Teléfono")),
                ft.DataColumn(ft.Text("Código Persona")),
                ft.DataColumn(ft.Text("Acciones")),
            ],
            rows=rows,
        )

    def eliminar_proveedor(self, e, proveedor):
        proveedor_id = proveedor[6]
        empresa = proveedor[3]

        dialogo_confirmar = ft.AlertDialog(
            title=ft.Text("Confirmar eliminación"),
            content=ft.Text(f"¿Desea eliminar al proveedor de la empresa {empresa}?"),
            actions=[
                ft.TextButton("Sí", on_click=lambda e: self.confirmar_eliminar(dialogo_confirmar, proveedor_id)),
                ft.TextButton("No", on_click=lambda e: self.cancelar_eliminar(dialogo_confirmar))
            ],
            modal=True
        )

        self.page.dialog = dialogo_confirmar
        self.page.update()

    def confirmar_eliminar(self, dialogo, proveedor_id):
        self.cursor.execute("DELETE FROM proveedor WHERE id_persona=%s", (proveedor_id,))
        self.cursor.execute("DELETE FROM persona WHERE id=%s", (proveedor_id,))
        self.connection.commit()
        self.page.dialog = None
        self.mostrar_proveedor()

    def cancelar_eliminar(self, dialogo):
        self.page.dialog = None
        self.page.update()

    def actualizar_proveedor(self, e, proveedor):
        self.page.clean()
        self.proveedor_a_modificar_id = proveedor[6]
        self.apellido = ft.TextField(label="Apellido", width=300, value=proveedor[0])
        self.nombre = ft.TextField(label="Nombre", width=300, value=proveedor[1])
        self.email = ft.TextField(label="Email", width=300, value=proveedor[2])
        self.empresa = ft.TextField(label="Empresa", width=300, value=proveedor[3])
        self.direccion = ft.TextField(label="Dirección", width=300, value=proveedor[4])
        self.telefono = ft.TextField(label="Teléfono", width=300, value=proveedor[5])

        guardar_btn = ft.ElevatedButton(text="Guardar Cambios", on_click=self.guardar_modificacion_proveedor)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_proveedor)
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Modificar Proveedor", size=24, weight="bold"),
                    self.apellido,
                    self.nombre,
                    self.email,
                    self.empresa,
                    self.direccion,
                    self.telefono,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_modificacion_proveedor(self, e):
        consulta = """
            UPDATE persona p
            JOIN proveedor pr ON pr.id_persona = p.id
            SET p.apellido = %s,
                p.nombre = %s,
                p.email = %s,
                pr.empresa = %s,
                p.direccion = %s,
                p.telefono = %s
            WHERE p.id = %s
        """
        datos = (
            self.apellido.value.strip(),
            self.nombre.value.strip(),
            self.email.value.strip(),
            self.empresa.value.strip(),
            self.direccion.value.strip(),
            self.telefono.value.strip(),
            self.proveedor_a_modificar_id
        )
        self.cursor.execute(consulta, datos)
        self.connection.commit()
        self.mostrar_proveedor()

    def formulario_alta_proveedor(self, e):
        self.page.clean()
        self.apellido = ft.TextField(label="Apellido", width=300)
        self.nombre = ft.TextField(label="Nombre", width=300)
        self.email = ft.TextField(label="Email", width=300)
        self.empresa = ft.TextField(label="Empresa", width=300)
        self.direccion = ft.TextField(label="Dirección", width=300)
        self.telefono = ft.TextField(label="Teléfono", width=300)

        guardar_btn = ft.ElevatedButton(text="Guardar", on_click=self.guardar_nuevo_proveedor)
        volver_btn = ft.ElevatedButton(text="Volver", on_click=self.mostrar_proveedor)

        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Alta de Nuevo Proveedor", size=24, weight="bold"),
                    self.apellido,
                    self.nombre,
                    self.email,
                    self.empresa,
                    self.direccion,
                    self.telefono,
                    ft.Row(controls=[guardar_btn, volver_btn], alignment=ft.MainAxisAlignment.CENTER)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
        )

    def guardar_nuevo_proveedor(self, e):
        self.mensaje = ft.Text("")

    # Chequear campos vacíos
        if (not self.apellido.value.strip() or
            not self.nombre.value.strip() or
            not self.email.value.strip() or
            not self.telefono.value.strip() or
            not self.direccion.value.strip() or
            not self.empresa.value.strip()):
            # Mostrar mensaje de error y cortar la ejecución
            self.mensaje.value = "⚠️ Completa todos los campos antes de guardar"
            self.mensaje.color = "red"
            self.page.update()
            return   # con este return NO se guarda nada

        # --- si llega acá es porque todos los campos están completos ---
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

        consulta_proveedor = "INSERT INTO proveedor (id_persona, empresa) VALUES (%s, %s)"
        self.cursor.execute(consulta_proveedor, (id_nueva_persona, self.empresa.value.strip()))
        self.connection.commit()

        # Mensaje de éxito
        self.mensaje.value = "✅ Proveedor guardado correctamente"
        self.mensaje.color = "green"
        self.page.update()

        # Refrescar listado
        self.mostrar_proveedor()


    def consulta_proveedor(self, e, empresa_buscada):
        if empresa_buscada:
            self.tabla_De_Datos = self.crear_tablaProveedor(filtro_empresa=empresa_buscada)
        else:
            self.tabla_De_Datos = self.crear_tablaProveedor()

        self.page.controls[0].content.controls[3] = self.tabla_De_Datos
        self.page.update()
