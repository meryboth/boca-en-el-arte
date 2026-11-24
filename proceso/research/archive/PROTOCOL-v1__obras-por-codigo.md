# Protocolo — Museo Xeneize

> **BORRADOR. No se corre nada hasta que Marilyn lo apruebe.**
> Las decisiones abiertas están marcadas con **[DECIDIR]** y resumidas al final.
> Lo que cambie después de aprobado se anota en "Cambios al protocolo", con fecha y motivo.

Fecha de inicio: 2026-11-16 · Commit del protocolo: (pendiente, se completa al aprobar)

## 0. Qué es el proyecto

Un museo web estático: una sala 3D renderizada con Tesseract (Mirage) donde cuelgan
obras que reinterpretan pinturas del Renacimiento (dominio público) con los colores de Boca.
Las obras las genera Fable 5.2 **escribiendo código** (SVG, canvas, shaders). Fable no es
un modelo de difusión: no produce píxeles directamente, produce el programa que los dibuja.
Eso es lo que se pone a prueba.

El proyecto tiene dos partes con distinto nivel de evidencia:

- **Parte A (experimento comparativo):** las obras generativas. Tiene baseline, N y métricas.
- **Parte B (estudio de caso):** la sala en Tesseract. Es una sola sala, así que se documenta
  como bitácora de experiencia (tiempos, iteraciones, fallas), sin afirmaciones de mejora.

## 1. Pregunta

¿Mirar el render y corregir en rondas mejora las obras que Fable 5.2 genera por código,
respecto de escribirlas de una sola pasada sin ver el resultado?

Pregunta descriptiva secundaria (sin comparación): ¿qué proporción de las obras se reconoce
como la pintura de referencia y como homenaje a Boca?

## 2. Hipótesis y refutación

| Hipótesis | La confirma | La refuta |
|---|---|---|
| H1: iterar con feedback visual produce obras preferidas sobre la pasada única | En la comparación de a pares a ciegas, la tasa de victorias del método supera 50 % con intervalo bootstrap del 95 % que no incluye 50 % | El intervalo incluye 50 %, o la pasada única gana |
| H2: las obras del método se reconocen como la pintura de referencia | Tasa de reconocimiento a ciegas ≥ **[DECIDIR: 70 %]** en el set de evaluación | Tasa por debajo del umbral |

## 3. Condiciones

| Rol | Condición | Qué cambia respecto del baseline |
|---|---|---|
| Baseline | `oneshot`: un agente nuevo recibe el brief y escribe la obra de una pasada, sin renderizarla | — |
| Método | `iter3`: mismo brief; el agente renderiza, mira la captura y corrige, hasta 3 rondas | Feedback visual |
| Ablación | `iter3-sinref`: igual al método, pero el brief no incluye la descripción de la composición original (solo el título) | Se apaga la descripción de referencia; se espera perder reconocimiento |

Todas las condiciones usan el mismo modelo (`claude-fable-5-2`), el mismo brief por caso,
el mismo formato de salida (un archivo HTML autocontenido, lienzo de proporción fija) y la
misma herramienta de captura.

**Sobre las "semillas":** un LLM no expone una semilla. Acá una semilla es un **intento
independiente**: un agente nuevo, sin contexto de los otros intentos, con el mismo brief.
El emparejamiento por semilla es entonces nominal (intento 1 con intento 1); se declara
como límite.

## 4. Casos

Confirmadas por Marilyn el 2026-11-16:

| Caso | Por qué está | Qué nivel de la variable representa |
|---|---|---|
| La creación de Adán (Miguel Ángel, c. 1511) | Típico: dos figuras, gesto icónico | Composición simple y muy reconocible |
| La Gioconda (Leonardo, c. 1503–19) | Distinto: retrato, sfumato, un solo personaje | El reconocimiento depende de sutileza, no de composición |
| La escuela de Atenas (Rafael, 1509–11) | Elegido para romper el método: decenas de figuras y arquitectura | Complejidad alta |

Un caso por nivel de complejidad: lo que se diga sobre complejidad es **estudio de casos**.

## 5. Métricas

| Métrica | Definición exacta | Unidad | Mejor | Modo de falla que ve | Modo que no ve (y qué lo cubre) |
|---|---|---|---|---|---|
| Preferencia de a pares | Evaluador ve dos obras del mismo caso y semilla (método vs. baseline), orden al azar, sin etiqueta; elige la mejor. Victorias del método / pares | 0–1 | ↑ | Calidad global | No dice por qué → las dos siguientes |
| Reconocimiento de la pintura | Evaluador ve la obra sin título y responde qué pintura es. Aciertos / obras | 0–1 | ↑ | Composición irreconocible | Obra reconocible pero sin Boca → siguiente |
| Reconocimiento de Boca | Evaluador responde "¿a qué club alude?" sin pistas. Aciertos / obras | 0–1 | ↑ | Homenaje ausente o ambiguo | Boca presente sobre una pintura irreconocible → anterior |
| Cobertura azul y oro | Píxeles a CIEDE2000 ≤ **[DECIDIR: 10]** del azul o del oro de referencia / píxeles del lienzo, en la captura a 1600 px de lado mayor | 0–1 | informativa | Paleta ausente | Color correcto en el lugar equivocado → reconocimiento de Boca. **No es un gate**: no está validada contra juicio humano |
| Costo | Tokens de entrada y salida del agente, del log de la corrida | tokens | ↓ | — | — |
| Tiempo | Duración de pared del agente, del log | s | ↓ | — | Ruido de red: se reporta rango |
| Falla técnica | La obra no renderiza o tira error de consola. Fallas / corridas | 0–1 | ↓ | Código roto | — |

