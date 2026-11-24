# Bitácora — la sala del museo y el sitio

Cómo se armó la sala 3D y el recorrido que muestra el sitio. Escrita el 2026-11-18 a partir del registro
de la sesión de trabajo, no día por día: las fechas exactas de cada cambio no están. Es un relato de
construcción con las correcciones de Marilyn, no un experimento: no hay baseline ni mediciones.

## Decisiones de partida (Marilyn)

- Recorrido **pre-renderizado**: el sitio no corre 3D en vivo, muestra cuadros renderizados que avanzan con el scroll.
- Video de entrada hecho con Tesseract (`research/tesseract-log.md`).
- Las obras las eligió ella (`museo/seleccion.json`): 10 pinturas.
- Marca: azul `#103F79` y oro `#F3B229`, franja horizontal, sin escudo, sin sponsors, sin nombres. El sitio dice que no es oficial.
- El sitio no menciona la técnica de pintado ni el modelo usado.

## La sala (`scripts/blender_sala.py`, Blender 5.1 sin interfaz, EEVEE)

Todo se genera por script: no hay archivo de Blender editado a mano. Sala de 7,0 × 4,2 m de sección,
obras cada 5,6 m, ojo a 1,6 m.

| Qué | Primera versión | Qué dijo Marilyn | Cómo quedó |
|---|---|---|---|
| Arquitectura | Sala neutra | "Pongamos alguna arquitectura que dé cuenta que estamos dentro de un museo de Boca" | Túnel de entrada azul con tiras de luz, zócalo azul con franja oro, vigas y pilastras de hormigón, butacas de tribuna, lucernarios |
| Túnel | Con franjas oro | "Las franjas en el pasillo las evitaría" | Sin franjas |
| Marcos | Molduras generadas por código | "Los ornamentos no los veo realistas" | Marcos escaneados de Poly Haven, CC0 (`museo/assets/marcos/`) |
| Piso | Con vetas | No le gustó; pidió deck de madera o cemento alisado | Deck con textura: "se ve igual que el primero"; quedó cemento alisado, tono medio |
| Cantidad de obras | 5 | "Me gustaría que sumemos más cuadros" | 10 (las 5 nuevas con la técnica que mejor había funcionado) |
| Transición entre obras | Paneo de cámara | "Extraño"; "debería simular que la persona camina y se para en frente de otro cuadro" | Cámara hija de un cuerpo que camina, con balanceo de pasos y mirada que gira hacia la obra |
| Calidad de las pinturas | Texturas chicas | "Se ven muy pixeladas" | Originales de 3840 px e imágenes fijas de 2880 × 1620 en cada parada |
| Maqueta del estadio | No había | La pidió sobre una mesa al final de la sala | Cuatro intentos: `research/maqueta3d/BITACORA.md` |

Problemas técnicos que aparecieron: piso sobreexpuesto y borroso; el paspartú tapaba los lienzos (se separó
el lienzo 12 mm); con 10 obras la sala quedó primero oscura y después lavada (lucernarios a 60 W, mundo a 0,1);
avisos del búfer de sombras (lucernarios sin sombra). Wikimedia devolvía error 429 al bajar originales: se
usó su servicio de miniaturas.

Tiempo de render: unos 1,7 s por cuadro a 1600 × 900 en una RTX 2060 Max-Q (medido una vez); 1621 cuadros.
Render final con la maqueta limpia (2026-11-18): 1621 cuadros en 84,6 min, 3,1 s por cuadro (una corrida, por la hora
de archivo del primer y el último cuadro), sin errores en `museo/render/render.log`. No se investigó por qué tardó más que el anterior.

## El sitio (`scripts/build_sitio.py` + `scripts/sitio_template.html` → `museo/sitio/`)

Estático, sin servidor: un `canvas` que muestra una secuencia de cuadros WebP según el scroll, una imagen
fija de alta resolución en cada parada y un visor para ver la obra sola. 541 cuadros (uno de cada tres),
34 MB en total. Un error mío en el camino: una variable declarada dos veces rompía el dibujo.

## Qué no es

