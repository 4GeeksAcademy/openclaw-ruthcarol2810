# DISEÑO DE LA SKILL

## ¿Qué hace esta skill? Una frase.
Gestor de Acuerdos y Minutas: Asistente de Minutas y Seguimiento de Reuniones Automatizado

## ¿Qué input necesita el agente? ¿Qué le das, en qué formato — y qué ya sabe a partir de los cinco archivos de configuración?
Se agrega al agente a una reunión virtual en un grupo de Telegram, se le indica el inicio de la reunión, se plantea el objetivo de la reunión, se emiten opiniones por mensajes de texto o audios, se llega a acuerdos y se indica el cierre de la reunión. 
A partir de los archivos de configuración, el agente sabe que solo debe participar si se le pregunta algo directamente, mantenerse imparcial, mantener la seguridad de las conversaciones privadas, para no revelar información confidencial en ningún grupo. Cuando se anuncie el cierre de la reunión participar para validar los acuerdos. 

## ¿Cómo es un buen output? Formato, destino (un Doc, un evento de Calendar, un mensaje de Telegram…) y cómo sabrás que funcionó.
Al finalizar la reunión, el agente debe generar: 
- Un documento en Google Docs con la minuta. 
- Eventos en Google Calendar según los acuedos, los eventos deben estar vinculados a la minuta. 
- Mensaje en el grupo de Telegram, con resumen de la minuta, notificación y enlace del documento creado, y listado de eventos creados en base a los acuerdos de la reunión.
