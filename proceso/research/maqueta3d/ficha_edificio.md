# Ficha del edificio — de dónde sale cada número de `scripts/maqueta_limpia.py`

Contexto que se le da a Blender para modelar el estadio. **No es un relevamiento**: junta una medida
sobre una foto real, medidas sobre un modelo generado y lectura a ojo de las fotos. Cada fila dice cuál.

## Qué es el edificio (lectura de las 12 fotos aéreas de `fuentes/`)

- Planta en "D": tribunas en tres lados (un lateral largo y las dos cabeceras), unidas por esquinas curvas.
  El cuarto lado es recto y lo ocupa un edificio de palcos angosto y vidriado, con una torre en cada punta.
- Tres bandejas superpuestas: baja azul (poco profunda), media amarilla, alta azul (la más alta y empinada).
- Fachada por capas: base azul con ventanas, franja amarilla con tornapuntas azules en zigzag, galería en
  sombra, remate azul; pilastras verticales en todo el perímetro y una torre de escaleras en cada esquina curva.
- Marcador sobre la bandeja alta de una cabecera; reflectores sobre el borde; platea baja delante de los palcos.
- Sin escudo, sin marcas, sin letras ni números en las butacas (decisión de marca del proyecto).

## Medidas

| Dato | Valor | Fuente | Confianza |
|---|---|---|---|
| Cancha | 105 × 68 m | Medida reglamentaria, tomada como escala | Supuesto |
| Línea de cal → muro exterior, lateral largo | 50 m (44–53 según el punto) | Foto 08 rectificada con las 4 esquinas de la cancha, marcadas a ojo (`medidas__foto08.md`) | Media: ±5 m |
| Línea de fondo → muro exterior, cabeceras | 50 m | Foto 08 (37 y 48 m en las esquinas visibles) y modelo de Rodin (≈52 m) | Baja |
| Inicio de la tribuna baja | 6 m de la línea | Foto 08 (5,7 m) | Media |
| Pie de la platea de palcos | 5 m de la línea | Foto 08 (5,1 m) | Media |
| Radio de las esquinas | 52 m | Planta del modelo de Rodin (`medidas__rodin.json`, contorno cada 3°) | Baja |
| Altura del borde superior | 34 m | Modelo de Rodin (33,7–34,5 m), escalado por la cancha | Baja: Rodin infla el ancho ~6 % |
| Bandejas (frente/fondo, alturas) | baja 6–17 m, 1,2–5,5 m; media 15–29 m, 8–15,5 m; alta 27–48 m, 18–33 m | Cortes del modelo de Rodin a 0° y 180°, redondeados | Baja |
| Capas de la fachada | 0–11 azul, 11–18 amarillo, 18–22 galería, 22–34 azul | Proporciones leídas a ojo en las fotos 02 y 08 | Baja |
| Edificio de palcos | 9 m de fondo, 27 m de alto, 8 pisos, torres de 31 m | A ojo sobre las fotos 06, 08 y 09 | Baja |
| Filas, pasillos, cantidad de pilastras, ventanas | — | Inventados para que lea como maqueta | No son datos |

Lo que no se pudo medir: la altura real (la calibración de cámara de la foto 08 dio dos focales
incompatibles, así que no se usó), la inclinación de cada bandeja y cuánto vuela la bandeja alta sobre la calle.
No se encontraron planos ni medidas publicadas del edificio en la búsqueda web.
