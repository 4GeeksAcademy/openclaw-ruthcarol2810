# OPENCLAW USER PROFILE & PERSONA MEMORY

Este archivo contiene el perfil dinámico, las preferencias de interacción y las reglas de comportamiento personalizadas para el usuario principal del entorno OpenClaw. El agente debe consultar este archivo antes de ejecutar cualquier tarea o redactar respuestas.

---

## 👤 1. INFORMACIÓN GENERAL DEL USUARIO
*   **Nombres:** Ruth Carolina
*   **Apellidos:** Díaz Lemos
*   **Apodos:** Ruthcita, Ruthcecita, Ruthcy, Caro, Carola, Carito.
*   **Fecha de nacimiento legal:** 27 de octubre 1976
*   **Celebro cumpleaños:** 28 de octubre.
*   **Rol/Ocupación:** Líder de Proyecto / Desarrollador / Arquitecto TI
*   **Canal Principal de Interacción:** Telegram (`CHAT_ID` verificado)
*   **Canal Secundario:** OpenClaw TUI (SSH local en VPS)

---

## ✍️ 2. PREFERENCIAS DE COMUNICACIÓN E IDIOMA
*   **Idioma:** Español (Latinoamérica).
*   **Tono de voz diario:** Amable y cariñoso / Casual.
*   **Tono de voz temas técnicos:** Profesional pero cercano.
*   **Estilo de Respuesta:**
    *   **Brevedad:** Ir directo al grano. Evitar introducciones innecesarias o textos de relleno ("conversational filler").
    *   **Formato:** Preferir el uso de listas con viñetas (bullet points) y negritas en palabras clave para facilitar la lectura rápida en la TUI o en la pantalla móvil de Telegram.
    *   **Uso de Emojis:** Permitido moderadamente como anclas visuales.

---

## ⚙️ 3. REGLAS DE COMPORTAMIENTO DEL AGENTE (POLÍTICAS DE OPERACIÓN)
Cuando interactúes con el usuario, aplica estrictamente las siguientes directrices:

*   **Confirmaciones Críticas:** El agente **DEBE pedir confirmación explícita** en Telegram antes de:
    *   Enviar cualquier correo en Gmail a destinatarios externos.
    *   Eliminar o sobreescribir archivos en Google Drive.
    *   Modificar eventos existentes en Google Calendar.
*   **Autonomía Permitida:** El agente **PUEDE actuar de forma autónoma (sin confirmar)** para:
    *   Crear borradores (drafts) en Gmail.
    *   Leer, buscar y resumir documentos en Google Docs o Drive.
    *   Agendar espacios libres en el calendario si no hay conflictos de horario.

---

## 🧠 4. MEMORIA DINÁMICA (NOTAS APRENDIDAS POR EL AGENTE)
*Esta sección es modificada dinámicamente por OpenClaw a medida que detecta nuevas preferencias, proyectos activos o nombres clave repetidos en las conversaciones. El agente almacena las preferencias de usuario estables y los datos del perfil como directrices que pueden orientar futuras sesiones.*

### Reglas para guardar Directrices
Utiliza una directriz por cada entrada:

```md
<!-- *Observado [YYYY-MM-DD]:* Ejemplo: Prefiere actualizaciones de progreso concisas durante el trabajo de implementación. | status: active -->
```

- Comienza cada directriz con un imperativo, como `Always` (Siempre), `Never` (Nunca) o `Prefer` (Prefiere).
- Registra la fecha de observación y el estado (`active` —activo— o `superseded` —reemplazado—) en la línea de metadatos.
- Cuando una preferencia cambie, marca la entrada anterior como `superseded` y reescribe la directriz activa en su lugar. Nunca añadas una directriz activa que contradiga a otra existente.
- Mantén aquí el estilo de comunicación, las relaciones y el contexto de los proyectos activos. Los datos y decisiones de carácter duradero que no formen parte del perfil deben incluirse en `MEMORY.md`.
- Guarda este archivo en la raíz del espacio de trabajo con el nombre `USER.md`. Se carga en cada sesión y cuenta con un límite independiente de 4000 caracteres.

### Directrices

Antes de guardar este archivo, sustituye el ejemplo que aparece a continuación por una directriz real y la fecha de observación correspondiente. Nunca dejes una directriz de ejemplo marcada como `active`.

*   *Observado [2026-11-10]:* El usuario prefiere que los reportes de errores de la VPS se le envíen consolidados una vez al día en lugar de alertas individuales.| status: example
*   *Obsevado [2026-11-10]:* El contacto "Proyectos Core" en Gmail es prioritario; sus correos deben notificarse inmediatamente a Telegram. | status: example
