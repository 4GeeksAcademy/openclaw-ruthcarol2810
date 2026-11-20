---
name: academy-4geeks-get-assets
description: "Busca en el catálogo público de 4Geeks todos los assets asociados a una tecnología; resume los resultados en Telegram y crea un Google Doc nuevo con el listado detallado y su esquema de campos."
---

# Assets de 4Geeks por tecnología

## Activación

Activa esta skill cuando Ruth pida ubicar, listar o buscar los assets de 4Geeks para una tecnología, por ejemplo:

- «ubica en la lista de assets de 4Geeks todos los de Python»;
- «busca en 4Geeks todos los assets con React»;
- «¿qué recursos de 4Geeks hay para JavaScript?»;
- expresiones equivalentes que nombren claramente la tecnología.

La tecnología es un dato de entrada. Si no está especificada, pregunta cuál quiere consultar. Si la API encuentra varios candidatos plausibles, presenta sus nombres y slugs y pide que elija; no adivines.

## Procedimiento

1. Ejecuta `python3 skills/academy-4geeks-get-assets/scripts/get_assets.py "<tecnología>"` desde la raíz del workspace, sustituyendo el argumento por la tecnología indicada. El catálogo público no requiere token; no leas credenciales ni uses endpoints privados. Continúa solo si el helper devuelve JSON `status: ok`. Para `needs_selection`, `not_found` o `not_available`, informa el resultado de forma breve y, si aplica, pide una opción. Ante `status: error`, detén el flujo y explica el bloqueo sin reutilizar resultados antiguos.
2. Usa únicamente los assets devueltos por el helper y presenta en Telegram un resumen conciso: nombre de la tecnología canónica (título y slug), cantidad total, distribución por `asset_type` y una lista breve de títulos con tipo, idioma y dificultad cuando existan. Indica si hay cero resultados. La API es un catálogo público, no una lista de tareas asignadas a Ruth ni de contenido disponible para su cohorte.
3. No declares el catálogo exhaustivo si el helper falla en la paginación, o si su configuración/rangos fueron alterados. El helper valida conteo, enlaces de paginación y coincidencia exacta del slug en cada registro. No filtres resultados por cuenta personal o cohorte. La búsqueda usa `technologies=<slug canónico>`; no infieras semántica para búsquedas de múltiples tecnologías.
4. Forma el título del Google Doc como `Assets4GeeksAcademy-<slug>-RuthDiaz-<YYYY-MM-DD>`, usando la fecha del día en la zona `America/Caracas`. Escapa el título solo según lo exija el esquema de la acción, no cambies el slug canónico. Si ya existe un documento con el mismo título, no lo sobrescribas ni crees otro con el mismo nombre: informa y detente.
5. Para el documento detallado, crea una sección de resumen (tecnología, fecha, total, advertencia de catálogo público) y luego enumera cada asset con los campos proyectados por el helper: título, slug, tipo, idioma, descripción, dificultad, duración, estado, visibilidad, tecnologías, enlaces (`url`, `readme_url`, `preview`), categoría, indicadores (`graded`, `interactive`, `with_solutions`, `with_video`) y traducciones cuando estén presentes. Omite campos que no vengan en el resultado; no rellenes datos. Incluye una breve explicación del esquema: `slug` es el identificador legible; `asset_type` es la clase de recurso; `technologies` son tecnologías relacionadas; `lang` es el idioma; los campos de descripción, dificultad/duración, estado/visibilidad y enlaces son metadatos del catálogo; los indicadores son booleanos opcionales; `category` contiene título/slug; `translations` relaciona variantes idiomáticas cuando la API las informa. El documento contiene metadatos y enlaces públicos, no el cuerpo completo de cada lección; para ese contenido enlaza `readme_url` o `url` si están disponibles. No intentes descargar ni inferir esquemas internos de contenido desde campos `manifest` no proporcionados por el helper.
6. Descubre en tiempo de ejecución las herramientas y esquemas de Zapier MCP con la skill `mcporter`: `mcporter list zapier --schema`; `inspect_zapier_actions` primero sin argumentos y luego para Google Docs con el `selected_api` recién devuelto; inspecciona las acciones específicas por `tool_name`. Comprueba que la conexión de Google Docs es la cuenta autorizada de Ruth. No inventes acciones, parámetros, conexiones ni valores de carpeta. Busca por título exacto y, si no hay duplicado, crea un documento nuevo con la acción/esquema de creación de Google Docs disponible y el contenido detallado completo. Usa solo campos confirmados por el esquema. No actualices ni sobrescribas documentos. Si la acción no puede verificar duplicados o generar un documento con esos datos, detente y reporta el bloqueo; no uses una API alternativa ni una cuenta distinta.
7. Verifica la creación con la respuesta de la acción y vuelve a buscar/leer el documento mediante las acciones de lectura apropiadas si están disponibles. Confirma título, identificador/enlace y que el contenido tiene el resumen y los assets esperados (incluido el total, estructura y último asset). Reporta éxito solo después de verificar. Si el proveedor no devuelve contenido legible para confirmar, informa qué se verificó y qué quedó sin verificar; no presentes la creación como íntegramente comprobada.
8. Cierra la respuesta en Telegram con el resumen de resultados y el enlace al Google Doc si la creación fue comprobada. Si hubo duplicado, ambigüedad, error de API, falla de MCP o restricción de tamaño, explica claramente el motivo y no afirmes que el archivo se creó.

## Fuente y límites

- Tecnología: `GET https://breathecode.herokuapp.com/v1/registry/technology?like=<texto>` para resolver un slug canónico público.
- Assets: `GET https://breathecode.herokuapp.com/v1/registry/asset?technologies=<slug>&limit=100&offset=0` y siguientes páginas indicadas por `next`.
- El helper solo expone campos públicos seleccionados; no transmite autores, propietarios, IDs internos ni objetos de perfil.
- El API de catálogo puede incluir recursos de muchas academias y repositorios. No se atribuye el recurso a una cohorte o asignación de Ruth.
- Revisa el esquema Zapier vivo antes de cualquier escritura/lectura de Google Docs. No incluyas credenciales en URLs, títulos ni contenido.
