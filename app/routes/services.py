from flask import jsonify, request, g
from app import app
from app.utils import funciones as funcs
from app.auth.auth import requires_auth # Importar el decorador de autenticación

# -------------------- RUTA DE PRUEBA -------------------- #
# PRUEBA - Llamada a la función saludo desde funciones.py
@app.route("/saludo", methods=["GET"])
@requires_auth
def saludo_route():
    data = funcs.saludo()
    return jsonify({"saludo": data})

# --------------------  Obtener info del usuario autenticado -------------------- #
@app.route("/me", methods=["GET"])
@requires_auth
def get_my_info():
    user = g.user
    return jsonify({
        "id": user["id"],
        "email": user["email"]
    })

# -------------------- ACCESS TOKEN MICROSOFT GRAPH -------------------- #
# Devuelve un token de acceso para Microsoft Graph
@app.route("/test-token", methods=["GET"])
@requires_auth
def test_token():
    try:
        token = funcs.get_access_token()
        return jsonify({"token_preview": token[:50] + "..."})
    except Exception as e:
        return jsonify({"error": str(e)})

"""-----------------------------------------------------------------------
                       PROYECTOS
-----------------------------------------------------------------------"""
# -------------------- OBTENER PROYECTOS -------------------- #
# Devuelve todos los proyectos o filtra por nombre si se proporciona el parámetro
@app.route("/proyectos", methods=["GET"])
@requires_auth
def obtener_proyectos_endpoint():
    nombre = request.args.get("nombre")
    proyectos_raw = funcs.obtener_proyectos(nombre)

    # Transformar cada proyecto al formato esperado
    proyectos = [
        {
            "idProyecto": p["proyecto_id"],
            "nombre": p["nombre"],
            "descripcion": p["descripcion"],
            "proyecto_url": p["proyecto_url"]
        }
        for p in proyectos_raw
    ]
    return jsonify(proyectos)


# -------------------- OBTENER UN PROYECTO POR ID -------------------- #
# Devuelve un proyecto específico por su ID
@app.route("/proyectos/<int:id>", methods=["GET"])
@requires_auth
def obtener_proyecto_por_id_endpoint(id):
    proyecto_raw = funcs.obtener_proyecto_por_id(id)

    if not proyecto_raw:
        return jsonify({"mensaje": "No se encontró el proyecto con ese ID"}), 404

    # Transformar el resultado al formato esperado
    proyecto = {
        "idProyecto": proyecto_raw["proyecto_id"],
        "nombre": proyecto_raw["nombre"],
        "descripcion": proyecto_raw["descripcion"],
        "proyecto_url": proyecto_raw["proyecto_url"]
    }

    return jsonify(proyecto)


# -------------------- CREAR UN NUEVO PROYECTO -------------------- #
@app.route("/proyectos", methods=["POST"])
@requires_auth
def crear_proyecto_endpoint():
    # Obtener los datos del request body
    data = request.get_json()

    # Validar que vengan todos los campos requeridos
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")

    if not nombre or not descripcion:
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

    # Crear carpeta en Sharepoint y obtener URL + folder_id
    try:
        proyecto_url, id_sharepoint = funcs.crear_carpeta_sharepoint(nombre)
    except Exception as e:
        return jsonify({"error": f"No se pudo crear la carpeta en SharePoint: {str(e)}"}), 500

    # Guardar el nuevo proyecto en la BBDD
    proyecto_id = funcs.crear_proyecto(nombre, descripcion, proyecto_url, id_sharepoint)

    return jsonify({
        "mensaje": "Proyecto creado correctamente",
        "proyecto_id": proyecto_id,
        "proyecto_url": proyecto_url
    }), 200

# -------------------- MODIFICAR PROYECTO -------------------- #
@app.route("/proyectos/<int:id>", methods=["PUT"])
@requires_auth
def modificar_proyecto_endpoint(id):
    # Obtener datos del request
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos para actualizar"}), 400

    nombre = data.get("nombre")
    descripcion = data.get("descripcion")

    # Validar campos obligatorios (opcional si quieres que todos sean requeridos)
    if not all([nombre, descripcion]):
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400
    
    # --- 1. Modificar en SharePoint ---
    try:
        proyecto_url  = funcs.modificar_proyecto_sharepoint(id, nombre)
    except Exception as e:
        return jsonify({"error": f"No se pudo actualizar la carpeta en SharePoint: {str(e)}"}), 500
    
    # --- 2. Modificar en BBDD ---
    # Llamar a la función que actualiza el proyecto en la BBDD
    actualizado = funcs.modificar_proyecto_bbdd(id, nombre, descripcion, proyecto_url)

    if not actualizado:
        return jsonify({"mensaje": "No se pudo actualizar en la BBDD"}), 404

    return jsonify({"mensaje": "Proyecto actualizado correctamente"})


# -------------------- ELIMINAR PROYECTO -------------------- #
@app.route("/proyectos/<int:id>", methods=["DELETE"])
@requires_auth
def eliminar_proyecto_endpoint(id):
    # Llamamos a la función auxiliar que elimina el proyecto
    try: 
        eliminado = funcs.eliminar_proyecto(id)

    except Exception as e:
        return jsonify({"error": f"No se pudo eliminar el proyecto: {str(e)}"}), 500

    if not eliminado:
        return jsonify({"mensaje": "No se encontró el proyecto con ese ID"}), 404

    return jsonify({"mensaje": "Proyecto eliminado correctamente"})