- No es fotorrealista. Una usuaria de Tesseract mostró resultados hiperrealistas y Marilyn preguntó por qué
  el proyecto no se ve así: la sala son cajas con materiales simples y el motor es EEVEE; lo que falta es
  modelado y materiales, más que motor (ver la prueba con path tracer en `research/tesseract-log.md`).
- No se probó en celulares ni se midió el tiempo de carga.
- Nadie más que Marilyn y Fable lo evaluó.

## 2026-11-18 — El video de entrada entra al sitio

Hasta acá el video de Tesseract existía pero el sitio no lo usaba: Marilyn preguntó "no termino de entender
cuál es el video de Tesseract" y al revisar la plantilla no había ninguna referencia. Ahora `build_sitio.py`
copia `tesseract/intro/intro.mp4` a `museo/sitio/intro.mp4` (opción `--intro`; si el archivo no está, el sitio
queda como antes) y la portada lo reproduce una vez, sin sonido, sobre el primer cuadro; al terminar o al
primer scroll se desvanece y queda el recorrido.

- El título va dentro del video, así que mientras se reproduce se oculta el título HTML de la portada.
- Solo en pantallas apaisadas: en vertical el recorte taparía el título, y ahí queda la portada de antes.
- Tampoco se reproduce si el sistema pide reducir movimiento.
- Peso: el sitio pasa de 34,6 a 43,0 MB con el clip de 8,5 MB.
- Probado en navegador de escritorio a 1280 × 720 con el clip viejo: reproduce, oculta la portada, se
  apaga al hacer scroll, consola sin errores (`research/proceso/24_sitio-portada-con-video.jpg`).
  No probado: celulares, Safari, conexiones lentas (el video se baja entero al entrar).

## 2026-11-18 — Sale la Gioconda, entra Enrique VIII

Al ver el primer plano del teaser, Marilyn: "el tema con la Mona Lisa es que su cuadro no parece haber sido
intervenido para Boca, así que además lo reemplazaría por otro". Es cierto: el vestido ya era oscuro y las
mangas ocres, así que pasarlos a azul y oro casi no cambia la imagen. Eligió Enrique VIII entre cuatro opciones.

- Fuente: retrato de cuerpo entero del taller de Holbein, Wikimedia Commons, dominio público
  (`research/sources/README.md`). Commons lo fecha c. 1540–1547; yo le había dicho c. 1537 al ofrecerlo.
- Mismo método que la segunda tanda: una edición con Nano Banana 2 (4K, semilla 1) y `scripts/auto_hybrid.py`.
  Un intento, 38,46 créditos según la facturación (corrida `a0006`), aprobado por Marilyn antes de enviarlo.
- Pedido: manto rojo a azul, jubón gris plata a oro. Salió así al primer intento; la máscara automática pegó
  el 23,5 % del cuadro. Sin métricas ni evaluación: revisión a ojo mía sobre
  `research/proceso/27_enrique8-original-combinado-mascara.jpg`. No lleva franja horizontal.
- En la pared: el cuadro es muy angosto (0,68 × 1,2 m) y el marco le queda pesado. Probé colgarlo a 1,5 m de
  alto y el marco se salía del encuadre de la parada; volvió a 1,2 m. Queda así, declarado.
- La Gioconda intervenida sigue en `museo/obras/`; no se borró.
- Recorrido re-renderizado después del cambio (tercera vez en el día).

## 2026-11-20 — El teaser reemplaza al video de entrada en la portada

- Recorrido con Enrique VIII: 1621 cuadros sin errores en `museo/render/render.log` (terminó el 18 a las 15:58).
- `python scripts/build_sitio.py --intro tesseract/teaser/teaser.mp4`: 541 cuadros, 13 paradas, 43,7 MB (el teaser pesa 8,05 MB).
- Probado en el navegador integrado a 1280 × 720: el video arranca solo, llega a los 20 s, se apaga y vuelve la portada;
  la parada figura como "Enrique VIII"; consola sin errores.
- Lo que no pude comprobar: el panel del navegador estaba oculto y ahí las transiciones de opacidad no avanzan, así que en
  las capturas el título HTML aparece superpuesto al video. Las clases cambian cuando deben (`fuera` se quita al empezar,
  `con-intro` se saca al terminar), pero el fundido no lo vi correr en una ventana visible. Falta que Marilyn lo mire.
