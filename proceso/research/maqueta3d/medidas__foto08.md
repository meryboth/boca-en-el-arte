# Medidas sobre la foto 08 (plano del suelo rectificado)

Foto `fuentes/bombonera_aerea_08.jpg` (1920×1080). Esquinas de la cancha marcadas a ojo por Fable, en píxeles:
(680,390) (1235,390) (1285,580) (615,590). Homografía cancha (105×68 m) → imagen con OpenCV.
Control: el centro del círculo central cae en (50,9; 33,4) m; debería ser (52,5; 34). Error ≈ 1,7 m.

Puntos del suelo (x a lo largo de la cancha, y desde la línea lateral cercana; metros):

| Punto | x | y |
|---|---|---|
| Pie del muro exterior, lateral largo (5 puntos) | −24,7 … 136,4 | −44,1 … −52,7 |
| Esquinas visibles del muro | −37,1 y 153,5 | −41,9 y −45,0 |
| Borde interno de la tribuna baja, lateral largo | 52,8 | −5,7 |
| Pie de la platea de palcos | 51,8 | 73,1 |
| Inicio de la tribuna en las cabeceras | −8,4 y 111,6 | — |

Solo valen los puntos que están en el suelo. La calibración de cámara a partir de esta homografía no cerró
(f² = −512.323 y 3.296.944 según la ecuación), así que no se midieron alturas con esta foto.
