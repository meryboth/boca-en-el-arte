# Boca en el arte — Museo Xeneize

Un museo imaginario: pinturas clásicas con la ropa de azul y oro, colgadas en una sala que se recorre con el scroll.

**Proyecto no oficial.** No tiene relación con ningún club. No usa escudos, marcas, sponsors ni nombres de jugadores.

## Cómo verlo

Es un sitio estático: `index.html` más imágenes y un video. No necesita instalar nada ni compilar.

```
python -m http.server 8000
```

y abrir http://localhost:8000. También se puede publicar tal cual en cualquier hosting de archivos estáticos.

## Qué hay

- `index.html` — la página completa.
- `frames/` — el recorrido de la sala, cuadro por cuadro.
- `paradas/` — una imagen de alta resolución por cada obra.
- `obras/` — las obras solas, para verlas en grande.
- `intro.mp4` — el video de la portada (sin sonido).

## Créditos

- Las pinturas originales están en dominio público (vía Wikimedia Commons). Acá aparecen intervenidas: solo se cambió el color de las telas.
- Marcos: Poly Haven, CC0.
- La maqueta del estadio se modeló tomando como referencia fotos aéreas de ProtoplasmaKid (Wikimedia Commons, CC BY-SA 4.0).
