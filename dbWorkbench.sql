CREATE DATABASE IF NOT EXISTS taller_mecanico;
USE taller_mecanico;
-- TABLA BASE
-- ================================
CREATE TABLE persona (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    apellido VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    direccion VARCHAR(200)
);
-- ROLES DE PERSONA
-- ================================
CREATE TABLE cliente (
    id_persona INT PRIMARY KEY,
    dni VARCHAR(20) UNIQUE,
    FOREIGN KEY (id_persona) REFERENCES persona(id)
);

CREATE TABLE proveedor (
    id_persona INT PRIMARY KEY,
    empresa VARCHAR(100),
    FOREIGN KEY (id_persona) REFERENCES persona(id)
);

CREATE TABLE empleado (
    id_persona INT PRIMARY KEY,
    puesto VARCHAR(100),
    FOREIGN KEY (id_persona) REFERENCES persona(id)
);

-- Usuarios solo para empleados
CREATE TABLE usuario (
    id_empleado INT PRIMARY KEY,
    usuario VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_empleado) REFERENCES empleado(id_persona)
);
-- PRODUCTOS / REPUESTOS
-- ================================
CREATE TABLE productos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    descripcion VARCHAR(255),
    precio DECIMAL(10,2),
    stock INT
);
CREATE TABLE repuestos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    marca VARCHAR(100),
    precio DECIMAL(10,2),
    stock INT
);
-- VEHÍCULOS
-- ================================
CREATE TABLE vehiculos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    marca VARCHAR(100),
    modelo VARCHAR(100),
    anio INT,
    patente VARCHAR(20),
    id_cliente INT,
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_persona)
);
-- PRESUPUESTOS
-- ================================
CREATE TABLE presupuesto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_cliente INT NOT NULL,
    id_vehiculo INT NOT NULL,
    id_empleado INT NOT NULL,
    fecha DATE,
    descripcion VARCHAR(255),
    costo_mano_obra DECIMAL(10,2),
    estado ENUM('pendiente','aceptado','rechazado') DEFAULT 'pendiente',
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_persona),
    FOREIGN KEY (id_vehiculo) REFERENCES vehiculos(id),
    FOREIGN KEY (id_empleado) REFERENCES empleado(id_persona)
);

CREATE TABLE detalle_presupuesto (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_presupuesto INT NOT NULL,
    id_repuesto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    importe_total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_presupuesto) REFERENCES presupuesto(id),
    FOREIGN KEY (id_repuesto) REFERENCES repuestos(id)
);
-- FICHAS TÉCNICAS
-- ================================
CREATE TABLE ficha_tecnica (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_presupuesto INT NOT NULL,
    descripcion VARCHAR(255),
    fecha DATE,
    costo_mano_obra DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_presupuesto) REFERENCES presupuesto(id)
);

CREATE TABLE detalle_ficha_tecnica (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_ficha_tecnica INT NOT NULL,
    id_repuesto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    importe_total DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_ficha_tecnica) REFERENCES ficha_tecnica(id),
    FOREIGN KEY (id_repuesto) REFERENCES repuestos(id)
);
-- FACTURACIÓN
-- ================================
CREATE TABLE facturacion (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_ficha_tecnica INT NOT NULL,
    monto_total DECIMAL(12,2),
    fecha DATE,
    FOREIGN KEY (id_ficha_tecnica) REFERENCES ficha_tecnica(id)
);
-- EJEMPLOS DE DATOS
-- ================================
-- Personas
INSERT INTO persona (nombre, apellido, email, telefono, direccion) VALUES
('Lucía', 'Gómez', 'lucia.gomez@example.com', '1123456789', 'Buenos Aires'),
('Mateo', 'Fernández', 'mateo.fernandez@example.com', '1134567890', 'Rosario'),
('Valentina', 'Ruiz', 'valentina.ruiz@example.com', '1145678901', 'Córdoba'),
('Santiago', 'Pérez', 'santiago.perez@example.com', '1156789012', 'Mendoza'),
('Martina', 'López', 'martina.lopez@example.com', '1167890123', 'La Plata'),
('Juan', 'Pérez', 'juan.perez@example.com', '1150000000', 'CABA');

-- Clientes
INSERT INTO cliente (id_persona, dni) VALUES
(1, '47709475'),
(2, '47009475'),
(3, '47709005'),
(4, '77709475'),
(5, '40000475'),
(6, '12345678'); -- Juan Pérez también es cliente

-- Proveedores
INSERT INTO proveedor (id_persona, empresa) VALUES
(6, 'Repuestos Juan SRL');

-- Empleados
INSERT INTO empleado (id_persona, puesto) VALUES
(4, 'Mecánico'),
(5, 'Administrativo');

-- Usuarios (solo empleados)
INSERT INTO usuario (id_empleado, usuario, contraseña) VALUES
(4, 'sperez', '123'),
(5, 'mlopez', '456');

-- Repuestos
INSERT INTO repuestos (nombre, marca, precio, stock) VALUES
('Filtro de aceite', 'Bosch', 15.99, 50),
('Pastillas de freno', 'Brembo', 45.50, 30);


-- VEHÍCULOS
INSERT INTO vehiculos (marca, modelo, anio, patente, id_cliente) VALUES
('Toyota', 'Corolla', 2018, 'ABC123', 1),
('Ford', 'Fiesta', 2020, 'DEF456', 2),
('Volkswagen', 'Golf', 2019, 'GHI789', 3),
('Chevrolet', 'Onix', 2021, 'JKL012', 4),
('Renault', 'Kangoo', 2017, 'MNO345', 5),
('Honda', 'Civic', 2022, 'PQR678', 6);