## 6. Muestra

- Semillas (intentos independientes) por condición y caso: 5 (1, 2, 3, 4, 5)
- Vistas por caso: 1 (captura fija del lienzo)
- Total de corridas previstas: 3 condiciones × 3 casos × 5 semillas = **45**
- Pares para la evaluación humana: 15 (método vs. baseline) + 15 (método vs. ablación)

## 7. Umbrales y evaluación humana

- No hay gate automático: la cobertura de color es informativa.
- Evaluación humana (decidido el 2026-11-16): Marilyn más 2 o 3 personas, a ciegas. Fable
  no puede ser juez de su propia obra. Se reporta el acuerdo entre evaluadores (kappa).
  El reconocimiento lo responden solo las personas que **no** conocen la lista de obras;
  Marilyn la conoce, así que participa en la preferencia de a pares y no en esa métrica.
- Se arma una página de evaluación a ciegas (orden aleatorio, sin etiquetas, respuestas a JSON).
- El umbral de H2 se fija antes de evaluar y no se toca.

## 8. Presupuesto

| Paso | Dónde corre | Costo estimado | Tope |
|---|---|---|---|
| 45 generaciones de obra | Subagentes Fable 5.2 en Claude Code | Sin estimación todavía: se mide en una corrida piloto de 1 obra y se extrapola | **[DECIDIR]** |
| Capturas y métrica de color | Local | $0 | — |
| Sala 3D | Tesseract local (según Mirage, gratis; sin verificar) | $0 + tokens del agente | **[DECIDIR]** |
| Texturas con modelo de imagen | No previsto. Si la sala las necesita, se pide aprobación aparte | — | — |

**Piloto del 2026-11-16** (corrida `p0001`, `oneshot`, caso `adan`, n = 1): 127.969 tokens
totales y 736 s, según el aviso de fin del subagente (sin desglose de entrada y salida).
Extrapolación lineal para las 15 corridas `oneshot`: ≈ 1,9 M de tokens. Las condiciones
`iter3` e `iter3-sinref` no están medidas; van a costar más por las rondas de captura y
corrección. Con n = 1 esto es un orden de magnitud, no una estimación.

Toda corrida que consuma cuota se aprueba antes de lanzarse. El costo real sale de los logs.

## 9. Parte B — Tesseract (estudio de caso)

Una sola sala, sin baseline: no se afirma que Tesseract sea mejor ni peor que nada.
Se registra en `research/tesseract-log.md` y en `runs.jsonl` (condición `tesseract`):

- Instalación: pasos, errores, tiempo, versión.
- Por cada render: qué se pidió, tiempo de render, hardware, resultado, si hubo que rehacer.
- Qué formatos exporta de verdad (video, stills, transparencia, glTF) y cuál se usa en la web.
- Cantidad de iteraciones hasta una sala aceptable y qué falló en cada una.

Paso previo: prueba mínima (una escena con un cubo y una luz) para confirmar que funciona
en esta máquina antes de diseñar el sitio alrededor.

## 10. Marca y derechos

- Las pinturas de referencia son de dominio público. Las obras son composiciones nuevas
  dibujadas por código, no copias de fotografías de museos.
- El estándar de research dice que el material de prueba no imita identidades reales.
  Boca Juniors es una marca real. Decidido el 2026-11-16: homenaje de hincha con azul y oro
  y la franja horizontal, **sin** escudo oficial, sin sponsors y sin nombres de jugadores;
  el sitio aclara que no es oficial ni está afiliado al club.

## 11. Qué se publica

- Datos: `research/runs.jsonl`, `research/results.json`, las 45 obras crudas (HTML + captura).
- Informe: `research/report.md` generado con `render_report.py`.
- Bitácora de Tesseract: `research/tesseract-log.md`.
- El museo muestra una selección curada; el informe muestra **todas**, incluidas las fallidas.
- Nota del portfolio: **[DECIDIR]**.

## Decisiones abiertas

Cerradas el 2026-11-16: marca (§10), obras (§4), evaluadores (§7), instalar Tesseract (sí).

Siguen abiertas:

1. Tope de cuota para las 45 generaciones (después del piloto).
2. Umbrales marcados en §2 y §5.
3. Repo: ¿público en GitHub? ¿nombre `museo-xeneize`?
4. Nota del portfolio (§11).

## Cambios al protocolo

| Fecha | Qué cambió | Por qué | ¿Se decidió antes o después de ver resultados? |
|---|---|---|---|
