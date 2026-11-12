# Pruebas de Skill 2 — Obtener proyectos

## Evidencia de API de producción (2026-11-11)
- Helper de autenticación de la Skill 1: `python3 scripts/check_auth.py` → `{"status":"authenticated"}`.
- Solicitud autenticada `GET /v1/assignment/user/me/task?task_type=PROJECT&limit=100&offset=0` → HTTP 200, respuesta JSON paginada con `count=29`, 29 resultados y sin siguiente página.
- Todos los resultados tenían `task_type=PROJECT`; conteo de estados `task_status`: `PENDING=10`, `DONE=19`; revisión `revision_status`: `PENDING=12`, `APPROVED=17`.
- Campos observados: `title`, `cohort`, `task_status`, `revision_status`, `created_at`, `updated_at`, `delivered_at`, `reviewed_at` y URLs de entrega.
- No se guardó en este documento ni en los logs el token, cabecera de autorización o contenido personal de cada proyecto.

## Pruebas locales y pendientes
- La validación `quick_validate.py` informó «Skill is valid» y la sintaxis del helper se compiló correctamente.
- Las pruebas locales cubren la traducción de estados, validación/avance de la URL `next` de paginación y el bloqueo de la consulta cuando la autenticación falla. No se repitió la consulta real a la API durante esta revisión.
- En la tarea anterior se creó y verificó el archivo Markdown de proyectos en Google Drive; en esta continuación se volvió a comprobar su existencia, pero no se releyó su contenido ni se repitió la escritura.
- Queda como prueba futura repetir el ciclo completo (autenticación, consulta de API y creación en Drive) con datos nuevos; no es necesario repetirlo para documentar el flujo MCP.

## Evidencia de Google Drive y proceso MCP (2026-11-12)
- En la reanudación de la tarea se inspeccionó la configuración `config/mcporter.json` y se verificaron con `mcporter list zapier --schema` e `inspect_zapier_actions` las acciones de Google Drive, sus esquemas y la conexión predeterminada de Ruth. La carpeta dinámica `4geeks_academy` se resolvió al ID `1TI0qM1xSaFlFhI85SIR1SFfwskn-zfCr`.
- Se inspeccionó la búsqueda exacta `google_drive_find_a_file` y el esquema de creación `google_drive_create_file_from_text`. La búsqueda exacta del nombre `Proyectos4GeeksAcademy-RuthDiaz-2026-11-12.md` dentro de la carpeta objetivo encontró el archivo existente con ID `1D6p1vbotxuB-5jZo4-IsjSkvJ9grTvcs`, propietario Ruth y `mimeType=text/plain`; su `alternateLink` es `https://drive.google.com/file/d/1D6p1vbotxuB-5jZo4-IsjSkvJ9grTvcs/view?usp=drivesdk`.
- No se repitió la creación porque el archivo ya existía. La comprobación confirma nombre y carpeta (ID incluido en `parents`), pero no vuelve a leer el contenido. El enlace y la existencia se habían verificado previamente en esta conversación al terminar la carga.
- Actualizada la skill y su diseño para documentar la creación de `.md` en Drive mediante Zapier MCP, la consulta de duplicados, los parámetros descubiertos, el destino autorizado y la verificación antes de reportar. La consulta API y la escritura no se repitieron en esta continuación.
