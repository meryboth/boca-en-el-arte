# Protocolo — Museo Xeneize (v2)

> **Aprobado por Marilyn el 2026-11-16** (casos, prompts, presupuesto y lanzamiento). Congelado en el
> commit que lo incluye junto con scripts, briefs y zonas. Lo que cambie desde acá va a "Cambios al protocolo".
> La v1 (obras dibujadas enteras por código) está en `archive/PROTOCOL-v1__obras-por-codigo.md`.
> El motivo del cambio está en "Cambios al protocolo".

Fecha de inicio: 2026-11-16 · Commit del protocolo: (pendiente, se completa al aprobar)

## 0. Qué es el proyecto

Un museo web estático: una sala 3D renderizada con Tesseract (Mirage) donde cuelgan pinturas
clásicas en dominio público **intervenidas**: la ropa de los personajes pasa a azul y oro,
como homenaje de hincha a Boca. El resto del cuadro tiene que seguir siendo el original.

Dos partes con distinto nivel de evidencia:

- **Parte A (experimento comparativo):** cómo se intervienen las pinturas.
- **Parte B (estudio de caso):** la sala en Tesseract. Una sola sala, sin baseline: se
  documenta como bitácora (`tesseract-log.md`), sin afirmaciones de mejora.

## 1. Pregunta

Para vestir de azul y oro a los personajes de una pintura clásica sin tocar el resto,
¿el recoloreo por código escrito por Fable 5.2 da un resultado preferido al de un modelo de
edición de imagen, y cuánto altera cada uno las zonas que no son ropa?

## 2. Hipótesis y refutación

| Hipótesis | La confirma | La refuta |
|---|---|---|
| H1: los evaluadores prefieren el recoloreo por código al modelo de edición | Tasa de victorias del código en pares a ciegas > 50 %, con intervalo bootstrap del 95 % que no incluye 50 % | El intervalo incluye 50 % (empate) o gana el modelo de edición |
| H2: el modelo de edición altera las zonas protegidas (caras, manos, fondo) | Mediana de CIEDE2000 en zonas protegidas por encima de 2,0 en el set de evaluación | Mediana por debajo del umbral |
| H4: el combinado es preferido a la edición sola y al código solo | Gana en pares contra `edit` y contra `code`, los dos intervalos sin el 50 % | Empata o pierde contra alguno de los dos |
| H3: la clave de color aporta al recoloreo por código | El código con clave gana en pares al código sin clave, intervalo sin el 50 % | Empate o gana la ablación |

H2 es casi cierta por construcción para el código (los píxeles fuera de la máscara se copian
del original), así que para el código esa métrica es una verificación, no un hallazgo.

## 3. Condiciones

| Rol | Condición | Qué cambia respecto del baseline |
|---|---|---|
| Baseline | `edit`: un modelo de edición de imagen recibe la pintura y un prompt fijo por caso | — |
| Método | `code`: un agente Fable 5.2 nuevo escribe la config de `scripts/recolor.py` (polígonos, clave de color, niveles) mirando el resultado, hasta 4 rondas | La intervención la hace código determinista, no un modelo generativo |
| Ablación | `code-sinclave`: igual al método, con la clave de color apagada (solo polígonos) | Se espera perder precisión en los bordes |
| Método combinado | `hybrid`: la ropa de la salida `edit` pegada sobre el original con la máscara del intento `code` de la misma semilla (pipeline de ComfyUI `museo-xeneize__nb2-mascara-original`, o `scripts/composite.py`) | Ropa pintada por el modelo; cara, manos y fondo del original |

Detalles que se fijan antes de correr:

- **Modelo de edición:** Nano Banana, corrido desde un nodo de Comfy Cloud con la cuenta de
  Marilyn, sin API key propia (decidido el 2026-11-16). Nodo `GeminiImage2Node`, salida 4K.
  Tier: Nano Banana 2 (Gemini 3.1 Flash Image), elegido por Marilyn el 2026-11-16.
  Piloto p0003: 38,53 créditos por una imagen (registro de facturación), salida 3520×4780.
  Extrapolación para las 20: ≈ 770 créditos, sin reintentos.
- **Prompt de `edit`:** uno por caso, escrito antes de la primera corrida siguiendo la guía
  del modelo, y congelado. No se itera: es la "alternativa ingenua". Esto favorece al
  código, que sí itera; se declara en límites.
- **Conflicto de interés:** Fable escribe el código y también el prompt del rival. Marilyn
  revisa y aprueba los prompts de `edit` antes de congelarlos.
- **`scripts/recolor.py` se congela** (commit) antes de las corridas. Lo que varía entre
  intentos es solo la config que escribe cada agente.
