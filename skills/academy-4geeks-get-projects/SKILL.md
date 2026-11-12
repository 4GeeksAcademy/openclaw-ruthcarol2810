---
name: academy-4geeks-get-projects
description: "Activa con ‘obtener mis proyectos’ o sinónimos como ver, listar o consultar mis proyectos asignados de 4Geeks; recupera su estado y guarda un archivo Markdown nuevo en Google Drive."
---

# Proyectos de 4Geeks Academy

## Frases de activación
Activa esta skill cuando la usuaria pida «obtener mis proyectos» o use una expresión equivalente, por ejemplo: «ver mis proyectos», «listar mis proyectos», «consultar mis proyectos», «mostrar mis proyectos», «¿qué proyectos tengo?» o «mis proyectos asignados».

## Procedimiento
1. Lee la referencia de API de `skills/autentication-4geeks-academy/STUDENT_API_CALLS_REFERENCE_es.md` y ejecuta `python3 skills/academy-4geeks-get-projects/scripts/get_projects.py` desde la raíz del workspace. El helper primero comprueba el token reutilizando la comprobación de la Skill 1 y solo si está autenticado consulta proyectos. Continúa solo con `status: ok`; ante rechazo, autenticación inconclusa o error, informa el motivo no sensible y detén el flujo. Nunca leas, muestres ni registres el token o la cabecera de autorización.
2. Comprueba que la salida sea JSON con `status: ok`, `count` y una lista `projects`; el helper pagina el endpoint documentado `GET /v1/assignment/user/me/task` con `task_type=PROJECT`, `limit` y `offset`, y falla si detecta una respuesta inválida o paginación incompleta. No hagas una segunda petición manual ni consultes cohortes u otros datos académicos.
3. Usa la lista estructurada devuelta por el helper. Presenta cada proyecto con título, estado y contexto disponible, incluyendo fechas útiles cuando existan. Los estados conocidos ya vienen traducidos; conserva `task_status` y `revision_status` si están disponibles, y muestra estados desconocidos literalmente sin adivinarlos. Si `projects` está vacía, indícalo expresamente.
4. Obtén la fecha actual de Venezuela en `America/Caracas`, formato `YYYY-MM-DD`, y forma el nombre exacto `Proyectos4GeeksAcademy-RuthDiaz-<fecha>.md`. Antes de crear, comprueba en la carpeta destino si ya existe un archivo con ese nombre; ante cualquier coincidencia, no lo sobrescribas ni crees otro con el mismo nombre: informa el hallazgo y pregunta cómo proceder.
5. Crea un archivo Markdown nuevo en Google Drive mediante la conexión Zapier MCP definida en `config/mcporter.json`. Sigue la skill `mcporter`: descubre herramientas con `mcporter list zapier --schema`; llama `inspect_zapier_actions` primero sin argumentos y luego con `selected_api` de Google Drive para confirmar la acción, y solicita el esquema específico de cada herramienta mediante `tool_name`. Usa `google_drive_find_a_file` (`file_v2`) con `title=<nombre exacto>`, `folder="1TI0qM1xSaFlFhI85SIR1SFfwskn-zfCr"` y `search_type="exact"` para comprobar duplicados. Ese ID corresponde a la carpeta `4geeks_academy`; confirma/descubre el valor en el esquema dinámico `folder` de la acción antes de usarlo. Si la carpeta no está disponible o el ID no coincide con ese nombre, detente y resuelve la carpeta; no guardes en otra ubicación.
6. Solo si la búsqueda exacta no devuelve coincidencias, crea el archivo con `google_drive_create_file_from_text` (`newtxtfile`), usando exclusivamente parámetros confirmados por el esquema: `title=<nombre exacto con .md>`, `file=<contenido Markdown completo de los proyectos>` y `folder=<ID confirmado de 4geeks_academy>`. Usa la conexión Google Drive predeterminada, que se puede comprobar con `inspect_zapier_actions`; el esquema admite `convert` si se requiere, pero para conservar un `.md` como archivo de texto plano no lo conviertas a Google Docs. No uses acciones de reemplazo ni de actualización.
7. Verifica que la acción de creación devolvió un identificador/enlace y vuelve a buscar el nombre exacto en la carpeta. Confirma que el archivo devuelto es el nuevo y está dentro de `4geeks_academy`; usa su `alternateLink`/enlace web para informar el resultado. Solo entonces comunica el nombre, cantidad de proyectos y enlace. Si MCP falla, no afirmes que se guardó; entrega el resumen en el chat e indica el bloqueo.

## Referencia de API
- Autenticación: procedimiento y helper definidos en `skills/autentication-4geeks-academy/SKILL.md` y `skills/autentication-4geeks-academy/scripts/check_auth.py`.
- Flujo combinado autenticación + consulta: `skills/academy-4geeks-get-projects/scripts/get_projects.py`; no pases el token entre herramientas ni hagas una consulta manual separada.
- Proyectos asignados: `GET /v1/assignment/user/me/task` con `task_type=PROJECT`; parámetros de paginación `limit` y `offset`.
- `task_status`: `PENDING`, `DONE`, `APPROVED`, `REJECTED`. Para distinguir entregado de calificado, interpreta `DONE` junto con `revision_status` cuando esté presente; conserva ambos campos si no está claro.
- Base de producción: `https://breathecode.herokuapp.com`.
- Zona horaria del nombre del documento: `America/Caracas` (Venezuela, UTC−04:00).

## Google Drive mediante Zapier MCP
- Cliente MCP: servidor `zapier` definido en `config/mcporter.json`; descubre los esquemas en tiempo de ejecución con `mcporter list zapier --schema` e `inspect_zapier_actions`, sin inventar acciones ni campos.
- Buscar duplicado: acción Google Drive `google_drive_find_a_file` (clave `file_v2`); parámetros relevantes `title`, `folder` y `search_type="exact"`.
- Crear: acción Google Drive `google_drive_create_file_from_text` (clave `newtxtfile`); parámetros obligatorios `file` (texto plano) y `title`; `folder` selecciona ubicación y `convert` es opcional.
- Destino autorizado: carpeta `4geeks_academy`, ID `1TI0qM1xSaFlFhI85SIR1SFfwskn-zfCr`. La selección dinámica de la carpeta debe verificarse contra su nombre antes de ejecutar.
- Nombre: `Proyectos4GeeksAcademy-RuthDiaz-YYYY-MM-DD.md`, fecha de `America/Caracas`. No sobrescribir duplicados; verifica creación, carpeta y enlace antes de reportar éxito.
