# REGLAS DE FORMATO DE MINUTAS Y MENSAJES

Este documento define las reglas de diseño, estructura y normalización de datos que el agente debe aplicar estrictamente al generar contenido en Google Docs y Telegram.

---

## 1. NORMALIZACIÓN DE DATOS Y FECHAS
* **Fecha de referencia:** Al procesar una minuta, consulta la fecha vigente del sistema y úsala como referencia para resolver expresiones temporales relativas. Las fechas incluidas en los ejemplos de este archivo —como `2026-11-09`— son ilustrativas; no son una fecha actual fija.
* **Cálculo de fechas relativas:** Convierte expresiones temporales relativas a fechas exactas en formato `AAAA-MM-DD`, usando como base la fecha vigente. Si el chat confirma otro punto de referencia para una frase (por ejemplo, “el viernes después de la reunión del 9 de noviembre”), usa ese punto de referencia explícito. Si la expresión sigue siendo ambigua, valida el contexto de la reunión y pide aclaración antes de agendar.
  * *Ejemplos ilustrativos, suponiendo como fecha de referencia el lunes `2026-11-09`:* "Este viernes" -> `2026-11-13`; "El lunes de la próxima semana" -> `2026-11-16`. En uso real, vuelve a calcular con la fecha vigente.
* **Nombres Propios:** Capitaliza siempre la primera letra de los nombres de los participantes y responsables (ej. *Luis Morales*, nunca *luis morales* o *luis*).

---

## 2. ESTRUCTURA OBLIGATORIA PARA GOOGLE DOCS
El documento generado en Google Docs debe seguir estrictamente la siguiente jerarquía y sintaxis Markdown simplificada:

```text
# Minuta de Reunión: [Tema Central de la Reunión]
**Fecha:** [AAAA-MM-DD]
**Participantes:** [Nombre 1], [Nombre 2], [Nombre 3]

## 1. Puntos Tratados
* [Breve resumen del punto discutido 1 en verbo pasado/presente]
* [Breve resumen del punto discutido 2 en verbo pasado/presente]

## 2. Acuerdos y Plan de Acción
* **[Nombre del Responsable]:** [Acción a realizar en verbo infinitivo] — *Fecha límite: [AAAA-MM-DD]*

## 3. Próxima Reunión (Si aplica)
* **Fecha y Hora:** [AAAA-MM-DD] a las [HH:MM]
```

*Nota: No agregues secciones vacías. Si no se acordó una próxima reunión, omite la sección 3.*

---

## 3. FORMATO DEL MENSAJE DE CIERRE EN TELEGRAM
Para evitar errores de parseo con la API de Telegram y garantizar una lectura rápida, el mensaje debe ser un resumen ejecutivo directo que cumpla con:

* **Laconismo:** Máximo 150 palabras. No dupliques el contenido completo de la minuta.
* **Uso de Enlaces Enmascarados:** Queda prohibido mostrar URLs largas y crudas. Usa la sintaxis `[Texto del enlace](URL)`.
* **Emojis Funcionales:** Utiliza únicamente los siguientes emojis como anclajes visuales al inicio de la línea:
  * ✅ Al inicio del mensaje para confirmar el éxito del flujo.
  * 📄 Para presentar el enlace del documento de Google Docs.
  * 📅 Para introducir la lista de eventos creados en Google Calendar.
  * 👤 Para denotar a los responsables de una tarea en el resumen de eventos.

### PLANTILLA DEL MENSAJE EN TELEGRAM:
```text
✅ ¡Minuta procesada con éxito!

📄 [Ver Minuta en Google Docs]([URL_DEL_DOC])

📅 **Eventos agendados en Calendar:**
* 👤 **[Responsable]:** [Nombre de la Tarea] ([Día de la semana], [DD] de [Mes Corto])
```

---

## 4. EJEMPLO DE TRANSFORMACIÓN (CASO DE ÉXITO)

> **Ejemplo ilustrativo:** las fechas `2026-11-09`, `2026-11-13` y `2026-11-16` de esta sección muestran cómo se resolvería el caso con fecha de referencia lunes 9 de noviembre de 2026. No son valores fijos ni deben usarse como fechas actuales en otras minutas.

### ENTRADA DESDE TELEGRAM:
> *Carlos: "Buenas, iniciamos la reunión. Está María y también ingresó Luis. Hay que definir el logo. Luis dice que lo puede tener listo para este viernes. María, ¿puedes armar el presupuesto para el lunes 16 de noviembre?"*

### SALIDA PROCESADA PARA GOOGLE DOCS:
```text
# Minuta de Reunión: Definición de Logo y Presupuesto
**Fecha:** 2026-11-09
**Participantes:** Carlos, María, Luis

## 1. Puntos Tratados
* Coordinación inicial sobre el diseño del nuevo logo del proyecto.
* Planificación de los tiempos de entrega para el presupuesto financiero.

## 2. Acuerdos y Plan de Acción
* **Luis:** Entregar propuesta de diseño del logo — *Fecha límite: 2026-11-13*
* **María:** Armar y presentar el presupuesto del proyecto — *Fecha límite: 2026-11-16*
```

### SALIDA PROCESADA PARA TELEGRAM:
```text
✅ ¡Minuta procesada con éxito!

📄 [Ver Minuta en Google Docs](https://google.com)

📅 **Eventos agendados en Calendar:**
* 👤 **Luis:** Entrega de diseño de logo (Viernes, 13 de Nov)
* 👤 **María:** Entrega de presupuesto (Lunes, 16 de Nov)
```
