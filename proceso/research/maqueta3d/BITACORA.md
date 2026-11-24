# Bitácora — maqueta 3D de la Bombonera

Estudio de caso: cómo se llegó a la maqueta que está en la sala. Un solo objeto y sin baseline formal,
así que acá se describe lo que pasó; no se afirma que un camino sea mejor que otro en general.

## Etapa 1 — Maqueta por código (descartada por Marilyn)

Tres versiones armadas con cubos escalados desde `scripts/maqueta_bombonera.py`:

| Versión | Con qué referencia | Qué tenía | Por qué no alcanzó |
|---|---|---|---|
| v1 | De memoria | Cancha, tribuna en U escalonada, pared de palcos | "Muy básica y no representa realmente el estadio" (Marilyn) |
| v2 | Fotos aéreas de Commons | Fachada con franja amarilla en zigzag, tres bandejas, palcos vidriados | Seguía siendo un rectángulo de esquinas redondeadas |
| v3 | Fotos aéreas y un render de referencia que pasó Marilyn | Tribuna curva (superelipse), letras en la bandeja alta, edificio de palcos de hormigón, reflectores, marcador | "No veo que la reconstrucción sea precisa" (Marilyn) |

Errores míos en el camino: en la v3 las letras salieron espejadas en la primera prueba, y el marcador
de la v2 quedó flotando. Imágenes de prueba en `museo/render/stills/parada_11_maqueta__v2.jpg` y `__v3.jpg`.

Límite de este camino: piezas rectas, proporciones a ojo, sin planos. Reconoce el estadio pero no lo reproduce.

## Etapa 2 — Buscar un modelo hecho

Tres modelos encontrados, ninguno gratis y de uso libre a la vez: Sketchfab (65 USD, licencia editorial),
Free3D (licencia contradictoria entre páginas; el sitio bloqueó la lectura automática) y MakerWorld
(gratis, prohíbe redistribuir los archivos). No se usó ninguno. No se buscó en Printables ni Thingiverse.

## Etapa 3 — Reconstrucción con modelos de imagen a 3D en ComfyUI

### Fuentes

Doce fotos aéreas de 2025 en Wikimedia Commons, `File:Vista aérea del Estadio Alberto J. Armando "La Bombonera" 01–12.jpg`,
autor ProtoplasmaKid, licencia **CC BY-SA 4.0** (según Commons). Originales de unos 8064×4536; se bajaron
las versiones de 1920 px que genera Commons, en `fuentes/`. Hoja de contacto: `hoja_fotos_aereas.jpg`.
La licencia pide atribución y compartir igual: el modelo 3D que salga de ellas es una obra derivada.

### Recorte del estadio

Los modelos de imagen a 3D esperan un objeto solo sobre fondo liso, y en las fotos el estadio está metido en el barrio.

1. **Recorte automático por color** (`scripts/recorte_estadio.py`): azul, amarillo y verde saturados, cerrados
   con un núcleo grande. **Falló**: en 5 de 7 fotos se comió tribunas en sombra o el edificio de palcos gris,
   o arrastró techos y piletas vecinas (`hoja_recortes.jpg`). Quedó documentado y no se usa.
2. **Contorno a mano** (`contornos.json` + `scripts/recorte_contorno.py`): tracé el contorno de 4 fotos
   (01, 05, 09, 11) sobre copias de 960×540 con grilla. Resultado limpio en las cuatro (`hoja_recortes_mano.jpg`).

### Modelos disponibles en Comfy Cloud y su costo estimado (`estimate_credits`, 2026-11-18)

| Plantilla | Entrada | Créditos estimados |
|---|---|---|
| Pixal3D / TRELLIS.2 | 1 imagen | 0 de API (corre en GPU de la nube; ese tiempo no está estimado) |
| Tripo H3.1 multivista | frente, costado y dorso | ~63 |
| Rodin Gen2.5 | 1 o varias imágenes | 158 |
| Hunyuan3D (API) | 1 imagen | 190 |
| Meshy 7.1 | 1 imagen | 362 |

### Plan (pedido de Marilyn): normalizar las vistas antes de reconstruir

Las fotos reales están tomadas desde ángulos y alturas distintos, no desde las vistas canónicas que
esperan los modelos multivista. El pipeline propuesto:

1. Las 4 fotos recortadas entran como referencia a un modelo generativo de imagen (Nano Banana 2).
2. Ese modelo devuelve el estadio en vistas normalizadas: frente, costado y dorso, misma escala, fondo blanco.
3. Esas vistas alimentan al modelo de reconstrucción (Tripo H3.1 multivista), que devuelve un GLB con textura.
4. El GLB se importa en Blender y reemplaza a la maqueta por código sobre la mesa.

Riesgo conocido antes de correr: el paso 2 **inventa** lo que las fotos no muestran. Las vistas van a ser
coherentes entre sí, pero no son fotos del estadio; la "precisión" del resultado depende de cuánto
respete el generador a las referencias. Por eso se guardan las vistas generadas junto a las fotos reales.

### Corridas (2026-11-18, aprobadas por Marilyn con una estimación de ~102 créditos)

