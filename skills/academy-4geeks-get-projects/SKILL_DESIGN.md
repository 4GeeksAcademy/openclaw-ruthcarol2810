# Diseño de la skill

## Objetivo
Validar autenticación con la Skill 1, consultar todos los proyectos asignados por la API de 4Geeks con su estado y guardarlos en un archivo Markdown nuevo en Google Drive, con fecha venezolana en el nombre.

## Entrada
Solicitud de la persona usuaria; autenticación existente configurada fuera del repositorio; conexión MCP de Zapier con Google Drive disponible en la sesión.

## Salida esperada
Archivo Markdown nuevo `Proyectos4GeeksAcademy-RuthDiaz-YYYY-MM-DD.md`, con la lista de proyectos y estado legible, ubicado en la carpeta Drive `4geeks_academy`. La fecha se calcula en `America/Caracas` al momento de la ejecución. No sobrescribir duplicados. Informar enlace y número de proyectos solo tras verificar nombre, ubicación y creación.

## Dependencias
- `skills/autentication-4geeks-academy/SKILL.md` y su helper `scripts/check_auth.py`.
- `skills/autentication-4geeks-academy/STUDENT_API_CALLS_REFERENCE_es.md`.
- Zapier MCP configurado en `config/mcporter.json`; descubrir las acciones y esquemas disponibles con `mcporter list zapier --schema` e `inspect_zapier_actions` antes de cualquier llamada.
- Google Drive predeterminado conectado por Zapier MCP. Acción de búsqueda `google_drive_find_a_file` y acción de escritura `google_drive_create_file_from_text`; recuperar sus parámetros con `inspect_zapier_actions` (y el esquema dinámico de `folder`) en cada ejecución.
- Carpeta autorizada `4geeks_academy`, ID `1TI0qM1xSaFlFhI85SIR1SFfwskn-zfCr`; confirmar que sigue correspondiendo a ese nombre antes de escribir.
- Contenido tipo texto plano; conservar extensión `.md` y no convertir a Google Docs (`convert` omitido/falso).
