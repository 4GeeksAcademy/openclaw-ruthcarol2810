# Diseño de la Skill 6 — Assets por tecnología

## Objetivo
Dada una tecnología indicada por Ruth, resolver su slug público canónico en 4Geeks, recuperar todos los assets vinculados a ese slug, resumirlos en Telegram y crear un Google Doc nuevo con la lista detallada y la explicación del esquema de campos observado.

## Activación y entrada
Activar ante solicitudes para buscar/ubicar/listar assets de 4Geeks asociados a una tecnología. La tecnología es un argumento obligatorio. Si falta, preguntar; si el registro devuelve candidatos ambiguos, enumerarlos y esperar selección. No se infiere una tecnología de ejemplos previos.

## Salida esperada
- Mensaje de Telegram con tecnología canónica, total, conteo por tipo y muestra/lista resumida con título, tipo, idioma y dificultad cuando estén disponibles.
- Google Doc titulado `Assets4GeeksAcademy-<slug>-RuthDiaz-YYYY-MM-DD`, con fecha de `America/Caracas`, resumen, glosario de campos y un apartado por asset con todos los campos proyectados no vacíos y enlaces.
- Confirmar el enlace y la creación únicamente después de verificar identificador, contenido y coincidencia de título. No sobrescribir un documento previo.

## API verificada
La referencia local `skills/autentication-4geeks-academy/STUDENT_API_CALLS_REFERENCE_es.md` documenta el endpoint del catálogo y el filtro `technologies`. La consulta pública live del 2026-11-20 confirmó que `GET /v1/registry/technology?like=python&limit=100&offset=0` devuelve el slug `python`, título `Python`, `visibility=PUBLIC` y `is_deprecated=false`; `GET /v1/registry/asset?technologies=python&limit=100&offset=0` produce un envelope paginado con `count=374` y `results`. El helper live recuperó las 374 entradas, incluyendo los tipos ARTICLE, EXERCISE, LESSON, PROJECT y STARTER. Ninguna petición utilizó token de estudiante.

La API observada devuelve recursos públicos de catálogo, no asignaciones del estudiante. Una comprobación adicional live confirmó que el filtro `technologies=python` funciona y que las respuestas filtradas son un envelope paginado (`count`, `first`, `next`, `previous`, `last`, `results`), aunque la referencia local lo resume como lista. La paginación por `offset` produjo páginas distintas. También se verificó que los filtros se pueden combinar con `asset_type` y `difficulty`. El API aceptó una lista de tecnologías separadas por coma, pero no se estableció si combina como OR u otra semántica, por lo que la skill solo usa una tecnología por búsqueda. El catálogo contiene tipos adicionales como `STARTER` además de LESSON/EXERCISE/PROJECT. La skill no presenta los resultados como trabajo personal ni como contenido de una cohorte concreta. Campos de detalle como `manifest`, `config`, autores y propietarios pueden estar ausentes de la respuesta filtrada y se excluyen del helper; no se asegura que el Google Doc reproduzca el cuerpo completo del contenido. Los enlaces `readme_url`/`url` son referencias, no garantía de disponibilidad.

## Diseño de resolución y fallos
El helper consulta `GET /v1/registry/technology?like=<entrada>` y pagina por `count`/`next` para decidir el slug. Solo acepta el candidato público/no deprecated inequívoco según el valor exacto de slug/título o una única opción pública; en otro caso pide selección. Luego consulta el filtro de assets por el slug exacto, valida que cada registro incluya esa tecnología y pagina hasta igualar el total. Valida host, path, parámetros, offsets y conteos; limita el tamaño de respuesta y el número de páginas; no sigue redirecciones. Si hay inconsistencia, falta de páginas o esquema inesperado, la ejecución termina como error y la skill no guarda datos parciales.

## Google Docs / Zapier
En la comprobación viva del 2026-11-20, `mcporter list zapier --schema` e `inspect_zapier_actions` confirmaron una conexión Google Docs predeterminada de Ruth. Se localizaron acciones vigentes para crear desde texto, buscar por título/carpeta y leer contenido por ID. El enum dinámico identificó la carpeta `4geeks_academy`. Los IDs y parámetros deben redescubrirse en cada ejecución y no se codifican como valores fijos en las instrucciones de runtime. No se ha creado un Google Doc en esta fase porque no se solicitó una tecnología concreta para producir un reporte de usuario.
