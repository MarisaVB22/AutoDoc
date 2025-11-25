-- Crear esquema si no existe
CREATE SCHEMA IF NOT EXISTS autodoc AUTHORIZATION autodoc_user;

-- Tabla de proyectos
CREATE TABLE IF NOT EXISTS autodoc.proyectos (
    proyecto_id SERIAL PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    proyecto_url VARCHAR(250),      -- URL pública de la carpeta
    id_sharepoint VARCHAR(100),     -- ID de la carpeta en SharePoint
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de documentos
CREATE TABLE IF NOT EXISTS autodoc.documentos (
    documento_id SERIAL PRIMARY KEY,
    proyecto_id INT NOT NULL REFERENCES autodoc.proyectos(proyecto_id) ON DELETE CASCADE,
    nombre VARCHAR(150) NOT NULL,
    descripcion TEXT,
    url VARCHAR(250),               -- URL del archivo en SharePoint/OneDrive
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar datos de ejemplo
INSERT INTO autodoc.proyectos (nombre, descripcion, proyecto_url, id_sharepoint)
VALUES 
('Proyecto AutoDoc', 'Proyecto para gestionar documentos automáticamente.', 'https://mi-proyecto.com', 'b!EjemploFolderID');

INSERT INTO autodoc.documentos (proyecto_id, nombre, descripcion, url)
VALUES
(1, 'Manual de usuario', 'Manual de usuario para AutoDoc', 'https://onedrive.fake/manual.pdf'),
(1, 'Guía de instalación', 'Guía paso a paso para instalar AutoDoc', 'https://onedrive.fake/guia.pdf');