- **Semillas:** en `edit`, la semilla del modelo (1 a 5). En `code`, una semilla es un
  intento independiente: agente nuevo, sin contexto de los otros. El emparejamiento por
  semilla entre condiciones es nominal.

## 4. Casos

Criterio: dominio público, mucha tela visible, y que no repitan las obras de las
referencias que trajo Marilyn. Lista confirmada por Marilyn el 2026-11-16.

**Resolución de trabajo:** las tres condiciones parten de la misma copia en
`research/sources/work/`, con el lado mayor limitado a 4500 px (Lanczos, JPEG 95). Motivo: la
máquina tiene 15,4 GB de RAM y el recoloreo de 48 MP no entra con varios agentes a la vez.

**Solo telas** (pedido de Marilyn, 2026-11-16): se interviene ropa y paños. No se pintan de
azul y oro muebles ni objetos. Los prompts de evaluación ya cumplían; el del piloto `julio2`
incluía el sillón y queda como estaba, fuera de la evaluación.

| Caso | Por qué está | Qué nivel de la variable representa |
|---|---|---|
| `julio2` — Rafael, Retrato de Julio II (1511) | **Desarrollo.** Con él se escribió y ajustó el script | Fuera de la evaluación |
| `prato` — Rafael, Madonna del Prato (1505–06) | Típico: pocas figuras, telas grandes (vestido rojo, manto ya azul) | Simple |
| `arnolfini` — Van Eyck, Matrimonio Arnolfini (1434) | Distinto: tela verde y oscura, pieles, interior | Otro color de origen y otro material |
| `baco` — Tiziano, Baco y Ariadna (1520–23) | Paños rosados pegados a la piel, varias figuras | Ropa difícil de separar de la piel |
| `atenas` — Rafael, La escuela de Atenas (1509–11) | Elegido para romper el método: decenas de figuras y telas de muchos colores | Complejidad alta |

`julio2` es el set de **calibración**; los otros cuatro son el set de **evaluación** y no se
tocan hasta congelar el script. Un caso por nivel: lo que se diga sobre complejidad es
estudio de casos.

## 5. Métricas

Antes de correr, por cada caso se dibujan y congelan dos juegos de parches sobre el original
(los dibuja Fable, los revisa Marilyn): **zonas protegidas** (caras, manos, fondo; no deben
cambiar) y **zonas de ropa** (deben quedar azules u oro). Son parches chicos en el interior
de cada zona, no máscaras completas, para no depender de los bordes.

Las salidas de `edit` se reescalan al tamaño del original antes de medir. Si el modelo
cambió el encuadre, se registra como falla y no se mide.

| Métrica | Definición exacta | Unidad | Mejor | Modo de falla que ve | Modo que no ve (y qué lo cubre) |
|---|---|---|---|---|---|
| Preferencia de a pares | Evaluador ve dos intervenciones del mismo caso y semilla, orden al azar, sin etiqueta; elige "cuál colgarías". Victorias / pares | 0–1 | ↑ | Calidad global | No dice por qué → el resto |
| Alteración en zonas protegidas | Mediana de CIEDE2000 píxel a píxel contra el original, dentro de los parches protegidos | ΔE00 | ↓ | Lo que sobra: caras o fondo retocados | Ropa sin cambiar → la siguiente |
| Error de tono en ropa | Mediana de la diferencia de ángulo de tono (CIELAB) contra el azul `#103F79` o el oro `#F3B229`, el más cercano, en los parches de ropa. Solo tono, para no penalizar luces y sombras | grados | ↓ | Lo que falta: ropa que quedó del color original o de otro | Color correcto pero plano → la siguiente |
| Conservación de pliegues | Correlación de Pearson de la luminosidad L* entre salida y original, en los parches de ropa | −1 a 1 | ↑ | Tela aplanada o repintada | Pliegues conservados sobre un color malo → la anterior |
| "Se nota intervenida" | Evaluador ve una sola imagen y marca dónde ve algo raro, o "nada". Imágenes con alguna marca / total | 0–1 | ↓ | Halos, bordes duros, artefactos | — |
| Resolución de salida | Píxeles de la salida / píxeles del original | razón | informativa | Pérdida de detalle | — |
| Falla | Salida inutilizable: rechazo del modelo, encuadre cambiado, error del script. Fallas / corridas | 0–1 | ↓ | — | — |
| Costo | Créditos de Comfy Cloud (del registro de facturación) y tokens del agente (del aviso de fin) | créditos, tokens | ↓ | — | — |
| Tiempo | Duración de pared por corrida, del log | s | ↓ | — | Ruido de red: se reporta rango |

Las tres métricas automáticas no son gates: se reportan junto al juicio humano y, si lo
contradicen, se dice.

## 6. Muestra

