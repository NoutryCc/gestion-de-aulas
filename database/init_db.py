"""Crea la base de datos y carga los datos de prueba.

Uso:  python database/init_db.py            (crea esquema y datos)
      python database/init_db.py --reset    (borra todo y vuelve a crear)
"""
import sys
from pathlib import Path

import mysql.connector

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DB_CONFIG, DB_NAME  # noqa: E402

HERE = Path(__file__).resolve().parent


def run_script(cursor, path):
    statements = [s.strip() for s in path.read_text(encoding='utf-8').split(';')]
    for statement in statements:
        lines = [l for l in statement.splitlines() if not l.strip().startswith('--')]
        sql = '\n'.join(lines).strip()
        if sql:
            cursor.execute(sql)


def main():
    reset = '--reset' in sys.argv
    server = {k: v for k, v in DB_CONFIG.items() if k != 'database'}
    try:
        connection = mysql.connector.connect(**server)
    except mysql.connector.Error as error:
        sys.exit(f"No se pudo conectar a MySQL: {error}\nRevisa DB_USER y DB_PASSWORD en .env")
    cursor = connection.cursor()
    if reset:
        cursor.execute(f"DROP DATABASE IF EXISTS `{DB_NAME}`")
    cursor.execute(
        f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
    )
    cursor.execute(f"USE `{DB_NAME}`")
    run_script(cursor, HERE / 'schema.sql')
    cursor.execute("SELECT COUNT(*) FROM administracion")
    if cursor.fetchone()[0] == 0:
        run_script(cursor, HERE / 'seed.sql')
        print("Datos de prueba cargados.")
    else:
        print("La base ya tiene datos; use --reset para recrearla.")
    connection.commit()
    cursor.close()
    connection.close()
    print(f"Base de datos '{DB_NAME}' lista.")


if __name__ == '__main__':
    main()
