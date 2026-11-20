# Diseño de la Skill 5 — Eventos 4Geeks

## Objetivo
Mostrar en Telegram los eventos futuros publicados por 4Geeks y crear automáticamente en el calendario principal de Ruth los eventos cuya relación con IA sea explícita, con recordatorios popup de 24 horas, 1 hora y 5 minutos cuando esos momentos aún estén en el futuro.

## Entrada y salida
- Entrada: petición para mostrar eventos de 4Geeks y sinónimos.
- Salida: lista breve y localizada a `America/Caracas`; eventos AI creados se enumeran solo tras confirmar Calendar API + verificación de recordatorios.

## Fuente y confianza
- Endpoint público documentado: `GET /v1/events/all`, con `upcoming` y `limit`; la referencia local no documenta paginación específica de eventos.
- Ejecución no autenticada observada: HTTP 200, lista JSON directa con un evento futuro. El endpoint ofrece `starting_at`, `ending_at`, `event_type`, `excerpt`, `description`, `online_event`, `venue`, `academy`, `tags`, `url`, `status`.
- No se confirmó si la lista está limitada a una academia; se muestra la academia reportada y no se atribuye a sede/cohorte específica sin evidencia.
- Los términos de IA se comparan heurísticamente en texto y etiquetas string/estructuradas; criterios vagos no bastan para autoagendar.

## Calendario y efectos
- Zapier MCP conecta la cuenta Google Calendar de Ruth. El calendario principal consultado está en `America/Caracas`; acciones y schemas se deben redescubrir en cada ejecución.
- Se investigaron Find Events, Find Busy Periods, Retrieve Event by ID y las solicitudes API autenticadas. Se verificó lectura del calendario y aceptación de URL HTTPS `https://www.googleapis.com/calendar/v3/calendars/primary`.
- Se creó un evento AI real elegible después de verificar que no había duplicado ni conflicto; Retrieve Event by ID confirmó horario y los tres avisos popup.
- Los tres recordatorios requieren el endpoint API de Calendar, ya que la acción Create Detailed Event solo expone un único número de minutos. Nunca informar éxito si no se verifican avisos.