| Corrida | Qué | Resultado | Créditos (facturación de Comfy) |
|---|---|---|---|
| m0001 | Nano Banana 2, 4 recortes de referencia, semilla 1, 4K 16:9 | Hoja de 5504×3072. **Cumplió a medias**: el panel del frente salió bien; el del medio salió girado e inservible; el tercero no fue el dorso pedido sino una planta desde arriba | 38,9 |
| m0002 | Tripo multivista solo con el frente | **Rechazada** por el nodo: "At least one of left, back, or right image must be provided". Error mío: no leí ese requisito | sin evento de cobro |
| m0003 | Tripo v3.1 multivista, frente + dorso, semillas 42 | GLB de 12 MB, 167.744 vértices, 273.656 caras, texturas 2048 px | 63,3 |

Total facturado: **102,2 créditos**.

**El dorso de m0003 no es una vista del estadio.** Como la normalización no devolvió dorso, usé el frente
espejado (`vistas/vista_dorso__espejo-del-frente.jpg`). Consecuencia: el modelo no tiene información real
del lado opuesto; Tripo lo completó.

### Qué salió (`hoja_modelo_tripo.jpg`, `modelo/vista__*.jpg`; juicio mío, una sola corrida)

- Se reconoce el estadio: tribuna curva en tres bandejas azul, amarilla y azul, fachada con la franja
  amarilla de tornapuntas, lado recto con el edificio de palcos, reflectores, cancha.
- No es un relevamiento. Las líneas de la cancha están mal (una grilla de más), los carteles tienen
  letras inventadas, la superficie está "derretida" de cerca y hay una mancha clara en la bandeja alta.
- **Marcas.** La textura traía en las cuatro torres de esquina un escudo y un logo de indumentaria, que
  el prompt pedía no poner y que van contra la decisión de marca del proyecto. Los tapé en la textura
  (`scripts/blender_glb_caras_esquina.py` + `scripts/tapar_logos.py`, 11.746 px pintados de azul).
  Queda el contorno apenas visible y, en dos esquinas, el tapado se comió un borde de la franja amarilla.
  Modelo usado en la sala: `modelo/bombonera__tripo__frente-nb2__s42__sin-logos.glb`.
- Marilyn, al verlo sobre la mesa (`museo/render/stills/parada_11_maqueta__tripo.jpg`): "creo que hay que
  usar un modelo mejor de reconstrucción 3D".

Pipeline guardado en Comfy Cloud: `museo-xeneize__bombonera-vistas-a-3d`, id `ff5dec71-5f8e-4e9f-93bf-7896f11f55ec`.
Se corrió en dos etapas con el recorte del panel hecho en local; el grafo único guardado (con nodos de
recorte y espejado) **no se corrió de punta a punta**.

### Segunda reconstrucción: Rodin Gen-2.5 con las fotos reales (2026-11-18, aprobada por Marilyn, 158 créditos estimados)

Marilyn pidió "un modelo mejor de reconstrucción 3D". Esta vez sin normalizar: los 4 recortes a mano
(fotos 01, 05, 09, 11) entran directo a Rodin Gen-2.5, modo Regular, nivel High, 500K triángulos, PBR, semilla 42.

| Corrida | Resultado | Créditos |
|---|---|---|
| m0004 | **Falló** antes de llamar a Rodin: el nodo exige también los parámetros opcionales. Error mío al armar el grafo | sin evento de cobro |
| m0005 | GLB de 37 MB, 600.556 vértices, 500.000 caras, texturas 2048 px | 158,25 |

Comparación (`hoja_comparacion__tripo-arriba__rodin-abajo.jpg`, `hoja_modelo_rodin.jpg`; juicio mío, una corrida
de cada uno, entradas distintas, así que **no separa el efecto del modelo del efecto de la entrada**):

| | Tripo (frente normalizado + espejo) | Rodin (4 fotos reales) |
|---|---|---|
| Planta | Simétrica, casi cuadrada: inventada | Asimétrica, en "D", con el lado recto de palcos: más parecida a las fotos |
| Cancha | Líneas de más, en grilla | Líneas correctas |
| Lado de palcos | Inventado, prolijo | Sale de las fotos, pero roto y con restos de edificios vecinos |
| Bandejas y fachada | Nítidas, colores saturados | Blandas, sin escalones; amarillo lavado |
| Bordes | Limpios | Dentados, con pedazos sueltos en un extremo |
| Marcas | Escudo y logo (tapados) | No se ven a esta distancia; no revisado de cerca |

Ninguno de los dos es preciso como relevamiento. Rodin es más fiel en forma general; Tripo se ve más
terminado. Cuál va a la mesa queda a decisión de Marilyn; mientras tanto la sala usa el de Tripo.

Total facturado en la etapa 3: **260,45 créditos** (38,9 + 63,3 + 158,25).

### No hecho

Sin comparación contra Tripo alimentado con las fotos reales sin normalizar, así que no se puede decir si
la normalización ayudó. Una sola semilla por paso. No se probaron Hunyuan3D, Meshy ni TRELLIS.2. No se corrió Rodin con el frente normalizado ni Tripo con las fotos reales.
No se probó fotogrametría con las 12 fotos reales.

