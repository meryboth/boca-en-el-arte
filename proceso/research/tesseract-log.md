# Bitácora de Tesseract

Estudio de caso (Parte B del protocolo). Se anota todo, incluido lo que falla.
Los tiempos salen de la salida de los comandos, no de estimaciones.

## 2026-11-16 — Instalación de las skills

- Comando: `npx skills add mirage-hq/Tesseract --yes` en la raíz del repo.
- Entorno: Windows 11 Home, Node v24.19.0, npm 11.17.0.
- Tiempo de pared: 17,0 s (`time`, una corrida).
- Resultado: 5 skills en `.agents/skills/` (`tesseract-3d`, `-design`, `-editor`, `-motion`,
  `-video`), enlazadas en `.claude/skills/`.
- Evaluación de riesgo que muestra el instalador: Gen "Safe" en las cinco; Socket 0 alertas,
  salvo `tesseract-editor` con 1; Snyk "Med Risk" en `tesseract-3d` y `tesseract-editor`,
  "Low Risk" en el resto. No se investigó todavía qué es la alerta de `tesseract-editor`.

## 2026-11-16 — Lo que se supo leyendo la skill (antes de renderizar)

- **Las skills son solo instrucciones.** El motor es un CLI aparte (`tsrct`), versión
  requerida 0.7.0, que se baja de GitHub Releases:
  `tesseract-0.7.0-windows-x86_64.zip`, 181.607.657 bytes (≈173 MiB, del header
  `Content-Length`). No estaba instalado en esta máquina.
- El bundle de Windows **no está firmado**: SmartScreen puede advertir. La guía pide verificar
  el SHA-256 y no saltear la advertencia.
- **Telemetría activada por defecto** en `project create`, `export`, `preview` y `filmstrip`.
  Según la documentación de la skill manda comando, versión, sistema operativo, arquitectura,
  IDs aleatorios, éxito o falla y duración; no manda rutas, contenidos ni prompts.
  Se apaga con `tsrct telemetry disable`. Sin verificar de forma independiente.
- Importa `.glb`, `.gltf` y `.blend`. Dos renderers: `raster` (rápido) y `path-tracer`
  (lento, mucho más sin GPU). El documento es un `.tsrct` editable.
- La reproducción en navegador usa raster aunque el export haya sido path-traced: para la
  web conviene exportar video o stills ya renderizados.
- El flujo de la skill exige una revisión con dos "críticos" (subagentes) hasta 8,5/10, con
  un máximo de tres rondas. Suma consumo de tokens: hay que contarlo en el presupuesto.

## 2026-11-16 — Instalación del CLI

Aprobada por Marilyn ("Sí, sin telemetría").

- Descarga del zip (181.607.657 bytes) más el `.sha256`: 11,0 s de pared.
- SHA-256 calculado igual al publicado: `874032ce…af09581`.
- `install.ps1` terminó sin errores ni advertencia de SmartScreen visible en la salida.
  Instalado en `%LOCALAPPDATA%\Tesseract\bin\tsrct.cmd`.
- Versión: `tsrct 0.7.0 (f417fba5…)`, coincide con la requerida.
- Telemetría apagada **antes** del primer comando que la emite:
  `tsrct telemetry status` → `{"enabled":false,"retired":false}`.
- Soporte 3D confirmado: `createFxScene3DLayer` aparece en `project schema`
  (schema de 1,48 MB, `fxSchemaVersion` 87).

## 2026-11-16 — Prueba mínima de render

Hardware: AMD Ryzen 9 4900HS, NVIDIA GeForce RTX 2060 Max-Q (más Radeon integrada).
No se verificó cuál de las dos GPU usó el renderer.

Escena: el ejemplo de la documentación de la skill (un cubo azul, una luz paralela, cámara
ortográfica), sin animación. Lienzo por defecto 1080×1920. Archivos en `tesseract/smoke/`.
El batch de 7 acciones se aplicó al primer intento, sin advertencias.

| Render | Flags | `renderSeconds` | Pared (`time`) | Salida |
|---|---|---|---|---|
| Raster | (por defecto) | 6,31 | 12,4 s | `smoke-raster.png` |
| Path tracer | `--renderer path-tracer --samples 16` | 21,01 | 26,9 s | `smoke-pt16.png` |

