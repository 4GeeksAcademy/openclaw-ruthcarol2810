# Diseño de la skill

## Objetivo
Autenticar con la Skill 1, listar asignaciones cuyo estado explícito sea `PENDING` o `REJECTED` en cualquier tipo/cohorte y guardar un informe Markdown nuevo en Drive, mostrando esos dos grupos por separado.

## Entrada
Solicitud de Ruth para conocer qué trabajo le falta completar.

## Salida esperada
Archivo `TrabajosPendientes4GeeksAcademy-RuthDiaz-YYYY-MM-DD.md` en `4geeks_academy`, con los grupos `PENDING` (por completar) y `REJECTED` (por corregir), tipos y contexto disponible, o una indicación clara de que ambos grupos están vacíos. Fecha en `America/Caracas`. Reportar éxito solo tras verificar nombre, carpeta y enlace. Nunca sobrescribir duplicados.

## Criterio de alcance
Se consultan `task_status=PENDING` y `task_status=REJECTED` por separado según la referencia API. Se incluyen todos los tipos de tarea y cohortes. Los rechazados se describen como entregas que requieren corrección, sin fusionarlos semánticamente con PENDING. `revision_status=PENDING` por sí solo no hace que una tarea con otro `task_status` sea trabajo por completar.

## Dependencias
- Autenticación: `skills/autentication-4geeks-academy/SKILL.md`, helper `scripts/check_auth.py` y referencia `STUDENT_API_CALLS_REFERENCE_es.md`.
- Helper determinista con paginación/validación: `scripts/get_pending_work.py`.
- Zapier MCP/Google Drive definido en `config/mcporter.json`; descubrir acciones y esquemas vigentes antes de llamar. Confirmar dinámicamente la carpeta autorizada `4geeks_academy` (ID conocido `1TI0qM1xSaFlFhI85SIR1SFfwskn-zfCr`), buscar duplicados exactos y crear archivo de texto plano con la acción Drive disponible.
