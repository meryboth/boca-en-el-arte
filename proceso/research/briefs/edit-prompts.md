# Prompts de edición — set de evaluación

**Aprobados por Marilyn el 2026-11-16, con el reparto de colores tal como está. Congelados: cualquier cambio va a "Cambios al protocolo".**
Mismo texto para las 5 semillas de cada caso, sin iterar.

Nodo `GeminiImage2Node`, modelo "Nano Banana 2 (Gemini 3.1 Flash Image)", 4K, aspecto `auto`,
solo imagen, `system_prompt` por defecto. Todos comparten la misma estructura que el prompt del
piloto (`julio2__edit-prompt.md`): primera línea, lista de cambios, y el mismo párrafo final.

Qué prenda pasa a qué color es una **decisión de diseño** que también vale para las condiciones
`code` e `hybrid`: los agentes que escriben las máscaras reciben la misma lista.

Párrafo final común (`{PROTEGER}` cambia por caso):

```
Do not change {PROTEGER}. Keep the original composition, framing, brushwork, lighting, fold shading and the craquelure of the aged paint. Do not add any text, logos, emblems or new objects.
```

## `prato` — Rafael, Madonna del Prato

Idea: el manto ya es azul; solo el vestido rojo pasa a oro.

```
Edit this Renaissance oil painting. Change only the colour of the fabrics, keep everything else exactly as it is.

- The Virgin's red dress becomes golden yellow (#F3B229).
- Her blue mantle stays blue; make it deep royal blue (#103F79) only if it needs to match.

Do not change the faces, hair, skin of the three figures, the grey cloth of the kneeling child, the thin cross, the dark embroidered neckline and trims, the landscape or the sky. Keep the original composition, framing, brushwork, lighting, fold shading and the craquelure of the aged paint. Do not add any text, logos, emblems or new objects.
```

## `arnolfini` — Van Eyck, Matrimonio Arnolfini

Idea: él de azul con franja dorada, ella de oro conservando las mangas azules.

```
Edit this early Netherlandish oil painting. Change only the colour of the fabrics, keep everything else exactly as it is.

- The man's dark purple-brown fur-trimmed tabard becomes deep royal blue (#103F79), with one wide horizontal golden-yellow band (#F3B229) across the chest, following its folds.
- The woman's green gown becomes golden yellow (#F3B229). Her blue sleeves stay blue.

Do not change the faces, hands, the man's black hat, the woman's white headdress, the fur trims, the dog, the mirror, the chandelier, the red bed and hangings, the window, the floor or the shoes. Keep the original composition, framing, brushwork, lighting, fold shading and the craquelure of the aged paint. Do not add any text, logos, emblems or new objects.
```

## `baco` — Tiziano, Baco y Ariadna

Idea: Ariadna ya viste de azul; los paños rosados y rojos se reparten entre azul y oro.

```
Edit this Renaissance oil painting. Change only the colour of the fabrics, keep everything else exactly as it is.

- The pink cloak flying behind the leaping man and the pink cloth at his hips become deep royal blue (#103F79).
- The red sash of the woman on the left becomes golden yellow (#F3B229). Her blue dress stays blue.
- The orange dress of the woman with cymbals becomes golden yellow (#F3B229). Her blue skirt stays blue.
- The reddish drape of the small faun and the red cloth lying on the ground become golden yellow (#F3B229).

Do not change the faces, bodies and skin of any figure, the white cloths, the cheetahs, the dog, the chariot, the trees, the landscape, the sea or the sky. Keep the original composition, framing, brushwork, lighting, fold shading and the craquelure of the aged paint. Do not add any text, logos, emblems or new objects.
```

## `atenas` — Rafael, La escuela de Atenas

Idea: toda la multitud en azul y oro. Es el caso elegido para romper los métodos.

```
Edit this Renaissance fresco. Change only the colour of the robes of the figures, keep everything else exactly as it is.

- Every robe, cloak or tunic that is red, pink, orange, green, purple or brown becomes either deep royal blue (#103F79) or golden yellow (#F3B229).
- Alternate the two colours between neighbouring figures, and between the tunic and the cloak of the same figure, so the whole crowd reads as blue and gold.
- Robes that are already blue or yellow keep their colour. White and grey robes stay as they are.

Do not change the faces, hair, hands and skin of any figure, their poses, the books and objects they hold, the statues, the architecture, the floor, the sky or the painted arch and decoration around the scene. Keep the original composition, framing, brushwork, lighting, fold shading and the surface of the aged fresco. Do not add any text, logos, emblems or new objects.
```

## Para revisar

1. ¿Está bien el reparto de colores de cada cuadro?
2. En `arnolfini` la cama y las cortinas rojas quedan rojas. ¿O las querés cambiar también?
3. En `prato` el cambio es chico (solo el vestido). ¿Alcanza, o sumamos una franja dorada al manto?
4. Ningún prompt pide franja salvo `arnolfini`. La franja horizontal es lo que más dice "Boca";
   se puede pedir en todos, pero el recoloreo por código la dibuja peor que el modelo.