n = 1 por fila y ambas son la **primera** corrida de cada renderer, así que incluyen
compilación de shaders en frío (y el path tracer, posiblemente la descarga del denoiser).
No sirven para estimar un export largo ni para comparar renderers.

Lo que se ve: un cubo azul centrado con tres caras de distinto tono sobre fondo blanco, en
las dos imágenes. A simple vista son iguales (juicio mío, sin métrica): la escena no tiene
piso, sombras ni reflejos, que es donde el path tracer debería diferenciarse.

Formatos de salida confirmados con `--help`:

- `preview`: PNG de un cuadro (8 bits, o 16 bits con `--hdr`).
- `filmstrip`: PNG con grilla de cuadros.
- `export`: MP4 o ProRes 4444 MOV, a 720p, 1080p o 4K; `--fx-solo` da overlay transparente.
- **No hay export de glTF/GLB ni de escena para tiempo real.** Para la web, la sala va a
  ser video o stills pre-renderizados.

## Pendiente

- Diseñar la sala y definir cómo se navega en la web (video con scroll o stills).
- Medir tiempos en caliente con una escena que tenga piso, paredes y sombras.
- Revisar la alerta de Socket en `tesseract-editor` si se llega a usar esa skill.

## 2026-11-17 — La sala se arma en Blender, no en Tesseract

Decisión de Marilyn: recorrido pre-renderizado, con la sala construida en Blender 5.1.2 por script
(`scripts/blender_sala.py`, corrido en modo headless) y Tesseract reservado para un video de entrada.

- Blender en esta instalación solo lista el motor `BLENDER_EEVEE` en modo headless; no se probó activar Cycles.
- Primera corrida de la sala (5 obras, 1280×720, 32 muestras): 23,2 s el primer cuadro (incluye carga de texturas
  y compilación) y 0,4 a 0,5 s cada uno de los siguientes. Una sola medición.
- Tres pasadas hasta una sala aceptable: la primera salió sobreexpuesta y con piso borroso; la segunda corrigió
  luz y piso pero el filete nuevo del marco tapó los lienzos (error mío de profundidades); la tercera lo corrigió.
- El recorrido son 577 cuadros a 24 fps (6 paradas de 36 cuadros y 5 traslados de 72).

## 2026-11-18 — Video de entrada: la sala de Blender, trazada en Tesseract

Objetivo: una toma de 8 s que sale del túnel hacia la sala, con el título encima. Proyecto en `tesseract/intro/`.

**Importar la sala.** `project import-asset --kind model3d` sobre `museo/sala.blend` (75 MB): 4,5 s, sin errores.
Entraron 1.576 nodos, 24 materiales y 3 animaciones. El informe de conversión listó 50 avisos; lo que se perdió:

- Las 15 luces de área (lucernarios y túnel): "area lights have no glTF equivalent". Los 27 focos quedan como nodos vacíos, no como luces de la escena.
- El piso procedural (nodos de ruido, rampa y relieve): queda con su color plano.
- La restricción de la cámara (Track To): no se aplica.

Consecuencia: hubo que rehacer en Tesseract las 21 luces y la cámara, a partir de las posiciones del script de Blender.
La orientación y la escala entraron bien al primer intento (metros de Blender × 100 px; el eje Y de Blender pasa a ser la profundidad).

**Errores míos al escribir las acciones.** Dos lotes rechazados: el color de las luces pide 4 componentes y mandé 3; y adiviné un nombre de acción (`updateFxScene3DLightControls`) que no existe, contra lo que indica la guía de la skill. Los lotes son atómicos, así que no quedó nada a medias.

**El path tracer no entró en la memoria de la placa.** Con la sala completa falló en los tres intentos (traversal automático, por software y por hardware) con `scene3d_path_tracer_frame` y "Not enough memory resources are available" (0x8007000E), en la RTX 2060 Max-Q. El raster sí renderizaba (66 s el primer cuadro).
Solución: una copia liviana de la sala con todas las texturas reducidas a 1280 px (`blender_sala.py --tex-max 1280`, 25 MB). Con esa copia el path tracer funcionó. Costo: las pinturas pierden definición en este video; no afecta al sitio, que usa los renders de Blender.

