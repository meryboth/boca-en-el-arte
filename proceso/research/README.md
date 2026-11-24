# Museo Xeneize — README técnico de la investigación

Punto de entrada para escribir el caso de estudio del portfolio (https://marilynbotheatoz.vercel.app/research).
Resume qué se hizo, con qué, qué salió y qué no se puede afirmar. Cada número de este archivo está copiado de
`report.md`, que se genera desde los datos; si alguno no coincide, vale `report.md`.

- **Sitio publicado:** https://meryboth.github.io/boca-en-el-arte/
- **Repo público (solo el sitio):** https://github.com/meryboth/boca-en-el-arte
- **Informe completo, en inglés:** `report.md` (no editarlo a mano: sale de `report.template.md`)
- **Este proyecto en disco:** `C:\Users\mboth\OneDrive\Desktop\teserract` — no tiene remoto; todo lo que no es el sitio existe solo acá.

Fechas registradas: commits del 2026-11-16 y 2026-11-17 (protocolo y evaluación), bitácoras del 2026-11-18 al 2026-11-24. No hay una fecha de inicio anotada. Proyecto no oficial: sin escudo, sin sponsors, sin nombres de jugadores.

## 1. Qué es

Diez pinturas clásicas en dominio público con la ropa repintada de azul `#103F79` y oro `#F3B229`, colgadas en una
sala 3D hecha por script, que se recorre con el scroll y termina en una maqueta del estadio. La portada del sitio
reproduce un teaser renderizado con path tracing.

El encargo original era probar dos herramientas sobre algo publicable: **Claude Fable 5.2** como "artista generativo"
y **Tesseract** (Mirage) para 3D. Por el camino se hizo un experimento formal (parte 1) y cuatro relatos de construcción.

## 2. Con qué se hizo

| Pieza | Herramienta | Para qué |
|---|---|---|
| Dirección, agentes y código | Claude Fable 5.2 (Claude Code) | Escribir scripts, configurar el recoloreo, armar la sala, el sitio y la maqueta |
| Edición de imagen | Nano Banana 2 (Gemini 3.1 Flash Image), nodo de Comfy Cloud, 4K | Repintar la ropa |
| Recoloreo determinista | `scripts/recolor.py` (CIELAB, polígonos y clave de color por zona) | Método `code` |
| Imagen a 3D | Tripo v3.1 multivista y Rodin Gen-2.5, vía Comfy Cloud | Intentos de maqueta |
| Sala y recorrido | Blender 5.1.2 sin interfaz, EEVEE | 1.621 cuadros + imágenes fijas por parada |
| Video | Tesseract CLI 0.7.0, path tracer, 48 muestras, 1080p, 24 fps | Video de entrada y teaser |
| Sitio | HTML estático, `canvas` + 541 cuadros WebP | Recorrido con scroll, 43 MB |
| Hosting | GitHub Pages | Publicación |

Máquina: Ryzen 9 4900HS, RTX 2060 Max-Q (6 GB), 15,4 GB de RAM, Windows 11. Todos los tiempos son de una sola medición en esta máquina.

## 3. Parte 1 — El experimento: ¿quién repinta mejor la ropa?

Registro: `PROTOCOL.md` (v2, con registro de cambios; la v1 está en `archive/`), `runs.jsonl` (e0001–e0060),
`results.json`, `eval-results.json`, `zones/zones.json`, salidas crudas en `runs/`.
Protocolo congelado en el commit `032ee07`; evaluación en `bf7f79b`.

**Cómo empezó.** El primer piloto hizo que Fable dibujara una pintura "renacentista" entera por código (`p0001`).
Marilyn: no era realista ni lo que quería; quería pinturas reales con la camiseta. Eso reescribió el protocolo.

**Tres métodos** sobre el mismo archivo fuente (lado largo 4.500 px):

| Condición | Quién pinta | Itera | Costo por imagen (mediana) |
|---|---|---|---|
| `edit` (baseline) | Nano Banana 2, un prompt congelado por pintura | no | 38,46 créditos |
| `code` | script de recoloreo; la config la escribe un agente Fable nuevo por intento | hasta 4 rondas (mediana 4) | 133.900 tokens, 512 s |
| `hybrid` | la ropa de `edit` pegada sobre el original con la máscara de `code` | no | reutiliza los dos anteriores |

Diseño: 4 pinturas × 3 métodos × 5 semillas = 60 corridas. Una quinta pintura (Julio II) solo para desarrollar el script.
Regla de Marilyn desde los pilotos: se tocan solo telas, no sillas ni objetos.

**Métricas** (sobre parches chicos congelados antes de correr; ninguna es un gate):
alteración (mediana CIEDE2000 en caras, manos y fondo; más bajo es mejor), error de matiz (grados respecto del azul u
oro de marca en la ropa; más bajo es mejor) y pliegues (correlación de Pearson de L* con el original; más alto es mejor).

| Las cuatro pinturas, n = 20 | `edit` | `code` | `hybrid` |
|---|---|---|---|
| Alteración (ΔE00) | 5,19 | 0,00 | 0,00 |
| Error de matiz | 12,7° | 0,9° | 12,6° |
| Pliegues | 0,83 | 0,91 | 0,85 |

Por pintura, la alteración de `edit` va de 4,31 a 5,74. La tabla completa es la Tabla 2 de `report.md`.

**Evaluación humana a ciegas** (una evaluadora, 60 pares y 60 imágenes sueltas):

| Par | Total | Intervalo 95 % del primero | Veredicto |
|---|---|---|---|
| `code` vs `edit` | 9–11 | 25,0 % – 65,0 % | sin ganador |
| `hybrid` vs `code` | 11–9 | 35,0 % – 75,0 % | sin ganador |
| `hybrid` vs `edit` | 11–5 (4 sin decidir) | 43,8 % – 87,5 % | sin ganador |

"Se nota retocado": `code` 5/20 (los cinco intentos del Arnolfini), `edit` 0/20, `hybrid` 0/20.

**Hipótesis:**
- **H2, confirmada.** El modelo de imagen cambia lo que debía dejar intacto: 5,2 ΔE00 contra un umbral de 2,0 fijado antes; peor parche 12,5. Además devuelve otro tamaño (0,92× a 1,67× los píxeles del original).
- **H1, no confirmada.** La gente no prefirió el código: 9–11. El empate esconde dos goleadas opuestas: en las dos pinturas con pocas prendas grandes ganó el modelo todos los pares (Prato y Arnolfini, 0–5); en las dos con muchas figuras ganó el código 9 de 10 (Baco 4–1, Atenas 5–0).
- **H4, no confirmada.** El combinado no le ganó a los dos.
- **H3, no probada.** La ablación se canceló para no pasar el presupuesto de tokens.

**Qué es cierto por construcción y no es hallazgo:** `code` y `hybrid` dan ~0 de alteración porque copian el original
fuera de la máscara; `hybrid` iguala a `edit` en matiz porque es la tela del modelo.

**Hallazgo incómodo:** el código acierta el matiz de marca mucho mejor (0,9° contra 12,7°) y eso no fue lo que la
evaluadora premió. Y la métrica de pliegues le dio su mejor puntaje (0,99) a las imágenes del Arnolfini que ella marcó
como retocadas: no sirve para tela oscura.

## 4. Qué cuelga en el museo

`../museo/seleccion.json` (elegidas por Marilyn con `scripts/build_curaduria.py`):

| Obra | Método |
|---|---|
| Madonna del Prato, Matrimonio Arnolfini, Baco y Ariadna | Combinado (`hybrid`) del experimento |
| La escuela de Atenas | Código |
| Retrato de Julio II | Combinado, edición con franja bordada |
| La dama del armiño, Castiglione, Eleonora de Toledo, Los embajadores, Enrique VIII | Combinado con máscara automática (`scripts/auto_hybrid.py`) |

La variante de máscara automática (la máscara sale de dónde el modelo cambió el matiz, sin agente) **nunca se midió ni
se evaluó**. Enrique VIII reemplazó a la Gioconda: su vestido ya era oscuro y la intervención casi no se notaba.

## 5. Parte 2 — Tesseract

Registro: `tesseract-log.md`, `../tesseract/intro/`, `../tesseract/teaser/`, `../scripts/tesseract_teaser.py`.

- La sala es de Blender; Tesseract hizo el video. Al importar el `.blend` se perdieron las luces de área, los materiales procedurales y la restricción de cámara: las luces se rehicieron en watts (17, 34 y 95 W).
- El path tracer se quedaba sin memoria en la placa de 6 GB hasta bajar todas las texturas a 1.280 px.
- Un cuadro 1080p: 22,4 s con 16 muestras, 37,5 s con 48, 75,2 s con 128.
- Primer video: 192 cuadros, 110 min de export (34,5 s por cuadro).
- Teaser final: 5 planos, 408 cuadros, 17 s, un proyecto por plano unidos con ffmpeg. Se renderizaron 6; el de las vigas se sacó porque mostraba solo techo.
- El export del teaser fue el paso menos confiable: 4,3 h en total para los 6 planos (28,1–35,9 s por cuadro). El tercer plano falló dos veces: "GPU device lost" en el cuadro 29 de 72, y un cuelgue de unas 40 h en el cuadro 61 sin dar error. Se resolvió con un vigilante que mata el export a los 600 s sin cuadro nuevo. Causa de las dos fallas: desconocida.
- La luz rebotada es claramente mejor que EEVEE; las cajas siguen siendo cajas. No es fotorrealista.

## 6. Parte 3 — Sala y sitio

Registro: `../museo/BITACORA.md`, `../scripts/blender_sala.py`, `../scripts/build_sitio.py`, `../scripts/sitio_template.html`, `../scripts/publicar_sitio.sh`.

- Un solo script arma paredes, túnel, vigas, lucernarios, marcos, cámara y paradas; no hay archivo de Blender editado a mano.
- Casi todo se rehízo después de que Marilyn lo vio: ornamentos por código → marcos escaneados de Poly Haven; piso con vetas → cemento alisado; paneo de cámara → cuerpo que camina, se balancea y gira hacia cada obra; lienzos pixelados → fuentes de 3.840 px e imágenes fijas de 2.880 px.
- Render final: 1.621 cuadros en 85 min (3,1 s por cuadro).
- Sitio: recorrido pre-renderizado, 541 cuadros, una imagen fija por parada, visor de obra, teaser en la portada. No menciona la técnica ni el modelo (decisión de Marilyn).
- Publicado con GitHub Pages el 2026-11-24. Probado en un navegador de escritorio: teaser, recorrido hasta la parada de Enrique VIII y consola sin errores. No probado: las 13 paradas una por una, celulares, Safari, tiempo de carga.

## 7. Parte 4 — La maqueta del estadio

Registro: `maqueta3d/BITACORA.md`, `maqueta3d/ficha_edificio.md`, `runs.jsonl` (m0001–m0005), `../scripts/blender_medir_estadio.py`, `../scripts/maqueta_limpia.py`.

| Camino | Resultado | Veredicto de Marilyn | Costo |
|---|---|---|---|
| 1. Cubos por código, 3 versiones | reconocible, proporciones a ojo | "muy básica"; no la veía precisa | 0 |
| 2. Modelo ya hecho | ninguno gratis y reutilizable (uno a US$ 65, licencia editorial) | no se usó | 0 |
| 3a. Vistas normalizadas con Nano Banana 2 + Tripo | 167.744 vértices; nítido, planta y dorso inventados | "necesitamos un modelo mejor" | 38,9 + 63,3 créditos |
| 3b. Rodin Gen-2.5 sobre fotos reales | 600.556 vértices; mejor planta, gradas blandas | pidió modelado limpio | 158,25 créditos |
| 4. Modelo limpio desde una ficha | 23.902 caras en 9 objetos | "me gusta, usemos ese" | 0 |

- El cuarto camino es el aporte: la malla generada se **midió** en vez de usarse. Los vértices verdes dan la cancha (origen, ejes, escala de 105 m) y de ahí salen el contorno cada 3°, ocho cortes y la altura del borde (~34 m). La cancha de Rodin mide 72,1 m de ancho en vez de 68: la fuente tiene ~6 % de error.
- Una foto real rectificada desde las cuatro esquinas de la cancha (control: el punto central cae a 1,7 m) da unos 50 m de la línea de banda al muro exterior.
- Fallas registradas: el recorte automático por color falló en 5 de 7 fotos; la normalización de vistas dio una vista buena de tres; 2 de 5 corridas 3D fallaron por errores de armado del grafo; Tripo pintó un escudo y una marca de indumentaria (tapados en la textura, 11.746 px).
- Con un objeto, una corrida por camino y una persona juzgando, es un estudio de un caso: no se puede decir qué servicio de imagen a 3D es mejor.

## 8. Parte 5 — Pipelines de ComfyUI

Registro: `../comfy/README.md`. Dos grafos guardados en Comfy Cloud: edición + máscara sobre el original, y vistas a 3D.
El de 3D no se corrió de punta a punta (se hizo en dos etapas con el recorte en local).

## 9. Costos

| Etapa | Corridas | Costo |
|---|---|---|
| Pilotos | 6 | 76,99 créditos |
| Evaluación `edit` | 20 | 769,26 créditos |
| Evaluación `code` | 20 agentes | 2.898.475 tokens, 3,6 h de agente |
| Evaluación `hybrid` | 20 | 0 |
| Cinco pinturas más y un reemplazo | 6 | 230,72 créditos |
| Estadio, imagen a 3D | 5 (2 fallidas) | 260,45 créditos |
| Sala, video, sitio, maqueta limpia | — | 0 (máquina propia) |
| **Total** | **77** | **1.337,42 créditos + 2,90 M tokens** |

Los créditos son la cifra de Comfy Cloud por trabajo, no un monto facturado; no hay conversión a dólares.
No se cuentan los tokens de la conversación que dirigió todo.

## 10. Límites que hay que escribir en la nota

- **Una sola evaluadora, que es la autora, y rápida:** 120 respuestas en 259 s; 33 de las 60 de imagen suelta en menos de un segundo. Conocía los métodos.
- **El baseline no pudo iterar y el código sí** (hasta 4 rondas). Favorece al código, que igual no ganó.
- **Las semillas emparejan solo de nombre:** Nano Banana 2 no devuelve la misma imagen con la misma semilla.
- **Cuatro pinturas, una por nivel de dificultad:** el reparto por pintura es un patrón a probar, no un resultado.
- **Las métricas no se validaron contra una persona** antes de usarlas; la de pliegues falla en tela oscura.
- **La mitad del museo no está medida** (máscara automática).
- **La maqueta no es un relevamiento.**
- **Tiempos de una sola medición**, en una máquina.
- **No hecho:** sonido del teaser, prueba en celulares, segunda evaluadora, H3, revisión de dos críticos de Tesseract.

## 11. Mapa de archivos

Rutas relativas a la raíz del proyecto.

| Qué | Dónde |
|---|---|
| Informe (inglés) | `research/report.md` · plantilla `report.template.md` · datos `report-data.json`, `report-extra.json` |
| Protocolo y cambios | `research/PROTOCOL.md`, `research/archive/` |
| Registro de corridas | `research/runs.jsonl` (77 líneas) |
| Resultados | `research/results.json`, `research/eval-results.json`, `research/eval-key.json` |
| Salidas crudas | `research/runs/`, `research/pilots/`, `research/outputs/` |
| Parches de medición | `research/zones/` |
| Fuentes y hashes | `research/sources/README.md` |
| Bitácoras | `research/tesseract-log.md`, `research/maqueta3d/BITACORA.md`, `museo/BITACORA.md`, `comfy/README.md` |
| Checklist de publicación | `research/checklist.md` |
| Hojas de proceso (31 imágenes, 01–30) | `research/proceso/` |
| Maqueta: fotos, recortes, modelos, ficha | `research/maqueta3d/` |
| Obras finales y máscaras | `museo/obras/`, `museo/seleccion.json` |
| Imágenes fijas de la sala | `museo/render/stills/`, `museo/render/pisos/` |
| Sitio construido | `museo/sitio/` |
| Videos | `tesseract/teaser/teaser.mp4`, `tesseract/intro/intro__maqueta-codigo.mp4` |
| Código | `scripts/` |

**Imágenes más útiles para la nota:** `proceso/01` (piloto por código), `03` (tres métodos), `14` y `18` (Arnolfini y
Atenas), `27` (Enrique VIII), `30` (teaser), `maqueta3d/hoja_fotos_aereas.jpg`,
`maqueta3d/hoja_comparacion__tripo-arriba__rodin-abajo.jpg`, `maqueta3d/limpia/hoja_v4a.jpg`,
`../museo/render/stills/parada_11_maqueta.jpg`. La `proceso/12_tesseract-prueba.jpg` está duplicada con la 20.

## 12. Cómo reproducir

```
python scripts/measure.py …            # métricas sobre zones/zones.json
python scripts/summarize_runs.py research/runs.jsonl --baseline edit --out research/results.json
blender --background --python scripts/blender_sala.py -- --stills --anim
python scripts/build_sitio.py --intro tesseract/teaser/teaser.mp4
python scripts/tesseract_teaser.py build | preview | export | join
python scripts/build_report_data.py
python scripts/render_report.py research/report.template.md research/report-data.json research/report.md
bash scripts/publicar_sitio.sh "mensaje" --push     # sube solo museo/sitio al repo público
```

Las imágenes a resolución completa y los `.blend` están fuera de git (`.gitignore`); existen en este disco.

## 13. Licencias a citar

- Pinturas: dominio público, vía Wikimedia Commons (`sources/README.md`, con hashes).
- Fotos aéreas del estadio: ProtoplasmaKid, CC BY-SA 4.0. Los modelos 3D derivados heredan atribución y compartir igual.
- Marcos: Poly Haven, CC0.
- El proyecto no es oficial ni usa escudo, marcas ni nombres.

## 14. Pendiente

1. Revisión de Marilyn del informe (`report.md`) y del sitio publicado.
2. Commit y respaldo: desde `bf7f79b` casi todo está sin commitear y el repo local no tiene remoto.
3. `report.md` no menciona la publicación en GitHub Pages del 2026-11-24 (está en `museo/BITACORA.md`); agregarla si la nota la cuenta.
4. Captura del lienzo de ComfyUI (necesita que Marilyn inicie sesión en el navegador).
5. La nota del portfolio va en inglés casual; las bitácoras están en castellano.
