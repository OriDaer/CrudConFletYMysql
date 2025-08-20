CREATE DATABASE taller_mecanico;
USE taller_mecanico;

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    email VARCHAR(100),
    dni VARCHAR(20),
    telefono VARCHAR(20),
    direccion VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS proveedores (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  email VARCHAR(100),
  telefono VARCHAR(20),
  direccion VARCHAR(200)
);

CREATE TABLE IF NOT EXISTS productos (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  descripcion VARCHAR(255),
  precio DECIMAL(10,2),
  stock INT
);

CREATE TABLE IF NOT EXISTS empleados (
  id INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100),
  apellido VARCHAR(100),
  email VARCHAR(100),
  telefono VARCHAR(20),
  puesto VARCHAR(100)
);
CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    anio INT,
    patente VARCHAR(20),
    id_cliente INT,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);

CREATE TABLE repuestos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    marca VARCHAR(100),
    precio DECIMAL(10,2),
    stock INT
);

CREATE TABLE ficha_tecnica (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_vehiculo INT NOT NULL,
    id_cliente INT NOT NULL,
    id_empleado INT NOT NULL,
    descripcion VARCHAR(255),
    fecha DATE,
    FOREIGN KEY (id_vehiculo) REFERENCES vehiculos(id),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id),
    FOREIGN KEY (id_empleado) REFERENCES empleados(id)
);

CREATE TABLE detalle_ficha_tecnica (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_ficha_tecnica INT,
    id_repuesto INT,
    cantidad INT,
    precio_unitario DECIMAL(10,2),
    importe_total DECIMAL(10,2),
    FOREIGN KEY (id_ficha_tecnica) REFERENCES ficha_tecnica(id),
    FOREIGN KEY (id_repuesto) REFERENCES repuestos(id)
);

CREATE TABLE facturacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT,
    monto_total DECIMAL(12,2),
    fecha DATE,
    FOREIGN KEY (id_cliente) REFERENCES clientes(id)
);
ALTER TABLE ficha_tecnica ADD costo_mano_obra DECIMAL(10,2);
INSERT INTO clientes (nombre, apellido, email,dni, telefono, direccion) VALUES
('Lucía', 'Gómez', 'lucia.gomez@example.com', '47709475','1123456789', 'Buenos Aires'),
('Mateo', 'Fernández', 'mateo.fernandez@example.com','47009475', '1134567890', 'Rosario'),
('Valentina', 'Ruiz', 'valentina.ruiz@example.com', '47709005','1145678901', 'Córdoba'),
('Santiago', 'Pérez', 'santiago.perez@example.com', '77709475','1156789012', 'Mendoza'),
('Martina', 'López', 'martina.lopez@example.com', '40000475', '1167890123', 'La Plata'),
('Joaquín', 'Torres', 'joaquin.torres@example.com', '47709000','1178901234', 'San Miguel de Tucumán'),
('Camila', 'Díaz', 'camila.diaz@example.com', '48709475', '1189012345', 'Salta'),
('Benjamín', 'Sosa', 'benjamin.sosa@example.com', '52709475','1190123456', 'Mar del Plata'),
('Emma', 'Castro', 'emma.castro@example.com', '49909475','1101234567', 'Neuquén'),
('Thiago', 'Molina', 'thiago.molina@example.com', '42709475','1121345678', 'San Juan');
INSERT INTO proveedores (nombre, email, telefono, direccion) VALUES
('Repuestos Córdoba', 'contacto@repcba.com', '3511234567', 'Av. Colón 1234, Córdoba'),
('Lubricantes del Sur', 'ventas@lubrisur.com', '2217654321', 'Calle 9 N°450, La Plata'),
('Frenos y Más', 'info@frenosymas.com', '3419876543', 'San Martín 789, Rosario'),
('Motores Mendoza', 'soporte@motoresmza.com', '2615556677', 'Av. San Martín 2500, Mendoza'),
('Carrocerías Norte', 'carrocerias@norte.com', '3814445566', 'Belgrano 150, Tucumán'),
('Baterías del Litoral', 'ventas@batlitoral.com', '3793322110', 'Av. Costanera 500, Corrientes'),
('Accesorios Patagonia', 'contacto@patagoniaacc.com', '2944556677', 'Mitre 890, Bariloche');
select * from proveedores;