## Etapa 4 — Modelado limpio en Blender desde una ficha del edificio (2026-11-18)

Pedido de Marilyn: "usemos Blender, pero démosle un contexto bien específico sobre el edificio, incluso
utilizando estos modelos como referencia, el de Rodin por ejemplo, y que Blender haga un modelado limpio".
No hay un MCP de Blender conectado; se maneja Blender por script, igual que el resto de la sala.

1. **Medir el modelo de Rodin** (`scripts/blender_medir_estadio.py` → `medidas__rodin.json`): cada vértice toma el
   color de la textura; los verdes dan el centro, los ejes y la escala (largo de cancha = 105 m). Salen el
   contorno cada 3°, el inicio de las tribunas, la altura por dirección y ocho cortes. Control: el ancho de
   cancha da 72,1 m en vez de 68, o sea que Rodin deforma alrededor de 6 %.
2. **Medir una foto real** (`medidas__foto08.md`): plano del suelo de la foto 08 rectificado con las esquinas
   de la cancha. Da la distancia de la cancha al muro exterior (unos 50 m). Las alturas no se pudieron
   medir así: la calibración de cámara no cerró.
3. **Buscar medidas publicadas**: una búsqueda web, sin planos ni dimensiones del edificio.
4. **Ficha** (`ficha_edificio.md`): cada número con su fuente y su confianza. La mayoría es de confianza baja.
5. **Modelo** (`scripts/maqueta_limpia.py`): las superficies se barren a lo largo de la planta (dos cabeceras
   rectas, dos esquinas de cuarto de círculo y un lateral recto), así bandejas, barandas y muro quedan
   paralelos. 23.902 caras en 9 objetos, uno por material. Sin escudo, marcas ni letras.

Resultado: `limpia/hoja_v4a.jpg` y `museo/render/stills/parada_11_maqueta__limpia.jpg`. Juicio mío: geometría nítida y planta en "D" correcta; la fachada, las filas y el
edificio de palcos son esquemáticos, y las alturas dependen de un modelo generado. Costo: 0 créditos.

**Veredicto de Marilyn (2026-11-18):** "la maqueta de Blender la veo bien, usemos esa". Es la que queda en la sala.

## Conclusión — modelos de imagen a 3D en ComfyUI contra modelado desde una ficha

Un solo objeto, una corrida por método y una sola persona juzgando: vale para este caso, no como regla.

| | Tripo (vistas normalizadas) | Rodin (fotos reales) | Blender desde la ficha |
|---|---|---|---|
| Qué define la forma | El modelo, a partir de una vista generada y su espejo | El modelo, a partir de 4 fotos oblicuas | Medidas explícitas, con su fuente |
| Planta | Inventada, casi simétrica | La más parecida a las fotos | La de Rodin y la foto 08, regularizada |
| Superficies | Nítidas pero "derretidas" de cerca | Blandas, bordes dentados, restos del barrio | Aristas limpias, piezas paralelas |
| Marcas | Agregó escudo y logo que se pidió no poner | No revisado de cerca | Ninguna: solo existe lo que se modeló |
| Se puede corregir una parte | No: hay que volver a generar | No | Sí: se cambia un número de la ficha |
| Costo | 102,2 créditos | 158,25 créditos | 0 créditos |
| Veredicto de Marilyn | "Hay que usar un modelo mejor" | Pidió modelado limpio | "La veo bien, usemos esa" |

Lo que se concluye para este caso:

1. **Para un edificio, los modelos de imagen a 3D no dieron una maqueta usable.** Los dos devuelven algo
   reconocible en minutos, pero un estadio es geometría regular y repetida (filas, pilastras, capas), y ahí
   se nota cada superficie blanda y cada parte inventada. Ninguno pasó el juicio de Marilyn.
2. **Sí sirvieron como instrumento de medida.** La planta y los cortes del modelo de Rodin, escalados con la
   cancha, son lo que permitió pasar de una maqueta "a ojo" (rechazada tres veces) a una con proporciones
   justificadas. El gasto en Rodin no fue en la maqueta final sino en sus medidas.
3. **Lo que cambió el resultado fue el contexto, no la herramienta.** Las maquetas por código de la etapa 1 y
   la de la etapa 4 se hicieron con el mismo Blender y el mismo modelo de lenguaje. La diferencia es que la
   cuarta parte de una ficha con medidas y de una forma de construir (barrer perfiles sobre la planta) en
   vez de cubos acomodados mirando fotos.
4. **Normalizar las vistas con un modelo generativo no quedó demostrado.** Devolvió una vista buena de tres,
   y no se corrió la comparación que diría si ayuda (Tripo con las fotos reales sin normalizar).
5. **La maqueta aceptada no es más "precisa" en sentido estricto**: sus alturas salen de un modelo generado
   que deforma ~6 % y de lecturas a ojo. Es más limpia y más controlable; un relevamiento pediría planos
   o fotogrametría.

Costo de llegar: 260,45 créditos en la etapa 3, cero en la 4.
