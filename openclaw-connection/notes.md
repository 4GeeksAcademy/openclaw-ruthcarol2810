# NOTAS DE CONFIGURACIÓN Y CONEXIÓN DEL AGENTE OPENCLAW

## AGENTE OPENCLAW

### Decisiones de configuración
. Uso de VPS provista en los recursos de 4Geeks Academy.
. Conexión ssh desde terminal local.
. Instalación de OpenClaw, selección de modelos vinculados. 
. OpenClaw funcionando por OpenClaw Tui.

### Problemas encontrados
. Sin inconveninetes encontrados. 

## CONEXIÓN CON TELEGRAM

### Decisiones de configuración 
. Conexión usando BotFather, sin inconvenientes.
. Modificación del archivo openclaw.json para agregar el canal Telegram
. Reinicio del Gateway de OpenClaw
. Conexión establecida con éxito. 
. Configuración del bot en Telegram.

### Problemas encontrados
. Sin inconvenientes.


## CONEXIÓN CON ZAPIER

### Decisiones de configuración
. Creación de cuenta de correo, para uso exclusivo del Agente.
. Creación de cuenta en Zapier, vinculada al nuevo correo.
. Conexión de Zapier con OpenClaw, con inconvenientes.
. Luego de resolver inconvenientes con la VPS, se logra la conexión con Zapier, gestionada por el agente desde Telegram.
. Conexión establecida con exito.

### Problemas encontrados
. Timeout al intentar conectar.
. Error de autenticación con el LLM.

### Gestión y procesos aplicados para corregir los errores
. Revisar status y doctor de openclaw.
. Reinicio de gateway OpenClaw.
. Revisión de VPS que solicita instalar actualizaciones y reinicio. Se instalan las actualizaciones, se reinicia la VPS. 
. Se incrementa la memoria swap de 2 a 4Gb.
. Se genera nueva API Key del Lite LLM.
. Se configura nuevamente el modelo Luna, sin embargo, se conserva el Claude de base. 
. Revisar status y doctor de openclaw.
. Reinicio de gateway OpenClaw.

### Gestión y procesos aplicados para corregir los errores en mentoría
. Revisar status y doctor de openclaw.
. Reinicio de gateway OpenClaw.
. Se configura el modelo Luna unicamente, quitando el Claude de base. 
. Instalación de actualizaciones, reinicio de VPS.

## CONEXIÓN CON GOOGLE CALENDAR

### Decisiones de configuración
. Conexión gestionada con OpenClaw desde Telegram (NucitaBot).
. Conexión con configuración por Defecto. 

### Problemas encontrados
. Sin inconvenientes 

## CONEXIÓN CON GOOGLE DOCS

### Decisiones de configuración
. Conexión gestionada con OpenClaw desde Telegram (NucitaBot).
. Conexión con configuración por Defecto. 

### Problemas encontrados
. Sin inconvenientes 
