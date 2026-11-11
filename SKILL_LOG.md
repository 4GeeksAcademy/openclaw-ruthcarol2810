# Registro de skills — 4Geeks Academy

## Skill 1 — Autenticación

- **Prompt inicial en lenguaje natural:** «La primera skill es para autenticarnos en la API de estudiantes de 4Geeks Academy, dónde estoy haciendo el Bootcamp de AI Engineering».
- **Alcance aclarado durante la conversación:** «En esta primera skill solo debemos autenticarnos con exito».
- **Qué hace:** comprueba si el token de estudiante existente permite autenticarse. Informa solo el resultado de autenticación; no consulta cohorte, estado de inscripción ni otros datos académicos.
- **Endpoint:** `GET https://breathecode.herokuapp.com/v1/admissions/user/me`, con `Authorization: Token <token>` según `skills/autentication-4geeks-academy/STUDENT_API_CALLS_REFERENCE_es.md`.
- **Manejo del secreto:** el helper lee `TOKEN_4GEEKS` del entorno o de un `.env` privado ubicado fuera del repositorio. El secreto no está escrito en la skill ni en este registro, y no se imprime.
- **Prueba:** ejecución de `python3 scripts/check_auth.py` desde `skills/autentication-4geeks-academy/` contra la API real; resultado `{"status": "authenticated"}`. No se expusieron datos del usuario.
- **Validación:** `quick_validate.py` informó «Skill is valid»; también pasó la compilación de Python y pruebas simuladas para respuesta exitosa, 401 y redirección.
