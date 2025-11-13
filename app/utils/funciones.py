from flask import g, jsonify
from app.db.psql_connection_pool import PsqlConnectionPool
from app.config.config import DB_CONFIG # Configuración de la BBDD
from app.db import queries as db # Consultas a la BBDD


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
