from pathlib import Path

from flask import Blueprint, jsonify, render_template, send_from_directory, session


estudiante_bp = Blueprint('estudiante', __name__)
MAP_DIRECTORY = Path(__file__).resolve().parent.parent / 'mapa_3d'
MAP_FILENAME = 'Universidad_Modular_Abierta___San_Miguel_3D_optimizado.html'


@estudiante_bp.route('/estudiante/mapa-3d')
@estudiante_bp.route('/mapa-3d')
def student_map():
    if not session.get('user'):
        return jsonify({"success": False, "message": "Inicia sesión para continuar"}), 401
    return render_template(
        'mapa_3d.html',
        map_url='/estudiante/mapa-3d/archivo',
        is_admin=bool(session.get('is_admin'))
    )


@estudiante_bp.route('/estudiante/mapa-3d/archivo')
@estudiante_bp.route('/mapa-3d/archivo')
def student_map_file():
    if not session.get('user'):
        return jsonify({"success": False, "message": "Inicia sesión para continuar"}), 401
    return send_from_directory(str(MAP_DIRECTORY), MAP_FILENAME)
