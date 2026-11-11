---
name: autentication-4geeks-academy
description: "Autentica con la API de estudiantes de 4Geeks o comprueba si un token existente sigue vigente; informa únicamente el estado de autenticación."
---

# Autenticación en 4Geeks Academy

1. Ejecuta `python3 scripts/check_auth.py` desde esta carpeta para comprobar el token de estudiante existente. La referencia de la API indica `GET /v1/admissions/user/me` con `Authorization: Token <token>`; no uses login con contraseña.
2. El helper toma `TOKEN_4GEEKS` del entorno o, si no está definido, lee solo esa clave del archivo `/root/.openclaw/.env`, fuera del repositorio. Exige que el archivo sea regular, no sea un enlace simbólico y tenga permisos privados. Nunca muestres el secreto, el `.env`, la cabecera de autorización ni el cuerpo de la respuesta.
3. Considera la autenticación exitosa solo si la API oficial de producción devuelve HTTP 2xx y un objeto JSON. Informa únicamente “autenticación exitosa”. Ante 401/403, informa “token rechazado”; ante configuración ausente, redirección, límite, error de red, timeout, respuesta inesperada u otro código, informa que la comprobación quedó inconclusa, sin atribuirlo a token inválido.
4. No consultes cohorte, estado de inscripción, perfil detallado, cursos, tareas ni otros datos académicos: esta skill solo valida autenticación. No reintentes en bucle.
5. Verifica que la salida contenga solo un estado y, cuando corresponda, una razón técnica no sensible. No imprimas datos del usuario ni guardes la respuesta.
