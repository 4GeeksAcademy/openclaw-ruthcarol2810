# Diseño de Skill 4 — Resumen de progreso

## Objetivo
Tras validar autenticación con la Skill 1, consultar las asignaciones del estudiante y resumirlas por estado, tipo y cohorte informada; responder en el chat actual de Telegram si la consulta actual fue válida.

## Evidencia y métricas
La referencia de API no documenta un endpoint, denominador curricular ni fórmula oficial de progreso del curso. Por ello el helper cuenta resultados de `/v1/assignment/user/me/task` como tareas asignadas visibles. No calcula porcentajes ni infiere progreso de syllabus. Mantiene por separado `task_status` y `revision_status`, y preserva estados/tipos desconocidos.

## Datos y endpoints
- Validación previa: helper existente de Skill 1 (`GET /v1/admissions/user/me`).
- Tareas asignadas: `GET /v1/assignment/user/me/task?limit=100&offset=...`; se pagina hasta completar el total publicado o hasta `next=null`.
- Los conteos por cohorte se obtienen de los registros de tareas que incluyen el campo `cohort`; no requiere una consulta de inscripciones adicional.

## Salida
Respuesta breve en Telegram con hora local de Venezuela, total de asignaciones, conteos por estado y tipo, conteos por cohorte cuando estén informados y nota explícita de que no es porcentaje oficial.

## Límites
No usar `/v1/activity/me` para estimar porcentaje: la respuesta está insuficientemente definida en la referencia. No consultar actividad agregada de cohorte ni incluir datos de otras personas. No modificar tareas ni escribir a Drive. No reportar cifras si auth, consulta o paginación falla.