- No probado, igual que antes: celulares, Safari, conexiones lentas.
- Cómo se hizo el teaser y por qué tardó dos días: `research/tesseract-log.md`.

## 2026-11-24 — El sitio sube a un repo público

Marilyn creó https://github.com/meryboth/boca-en-el-arte (público) y eligió subir **solo el sitio**; el resto del
proyecto queda en su máquina como referencia para la nota de research del portfolio.

- `bash scripts/publicar_sitio.sh "mensaje" --push` arma un commit con `museo/sitio/` en la raíz más
  `scripts/sitio_README.md` como `README.md`, usando un índice temporal: no toca la rama ni el índice del proyecto.
- Primer commit `95698f2`: 567 archivos, 42,7 MB (541 cuadros, paradas, obras, teaser de 17 s).
- El README dice que no es oficial y lleva los créditos (dominio público, Poly Haven CC0, fotos de ProtoplasmaKid
  CC BY-SA 4.0 como referencia de la maqueta). No menciona la técnica ni el modelo usado.
- No hecho: desplegarlo en un hosting; nadie abrió todavía el sitio desde el repo.
- El repo local sigue sin remoto y sin commitear desde `bf7f79b`: todo lo que no es el sitio existe solo en este disco.
- Mismo día: Marilyn activó GitHub Pages. Publicado en https://meryboth.github.io/boca-en-el-arte/. Probado en el
  navegador integrado: el teaser se reproduce (17 s, sin error), 13 paradas y 541 cuadros en los datos, 250 recursos
  cargados sin ninguno fallido hasta la parada de Enrique VIII, consola sin errores. No recorrí las 13 paradas ni probé
  en celular; el panel era casi cuadrado, así que el encuadre apaisado no se comprobó ahí.
- Mismo día: el README del repo público (`scripts/sitio_README.md`) pasó a incluir el resumen técnico de la investigación, a pedido de Marilyn. Ahí sí se nombran las herramientas y los modelos; la regla de no mencionarlos sigue valiendo para la página.
- Mismo día: el README público suma 8 imágenes de proceso y 3 GIFs (antes/después de seis obras, recorrido acelerado,
  teaser a 448 px y 8 cuadros por segundo), en `museo/readme/`, que se publica como `readme/`. No se incluyeron las
  fotos aéreas del estadio (tienen publicidad real a la vista) ni la hoja de Tripo y Rodin (uno de esos modelos traía
  un escudo que no revisé si quedó tapado en esa hoja). El GIF de antes/después se arma con las fuentes de
  `research/sources/` y las obras del sitio; los otros dos con ffmpeg.
- Mismo día: Marilyn pidió sacar del README público la imagen del piloto por código ("era horrible y encima no era lo que yo pedí"). Se quitó de `museo/readme/` y del README; el original sigue en `research/proceso/01_piloto-obra-por-codigo.jpg` y la imagen queda en el historial de commits del repo público.
- Mismo día: Marilyn pidió subir también el proceso, en una carpeta aparte que no afecte el deploy. `publicar_sitio.sh`
  ahora agrega `proceso/` (394 archivos, unos 87 MB): `research/`, `comfy/`, `scripts/`, esta bitácora, `seleccion.json`
  y las imágenes fijas de la sala, con la misma estructura de carpetas para que los enlaces relativos sigan andando.
  Los scripts los sumé yo sin que los pidiera, porque el informe los cita.
- Fuera de `proceso/`, a propósito: lo que git ya ignora (imágenes a resolución completa, `.blend`, respuestas de la
  evaluación), los modelos 3D, las fotos aéreas con sus recortes y vistas, y todo lo del piloto por código (`outputs/`,
  `proceso/01`, `briefs/adan.md`). Las bitácoras siguen mencionando esos archivos; el `README.md` de la carpeta lo avisa.
- Al informe se le quitaron dos imágenes que apuntaban a archivos no publicados (el piloto y la hoja de fotos aéreas).
- Se agregó `.nojekyll` en la raíz: Pages sirve los archivos tal cual y no procesa los `.md` del proceso.
- Pages sirve todo el repo, así que `proceso/` también queda accesible bajo la dirección del sitio; la página no lo enlaza.
  Los archivos del sitio no cambiaron respecto del commit anterior (diff vacío).
