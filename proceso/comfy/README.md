# Pipelines de ComfyUI

- `museo-xeneize__nb2-mascara-original` — guardado en Comfy Cloud, id `48be1d25-88b3-4792-bd4d-e5ed31198bde`, versión 1.
  Nano Banana 2 viste la pintura de azul y oro; la salida se lleva al tamaño del original y se pega
  solo la zona de ropa (máscara de `scripts/recolor.py`, agrandada 6 px y suavizada) sobre el original.
  Guarda dos imágenes: el combinado y la edición cruda.
  Entradas por caso: la pintura original, la máscara y el prompt del nodo 2.

- `museo-xeneize__bombonera-vistas-a-3d` — guardado en Comfy Cloud, id `ff5dec71-5f8e-4e9f-93bf-7896f11f55ec`, versión 1.
  Cuatro fotos aéreas recortadas entran a Nano Banana 2, que arma una hoja de vistas normalizadas; se recorta
  el panel del frente, se espeja para hacer de dorso y Tripo multivista devuelve el GLB.
  Se corrió en dos etapas (recorte en local); el grafo único no se corrió de punta a punta.
  Detalle y resultados: `research/maqueta3d/BITACORA.md`.
