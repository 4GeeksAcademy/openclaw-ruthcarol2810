# Pruebas de Skill 6 — Assets por tecnología

## Automatizadas
Archivo: `tests/test_get_assets.py`.

Cinco pruebas unitarias simulan la API y cubren:

1. resolución canónica pública por nombre exacto, y ambigüedad con candidatos múltiples;
2. proyección de campos permitidos, omisión de datos privados y verificación del slug de tecnología exacto;
3. paginación completa, verificación de `count` y ausencia de cabecera Authorization;
4. rechazo de URL de paginación cross-host e incompletitud;
5. resultado vacío y forma de respuesta inesperada.

Comando ejecutado: `python3 -m unittest discover -s skills/academy-4geeks-get-assets/tests -v`. Resultado: **5 pruebas, todas pasan**. `python3 -m py_compile skills/academy-4geeks-get-assets/scripts/get_assets.py` pasó.

## Comprobación live (solo GET público)

El 2026-11-20 se consultó el catálogo de tecnologías y assets de Python sin credenciales. La tecnología se resolvió como `Python` (`python`, pública, no deprecated); el helper obtuvo **374 assets** y completó su paginación, con tipos: 65 ARTICLE, 19 EXERCISE, 194 LESSON, 89 PROJECT y 7 STARTER. La investigación live adicional confirmó que el filtro `technologies=python` funciona; el listado filtrado devuelve un envelope (`count`, `first`, `next`, `previous`, `last`, `results`) y `offset` cambia la página. También se probó una combinación de filtros de tecnología, tipo y dificultad. Se observó una consulta no encontrada con `count=0`. La consulta con varias tecnologías separadas por coma se acepta, pero no se determinó su semántica; la skill por eso usa una sola tecnología por ejecución. No se creó documento Google Docs en esta comprobación, porque no había una petición de Ruth para listar una tecnología particular como ejecución separada; la conexión y los esquemas de Docs fueron inspeccionados, no se hizo escritura.

La respuesta de listado filtrada incluye campos de metadatos. Los detalles individuales pueden incluir campos adicionales (por ejemplo, author, owner, config, manifest), que no se transmiten en la salida del helper.

## Validación

`python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/quick_validate.py skills/academy-4geeks-get-assets` informó `Skill is valid!`. La comprobación de `git diff --check` global encontró trailing whitespace preexistente dentro de otros artefactos de memoria no relacionados; no se modificaron para evitar tocar trabajo ajeno a esta skill.
