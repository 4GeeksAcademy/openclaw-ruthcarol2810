---
name: academy-4geeks-get-progress-summary
description: "Activa con ‘cómo va mi progreso en el curso’, ‘cuánto he avanzado en el bootcamp’, ‘cómo voy con el bootcamp’ y sinónimos; valida autenticación y resume los estados y tipos de tareas asignadas en 4Geeks, sin presentarlo como porcentaje oficial del curso."
---

# Resumen de progreso en 4Geeks Academy

## Frases de activación
Activa con «¿cómo va mi progreso en el curso?», «¿cuánto he avanzado en el bootcamp?», «¿cómo voy con el bootcamp?» y sinónimos como «muéstrame mi progreso», «qué tanto he completado», «dame un resumen de mi avance» o «cómo voy en el curso».

## Procedimiento
1. Desde la raíz del workspace, ejecuta `python3 skills/academy-4geeks-get-progress-summary/scripts/get_progress_summary.py`. El helper obtiene el token y verifica la autenticación llamando primero al helper de `autentication-4geeks-academy`; solo si responde `authenticated` consulta tareas. Si falta el token, se rechaza o la autenticación es inconclusa, detente y comunica que no fue posible obtener datos actuales; no uses datos anteriores como actuales.
2. Acepta solo JSON con `status: ok`. Comprueba que `total_assignments` sea igual a la suma de `counts_by_task_status`, de `counts_by_revision_status` y de `counts_by_type`; comprueba que los subtotales por cohorte sumen el total cuando cada asignación trae cohorte. Si el helper falla, produce un campo inesperado o los totales no cuadran, no presentes el resultado como completo.
3. Prepara el resumen para responder en el chat actual de Telegram. Incluye la hora/fecha local de Venezuela (`as_of_venezuela`), el total de asignaciones, conteos por `task_status` y `task_type`, y cohortes cuando estén informadas. Separa `task_status` de `revision_status`; explica que `PENDING` está pendiente, `DONE` indica completada por la estudiante, `APPROVED` aprobada y `REJECTED` requiere correcciones. Conserva estados desconocidos como se devuelvan.
4. Incluye la nota `metric_note` del resultado: esto cuenta asignaciones visibles de la API, no representa un porcentaje oficial del avance del curso. No calcules ni prometas un porcentaje de curso o syllabus: la referencia disponible no define el total curricular ni una fórmula oficial.
5. No llames a `/v1/activity/me` para deducir porcentaje: su esquema documentado es insuficiente. No es necesario consultar cohortes ni actividad agregada; no consultes datos de otras personas. No modifiques, entregues ni guardes tareas o informes en Drive.
6. Entrega el resumen solo después de validar autenticación, respuesta y conteos; verifica que la respuesta final del chat indique claramente la limitación de la métrica. Si la autenticación fue rechazada/inconclusa, no envíes cifras de progreso.

## Referencias API
- Autenticación: `skills/autentication-4geeks-academy/SKILL.md` y `skills/autentication-4geeks-academy/scripts/check_auth.py` (`GET /v1/admissions/user/me`).
- Tareas asignadas: `GET /v1/assignment/user/me/task?limit=100&offset=0`; la referencia local documenta paginación y estados/tipos. El helper comprueba host, ruta, offset, consistencia del conteo y límite de paginación.
- Base documental: `skills/autentication-4geeks-academy/STUDENT_API_CALLS_REFERENCE_es.md`.

## Formato sugerido
«Resumen de tus tareas registradas (fecha/hora Venezuela): N asignaciones. Por estado: … Por tipo: … [por cohorte, si está disponible]. PENDING: por completar; DONE: completada; APPROVED: aprobada; REJECTED: requiere correcciones. Esto resume asignaciones visibles en 4Geeks; no es el porcentaje oficial de avance del curso».