**Tiempos de un cuadro a 1920×1080, path tracer con denoise** (una medición cada uno, misma sesión):

| Muestras | `renderSeconds` |
|---|---|
| 16 | 22,4 |
| 48 | 37,5 |
| 128 | 75,2 |

Hay un costo fijo de unos 15 s por cuadro más unos 0,47 s por muestra.

**Luz.** Las potencias de Blender no sirven en Tesseract, que usa vatios físicos: con los mismos números las pinturas salían quemadas. Quedaron en 17 W los focos de obra, 34 W el del fondo y 95 W cada lucernario, ajustadas a ojo en tres pruebas.

**Lo que se ve** (juicio mío, `Previews/cuadro-2s5__path-tracer-48.png`): la luz rebotada llena el techo y las vigas, el túnel se ilumina desde sus tiras de luz y el piso refleja; es más creíble que el render de Blender en EEVEE. Las cajas siguen siendo cajas: el realismo que falta es de modelado y materiales, no de motor.

**Texto.** Dos capas 2D sobre la escena, en Georgia (la misma del sitio), tomada de las fuentes de Windows. Tesseract avisa que la fuente queda embebida en el `.tsrct`: ese archivo no se publica.

**Export.** 8 s, 24 fps, 1080p, 48 muestras: 192 cuadros. Terminó sin errores en 6.622 s (1 h 50 min), 34,4 s por cuadro según el CLI; `intro.mp4`, H.264, 1920×1080, 8,5 MB. Hoja de cuadros: `research/proceso/22_tesseract-intro-hoja.jpg`. El video muestra la maqueta por código, anterior a la reconstruida.

**No hecho.** La revisión con dos críticos que pide la skill (hasta tres rondas) no se corrió, para no gastar tokens; y el video no tiene sonido.

## 2026-11-18 (tarde) — Del video de entrada al teaser

- **El video no estaba en el sitio.** Marilyn preguntó cuál era el video de Tesseract: existía el archivo, pero
  la plantilla del sitio no lo usaba. Se integró en la portada (`museo/BITACORA.md`).
- **Re-export con la maqueta limpia, cortado.** Se rearmó el proyecto con `sala_ligera.blend` nueva y se lanzó el
  mismo export (48 muestras). Dos cuadros de prueba mostraron que la maqueta ocupa unos 90 × 20 px al fondo:
  el video nuevo y el viejo son iguales a simple vista. Lo corté en el cuadro 118 de 192 cuando Marilyn pidió
  otra cosa; el log parcial quedó en `tesseract/intro/.tesseract-work/export__maqueta-limpia__cortado.log`.
  El primer video se conserva como `intro__maqueta-codigo.mp4`.
- **Por qué no se distinguía en el sitio.** Arrancaba más de 3 s tarde (competía con 541 cuadros) y la toma es
  casi la del primer cuadro del recorrido. Se corrigió el orden de carga; lo segundo no tiene arreglo con esa toma.
- **Teaser.** Pedido de Marilyn: "¿el video puede ser más extenso? con diferentes puntos de vista del museo,
  como una especie de teaser". Seis planos, 20 s, 480 cuadros, 48 muestras (eligió calidad alta sobre 16 muestras).
  `scripts/tesseract_teaser.py` arma un proyecto por plano y los une con ffmpeg: un corte es un límite de
  archivo y un plano que falla se rehace solo. Mismas luces y potencias que el primer video.
- **Encuadres.** Primera ronda (`research/proceso/25_…`): la Gioconda y la maqueta salían cortadas y el plano de
  pared no se diferenciaba del general. Segunda ronda (`26_…`): corregidos. Marilyn pidió sacar a la Gioconda
  del primer plano (y de la sala); el plano 3 pasó a Julio II (`28_…`).
- Cuadros de prueba a 16 muestras: 24,6 a 27,6 s cada uno (una medición por plano).

### Export del teaser: se cayó la GPU en el tercer plano (2026-11-18, 17:47)

- Planos 1 y 2 exportados: 72 cuadros en 2587 s y 84 cuadros en 2967 s (35,9 y 35,3 s por cuadro; una corrida cada uno,
  `tesseract/teaser/.tesseract-work/*__export.out`).
