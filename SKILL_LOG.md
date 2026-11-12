# Registro de skills — 4Geeks Academy

## Skill 1 — Autenticación

- **Prompt inicial en lenguaje natural:** «La primera skill es para autenticarnos en la API de estudiantes de 4Geeks Academy, dónde estoy haciendo el Bootcamp de AI Engineering».
- **Alcance aclarado durante la conversación:** «En esta primera skill solo debemos autenticarnos con exito».
- **Qué hace:** comprueba si el token de estudiante existente permite autenticarse. Informa solo el resultado de autenticación; no consulta cohorte, estado de inscripción ni otros datos académicos.
- **Endpoint:** `GET https://breathecode.herokuapp.com/v1/admissions/user/me`, con `Authorization: Token <token>` según `skills/autentication-4geeks-academy/STUDENT_API_CALLS_REFERENCE_es.md`.
- **Manejo del secreto:** el helper lee `TOKEN_4GEEKS` del entorno o de un `.env` privado ubicado fuera del repositorio. El secreto no está escrito en la skill ni en este registro, y no se imprime.
- **Prueba:** ejecución de `python3 scripts/check_auth.py` desde `skills/autentication-4geeks-academy/` contra la API real; resultado `{"status": "authenticated"}`. No se expusieron datos del usuario.
- **Validación:** `quick_validate.py` informó «Skill is valid»; también pasó la compilación de Python y pruebas simuladas para respuesta exitosa, 401 y redirección.

## Skill 2 — Obtener mis proyectos

- **Prompt inicial en lenguaje natural:** «Vamos a crear la Skill 2 — Obtener mis proyectos (academy-4geeks-get-projects): OpenClaw puede recuperar la lista de proyectos asignados a ti con su estado actual (pendiente, entregado, calificado). En esta skill el primer paso será verificar la autenticación, con la skill autentication-4geeks-academy, luego usar el endpoint correspondiente para recuperar los proyectos, la lista de proyectos la colocamos en un documento de Google Docs, con el nombre Proyectos4GeeksAcademy-RuthDiaz-<fechaActual>, dónde fechaActual es la fecha, de Venezuela».
- **Activación:** «obtener mis proyectos» y sinónimos como «ver mis proyectos», «listar mis proyectos», «consultar mis proyectos», «mostrar mis proyectos», «¿qué proyectos tengo?» o «mis proyectos asignados».
- **Qué hace:** valida primero autenticación con el helper de Skill 1; consulta todos los proyectos asignados, traduce sus estados y guarda un archivo Markdown nuevo en Google Drive, en la carpeta `4geeks_academy`, con fecha local venezolana en el nombre. No modifica tareas ni reemplaza documentos existentes.
- **Endpoints:** `GET https://breathecode.herokuapp.com/v1/admissions/user/me` para validar autenticación mediante el helper existente; `GET https://breathecode.herokuapp.com/v1/assignment/user/me/task?task_type=PROJECT&limit=...&offset=...` para proyectos y paginación.
- **Prueba API:** el 2026-11-11 el helper real respondió `authenticated`. La consulta de proyectos devolvió HTTP 200 y 29 resultados (19 `DONE`, 10 `PENDING`), sin página siguiente; `revision_status` fue `APPROVED` en 17 y `PENDING` en 12.
- **Método de Google Drive:** la Skill descubre herramientas y esquemas con `mcporter list zapier --schema` e `inspect_zapier_actions`; busca un duplicado exacto mediante `google_drive_find_a_file` y crea texto plano con `google_drive_create_file_from_text`. La carpeta `4geeks_academy` fue confirmada como ID `1TI0qM1xSaFlFhI85SIR1SFfwskn-zfCr`; se valida el destino y se prohíbe sobrescribir. No usar los nombres de herramientas/parámetros sin volver a descubrir sus esquemas vigentes.
- **Archivo generado y verificado:** `Proyectos4GeeksAcademy-RuthDiaz-2026-11-12.md`, guardado en la carpeta `4geeks_academy`, con 29 proyectos. Enlace: https://drive.google.com/file/d/1D6p1vbotxuB-5jZo4-IsjSkvJ9grTvcs/view?usp=drivesdk
- **Archivos:** `skills/academy-4geeks-get-projects/SKILL.md`, `SKILL_DESIGN.md`, `SKILL_TESTS.md`, `README.md` y `scripts/get_projects.py`.
- **Validación local:** `quick_validate.py` informó «Skill is valid» y `git diff --check` pasó. La Skill manda usar el helper combinado `get_projects.py`, que valida la autenticación antes de consultar y valida/avanza la paginación. La existencia del archivo se re-verificó en Drive durante la actualización de la documentación; no se repitió la creación porque ya existía.
