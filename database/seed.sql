-- Datos de prueba. Solo para desarrollo.
-- Formato de aula: "Nivel N - Nombre del aula" (debe coincidir con el mapa 3D).
INSERT INTO administracion (usuario, password) VALUES ('admin', 'admin123');

INSERT INTO estudiantes (usuario, password, qr_payload) VALUES
 ('estudiante1', '123', 'ESTUDIANTE_2026_001'),
 ('estudiante2', '123', 'ESTUDIANTE_2026_002');

INSERT INTO docentes (usuario, password) VALUES
 ('docente1', '123'),
 ('docente2', '123');

INSERT INTO materias (codigo, nombre, descripcion) VALUES
 ('MAT101', 'Matemática I', 'Álgebra y cálculo básico'),
 ('INF201', 'Programación', 'Fundamentos de programación'),
 ('FIS110', 'Física General', 'Mecánica y termodinámica'),
 ('ING105', 'Inglés Técnico', 'Inglés aplicado a la ingeniería');

INSERT INTO horarios_clases (administrador_id, materia_id, docente_id, dia, horario, numero_aula) VALUES
 (1, 1, 1, 'Lunes',     '08:00 - 10:00', 'Nivel 2 - Aula 3'),
 (1, 2, 2, 'Martes',    '10:00 - 12:00', 'Nivel 2 - Centro de Cómputo 2'),
 (1, 3, 1, 'Miércoles', '08:00 - 10:00', 'Nivel 3 - Aula 5'),
 (1, 4, 2, 'Jueves',    '14:00 - 16:00', 'Nivel 1 - Aula A-2'),
 (1, 1, 1, 'Viernes',   '08:00 - 10:00', 'Nivel 2 - Aula 3');

INSERT INTO estudiante_materias (estudiante_id, materia_id) VALUES
 (1, 1), (1, 2), (1, 4),
 (2, 1), (2, 3);