- Plano 3 (`3_julio2`): falló en el cuadro 29 de 72 con "GPU device lost" (0x887A0005) a los 1004 s. No sé la causa: no medí
  temperatura ni memoria en ese momento. Tesseract conservó las 29 imágenes hechas en su caché de cuadros.
- Error mío en la cadena: el paso de unión corrió igual y dejó un `teaser.mp4` de 6,5 s con solo dos planos. No llegó al sitio;
  quedó apartado como `.tesseract-work/teaser__incompleto-2-planos.mp4`.
- Cambios: el log de export ahora se escribe en modo agregar (el intento fallido queda en el mismo archivo) y la cadena reintenta
  hasta cuatro veces y solo une si todos los planos terminaron. Relanzado a continuación.

### El relanzamiento se colgó 40 horas (visto el 2026-11-20, 09:40)

- El segundo intento del plano 3 reutilizó las 29 imágenes de la caché y avanzó a ~32 s por cuadro hasta el cuadro 61 de 72
  (1096 s, hacia las 18:07 del 18). Ahí dejó de avanzar sin dar error: siguió escribiendo una línea de progreso cada 5 s durante
  143 464 s, con la GPU al 0 % y 5,7 GB de memoria de video tomados. No sé la causa; la máquina pudo haber entrado en suspensión.
- Los reintentos que había puesto no servían para esto: solo reaccionaban a un error, no a un cuelgue.
- Maté el proceso a mano (la memoria de video volvió a 8 MiB). `tesseract_teaser.py export` ahora vigila el contador de
  cuadros y mata el export si pasan 600 s sin un cuadro nuevo; la cadena reintenta hasta cinco veces.
- El log del plano 3 pesa 6,4 MB por esas líneas repetidas; no se recortó.

### Teaser terminado (2026-11-20, 12:26)

Tercer lanzamiento, con el vigilante: un solo intento, sin cuelgues ni reintentos.

| Plano | Cuadros | Segundos | s por cuadro | Fecha |
|---|---|---|---|---|
| 1_tunel | 72 | 2587 | 35,9 | 18-nov |
| 2_pared | 84 | 2967 | 35,3 | 18-nov |
| 3_julio2 | 72 | 2311 | 32,1 | 20-nov (tercer intento; los dos anteriores fallaron) |
| 4_vigas | 72 | 2312 | 32,1 | 20-nov |
| 5_maqueta | 96 | 2702 | 28,1 | 20-nov |
| 6_sala | 84 | 2612 | 31,1 | 20-nov |

Tiempos de reloj de `tesseract_teaser.py export` (incluyen carga del proyecto y codificación), una corrida por plano,
path tracer, 48 muestras, 1080p, RTX 2060 Max-Q. Total de los exports que terminaron: 15 491 s (4 h 18 min). No incluye los
1004 s del intento que perdió la GPU ni el intento colgado.

`teaser.mp4`: 480 cuadros, 20,0 s, 1920 × 1080, 8,05 MB, sin sonido. Revisado a ojo por mí sobre 12 cuadros
(`research/proceso/29_teaser-final-12-cuadros.jpg`): los seis planos están, el título aparece solo en el último.
Marilyn todavía no lo vio.

### Sale el plano de las vigas (2026-11-20)

Marilyn, al ver el teaser: "los planos donde se ve tanto el techo los sacaría, no suman nada y en el techo no hay ningún
tipo de información sobre obras ni nada visualmente relevante". Saqué `4_vigas` del corte: es el único plano que apunta
al techo. No hizo falta renderizar nada: se volvió a unir. Queda en 5 planos, 408 cuadros, 17,0 s, 7,07 MB
(`research/proceso/30_teaser-sin-vigas-12-cuadros.jpg`). `4_vigas.mp4` y la versión de 20 s
(`.tesseract-work/teaser__v1-con-vigas.mp4`) se conservan; los 2312 s de ese export quedan como costo de un plano descartado.
Los planos generales (túnel, pared, sala) siguen mostrando techo en el tercio superior del cuadro; no los toqué.
En el sitio se reemplazó `museo/sitio/intro.mp4` copiando el archivo, sin reconstruir (42,7 MB en total).
