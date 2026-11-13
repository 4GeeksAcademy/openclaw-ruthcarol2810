# Pruebas de Skill 4 — Resumen de progreso

## Pruebas locales
Ejecuta:

```sh
python3 -m unittest discover -s skills/academy-4geeks-get-progress-summary/tests -v
```

Casos cubiertos: autenticación previa a las consultas de tareas; bloqueo completo cuando la autenticación falla; resumen por estado, tipo y cohorte; paginación con host/ruta/offset validados; estados desconocidos; inconsistencia de paginación; conjunto sin tareas.

## Prueba real pendiente
La única ejecución real del helper, el 2026-11-13, devolvió `{"status":"error","reason":"token_rejected"}` en la validación de autenticación. Por diseño no se consultaron tareas tras ese resultado. No se obtuvo un resumen actual ni se envió ningún mensaje con cifras a Telegram. Repetir la comprobación solo cuando el token privado haya sido renovado/corregido; no copiar secretos al repositorio ni a mensajes.

## Telegram
Cuando la autenticación y consulta actuales sean válidas, responder en el chat actual de Telegram con los datos del helper y la limitación de que no son un porcentaje oficial del curso. La entrega solo se considera hecha una vez que el canal confirma el envío. Nunca usar datos antiguos para simular una respuesta actual.
