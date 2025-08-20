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
        self.mostrar_proveedores()

    def mostrar_proveedores(self):
        self.page.clean()
        self.cursor.execute("SELECT nombre, email, telefono, direccion FROM proveedores ORDER BY nombre")
        datos = self.cursor.fetchall()
        rows = []
        for p in datos:
            eliminar_btn = ft.IconButton(ft.icons.DELETE, on_click=lambda e, c=p: self.eliminar_proveedor(e, c))
            actualizar_btn = ft.IconButton(ft.icons.EDIT, on_click=lambda e, c=p: self.actualizar_proveedor(e, c))
            rows.append(
                ft.DataRow(cells=[
                                        ft.DataCell(ft.Text(p[1])),
                                        ft.DataCell(ft.Text(p[2])),
                                        ft.DataCell(ft.Text(p[3])),
                                        ft.DataCell(ft.Text(p[4])),
                                        ft.DataCell(ft.Row([eliminar_btn, actualizar_btn]))
                                ]
                            ))
        header = ft.Row([ft.Text("Gestión de Proveedores", size=20, weight="bold"),
                        ft.ElevatedButton("Alta", on_click=self.formulario_alta_proveedor),
                        ft.ElevatedButton("<-- Volver", on_click=self.volver_al_menu)])
        self.page.add(
            ft.Column(
                [header, 
                    ft.DataTable(
                                columns=[
                                        ft.DataColumn(ft.Text("Nombre")),
                                        ft.DataColumn(ft.Text("Email")),
                                        ft.DataColumn(ft.Text("Teléfono")),
                                        ft.DataColumn(ft.Text("Dirección"))],
                rows=rows
        )]))

    def volver_al_menu(self, e):
        self.page.clean()
        self.main_menu_callback(self.page)

    def eliminar_proveedor(self, e, proveedor):
        self.cursor.execute("DELETE FROM proveedores WHERE id=%s", (proveedor[0],))
        self.connection.commit()
        self.mostrar_proveedores()

    def actualizar_proveedor(self, e, proveedor):
        self.page.clean()
        self.proveedor_id = proveedor[0]
        self.nombre = ft.TextField(label="Nombre", value=proveedor[1])
        self.email = ft.TextField(label="Email", value=proveedor[2])
        self.telefono = ft.TextField(label="Teléfono", value=proveedor[3])
        self.direccion = ft.TextField(label="Dirección", value=proveedor[4])

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar_modificacion)
        volver_btn = ft.ElevatedButton("Volver", on_click=self.mostrar_proveedores)

        self.page.add(ft.Column([self.nombre, self.email, self.telefono, self.direccion, ft.Row([guardar_btn, volver_btn])]))

    def guardar_modificacion(self, e):
        query = "UPDATE proveedores SET nombre=%s, email=%s, telefono=%s, direccion=%s WHERE id=%s"
        self.cursor.execute(query, (self.nombre.value, self.email.value, self.telefono.value, self.direccion.value, self.proveedor_id))
        self.connection.commit()
        self.mostrar_proveedores()

    def formulario_alta_proveedor(self, e):
        self.page.clean()
        self.nombre = ft.TextField(label="Nombre")
        self.email = ft.TextField(label="Email")
        self.telefono = ft.TextField(label="Teléfono")
        self.direccion = ft.TextField(label="Dirección")

        guardar_btn = ft.ElevatedButton("Guardar", on_click=self.guardar_nuevo_proveedor)
        volver_btn = ft.ElevatedButton("Volver", on_click=self.mostrar_proveedores)
        
        self.page.add(ft.Column([self.nombre, self.email, self.telefono, self.direccion, ft.Row([guardar_btn, volver_btn])]))

    def guardar_nuevo_proveedor(self, e):
        query = "INSERT INTO proveedores (nombre, email, telefono, direccion) VALUES (%s,%s,%s,%s)"
        self.cursor.execute(query, (self.nombre.value, self.email.value, self.telefono.value, self.direccion.value))
        self.connection.commit()
        self.mostrar_proveedores()

def main_menu_callback(page: ft.Page):
    page.clean()
    page.add(ft.Text("Menú Principal"))

def main(page: ft.Page):
    Herramienta_Proveedor(page, main_menu_callback)