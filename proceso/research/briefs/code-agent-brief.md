# Brief del agente de recoloreo — condición `code`

Mismo texto para todos los intentos. Lo que cambia por corrida va en el mensaje que lanza al
agente: caso, archivo fuente, lista de cambios de color y rutas de salida.

## Tarea

Vas a intervenir una pintura clásica para que la ropa indicada quede en azul (`#103F79`) y oro
(`#F3B229`), sin tocar nada más. No pintás: escribís un archivo de configuración JSON para
`scripts/recolor.py`, que recolorea zonas conservando luces, sombras y pincelada.

1. Leé `scripts/recolor.py` entero para entender el formato de la config y qué hace cada campo.
2. Generá una vista previa de la pintura fuente de 900 px de lado mayor y mirala. Las
   coordenadas de los polígonos van en píxeles de esa vista previa (`coord_width` = su ancho).
3. Escribí la config en la ruta indicada: polígonos por prenda, clave de color según el color
   de origen de esas prendas, y niveles de luminosidad y croma.
4. Corré el script y mirá la vista previa que genera (`<out>__preview.jpg`).
5. Corregí y repetí. **Máximo 4 corridas del script en total.** Cada corrida escribe a un
   `out` distinto (`…__r1`, `…__r2`, …) para que queden todas. La última es tu entrega.

## Qué se considera un buen resultado

- Toda la prenda indicada cambió de color, sin manchas del color original.
- Caras, pelo, piel, manos, fondo y prendas no indicadas quedaron intactos.
- Se conservan los pliegues y el relieve de la tela; el color no se ve plano ni eléctrico.
- Los bordes no muestran halos.

## Reglas

- Usá `scripts/recolor.py` tal como está: no lo modifiques ni escribas otro script de
  recoloreo. Podés escribir scripts auxiliares para generar vistas previas o recortes.
- No leas nada dentro de `research/pilots/`, `research/outputs/` ni `research/zones/`, ni
  otras configs existentes: tu intento tiene que ser independiente.
- No uses la web ni lances otros agentes.
- Python: `C:\Users\mboth\AppData\Local\Programs\Python\Python313\python.exe`. Corré los
  comandos desde la raíz del repo.

## Qué responder al terminar

Solo esto: cuántas corridas del script hiciste, la ruta de la entrega final, y en una línea
cada defecto que sabés que quedó.
