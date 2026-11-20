# Referencia del Registro de Sueños y Tendencias

El script `scripts/registro.py` mantiene un diario simbólico local optativo. Solo escribe después de consentimiento explícito. Este documento establece cómo clasificar las entradas y comunicar recurrencias sin atribuirles significado psicológico comprobado.

## Clasificación de Relatos (`--tipo`)

Al ejecutar `registro.py agregar`, el agente debe clasificar el sueño según los siguientes criterios:
- `propio`: Sueños directos de Ruth. Cuentan para las tendencias.
- `tercero`: Sueños contados por Ruth pero que le ocurrieron a otra persona. No se guardan por defecto; requiere autorización explícita de Ruth y, si la persona es identificable, también su consentimiento. Guarda solo metadatos no identificables. Se excluyen de las tendencias.
- `parcial`: Sueños propios fragmentados o incompletos. Cuentan para las tendencias, pero su recurrencia no activa recordatorios automáticamente.

## Estructura del Reporte de Hilos Recurrentes

Solo si Ruth pide ver sus patrones o autoriza relacionar un sueño actual con el diario, ejecuta `registro.py tendencias`. Si devuelve `"umbral_cumplido": true`, informa el conteo de símbolos entre entradas distintas con lenguaje tentativo. No sugieras que la repetición revela una causa, mensaje o resistencia psicológica.

### Hilos recurrentes en tus sueños
*Conteo en [X] relatos propios o parciales considerados.*

- **[Símbolo en Español] ([Símbolo en Inglés]):** Ha aparecido en [N] relatos distintos. Es una recurrencia del registro; su sentido depende de cada sueño y de lo que Ruth asocie con el símbolo.
  *Ejemplo:*
  - **Serpiente (snake):** Ha aparecido en 3 relatos distintos. Es una recurrencia del registro; su sentido depende de cada sueño y de lo que Ruth asocie con el símbolo.

## Reglas de Privacidad y Consentimiento

1. **Datos Sensibles:** El diario de sueños reside localmente en el entorno de OpenClaw. No debe indexarse en búsquedas globales ni transmitirse a servicios externos. Al consultar diccionarios web, usa solo términos simbólicos genéricos, nunca el relato, nombres propios o datos identificables.
2. **Sueños de terceros:** No guardar por defecto. Si Ruth solicita conservar metadatos simbólicos no identificables, pide consentimiento explícito y excluye esos registros de tendencias propias.
3. **Eliminación:** Si Ruth solicita borrar el diario, verifica que se refiere al diario local y elimina el archivo configurado en `OPENCLAW_DREAM_LOG` o, si esa variable no existe, `~/.local/share/openclaw/dream-journal/historial_suenos.json`. No confundas este diario con `memory/dreaming/` ni con la caché web.
