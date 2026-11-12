# Pruebas de Skill 3 — Obtener trabajo pendiente

## Pruebas offline
Ejecuta `python3 -m unittest discover -s skills/academy-4geeks-get-pending-work/tests -v`.

Casos cubiertos:
- La autenticación se verifica antes de consultar cualquiera de los dos estados.
- Una autenticación fallida bloquea toda petición a la API de tareas.
- El helper consulta `PENDING` y `REJECTED` por separado y rechaza registros que no coincidan con el estado consultado.
- El cursor `next` permanece en el host y ruta autorizados y conserva el filtro, límite y avance esperado para cada estado.
- La transformación conserva tipo, estado y contexto disponible sin añadir campos ausentes.

## Evidencia real API (2026-11-12)
- Ejecución del helper autenticó primero y consultó ambos filtros; total reportado 54: 54 `PENDING` y 0 `REJECTED`, en todos los tipos/cohortes. La ejecución anterior del mismo día había devuelto 49 `PENDING`; se conservan ambos resultados de ejecuciones distintas sin atribuir la diferencia a una causa no confirmada.
- La salida estructurada no contiene token ni cabeceras de autorización.

## Google Drive mediante Zapier MCP (2026-11-12)
- Se descubrieron herramientas/esquemas vigentes y se confirmó la carpeta dinámica `4geeks_academy`. La búsqueda exacta del archivo de ese día no encontró duplicados antes de su primera creación.
- El archivo creado previamente `TrabajosPendientes4GeeksAcademy-RuthDiaz-2026-11-12.md` fue verificado por nombre, tipo `text/plain`, carpeta y enlace. Contiene los 49 `PENDING` de la primera ejecución; se creó antes de que Ruth ampliara el alcance para incluir `REJECTED`.
- No se sobrescribió ni se creó otro archivo con el mismo nombre al ampliar el criterio; la skill exige detenerse ante duplicados. Para conservar el nombre diario y actualizar su contenido hará falta autorización explícita para modificar/sobrescribir, o continuar otro día con un nombre de fecha nuevo.