"""-----------------------------------------------------------------------
                       DOCUMENTOS
-----------------------------------------------------------------------"""

# -------------------- LISTAR DOCUMENTOS DE UN PROYECTO -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos", methods=["GET"])
@requires_auth
def obtener_documentos_endpoint(idProyecto):
    documentos_raw = funcs.obtener_documentos(idProyecto)

    # Transformar cada documento al formato esperado
    documentos = [
        {
            "idDocumento": d["documento_id"],
            "idProyecto": d["proyecto_id"],
            "nombre": d["nombre"],
            "descripcion": d["descripcion"],
            "url": d["url"],
            "fecha": d["fecha_creacion"]
        }
        for d in documentos_raw
    ]

    return jsonify(documentos)


# -------------------- SUBIR DOCUMENTO (ARCHIVO) A SHAREPOINT Y REGISTRARLO EN LA BBDD -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos", methods=["POST"])
@requires_auth
def crear_documento_endpoint(idProyecto):
    if "file" not in request.files:
        return jsonify({"mensaje": "No se recibió archivo"}), 400

    nombre = request.form.get("nombre")
    descripcion = request.form.get("descripcion")
    archivo = request.files["file"]

    if not nombre or not descripcion or not archivo:
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400
    
    # Obtener folder_id del proyecto
    folder_id = funcs.obtener_info_proyecto(idProyecto)

    # Subir el archivo a SharePoint
    try:
        contenido_bytes = archivo.read()
        archivo_url, archivo_id = funcs.subir_archivo_sharepoint(archivo.filename, contenido_bytes, folder_id)
    except Exception as e:
        return jsonify({"error": f"No se pudo subir el archivo a SharePoint: {str(e)}"}), 500

    # Registrar documento en BBDD
    documento_id = funcs.crear_documento(idProyecto, nombre, descripcion, archivo_url, archivo_id)

    return jsonify({
        "mensaje": "Documento creado correctamente",
        "documento_id": documento_id,
        "url": archivo_url
    }), 200



# -------------------- OBTENER DOCUMENTO POR ID -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos/<int:idDocumento>", methods=["GET"])
@requires_auth
def obtener_documento_por_id_endpoint(idProyecto, idDocumento):
    documento_raw = funcs.obtener_documento_por_id(idDocumento)

    if not documento_raw:
        return jsonify({"mensaje": "No se encontró el documento con ese ID"}), 404

    # Transformar al formato esperado
    documento = {
        "idDocumento": documento_raw["documento_id"],
        "idProyecto": documento_raw["proyecto_id"],
        "nombre": documento_raw["nombre"],
        "descripcion": documento_raw["descripcion"],
        "url": documento_raw["url"],
        "fecha": documento_raw["fecha_creacion"]
    }

    return jsonify(documento)


# -------------------- MODIFICAR DOCUMENTO -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos/<int:idDocumento>", methods=["PUT"])
@requires_auth
def modificar_documento_endpoint(idProyecto, idDocumento):
    """
    Endpoint para modificar un documento existente.
    Se puede actualizar:
    - Nombre visible del documento y descripción (en BBDD)
    - Archivo subido (reemplazando el anterior) (en SharePoint)
    """
    data = request.form
    archivo = request.files.get("file")
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")

    if not nombre or not descripcion:
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

    # --- 1. Si hay archivo, reemplazar en SharePoint y actualizar BD ---
    nueva_url = None
    if archivo:
        # --- Obtener info del documento ---
        try:
            sharepoint_id = funcs.obtener_info_documento(idDocumento)
        except Exception as e:
            return jsonify({"error": f"No se encontró el documento en SharePoint: {str(e)}"}), 404

        # --- Actualizar en SharePoint ---
        try:
            contenido_bytes = archivo.read() if archivo else None

            nueva_url = funcs.modificar_documento_sharepoint(sharepoint_id, contenido_bytes)
        except Exception as e:
            return jsonify({"error": f"No se pudo actualizar en SharePoint: {str(e)}"}), 500

    # --- 3. Actualizar en la BD ---
    try:
        actualizado = funcs.modificar_documento_bbdd(idDocumento, nombre, descripcion, nueva_url)
    except Exception as e:
        return jsonify({"error": f"No se pudo actualizar en la base de datos: {str(e)}"}), 500

    if not actualizado:
        return jsonify({"mensaje": "No se encontró el documento con ese ID"}), 404

    return jsonify({"mensaje": "Documento actualizado correctamente"})


# -------------------- ELIMINAR DOCUMENTO -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos/<int:idDocumento>", methods=["DELETE"])
@requires_auth
def eliminar_documento_endpoint(idProyecto, idDocumento):
    try:
        eliminado = funcs.eliminar_documento(idDocumento)
    except Exception as e:
        return jsonify({"error": f"No se pudo eliminar el documento: {str(e)}"}), 500

    if not eliminado:
        return jsonify({"mensaje": "No se encontró el documento con ese ID"}), 404

    return jsonify({"mensaje": "Documento eliminado correctamente"})