# Arquitectura

| Carpeta / archivo | Responsabilidad |
|---|---|
| `app.py` | Crea la aplicación Flask, registra los módulos y maneja login, sesión y logout |
| `config.py` | Lee la configuración del archivo `.env` |
| `modulos/administracion.py` | Pantalla y API de administración (materias, horarios, inscripciones) |
| `modulos/horarios.py` | API `/api/mis-horarios`, filtrada según el tipo de cuenta |
| `modulos/estudiante.py` | Rutas protegidas del mapa 3D |
| `modulos/utilidades.py` | Conexión a MySQL y validación de administración |
| `templates/` | Plantillas HTML (login, mapa con horarios, administración) |
| `static/css/estilos.css` | Hoja de estilos única compartida |
| `mapa_3d/` | Mapa 3D de la universidad |
| `database/` | Esquema, datos de prueba y script de inicialización |

## Flujo del mapa con horarios

1. La persona inicia sesión y abre `/mapa-3d`.
2. La página consulta `/api/mis-horarios`: estudiantes ven las materias en las que están inscritos, docentes las que imparten y administración todas las activas.
3. Al pulsar "Ver aula en el mapa" en una clase, la página envía un mensaje al mapa (`postMessage`) y este mueve la cámara al aula correspondiente.

## Formato del campo aula

El campo `numero_aula` debe escribirse como `Nivel N - Nombre`, con el nombre exacto que usa el mapa:

- Nivel 1: Aula A-1 a A-6, Biblioteca, Recepción, Auditorium
- Nivel 2: Aula 1 a Aula 8, Centro de Cómputo 2
- Nivel 3: Aula 1 a Aula 9

Ejemplo: `Nivel 2 - Aula 3`. El formulario de administración sugiere estos valores.
