import mysql.connector
from flask import Blueprint, current_app, jsonify, render_template, request, session

from modulos.utilidades import check_admin_access, get_db_connection


administracion_bp = Blueprint('administracion', __name__)


@administracion_bp.route('/admin')
def admin_module():
    allowed, error = check_admin_access()
    if not allowed:
        return error
    return render_template('administracion.html')


@administracion_bp.route('/admin/estudiantes', methods=['POST'])
def create_student():
    allowed, error = check_admin_access()
    if not allowed:
        return error

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "message": "Se requiere un objeto JSON válido"
        }), 400

    username = data.get('username')
    password = data.get('password')
    qr_payload = data.get('qr_payload') or None

    if not isinstance(username, str) or not isinstance(password, str):
        return jsonify({
            "success": False,
            "message": "El usuario y la contraseña son obligatorios"
        }), 400

    username = username.strip()
    password = password.strip()
    if not username or not password:
        return jsonify({
            "success": False,
            "message": "El usuario y la contraseña son obligatorios"
        }), 400
    if len(username) > 100 or len(password) > 255:
        return jsonify({
            "success": False,
            "message": "El usuario admite hasta 100 caracteres y la contraseña hasta 255"
        }), 400
    if qr_payload is not None and (
        not isinstance(qr_payload, str) or len(qr_payload) > 255
    ):
        return jsonify({
            "success": False,
            "message": "El código QR admite hasta 255 caracteres"
        }), 400

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            INSERT INTO estudiantes (usuario, password, qr_payload, activo)
            VALUES (%s, %s, %s, 1)
            """,
            (username, password, qr_payload)
        )
        connection.commit()
    except mysql.connector.IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return jsonify({
            "success": False,
            "message": "Ya existe un usuario con ese nombre"
        }), 409
    except mysql.connector.Error:
        if connection and connection.is_connected():
            connection.rollback()
        current_app.logger.exception("No se pudo crear el usuario estudiante")
        return jsonify({
            "success": False,
            "message": "No se pudo crear el usuario estudiante"
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

    return jsonify({
        "success": True,
        "message": "Estudiante creado correctamente"
    }), 201


@administracion_bp.route('/admin/api/docentes')
def admin_teachers():
    allowed, error = check_admin_access()
    if not allowed:
        return error
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, usuario FROM docentes WHERE activo = 1 ORDER BY usuario"
        )
        return jsonify({"success": True, "docentes": cursor.fetchall()})
    except mysql.connector.Error:
        current_app.logger.exception("No se pudieron consultar los docentes")
        return jsonify({"success": False, "message": "No se pudieron consultar los docentes"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@administracion_bp.route('/admin/api/estudiantes')
def admin_students():
    allowed, error = check_admin_access()
    if not allowed:
        return error
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, usuario FROM estudiantes WHERE activo = 1 ORDER BY usuario"
        )
        return jsonify({"success": True, "estudiantes": cursor.fetchall()})
    except mysql.connector.Error:
        current_app.logger.exception("No se pudieron consultar los estudiantes")
        return jsonify({"success": False, "message": "No se pudieron consultar los estudiantes"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@administracion_bp.route('/admin/api/inscripciones', methods=['GET', 'POST'])
def admin_enrollments():
    allowed, error = check_admin_access()
    if not allowed:
        return error
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        if request.method == 'GET':
            cursor.execute(
                """
                SELECT em.estudiante_id, em.materia_id,
                       e.usuario AS estudiante, m.codigo, m.nombre AS materia
                FROM estudiante_materias em
                JOIN estudiantes e ON e.id = em.estudiante_id
                JOIN materias m ON m.id = em.materia_id
                ORDER BY e.usuario, m.nombre
                """
            )
            return jsonify({"success": True, "inscripciones": cursor.fetchall()})

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "message": "Se requiere un objeto JSON válido"}), 400
        estudiante_id = data.get('estudiante_id')
        materia_id = data.get('materia_id')
        if (not isinstance(estudiante_id, int) or isinstance(estudiante_id, bool) or estudiante_id < 1
                or not isinstance(materia_id, int) or isinstance(materia_id, bool) or materia_id < 1):
            return jsonify({"success": False, "message": "Selecciona un estudiante y una materia"}), 400
        cursor.execute(
            """
            INSERT INTO estudiante_materias (estudiante_id, materia_id)
            SELECT e.id, m.id
            FROM estudiantes e
            JOIN materias m ON m.id = %s AND m.activo = 1
            WHERE e.id = %s AND e.activo = 1
            """,
            (materia_id, estudiante_id)
        )
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({
                "success": False,
                "message": "El estudiante o la materia no existe o no está activo"
            }), 400
        connection.commit()
        return jsonify({"success": True, "message": "Materia asignada al estudiante"}), 201
    except mysql.connector.IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return jsonify({
            "success": False,
            "message": "El estudiante ya está inscrito en esa materia"
        }), 409
    except mysql.connector.Error:
        if connection and connection.is_connected():
            connection.rollback()
        current_app.logger.exception("No se pudieron consultar o guardar las inscripciones")
        return jsonify({
            "success": False,
            "message": "No se pudieron consultar o guardar las inscripciones"
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@administracion_bp.route('/admin/api/inscripciones/<int:estudiante_id>/<int:materia_id>', methods=['DELETE'])
def admin_enrollment(estudiante_id, materia_id):
    allowed, error = check_admin_access()
    if not allowed:
        return error
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM estudiante_materias WHERE estudiante_id = %s AND materia_id = %s",
            (estudiante_id, materia_id)
        )
        if cursor.rowcount == 0:
            return jsonify({"success": False, "message": "No se encontró la inscripción"}), 404
        connection.commit()
        return jsonify({"success": True, "message": "Inscripción eliminada"})
    except mysql.connector.Error:
        if connection and connection.is_connected():
            connection.rollback()
        current_app.logger.exception("No se pudo eliminar la inscripción")
        return jsonify({"success": False, "message": "No se pudo eliminar la inscripción"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@administracion_bp.route('/admin/api/materias', methods=['GET', 'POST'])
def admin_subjects():
    allowed, error = check_admin_access()
    if not allowed:
        return error

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        if request.method == 'GET':
            cursor.execute(
                "SELECT id, codigo, nombre, descripcion, activo FROM materias ORDER BY nombre"
            )
            return jsonify({"success": True, "materias": cursor.fetchall()})

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "message": "Se requiere un objeto JSON válido"}), 400
        codigo = data.get('codigo')
        nombre = data.get('nombre')
        descripcion = data.get('descripcion') or None
        if (not isinstance(codigo, str) or not codigo.strip() or len(codigo.strip()) > 50
                or not isinstance(nombre, str) or not nombre.strip() or len(nombre.strip()) > 100
                or (descripcion is not None and not isinstance(descripcion, str))):
            return jsonify({"success": False, "message": "Verifica el código, nombre y descripción de la materia"}), 400
        cursor.execute(
            "INSERT INTO materias (codigo, nombre, descripcion) VALUES (%s, %s, %s)",
            (codigo.strip(), nombre.strip(), descripcion)
        )
        connection.commit()
        return jsonify({"success": True, "message": "Materia creada correctamente"}), 201
    except mysql.connector.IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return jsonify({"success": False, "message": "Ya existe una materia con ese código"}), 409
    except mysql.connector.Error:
        if connection and connection.is_connected():
            connection.rollback()
        current_app.logger.exception("No se pudieron consultar o guardar las materias")
        return jsonify({"success": False, "message": "No se pudieron consultar o guardar las materias"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@administracion_bp.route('/admin/api/materias/<int:materia_id>', methods=['PUT', 'DELETE'])
def admin_subject(materia_id):
    allowed, error = check_admin_access()
    if not allowed:
        return error
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        if request.method == 'DELETE':
            cursor.execute("UPDATE materias SET activo = 0 WHERE id = %s", (materia_id,))
        else:
            data = request.get_json(silent=True)
            if not isinstance(data, dict):
                return jsonify({"success": False, "message": "Se requiere un objeto JSON válido"}), 400
            active = data.get('activo')
            if not isinstance(active, bool):
                return jsonify({"success": False, "message": "El estado activo debe ser verdadero o falso"}), 400
            cursor.execute("UPDATE materias SET activo = %s WHERE id = %s", (active, materia_id))
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({"success": False, "message": "No se encontró la materia"}), 404
        connection.commit()
        return jsonify({"success": True, "message": "Materia actualizada correctamente"})
    except mysql.connector.Error:
        if connection and connection.is_connected():
            connection.rollback()
        current_app.logger.exception("No se pudo actualizar la materia")
        return jsonify({"success": False, "message": "No se pudo actualizar la materia"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@administracion_bp.route('/admin/api/horarios', methods=['GET', 'POST'])
def admin_schedules():
    allowed, error = check_admin_access()
    if not allowed:
        return error

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        if request.method == 'GET':
            cursor.execute(
                """
                SELECT h.id, h.materia_id, m.nombre AS materia, h.docente_id,
                       d.usuario AS docente,
                       h.dia, h.horario, h.numero_aula, h.activo
                FROM horarios_clases h
                JOIN materias m ON m.id = h.materia_id
                JOIN docentes d ON d.id = h.docente_id
                ORDER BY FIELD(h.dia, 'Lunes', 'Martes', 'Miércoles', 'Jueves',
                               'Viernes', 'Sábado', 'Domingo'), h.horario
                """
            )
            return jsonify({"success": True, "horarios": cursor.fetchall()})

        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({"success": False, "message": "Se requiere un objeto JSON válido"}), 400
        materia_id = data.get('materia_id')
        docente_id = data.get('docente_id')
        dia = data.get('dia')
        horario = data.get('horario')
        aula = data.get('numero_aula')
        dias = ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo')
        if (not isinstance(materia_id, int) or isinstance(materia_id, bool) or materia_id < 1
                or not isinstance(docente_id, int) or isinstance(docente_id, bool) or docente_id < 1
                or dia not in dias
                or not isinstance(horario, str) or not horario.strip() or len(horario.strip()) > 50
                or not isinstance(aula, str) or not aula.strip() or len(aula.strip()) > 50):
            return jsonify({"success": False, "message": "Completa materia, docente, día, horario y aula correctamente"}), 400
        cursor.execute(
            """
            INSERT INTO horarios_clases
                (administrador_id, materia_id, docente_id, dia, horario, numero_aula)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (session.get('admin_id'), materia_id, docente_id, dia, horario.strip(), aula.strip())
        )
        connection.commit()
        return jsonify({"success": True, "message": "Horario asignado correctamente"}), 201
    except mysql.connector.IntegrityError:
        if connection and connection.is_connected():
            connection.rollback()
        return jsonify({"success": False, "message": "La materia o el docente seleccionado no existe"}), 400
    except mysql.connector.Error:
        if connection and connection.is_connected():
            connection.rollback()
        current_app.logger.exception("No se pudieron consultar o guardar los horarios")
        return jsonify({"success": False, "message": "No se pudieron consultar o guardar los horarios"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@administracion_bp.route('/admin/api/horarios/<int:horario_id>', methods=['PUT', 'DELETE'])
def admin_schedule(horario_id):
    allowed, error = check_admin_access()
    if not allowed:
        return error
    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        if request.method == 'DELETE':
            cursor.execute("UPDATE horarios_clases SET activo = 0 WHERE id = %s", (horario_id,))
        else:
            data = request.get_json(silent=True)
            if not isinstance(data, dict) or not isinstance(data.get('activo'), bool):
                return jsonify({"success": False, "message": "El estado activo debe ser verdadero o falso"}), 400
            cursor.execute(
                "UPDATE horarios_clases SET activo = %s WHERE id = %s",
                (data['activo'], horario_id)
            )
        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({"success": False, "message": "No se encontró el horario"}), 404
        connection.commit()
        return jsonify({"success": True, "message": "Horario actualizado correctamente"})
    except mysql.connector.Error:
        if connection and connection.is_connected():
            connection.rollback()
        current_app.logger.exception("No se pudo actualizar el horario")
        return jsonify({"success": False, "message": "No se pudo actualizar el horario"}), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
