"""Utilidades compartidas: conexion a MySQL y validacion de administracion."""
import mysql.connector
from flask import current_app, jsonify, session

from config import DB_CONFIG


def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)


def check_admin_access():
    if not session.get('is_admin'):
        return False, (jsonify({
            "success": False,
            "message": "Solo administración puede acceder a este módulo"
        }), 403)

    connection = None
    cursor = None
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        if session.get('admin_source') == 'administracion':
            cursor.execute(
                "SELECT id FROM administracion WHERE id = %s AND activo = 1",
                (session.get('admin_id'),)
            )
        else:
            cursor.execute(
                "SELECT id FROM estudiantes WHERE usuario = %s AND activo = 1",
                (session.get('user'),)
            )
        if not cursor.fetchone():
            session.clear()
            return False, (jsonify({
                "success": False,
                "message": "La cuenta de administración no está activa"
            }), 403)
        return True, None
    except mysql.connector.Error:
        current_app.logger.exception("No se pudo validar la cuenta de administración")
        return False, (jsonify({
            "success": False,
            "message": "No se pudo validar la cuenta de administración"
        }), 500)
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
