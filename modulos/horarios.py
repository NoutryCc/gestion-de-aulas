import mysql.connector
from flask import Blueprint, current_app, jsonify, session

from modulos.utilidades import check_admin_access, get_db_connection


horarios_bp = Blueprint('horarios', __name__)


@horarios_bp.route('/api/mis-horarios')
def my_schedules():
    username = session.get('user')
    if not username:
        return jsonify({"success": False, "message": "Inicia sesión para continuar"}), 401

    user_type = session.get('user_type') or (
        'administracion' if session.get('is_admin') else 'estudiante'
    )
    if user_type == 'administracion':
        allowed, error = check_admin_access()
        if not allowed:
            return error
    elif user_type not in ('estudiante', 'docente'):
        return jsonify({"success": False, "message": "Tipo de cuenta no válido"}), 403

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT h.id, m.codigo, m.nombre AS materia, d.usuario AS docente,
                   h.dia, h.horario, h.numero_aula
            FROM horarios_clases h
            JOIN materias m ON m.id = h.materia_id AND m.activo = 1
            JOIN docentes d ON d.id = h.docente_id AND d.activo = 1
        """
        params = ()
        if user_type == 'estudiante':
            query += """
                JOIN estudiante_materias em ON em.materia_id = h.materia_id
                JOIN estudiantes e ON e.id = em.estudiante_id AND e.activo = 1
                WHERE em.estudiante_id = %s AND h.activo = 1
            """
            params = (session.get('user_id'),)
        elif user_type == 'docente':
            query += " WHERE h.docente_id = %s AND h.activo = 1"
            params = (session.get('user_id'),)
        else:
            query += " WHERE h.activo = 1"
        query += """
            ORDER BY FIELD(h.dia, 'Lunes', 'Martes', 'Miércoles', 'Jueves',
                           'Viernes', 'Sábado', 'Domingo'), h.horario
        """
        cursor.execute(query, params)
        return jsonify({
            "success": True,
            "user_type": user_type,
            "horarios": cursor.fetchall()
        })
    except mysql.connector.Error:
        current_app.logger.exception("No se pudieron consultar los horarios de la cuenta")
        return jsonify({
            "success": False,
            "message": "No se pudieron consultar los horarios"
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