- Semillas por condición y caso: 5 (1 a 5).
- Casos de evaluación: 4.
- Total de corridas: 4 condiciones × 4 casos × 5 semillas = **80**: 20 pagas en `edit`,
  40 de agentes Fable y 20 `hybrid`, que salen de la misma corrida paga que `edit` (el
  pipeline guarda la edición cruda y el combinado) y no suman créditos de modelo.
- Pares para evaluación humana: 20 (`code` vs `edit`) + 20 (`code` vs `code-sinclave`)
  + 20 (`hybrid` vs `edit`) + 20 (`hybrid` vs `code`) = 80 pares por evaluador.

## 7. Umbrales y evaluación humana

- No hay gate automático.
- Evaluadores (decidido el 2026-11-16): Marilyn más 2 o 3 personas, a ciegas. Se reporta el
  acuerdo entre evaluadores (kappa). Fable no evalúa.
- Página de evaluación a ciegas: orden aleatorio, sin etiquetas, respuestas a JSON.
- El umbral de H2 se fija antes de correr y no se toca.

## 8. Presupuesto

| Paso | Dónde corre | Costo estimado | Tope |
|---|---|---|---|
| 20 ediciones `edit` | Comfy Cloud, nodo `GeminiImage2Node` a 4K | Según `estimate_credits` (2026-11-16, puede estar desactualizado): ~61 créditos por imagen con Nano Banana Pro (≈ 1.220 por las 20) o ~39 con Nano Banana 2 (≈ 780). No incluye GPU, cola ni reintentos. Sin conversión a dólares: no la tengo. Se confirma con 1 edición piloto leída del registro de facturación | 20 ediciones, sin reintentos: ≈ 770 créditos (aprobado 2026-11-16) |
| 40 corridas de agentes (`code` y ablación) | Subagentes Fable 5.2 | Piloto p0006 (`julio2`, n = 1): 106.680 tokens y 308,5 s, con 3 corridas del script. Extrapolación lineal: ≈ 4,3 M de tokens. `julio2` es el caso más fácil; los de evaluación pueden costar más | 40 agentes, uno por corrida, sin relanzar: ≈ 4,3 M de tokens estimados (aprobado 2026-11-16) |
| Script de recoloreo, métricas, capturas | Local | $0. El script tarda 15,9 s en una imagen de 13 MP (una medición) | — |
| Sala 3D | Tesseract local | $0 + tokens | **[DECIDIR]** |

Toda corrida paga se aprueba antes de lanzarse. El costo real sale de los registros.

## 9. Parte B — Tesseract (estudio de caso)

Sin cambios respecto de la v1. Bitácora en `research/tesseract-log.md`. El CLI 0.7.0 está
instalado y la prueba mínima de render pasó (2026-11-16). Las obras se cuelgan en la sala
como texturas; la sala se entrega a la web como video o stills pre-renderizados, porque
Tesseract no exporta escenas para tiempo real.

## 10. Marca, derechos y texto

- Las pinturas son de dominio público. De cada fuente se guarda archivo, URL, licencia
  declarada y SHA-256 en `research/sources/`.
- Las obras de los artistas que Marilyn trajo como referencia no se copian ni se usan como
  entrada: sirven solo para fijar el nivel de calidad buscado.
- Boca (decidido el 2026-11-16): azul y oro y franja horizontal, sin escudo oficial, sin
  sponsors, sin nombres de jugadores. El sitio aclara que no es oficial.
- **[DECIDIR]** ¿Se permiten pintadas con frases de hincha, como en las referencias? El
  recoloreo por código no puede pintarlas; quedarían como un agregado aparte.

## 11. Qué se publica

- Datos: `research/runs.jsonl`, `research/results.json`, todas las salidas crudas (incluidas
  las fallidas y los pilotos), las configs de cada intento y los parches de medición.
- Informe: `research/report.md` generado con `render_report.py`.
- Los pilotos p0001 (obra entera por código) y p0002 (recoloreo de `julio2`) van al informe
  como antecedentes, fuera de las estadísticas.
- Nota del portfolio: **[DECIDIR]**.

## Límites conocidos desde el diseño

- `code` itera hasta 4 rondas y `edit` usa un prompt fijo: la comparación favorece al código.
- El script se desarrolló sobre un solo caso (`julio2`), el más fácil.
- Las zonas de medición las dibuja la misma parte que escribe el método.
- Un solo modelo de edición: lo que se concluya vale para ese modelo, no para "la edición
  con IA" en general.
- `hybrid` depende de la máscara de `code`: si la máscara falla, fallan los dos. Y lo que el
  modelo pinte fuera de la máscara (una bandera, una pintada) se pierde al pegar.
- El pipeline de ComfyUI no registra las dos imágenes; `composite.py` sí (ECC afín). En
  `julio2` el desfase medido fue de 0,3 px.
