# Pruebas de la Skill 5 — Eventos 4Geeks

## Validación local
Ejecuta:

```sh
python3 -m unittest discover -s skills/academy-4geeks-get-events/tests -v
python3 -m py_compile skills/academy-4geeks-get-events/scripts/get_events.py
python3 /usr/lib/node_modules/openclaw/skills/skill-creator/scripts/quick_validate.py skills/academy-4geeks-get-events
```

Seis pruebas verifican clasificación AI explícita/no vaga (incluidas etiquetas como lista/objeto), proyección y sanitización, validación de horarios/estado, no envío de token al endpoint público, rechazo de respuestas con forma inesperada y manejo de un resultado que alcanza el límite solicitado.

## Prueba real
- Autenticación 4Geeks: exitosa, aunque el endpoint de eventos es público y no usa ese token.
- Endpoint público: HTTP 200. El 2026-11-20 devolvió un evento futuro AI explícito, el 29 de noviembre de 2026, 18:00–19:00 UTC (14:00–15:00 Venezuela), online.
- Calendar: conexión y zona horaria validadas vía Zapier; búsqueda exacta de evento existente devolvió vacío y disponibilidad consultada libre.
- Evento AI de prueba funcional: ya quedó creado y verificado en el calendario de Ruth; la consulta `google_calendar_retrieve_event_by_id` confirmó la hora y los tres overrides popup. Esta prueba real está anotada en `SKILL_LOG.md`.
