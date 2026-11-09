# Gestión de Aulas

Sistema web para consultar horarios de clases y ubicar cada aula en un mapa 3D de la Universidad Modular Abierta. Incluye tres tipos de cuenta: estudiante, docente y administración.

## Requisitos

- Python 3.10 o superior
- MySQL Server 8.0 o superior (en ejecución)

## Estructura

```
gestion-de-aulas/
├── app.py                 Punto de entrada
├── config.py              Configuración
├── requirements.txt       Dependencias
├── .env.example           Plantilla de variables de entorno
├── modulos/               Lógica por módulo (administración, estudiante, horarios)
├── templates/             Plantillas HTML
├── static/                CSS e imágenes
├── mapa_3d/               Mapa 3D
├── database/              schema.sql, seed.sql, init_db.py
├── scripts/instalar.ps1   Instalación automática en Windows
└── docs/ARQUITECTURA.md   Documentación técnica
```

## Instalación

### Opción A: automática (Windows)

1. Abre PowerShell en la carpeta del proyecto.
2. Ejecuta `powershell -ExecutionPolicy Bypass -File scripts\instalar.ps1`.
3. Edita el archivo `.env` creado y escribe tu `DB_PASSWORD` de MySQL.
4. Ejecuta el script del paso 2 otra vez para crear la base de datos.

### Opción B: manual

1. Crear y activar el entorno virtual:
   ```
   python -m venv venv
   venv\Scripts\activate          (Windows)
   source venv/bin/activate       (Linux o macOS)
   ```
2. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Crear el archivo de configuración: copiar `.env.example` como `.env`, definir `DB_PASSWORD` y generar la clave secreta con:
   ```
   python -c "import secrets; print(secrets.token_hex(32))"
   ```
   Pegar el resultado en `FLASK_SECRET_KEY`.
4. Crear la base de datos con datos de prueba:
   ```
   python database/init_db.py
   ```
   Para borrarla y recrearla: `python database/init_db.py --reset`.

## Ejecución

```
python app.py
```

Abrir http://127.0.0.1:5000

## Cuentas de prueba

| Tipo | Usuario | Contraseña | Qué ve |
|---|---|---|---|
| Administración | `admin` | `admin123` | Panel de administración y todos los horarios |
| Estudiante | `estudiante1` | `123` | Sus materias: Matemática I, Programación, Inglés Técnico |
| Estudiante | `estudiante2` | `123` | Matemática I y Física General |
| Docente | `docente1` | `123` | Sus clases asignadas |
| Docente | `docente2` | `123` | Sus clases asignadas |

El código QR de `estudiante1` es `ESTUDIANTE_2026_001` y es opcional en el inicio de sesión.

## Uso desde un celular

El diseño se adapta a teléfonos: en pantallas pequeñas el mapa aparece arriba, los horarios debajo y las tablas de administración se muestran como tarjetas.

Para abrirlo desde un teléfono conectado al mismo Wi-Fi que la computadora:

1. En `.env` cambia `HOST=127.0.0.1` por `HOST=0.0.0.0` y `FLASK_DEBUG=1` por `FLASK_DEBUG=0`.
2. Inicia con `python app.py`. La terminal muestra la dirección, por ejemplo `http://192.168.1.25:5000`.
3. Escribe esa dirección en el navegador del teléfono.
4. Si no carga, permite Python en el Firewall de Windows (redes privadas).

Limitación: los navegadores móviles solo permiten la cámara en conexiones HTTPS, por lo que el escaneo de QR no funcionará con esa dirección. El inicio de sesión con usuario y contraseña funciona normal, ya que el QR es opcional.

## Uso del mapa con horarios

1. Inicia sesión como estudiante o docente.
2. Abre "Mapa 3D y mis horarios".
3. A la derecha aparece la lista de clases. Pulsa "Ver aula en el mapa" y la cámara se dirige al aula asignada.

## Administración

Desde `/admin` se registran materias, se asignan horarios a docentes, se inscriben estudiantes y se activan o desactivan registros. En el campo de aula use el formato `Nivel N - Nombre` (ver `docs/ARQUITECTURA.md`).

## Notas de seguridad

Este proyecto es una versión de prueba. Las contraseñas de los datos de ejemplo se guardan en texto plano; antes de un uso real deben almacenarse con hash (por ejemplo `werkzeug.security`). El archivo `.env` no debe subirse a un repositorio.