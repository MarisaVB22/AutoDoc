# ----------------- PROYECTOS -----------------
# Obtener todos los proyectos
GET_ALL_PROJECTS = "SELECT * FROM autodoc.proyectos;"

# Obtener un proyecto por su nombre (coincidencia parcial)
GET_PROJECT_BY_NAME = "SELECT * FROM autodoc.proyectos WHERE nombre ILIKE %s;"

# Obtener un proyecto por ID
GET_PROJECT_BY_ID = "SELECT * FROM autodoc.proyectos WHERE proyecto_id = %s;"

# Obtener url (id de sharepoint) de un proyecto por ID
GET_PROJECT_URL_BY_ID = "SELECT proyecto_url, id_sharepoint FROM autodoc.proyectos WHERE proyecto_id = %s;"

# Crear un nuevo proyecto
CREATE_PROJECT = """
    INSERT INTO autodoc.proyectos (nombre, descripcion, proyecto_url, id_sharepoint)
    VALUES (%s, %s, %s, %s) RETURNING proyecto_id;
"""
# Actualizar un proyecto existente
UPDATE_PROJECT = """
    UPDATE autodoc.proyectos
    SET nombre = %s, descripcion = %s, proyecto_url = %s
    WHERE proyecto_id = %s;
"""
# Eliminar un proyecto
DELETE_PROJECT = "DELETE FROM autodoc.proyectos WHERE proyecto_id = %s;"

# ----------------- DOCUMENTOS -----------------
# Obtener todos los documentos de un proyecto
GET_DOCUMENTS_BY_PROJECT = "SELECT * FROM autodoc.documentos WHERE proyecto_id = %s;"
# Obtener un documento por ID
GET_DOCUMENT_BY_ID = "SELECT * FROM autodoc.documentos WHERE documento_id = %s;"
# Crear un nuevo documento
CREATE_DOCUMENT = """
    INSERT INTO autodoc.documentos (proyecto_id, nombre, descripcion, url)
    VALUES (%s, %s, %s, %s) RETURNING documento_id;
"""
# Actualizar un documento existente
UPDATE_DOCUMENT = """
    UPDATE autodoc.documentos
    SET nombre = %s, descripcion = %s, url = %s
    WHERE documento_id = %s;
"""
# Eliminar un documento
DELETE_DOCUMENT = "DELETE FROM autodoc.documentos WHERE documento_id = %s;"