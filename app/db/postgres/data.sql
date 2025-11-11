-- Crear esquema si no existe
CREATE SCHEMA IF NOT EXISTS documentos AUTHORIZATION autodoc_user;

-- Crear tabla
CREATE TABLE IF NOT EXISTS documentos.documentos (
    documento_id SERIAL PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    contenido TEXT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de ejemplo
INSERT INTO documentos.documentos (titulo, contenido)
VALUES 
('Manual de usuario', 'Este es el manual de usuario para la aplicación AutoDoc.'),
('Guía de instalación', 'Instrucciones paso a paso para instalar y configurar AutoDoc.');