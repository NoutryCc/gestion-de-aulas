import mysql.connector
from flask import Flask, current_app, jsonify, render_template, request, session

import config
from modulos.administracion import administracion_bp
from modulos.estudiante import estudiante_bp
from modulos.horarios import horarios_bp
from modulos.utilidades import get_db_connection


app = Flask(__name__)
app.secret_key = config.SECRET_KEY
if not app.secret_key:
    raise RuntimeError("Falta FLASK_SECRET_KEY: copia .env.example a .env y define el valor")

app.register_blueprint(administracion_bp)
app.register_blueprint(estudiante_bp)
app.register_blueprint(horarios_bp)


@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login', methods=['POST'])
def login():
    data = request.json or {}
    username = data.get('username')
    password = data.get('password')
    scanned_qr = data.get('scanned_qr')

    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """
            SELECT id, usuario, password, qr_payload
            FROM estudiantes
            WHERE usuario = %s AND activo = 1
            """,
            (username,)
        )
        user = cursor.fetchone()
        admin_account = None
        teacher_account = None
        if not user:
            cursor.execute(
                """
                SELECT id, usuario, password
                FROM administracion
                WHERE usuario = %s AND activo = 1
                """,
                (username,)
            )
            admin_account = cursor.fetchone()
        if not user and not admin_account:
            cursor.execute(
                """
                SELECT id, usuario, password
                FROM docentes
                WHERE usuario = %s AND activo = 1
                """,
                (username,)
            )
            teacher_account = cursor.fetchone()
    except mysql.connector.Error:
        current_app.logger.exception("No se pudo consultar la base de datos")
        return jsonify({
            "success": False,
            "message": "No se pudo conectar con la base de datos"
        }), 500
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

    authenticated_user = user or admin_account or teacher_account
    if not authenticated_user or authenticated_user['password'] != password:
        return jsonify({
            "success": False,
            "message": "Usuario o contraseña incorrectos"
        }), 401

    if scanned_qr and user and user['qr_payload'] != scanned_qr:
        return jsonify({
            "success": False,
            "message": "El QR escaneado no corresponde a este usuario"
        }), 401
    if scanned_qr and not user:
        return jsonify({
            "success": False,
            "message": "El acceso con QR solo está disponible para estudiantes"
        }), 401

    session.clear()
    session['user'] = authenticated_user['usuario']
    session['is_admin'] = bool(admin_account) or (
        bool(user) and authenticated_user['usuario'] == 'admin'
    )
    if admin_account:
        session['admin_source'] = 'administracion'
        session['admin_id'] = admin_account['id']
        session['user_type'] = 'administracion'
        session['user_id'] = admin_account['id']
    elif session['is_admin']:
        session['admin_source'] = 'estudiantes'
        session['admin_id'] = None
        session['user_type'] = 'administracion'
        session['user_id'] = user['id']
    elif teacher_account:
        session['user_type'] = 'docente'
        session['user_id'] = teacher_account['id']
    else:
        session['user_type'] = 'estudiante'
        session['user_id'] = user['id']
    return jsonify({
        "success": True,
        "message": "¡Acceso concedido! Bienvenida/o.",
        "is_admin": session['is_admin'],
        "user_type": session['user_type']
    })



@app.route('/session')
def get_session():
    username = session.get('user')
    return jsonify({
        "logged_in": username is not None,
        "username": username,
        "is_admin": bool(session.get('is_admin')),
        "user_type": session.get('user_type') or (
            'administracion' if session.get('is_admin') else 'estudiante'
        )
    })



@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})



if __name__ == '__main__':
    if config.HOST == '0.0.0.0':
        import socket
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            probe.connect(('8.8.8.8', 80))
            print(f"\n  Desde el celular (misma red Wi-Fi) abre: http://{probe.getsockname()[0]}:{config.PORT}\n")
        except OSError:
            pass
        finally:
            probe.close()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)