- Las métricas de tono y de pliegues favorecen a `code` por construcción: fija el tono exacto y copia la luminosidad del original. Un modelo que repinta pliegues verosímiles pierde en "pliegues" aunque se vea mejor. La preferencia humana es la métrica principal.
- El recoloreo por código no agrega objetos (banderas, pintadas); esa parte de las
  referencias queda fuera de la comparación.

## Decisiones abiertas

1. Tope de consumo para la sala en Tesseract (Parte B).
2. Pintadas con frases de hincha (§10): con la regla de "solo telas", por ahora no se agregan.
3. Repo público y nombre; nota del portfolio.

## Cambios al protocolo

| Fecha | Qué cambió | Por qué | ¿Se decidió antes o después de ver resultados? |
|---|---|---|---|
| 2026-11-16 | Se reemplaza la v1 (obras dibujadas enteras por código; comparaba una pasada contra rondas de corrección) por la v2 (intervenir la pintura original; compara código contra modelo de edición). Cambian pregunta, condiciones, casos y métricas | Marilyn vio el piloto p0001 y pidió un nivel de realismo que el dibujo por código no alcanza; sus referencias son pinturas originales intervenidas | **Después** de ver el piloto p0001. Ninguna corrida de evaluación de la v1 se había lanzado |
| 2026-11-16 | Se agrega la condición `hybrid` y la hipótesis H4 | En los pilotos p0002–p0004 sobre `julio2` la edición pintó mejor la ropa pero alteró cara, manos y fondo, y el código hizo lo contrario; Marilyn pidió combinar con máscara en ComfyUI | Después de ver los pilotos, todos sobre el caso de calibración. Ninguna corrida de evaluación lanzada |
| 2026-11-16 | `julio2` pasa a set de calibración | Se usó para desarrollar `recolor.py` (piloto p0002, 4 versiones) | Después de usarlo; por eso se lo excluye |
| 2026-11-16 | `recolor.py` acepta una clave de color por región y claves por croma (antes una sola clave global, pensada para rojos) | Los casos de evaluación tienen prendas de varios colores de origen (verde, púrpura, rosa) y una clave global no puede cubrirlas | Antes de cualquier corrida de evaluación. Verificado que la salida del piloto `julio2` v4 no cambia (diferencia máxima 0) |
| 2026-11-16 | Resolución de trabajo limitada a 4500 px de lado mayor para las tres condiciones | Memoria de la máquina | Antes de cualquier corrida de evaluación |
| 2026-11-16 | Regla "solo telas": no se intervienen muebles ni objetos | Pedido de Marilyn al ver el sillón dorado del piloto | Después de ver los pilotos de `julio2`; los prompts de evaluación no cambiaron |
| 2026-11-17 | No se corre la ablación `code-sinclave` (20 agentes). H3 queda sin evaluar | Presupuesto: Marilyn pidió no gastar todos los tokens de la sesión tras tocar el límite de uso de 5 horas; los 20 agentes de `code` costaron 2,90 M de tokens contra 2,15 M estimados para esa mitad | Antes de correr ninguna corrida de esa condición; después de ver previews de `code` |
| 2026-11-17 | `hybrid` se compone en local con `scripts/composite.py` (con registro ECC) en vez de dentro del pipeline de Comfy Cloud. En la nube corre solo la edición | Evita subir 20 máscaras y agrega la alineación que el pipeline no tiene. El protocolo ya permitía cualquiera de las dos vías | Antes de generar ningún `hybrid` de evaluación |
| 2026-11-17 | Total de corridas: 60 (20 `code`, 20 `edit`, 20 `hybrid`) en vez de 80. Pares por evaluador: 60 en vez de 80 | Consecuencia de quitar la ablación | — |
| 2026-11-17 | Incidentes de `code`: límite de uso (429) cortó 3 agentes (baco s4, baco s5, atenas s1), retomados al día siguiente con el mismo agente; `recolor.py` se cae sin salida con `fill.erode` chico (baco s2: 2 corridas perdidas; atenas s4: 3 lanzamientos extra no contados por el agente) | Se registran, no se corrigen: el script está congelado | Durante la evaluación |
| 2026-11-17 | Evaluación humana: una sola evaluadora, Marilyn, en vez de Marilyn más 2 o 3 personas | Decisión de Marilyn | Después de ver las métricas automáticas y láminas comparativas de los tres métodos. Consecuencias: no hay acuerdo entre evaluadores (kappa); la evaluadora conoce los métodos y ya vio resultados sin anonimizar, así que la evaluación no es ciega en sentido estricto aunque la página oculte qué método hizo cada imagen; los intervalos reflejan la variación entre intentos, no entre personas. Se reporta como juicio de una persona |
