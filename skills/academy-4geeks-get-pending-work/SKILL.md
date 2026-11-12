---
name: academy-4geeks-get-pending-work
description: "Activa con ‘obtener trabajos pendientes’, ‘qué me falta completar’ y sinónimos; valida autenticación, lista tareas PENDING y REJECTED de todos los tipos y guarda un informe Markdown nuevo en Google Drive."
---

# Trabajo pendiente de 4Geeks Academy

## Frases de activación
Activa esta skill cuando Ruth pida obtener o revisar trabajo pendiente, empezando por «obtener trabajos pendientes» y sinónimos como: «obtener trabajo pendiente», «¿qué me falta completar?», «qué trabajos tengo pendientes», «listar mis tareas pendientes», «¿qué tareas me rechazaron?» o «qué debo corregir».

## Procedimiento
1. Lee `skills/autentication-4geeks-academy/STUDENT_API_CALLS_REFERENCE_es.md` y ejecuta `python3 skills/academy-4geeks-get-pending-work/scripts/get_pending_work.py` desde la raíz del workspace. El helper reutiliza la validación de autenticación de la Skill 1 antes de consultar tareas. Continúa solo con JSON `status: ok`; ante rechazo, resultado inconcluso o error, informa el motivo no sensible y detén el flujo. Nunca leas, muestres ni registres el token ni la cabecera de autorización.
2. Verifica que la salida tenga `status: ok`, `count` y una lista `tasks`, cada registro tenga `task_status` igual a `PENDING` o `REJECTED`, y ambas consultas paginadas hayan terminado correctamente. El helper hace una consulta autenticada por cada estado en `GET /v1/assignment/user/me/task`, con `task_status`, `limit` y `offset`; no consultes otra cohorte ni cambies o entregues tareas.
3. Incluye las tareas con estado explícito `PENDING` y `REJECTED`. Presenta `PENDING` como pendiente de completar y `REJECTED` como rechazada/por corregir, conservando su `task_status` y `revision_status` si existe; no cambies una tarea de estado basándote solo en `revision_status`. Incluye título, tipo (`PROJECT`, `EXERCISE`, `LESSON`, `QUIZ` u otro tal como venga) y cohorte/fechas/identificador solo cuando estén presentes. No incluyas tareas `DONE` o `APPROVED`. Si ambas consultas están vacías, indícalo claramente y prepara un informe sin tareas que corresponden a estos estados.
4. Obtén la fecha actual en `America/Caracas`, con formato `YYYY-MM-DD`. Forma el nombre exacto `TrabajosPendientes4GeeksAcademy-RuthDiaz-<fecha>.md`.
5. Usa Zapier MCP y Google Drive tal como se describe en «Google Drive mediante Zapier MCP» abajo. Descubre herramientas y esquemas vigentes; confirma carpeta `4geeks_academy`, busca coincidencia exacta por nombre y carpeta antes de escribir. Si ya existe el archivo, no lo sobrescribas ni crees un duplicado: avisa y pregunta cómo proceder.
6. Si no hay duplicado, redacta el Markdown en español con título, fecha/hora de consulta si se conoce, total combinado y, de ser posible, subtotales `PENDING` y `REJECTED`; lista las tareas agrupadas por estado. Para cada tarea usa los campos recibidos, sin completar datos ausentes mediante suposiciones. Si no hay resultados, incluye «No se encontraron tareas con estado PENDING ni REJECTED en la consulta». Crea un archivo de texto plano `.md` nuevo en la carpeta `4geeks_academy`; no lo conviertas a Google Docs ni uses acciones de actualización/reemplazo.
7. Verifica el resultado de creación, vuelve a buscar el nombre exacto en la carpeta y confirma identificador, nombre, ubicación y enlace web. Solo entonces informa cuántas tareas `PENDING` y `REJECTED` encontró y comparte el enlace. Si Zapier MCP falla, no afirmes que se guardó: informa el bloqueo y comparte el resumen en el chat si está disponible.

## Criterio de alcance
El informe cubre dos estados API distintos: `PENDING` (tarea pendiente de completar) y `REJECTED` (entrega rechazada, que requiere correcciones). Se consultan por separado para respetar el filtro documentado y luego se reúnen en el mismo informe, distinguiendo claramente los grupos. Incluye todos los tipos de tarea y cohortes. No incluyas `DONE` ni `APPROVED`, y no interpretes `revision_status=PENDING` como `task_status=PENDING`.

## Referencia de API
- Referencia de endpoints y estados: `skills/autentication-4geeks-academy/STUDENT_API_CALLS_REFERENCE_es.md`.
- Helper: `skills/academy-4geeks-get-pending-work/scripts/get_pending_work.py`; autentica antes de llamar a la API y devuelve salida JSON saneada, sin token ni cabeceras.
- Endpoint: `GET https://breathecode.herokuapp.com/v1/assignment/user/me/task?task_status=<PENDING|REJECTED>&limit=100&offset=0`; el helper consulta cada estado por separado, maneja paginación con `offset` y valida enlaces `next` antes de seguirlos. Evidencia de PENDING del 2026-11-12: 49 registros (33 ejercicios, 10 proyectos y 6 lecciones); sin filtrar por tipo ni cohorte.
- Estados documentados: `PENDING`, `DONE`, `APPROVED`, `REJECTED`; tipos documentados: `PROJECT`, `EXERCISE`, `LESSON`, `QUIZ`.
- Zona horaria del nombre: `America/Caracas` (Venezuela, UTC−04:00).

## Google Drive mediante Zapier MCP
- Configuración: servidor `zapier` de `config/mcporter.json`, cliente `mcporter`. Sigue la skill instalada `mcporter` y descubre el esquema vigente (`mcporter list zapier --schema`, después `inspect_zapier_actions` sin argumentos y con `selected_api` de Google Drive); solicita esquemas por `tool_name`. No inventes nombres, campos ni llamadas.
- Verifica que la conexión predeterminada sea la cuenta de Google Drive de Ruth indicada por el contexto; no enseñes identificadores internos al usuario.
- Antes de escribir, usa la acción de búsqueda exacta `google_drive_find_a_file` (clave `file_v2`) con el nombre generado, carpeta y `search_type="exact"`. Los parámetros y enumeraciones dinámicas deben confirmarse en el esquema.
- La carpeta autorizada conocida es `4geeks_academy`, ID `1TI0qM1xSaFlFhI85SIR1SFfwskn-zfCr`. Confirma que sigue apareciendo con ese mismo nombre en la selección dinámica; si no, detente y no guardes en otra carpeta.
- Solo si no existe duplicado, usa la acción `google_drive_create_file_from_text` (clave `newtxtfile`) con `title=<nombre exacto .md>`, `file=<Markdown completo>` y `folder=<ID confirmado>`. Usa los nombres/campos solo después de redescubrir su esquema. Mantén el archivo como texto plano (`convert` omitido o falso); nunca uses acciones de reemplazo/actualización.
- Después, confirma el resultado de creación y vuelve a buscar por nombre exacto en la carpeta. Usa el `alternateLink` o enlace web verificado al informar éxito.
