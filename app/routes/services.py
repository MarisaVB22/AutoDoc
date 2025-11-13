from flask import jsonify, request
from app import app
from app.utils import funciones as funcs  # Importa todo el módulo con un alias

# -------------------- RUTA DE PRUEBA -------------------- #
# PRUEBA - Llamada a la función saludo desde funciones.py
@app.route("/saludo", methods=["GET"])
def saludo_route():
    data = funcs.saludo()
    return jsonify({"saludo": data})

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
