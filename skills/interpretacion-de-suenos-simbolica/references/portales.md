# Referencia de portales y diccionarios de sueños

Este documento detalla el comportamiento esperado del agente al interactuar con las fuentes de inspiración web y cómo reaccionar ante contingencias técnicas.

## Fuentes configuradas y resultado de comprobación

El helper `../scripts/buscar_simbolos.py` devuelve un resultado por cada fuente configurada. Envía únicamente términos simbólicos genéricos breves en inglés, nunca el relato ni datos identificables. Reutiliza resultados exitosos guardados en caché por siete días; solo consulta en la web una fuente para la que no tenga un resultado exitoso vigente.

- **Dream Bible (inglés):** `https://www.dreambible.com/search.php?q=<símbolo>`. Verificado el 2026-11-20 para `snake`: HTTP 200; el HTML contenía una entrada con encabezado en negrita y el párrafo definitorio siguiente. El helper acepta el símbolo normalizado y su forma plural simple y extrae el párrafo siguiente.
- **AuntyFlo (inglés):** `https://www.auntyflo.com/dream-dictionary/<slug>`. Verificado el 2026-11-20 para `/snake`: HTTP 200, con un encabezado `h1` y párrafos de artículo. El helper requiere que el símbolo normalizado aparezca en algún encabezado `h1` y devuelve hasta tres párrafos suficientemente largos, excluyendo algunos bloques de navegación/aviso conocidos; no es una extracción semántica completa.
- **Dream Book (español):** `https://www.dreambook.es/`. El 2026-11-20 el dominio no resolvió por DNS desde el entorno (incluyendo el host con y sin `www`). El helper no lo consulta y siempre informa `unavailable` por esta comprobación; esto no demuestra que la falla sea permanente. No se debe decir que el sitio fue consultado ni escoger un dominio sustituto sin confirmación de Ruth.

El contenido de estos sitios es externo y puede cambiar. Parafrasea en la interpretación; los extractos breves solo sirven para inspiración y atribución con enlace. No son evidencia científica ni diagnóstico.

## Preferencias de fuente

- Esta skill no configura un archivo persistente de preferencias de fuente; respeta las preferencias expresadas en la conversación.
- El helper siempre devuelve los campos de Dream Bible y AuntyFlo, pero no tiene una opción para excluir una fuente de la consulta nueva. Reutiliza una entrada exitosa vigente por fuente; para cada fuente sin caché vigente intenta una consulta. Si Ruth prefiere una, puedes basar en ella la interpretación y citar solo sus resultados. Si pide no enviar el símbolo a una fuente, no ejecutes el helper: explica que esta versión no permite aislarla y continúa con una lectura creativa del relato, salvo que exista otra vía aprobada.
- En ausencia de preferencia, usa los resultados disponibles de Dream Bible y AuntyFlo; el helper consulta solo los resultados que no estén en caché vigente. Informa que Dream Book está deshabilitado/no disponible cuando sea pertinente.

## Planes de Contingencia y Mitigación de Errores

### Caso A: No hay una entrada utilizable (`not_found`)
1. Prueba un sinónimo breve en inglés una vez si es obvio (por ejemplo, `laptop` → `computer`). Ten en cuenta que la consulta nueva puede enviar ese término a ambas fuentes activas.
2. Si tampoco hay extracto con estado `ok`, interpreta ese símbolo solo desde el relato y la imaginación; indícalo como lectura creativa propia, no como tradición documentada.

### Caso B: Portal no disponible
- No repitas consultas en bucle. Usa las otras fuentes cuyo `status` sea `ok`.
- Si no hay ningún extracto, puedes continuar con una lectura basada en el relato, dejando claro que la inspiración es propia y no verificada en diccionarios.
- Indica de forma breve qué fuente no estuvo disponible. No le atribuyas una interpretación a una web que falló.
