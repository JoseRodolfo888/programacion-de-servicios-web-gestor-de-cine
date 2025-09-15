-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS cine;
USE cine;

-- Tabla de roles
CREATE TABLE IF NOT EXISTS roles (
    id_rol INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    edad INT NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña VARCHAR(255) NOT NULL,
    id_rol INT DEFAULT 2,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_rol) REFERENCES roles(id_rol)
);

-- Tabla de películas
CREATE TABLE IF NOT EXISTS peliculas (
    id_pelicula INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(255) NOT NULL,
    director VARCHAR(100),
    duracion INT NOT NULL,
    clasificacion VARCHAR(10),
    genero VARCHAR(50)
);

-- Tabla de salas
CREATE TABLE IF NOT EXISTS salas (
    id_sala INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    capacidad INT NOT NULL,
    estado ENUM('disponible', 'mantenimiento') DEFAULT 'disponible'
);

-- Tabla de funciones
CREATE TABLE IF NOT EXISTS funciones (
    id_funcion INT AUTO_INCREMENT PRIMARY KEY,
    id_pelicula INT,
    id_sala INT,
    horario DATETIME NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_pelicula) REFERENCES peliculas(id_pelicula),
    FOREIGN KEY (id_sala) REFERENCES salas(id_sala)
);

-- Tabla de asientos
CREATE TABLE IF NOT EXISTS asientos (
    id_asiento INT AUTO_INCREMENT PRIMARY KEY,
    id_funcion INT,
    numero_asiento VARCHAR(10) NOT NULL,
    estado ENUM('disponible', 'ocupado') DEFAULT 'disponible',
    FOREIGN KEY (id_funcion) REFERENCES funciones(id_funcion)
);

-- Tabla de boletos
CREATE TABLE IF NOT EXISTS boletos (
    id_boleto INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT,
    id_funcion INT,
    id_asiento INT,
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario),
    FOREIGN KEY (id_funcion) REFERENCES funciones(id_funcion),
    FOREIGN KEY (id_asiento) REFERENCES asientos(id_asiento)
);

-- Tabla de productos
CREATE TABLE IF NOT EXISTS productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    precio DECIMAL(10,2) NOT NULL,
    stock INT DEFAULT 0
);

-- Tabla de movimientos de inventario
CREATE TABLE IF NOT EXISTS movimientos_inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT,
    cantidad INT NOT NULL,
    tipo ENUM('entrada', 'salida') NOT NULL,
    motivo TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- Tabla de pagos
CREATE TABLE IF NOT EXISTS pagos (
    id_pago INT AUTO_INCREMENT PRIMARY KEY,
    id_boleto INT,
    metodo ENUM('tarjeta', 'paypal', 'efectivo', 'cripto') NOT NULL,
    estado ENUM('pendiente', 'completado', 'rechazado') DEFAULT 'pendiente',
    fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_boleto) REFERENCES boletos(id_boleto)
);

-- Tabla de devoluciones
CREATE TABLE IF NOT EXISTS devoluciones (
    id_devolucion INT AUTO_INCREMENT PRIMARY KEY,
    id_boleto INT,
    motivo TEXT NOT NULL,
    estado ENUM('pendiente', 'aprobada', 'rechazada') DEFAULT 'pendiente',
    fecha_solicitud TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_boleto) REFERENCES boletos(id_boleto)
);

-- Insertar datos iniciales
INSERT IGNORE INTO roles (id_rol, nombre) VALUES
(1, 'Administrador'),
(2, 'Usuario');

INSERT IGNORE INTO usuarios (nombre, edad, correo, contraseña, id_rol) VALUES
('Admin Principal', 30, 'admin@cinemagic.com', 'admin123', 1),
('Usuario Demo', 25, 'usuario@cinemagic.com', 'user123', 2);

INSERT IGNORE INTO peliculas (titulo, director, duracion, clasificacion, genero) VALUES
('El Padrino', 'Francis Ford Coppola', 175, 'A', 'Drama'),
('Pulp Fiction', 'Quentin Tarantino', 154, 'B', 'Crimen'),
('El Señor de los Anillos', 'Peter Jackson', 178, 'A', 'Fantasía');

INSERT IGNORE INTO salas (nombre, capacidad) VALUES
('Sala Premium 1', 100),
('Sala Standard 2', 80),
('Sala 3D 3', 120);

INSERT IGNORE INTO productos (nombre, precio, stock) VALUES
('Palomitas Grandes', 85.00, 50),
('Refresco', 45.00, 100),
('Nachos', 65.00, 30);