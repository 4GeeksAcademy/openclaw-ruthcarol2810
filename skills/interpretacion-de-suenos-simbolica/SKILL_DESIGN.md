# DISEÑO DE LA SKILL

## ¿Qué hace esta skill? Una frase.
Interpretar los sueños que le plantea el usuario

## ¿Qué input necesita el agente y qué recursos incorpora la skill?
El usuario relata un sueño en lenguaje coloquial, o pregunta por un símbolo concreto. El script de consulta devuelve resultados de Dream Bible y AuntyFlo; reutiliza caché por siete días por separado para cada fuente y consulta únicamente las fuentes sin resultado exitoso vigente. No puede excluir una fuente de las consultas nuevas. El otro script ofrece un diario local opcional con consentimiento explícito y conteo de símbolos recurrentes. Dream Book se informa como no disponible: el dominio indicado no resolvió en la comprobación del 2026-11-20; no se consulta ni se sustituye por otra fuente. No hacen falta wrappers ni cambios globales de OpenClaw. Las referencias de portales, scripts y diario están en `references/`; el formato de respuesta está definido en `SKILL.md`.

## ¿Cómo es un buen output? Formato, destino (un Doc, un evento de Calendar, un mensaje de Telegram…) y cómo sabrás que funcionó.
Al interpretar, el agente genera una lectura narrativa imaginativa y lúdica, basada primero en el relato y usando como inspiración únicamente extractos web obtenidos y atribuidos. Puede guardar metadatos limitados solo con consentimiento explícito, y consultar tendencias únicamente si Ruth las pide o autoriza relacionar el sueño actual con el diario.
