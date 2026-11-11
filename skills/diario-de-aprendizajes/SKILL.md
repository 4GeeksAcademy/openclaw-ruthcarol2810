---
nombre: Diario de Aprendizaje en Google Docs (Zapier MCP)
descripción: Formatea y añade registros estructurados de aprendizaje diario en un Google Doc a través de Zapier MCP.
---

# SKILL: DIARIO DE APRENDIZAJE EN GOOGLE DOCS (ZAPIER MCP)

## DESCRIPCIÓN
Esta Skill permite al agente procesar pensamientos, apuntes sueltos o lecciones del usuario al final de su día, estructurarlos de forma limpia y profesional con un formato uniforme, y guardarlos directamente en un documento centralizado de Google Docs utilizando el protocolo MCP conectado con Zapier.

## CUÁNDO USAR
Se activa cuando el usuario menciona lo que aprendió en el día o expresa la intención de guardar una entrada en su bitácora de conocimiento. Ejemplos de frases activadoras:
- "Hoy aprendí sobre el patrón Circuit Breaker..."
- "Anota esto en mi diario de aprendizaje: descubrí una nueva función de FastAPI..."
- "Quiero registrar lo que estudié hoy en mi bitácora..."

## PRERREQUISITOS
- Agente OpenClaw con el entorno Model Context Protocol (MCP) activo.
- Servidor MCP de Zapier configurado y vinculado a la cuenta del agente.
- Acceso autorizado de Zapier a Google Docs y Google Drive del usuario.
- Un archivo existente en Google Docs destinado a ser el diario de conocimiento (ej. "Diario de Aprendizaje <Nombre de usuario>").

## PROCEDIMIENTO
1. **Comprensión:** Analizar el texto del usuario para extraer las ideas principales y categorizar el tipo de aprendizaje de forma global (ej. PROGRAMACIÓN, IDIOMAS, FINANZAS).
2. **Estructuración:** Sintetizar las lecciones en viñetas claras y concisas usando el carácter "•". Si existe una meta o reflexión personal del usuario, aislarla en una línea dedicada a la reflexión.
3. **Formateo:** Construir el bloque de texto plano agregando la fecha del sistema en formato AAAA-MM-DD, separadores visuales y la estructura definida.
4. **Búsqueda/Selección:** Utilizar las herramientas de Zapier MCP para localizar el documento de destino en Google Docs.
5. **Inyección:** Invocar la acción correspondiente en Zapier para realizar un "Append Text" (añadir texto al final) enviando el bloque estructurado.

## SALIDA ESPERADA
- **Archivo modificado:** Google Doc seleccionado actualizado con la nueva entrada al final del documento.
- **Formato del contenido inyectado:**
  📅 [AAAA-MM-DD] | 🏷️ Categoría: [CATEGORÍA EN MAYÚSCULAS]
  • [Punto clave 1]
  • [Punto clave 2]
  💡 Reflexión: [Línea de reflexión si aplica]
  --------------------------------------------------------------------------------
- **Confirmación al usuario:** Mensaje directo del agente validando que los aprendizajes fueron procesados y guardados bajo la categoría respectiva.

## CASOS ESPECIALES
- **Error de conexión con el Servidor MCP:** Si el servidor MCP de Zapier no responde o falla la autenticación OAuth, el agente guardará el bloque formateado en su memoria contextual local, informará del fallo al usuario y le ofrecerá reintentar la operación o copiar el texto manualmente.
- **Documento no encontrado:** Si la herramienta de búsqueda de Zapier no localiza el diario por su nombre, el agente le solicitará explícitamente al usuario el nombre exacto del archivo o su ID único para reanudar el flujo.
