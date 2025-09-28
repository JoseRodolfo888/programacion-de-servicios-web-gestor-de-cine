-- Crear base de datos y tablas para el sistema de cine

CREATE DATABASE IF NOT EXISTS cine;
USE cine;

-- Tabla de roles
CREATE TABLE IF NOT EXISTS roles (
    id_rol INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL UNIQUE
);

-- Insertar roles por defecto
INSERT IGNORE INTO roles (id_rol, nombre) VALUES 
(1, 'admin'),
(2, 'user');

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    edad INT NOT NULL,
    correo VARCHAR(100) NOT NULL UNIQUE,
    contrasena VARCHAR(255) NOT NULL,
    id_rol INT DEFAULT 2,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- Insertar usuario administrador por defecto
INSERT IGNORE INTO usuarios (nombre, edad, correo, contrasena, id_rol) VALUES 
('Administrador', 30, 'admin@cinemagic.com', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 1);

-- Tabla de películas
CREATE TABLE IF NOT EXISTS peliculas (
    id_pelicula INT PRIMARY KEY AUTO_INCREMENT,
    titulo VARCHAR(200) NOT NULL,
    director VARCHAR(100) NOT NULL,
    duracion INT NOT NULL,
    clasificacion VARCHAR(10) NOT NULL,
    genero VARCHAR(50) NOT NULL,
    sinopsis TEXT,
    imagen_url VARCHAR(500),
    trailer_url VARCHAR(500),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de salas
CREATE TABLE IF NOT EXISTS salas (
    id_sala INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    capacidad INT NOT NULL,
    tipo VARCHAR(50) NOT NULL DEFAULT 'Estándar'
);

-- Insertar salas por defecto
INSERT IGNORE INTO salas (nombre, capacidad, tipo) VALUES 
('Sala 1', 50, 'Estándar'),
('Sala 2', 40, 'VIP'),
('Sala 3', 60, 'IMAX');

-- Tabla de funciones
CREATE TABLE IF NOT EXISTS funciones (
    id_funcion INT PRIMARY KEY AUTO_INCREMENT,
    id_pelicula INT NOT NULL,
    id_sala INT NOT NULL,
    horario DATETIME NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula) ON DELETE CASCADE,
    FOREIGN KEY (id_sala) REFERENCES salas(id_sala)
);

-- Tabla de asientos
CREATE TABLE IF NOT EXISTS asientos (
    id_asiento INT PRIMARY KEY AUTO_INCREMENT,
    id_funcion INT NOT NULL,
    numero_asiento INT NOT NULL,
    estado ENUM('disponible', 'ocupado', 'reservado') DEFAULT 'disponible',
    FOREIGN KEY (id_funcion) REFERENCES funciones(id_funcion) ON DELETE CASCADE,
    UNIQUE KEY unique_seat_per_function (id_funcion, numero_asiento)
);

-- Tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio DECIMAL(10,2) NOT NULL,
    categoria VARCHAR(50) NOT NULL,
    stock INT NOT NULL DEFAULT 0,
    imagen_url VARCHAR(500),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar productos por defecto
INSERT IGNORE INTO productos (nombre, descripcion, precio, categoria, stock) VALUES 
('Combo Clásico', 'Palomitas medianas + Refresco mediano', 8.50, 'combo', 100),
('Combo Familiar', 'Palomitas grandes + 2 Refrescos grandes + Nachos', 15.00, 'combo', 50),
('Palomitas Pequeñas', 'Palomitas de maíz sabor mantequilla', 3.50, 'snack', 200),
('Palomitas Medianas', 'Palomitas de maíz sabor mantequilla', 5.00, 'snack', 150),
('Palomitas Grandes', 'Palomitas de maíz sabor mantequilla', 6.50, 'snack', 100),
('Refresco Pequeño', 'Bebida  350ml', 2.50, 'bebida', 300),
('Refresco Mediano', 'Bebida  500ml', 3.50, 'bebida', 250),
('Refresco Grande', 'Bebida  750ml', 4.50, 'bebida', 200),
('Nachos con Queso', 'Nachos', 4.00, 'snack', 80),
('Dulces Variados', 'Selección de dulces y chocolates', 3.00, 'dulce', 150);

-- Tabla de boletos
CREATE TABLE IF NOT EXISTS boletos (
    id_boleto INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_funcion INT NOT NULL,
    numero_asiento INT NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('activo', 'usado', 'cancelado') DEFAULT 'activo',
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_funcion) REFERENCES funciones(id_funcion)
);

-- Tabla de ventas de productos
CREATE TABLE IF NOT EXISTS ventas_productos (
    id_venta INT PRIMARY KEY AUTO_INCREMENT,
    id_usuario INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    fecha_venta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Tabla de devoluciones
CREATE TABLE IF NOT EXISTS devoluciones (
    id_devolucion INT PRIMARY KEY AUTO_INCREMENT,
    id_boleto INT NOT NULL,
    motivo TEXT,
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado ENUM('pendiente', 'aprobada', 'rechazada') DEFAULT 'pendiente',
    FOREIGN KEY (id_boleto) REFERENCES boletos(id_boleto)
);

-- Crear índices para mejorar rendimiento
CREATE INDEX idx_funciones_horario ON funciones(horario);
CREATE INDEX idx_boletos_usuario ON boletos(id_usuario);
CREATE INDEX idx_asientos_funcion ON asientos(id_funcion);
CREATE INDEX idx_productos_categoria ON productos(categoria);
