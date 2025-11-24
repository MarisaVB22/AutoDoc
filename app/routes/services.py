from flask import jsonify, request
from app import app
from app.utils import funciones as funcs  # Importa todo el módulo con un alias

# -------------------- RUTA DE PRUEBA -------------------- #
# PRUEBA - Llamada a la función saludo desde funciones.py
@app.route("/saludo", methods=["GET"])
def saludo_route():
    data = funcs.saludo()
    return jsonify({"saludo": data})

# -------------------- ACCESS TOKEN MICROSOFT GRAPH -------------------- #
@app.route("/test-token", methods=["GET"])
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
def obtener_proyectos_endpoint():
    nombre = request.args.get("nombre")
    proyectos = funcs.obtener_proyectos(nombre)
    return jsonify(proyectos)


# -------------------- OBTENER UN PROYECTO POR ID -------------------- #
# Devuelve un proyecto específico por su ID
@app.route("/proyectos/<int:id>", methods=["GET"])
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
def crear_proyecto_endpoint():
    # Obtener los datos del request body
    data = request.get_json()

    # Validar que vengan todos los campos requeridos
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    proyecto_url = data.get("proyecto_url")

    if not nombre or not descripcion or not proyecto_url:
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

    # Llamar a la función auxiliar que inserta el proyecto
    proyecto_id = funcs.crear_proyecto(nombre, descripcion, proyecto_url)

    return jsonify({
        "mensaje": "Proyecto creado correctamente",
        "proyecto_id": proyecto_id
    }), 200

# -------------------- MODIFICAR PROYECTO -------------------- #
@app.route("/proyectos/<int:id>", methods=["PUT"])
def modificar_proyecto_endpoint(id):
    # Obtener datos del request
    data = request.get_json()
    if not data:
        return jsonify({"mensaje": "No se enviaron datos para actualizar"}), 400

    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    proyecto_url = data.get("proyecto_url")

    # Validar campos obligatorios (opcional si quieres que todos sean requeridos)
    if not all([nombre, descripcion, proyecto_url]):
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

    # Llamar a la función que actualiza el proyecto en la BBDD
    actualizado = funcs.modificar_proyecto(id, nombre, descripcion, proyecto_url)

    if not actualizado:
        return jsonify({"mensaje": "No se encontró el proyecto con ese ID"}), 404

    return jsonify({"mensaje": "Proyecto actualizado correctamente"})


# -------------------- ELIMINAR PROYECTO -------------------- #
@app.route("/proyectos/<int:id>", methods=["DELETE"])
def eliminar_proyecto_endpoint(id):
    # Llamamos a la función auxiliar que elimina el proyecto
    eliminado = funcs.eliminar_proyecto(id)

    if not eliminado:
        # No se encontró el proyecto con ese ID
        return jsonify({"mensaje": "No se encontró el proyecto con ese ID"}), 404

    # Proyecto eliminado correctamente
    return jsonify({"mensaje": "Proyecto eliminado correctamente"})

"""-----------------------------------------------------------------------
                       DOCUMENTOS
-----------------------------------------------------------------------"""

# -------------------- LISTAR DOCUMENTOS DE UN PROYECTO -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos", methods=["GET"])
def obtener_documentos_endpoint(idProyecto):
    documentos = funcs.obtener_documentos(idProyecto)
    return jsonify(documentos)


# -------------------- SUBIR DOCUMENTO (REGISTRO EN BBDD) -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos", methods=["POST"])
def crear_documento_endpoint(idProyecto):
    data = request.get_json()

    # Validar campos obligatorios
    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    url = data.get("url")  # URL de OneDrive, Sharepoint u otro

    if not nombre or not descripcion or not url:
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

    documento_id = funcs.crear_documento(idProyecto, nombre, descripcion, url)

    return jsonify({
        "mensaje": "Documento creado correctamente",
        "documento_id": documento_id
    }), 200


# -------------------- OBTENER DOCUMENTO POR ID -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos/<int:idDocumento>", methods=["GET"])
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
        "fecha": documento_raw["fecha"]
    }

    return jsonify(documento)


# -------------------- MODIFICAR DOCUMENTO -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos/<int:idDocumento>", methods=["PUT"])
def modificar_documento_endpoint(idProyecto, idDocumento):
    data = request.get_json()

    if not data:
        return jsonify({"mensaje": "No se enviaron datos para actualizar"}), 400

    nombre = data.get("nombre")
    descripcion = data.get("descripcion")
    url = data.get("url")

    if not all([nombre, descripcion, url]):
        return jsonify({"mensaje": "Faltan campos obligatorios"}), 400

    actualizado = funcs.modificar_documento(idDocumento, nombre, descripcion, url)

    if not actualizado:
        return jsonify({"mensaje": "No se encontró el documento con ese ID"}), 404

    return jsonify({"mensaje": "Documento actualizado correctamente"})


# -------------------- ELIMINAR DOCUMENTO -------------------- #
@app.route("/proyectos/<int:idProyecto>/documentos/<int:idDocumento>", methods=["DELETE"])
def eliminar_documento_endpoint(idProyecto, idDocumento):
    eliminado = funcs.eliminar_documento(idDocumento)

    if not eliminado:
        return jsonify({"mensaje": "No se encontró el documento con ese ID"}), 404

    return jsonify({"mensaje": "Documento eliminado correctamente"})
