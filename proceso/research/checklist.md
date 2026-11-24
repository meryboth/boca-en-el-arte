# Checklist de research-rigor — `report.md`, revisada el 2026-11-18

Hecho = ✔. Lo que no se cumple va marcado ✘ y figura en "Honest limits" del informe.

## Diseño
- ✔ Protocolo con fecha anterior a la primera corrida de evaluación (v2 aprobado 2026-11-16, commit `032ee07`). Los pilotos son anteriores y están declarados.
- ✔ Cada hipótesis tiene criterio de refutación (PROTOCOL §2).
- ✔ Baseline `edit` con las mismas entradas y semillas. ✘ parcial: el baseline no itera y el método sí (declarado).
- ✔ Grupo de control para la afirmación central (`code` y `hybrid` contra `edit`).
- ✘ Ablación `code-sinclave` no corrida: H3 sin evaluar (declarado, con motivo y fecha en el protocolo).
- ✔ Cambios al protocolo anotados con fecha y si fueron antes o después de ver resultados.

## Muestra
- ✔ Cada tabla dice su n.
- ✔ Ninguna comparación humana se declara ganada: las tres dicen "no winner". Las automáticas tienen n = 20 e intervalo.
- ✘ "Generaliza": 4 casos, uno por nivel, uno elegido para romper el método. Se reporta como estudio de casos.
- ✔ Parte de la maqueta: un caso, una corrida por método; se dice que no permite comparar servicios.

## Métricas
- ✔ Fórmula, región, unidad y dirección de cada métrica (PROTOCOL §5; resumidas en el informe).
- ✔ Lo que sobra (alteración) y lo que falta (tono) tienen métrica. ✘ La de pliegues falla en tela oscura (declarado).
- ✔ Las columnas dicen que son medianas; no hay gate.
- ✔ Los casos de evaluación no se usaron para desarrollar el script (calibración: `julio2`).

## Gate y umbrales
- No aplica gate automático: no hay. ✔ El umbral de H2 (2,0) se fijó antes de correr.
- ✘ Las métricas no se validaron contra juicio humano antes de usarse (declarado).

## Coherencia de los números
- ✔ Los 196 números del informe salen de `report-data.json` (render sin errores). Los que solo existían en una bitácora están en `report-extra.json` con su fuente.
- ✔ Las tarjetas se rastrean a una tabla.
- ✔ Revisado texto contra tablas: 9–11, 11–9, 11–5; reparto por pintura; 5 de 20 marcadas.
- ✔ Conteos: 76 corridas = 6 pilotos + 60 evaluación + 5 segunda tanda + 5 maqueta.
- ✘ `results.json` no se regeneró después de agregar las corridas `a` y `m` (quedó como al cierre de la evaluación, 66 corridas); el informe toma esas corridas de `runs.jsonl`.

## Costos y reproducibilidad
- ✔ Créditos del registro de facturación, tokens de los avisos de fin; incluyen pilotos, fallas y descartes.
  ✘ No incluye los tokens de la conversación principal. ✘ La segunda tanda se registró un día tarde.
- ✔ Hardware, modelos, semillas y commits declarados.
- ✔ `runs.jsonl`, `results.json` y salidas crudas en el repo. ✘ Lo posterior a `bf7f79b` está sin commitear.
- ✔ Toda corrida paga tuvo aprobación previa de Marilyn.

## Contenido
- ✔ Pinturas en dominio público; fotos CC BY-SA 4.0 atribuidas; marcos CC0. ✘ El estadio y los colores son de un club real: el sitio dice que no es oficial y no usa escudo, marcas ni nombres. Marilyn decidió el 2026-11-18 que así alcanza para publicar.
- ✔ Sin fechas ni cifras fuera de los datos. Las fechas del relato de la sala no existen y no se inventaron.
- ✔ "Honest limits" dice qué experimento cerraría los límites principales.

## Pendiente antes de publicar
1. Commit de todo y decidir si el repo es público.

Hecho el 2026-11-18: recorrido re-renderizado con la maqueta limpia (1621 cuadros, sin errores en `museo/render/render.log`), sitio reconstruido (541 cuadros, 34,6 MB) y verificado en navegador de escritorio; captura en `proceso/23_sitio-parada-maqueta.jpg`.
