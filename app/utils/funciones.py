import os
from flask import g, jsonify
from app.db.psql_connection_pool import PsqlConnectionPool
from app.config.config import DB_CONFIG # Configuración de la BBDD
from app.db import queries as db # Consultas a la BBDD
import requests

# Importar variables de entorno para Sharepoint
SITE_ID = os.getenv("SITE_ID")
DRIVE_ID = os.getenv("DRIVE_ID")


# ------------------ Pool por request ------------------ #
def get_db_pool():
    """
    Devuelve el pool de conexiones de la base de datos.
    Se almacena en g para que sea único por request.
    """
    if "db_pool" not in g:
        g.db_pool = PsqlConnectionPool(DB_CONFIG)
        g.db_pool.connect()  # Inicializa el pool si no está creado
    return g.db_pool

# ----------- MICROSOFT GRAPH ------------ #
# Obtiene un access token para Microsoft Graph usando Client Credentials.
def get_access_token():
    # Leer variables de entorno
    TENANT_ID = os.getenv("TENANT_ID")
    CLIENT_ID = os.getenv("CLIENT_ID")
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")

    # URL del endpoint de token de Azure AD (OAuth2)
    # Hacer la petición para obtener el token
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default"
    }
    response = requests.post(url, data=data, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

# ----------------- PRUEBA ----------------- #
def saludo():
    return "¡Hola desde funciones.py!"

"""-----------------------------------------------------------------------
                       PROYECTOS
-----------------------------------------------------------------------"""
# Devuelve la lista de proyectos. Si se pasa el parámetro "nombre", filtra por coincidencia parcial.
def obtener_proyectos(nombre=None):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        if nombre:
            cursor.execute(db.GET_PROJECT_BY_NAME, (f"%{nombre}%",))
        else:
            cursor.execute(db.GET_ALL_PROJECTS)
        proyectos = cursor.fetchall()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return proyectos

# Devuelve un proyecto por su ID.
def obtener_proyecto_por_id(proyecto_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(db.GET_PROJECT_BY_ID, (proyecto_id,))
        proyecto = cursor.fetchone()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return proyecto

# Inserta un nuevo proyecto en la base de datos y devuelve el ID
def crear_proyecto(nombre, descripcion, proyecto_url):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(db.CREATE_PROJECT, (nombre, descripcion, proyecto_url))
        proyecto_id = cursor.fetchone()["proyecto_id"]
        conn.commit()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return proyecto_id

# Crea una carpeta en Sharepoint para el proyecto
def crear_carpeta_sharepoint(nombre_carpeta):
    token = get_access_token()
    url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives/{DRIVE_ID}/root/children"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    body = {
        "name": nombre_carpeta,
        "folder": {},
        "@microsoft.graph.conflictBehavior": "rename"
    }

    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status() # Lanza error si falla
    folder_info = response.json() # JSON de Microsoft Graph

    # Devuelve la URL de la carpeta creada
    return folder_info.get("webUrl")



def modificar_proyecto(proyecto_id, nombre, descripcion, proyecto_url):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(db.UPDATE_PROJECT, (nombre, descripcion, proyecto_url, proyecto_id))
        conn.commit()
        # Si ninguna fila fue afectada, el proyecto no existía
        return cursor.rowcount > 0
    finally:
        cursor.close()
        pool.release_connection(conn)

# Elimina un proyecto dado su ID. Devuelve True si se eliminó, False si no existía.
def eliminar_proyecto(proyecto_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(db.DELETE_PROJECT, (proyecto_id,))
        if cursor.rowcount == 0:
            # No existía el proyecto
            return False
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        pool.release_connection(conn)

"""-----------------------------------------------------------------------
                       DOCUMENTOS
-----------------------------------------------------------------------"""


# Obtener todos los documentos de un proyecto
def obtener_documentos(proyecto_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(db.GET_DOCUMENTS_BY_PROJECT, (proyecto_id,))
        documentos = cursor.fetchall()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return documentos


# Crear un nuevo documento
def crear_documento(proyecto_id, nombre, descripcion, url):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            db.CREATE_DOCUMENT,
            (proyecto_id, nombre, descripcion, url)
        )
        documento_id = cursor.fetchone()["documento_id"]
        conn.commit()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return documento_id


# Obtener un documento por su ID
def obtener_documento_por_id(documento_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(db.GET_DOCUMENT_BY_ID, (documento_id,))
        documento = cursor.fetchone()
    finally:
        cursor.close()
        pool.release_connection(conn)

    return documento


# Modificar documento
def modificar_documento(documento_id, nombre, descripcion, url):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            db.UPDATE_DOCUMENT,
            (nombre, descripcion, url, documento_id)
        )
        conn.commit()

        # Si rowcount == 0 → NO existía
        return cursor.rowcount > 0

    finally:
        cursor.close()
        pool.release_connection(conn)


# Eliminar un documento
def eliminar_documento(documento_id):
    pool = get_db_pool()
    conn = pool.get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(db.DELETE_DOCUMENT, (documento_id,))
        if cursor.rowcount == 0:
            return False

        conn.commit()
        return True

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        cursor.close()
        pool.release_connection(conn)




# PRUEBA

SITE_ID = "autodocapp.sharepoint.com,0f312f13-1068-456c-9698-1e51cc3b7ab6,1a49da2b-2feb-46a1-b6b6-8fef07fe3178"
token = get_access_token()
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json"
}

url = f"https://graph.microsoft.com/v1.0/sites/{SITE_ID}/drives"
response = requests.get(url, headers=headers)
response.raise_for_status()

drives = response.json()["value"]
for drive in drives:
    print(drive["name"], drive["id"])  # Busca "Documentos compartidos"