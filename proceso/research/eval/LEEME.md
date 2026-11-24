# Evaluación a ciegas

Esta carpeta es todo lo que necesita un evaluador: `index.html` y la carpeta `img/`.
No dice en ningún lado qué método produjo cada imagen. La clave está en `research/eval-key.json`,
**fuera** de esta carpeta: no se la pases a los evaluadores.

## Cómo pasársela a alguien

1. Comprimí la carpeta `eval` entera (unos 28 MB) y mandala.
2. La persona la descomprime y abre `index.html` con doble clic, en cualquier navegador. No necesita internet.
3. Escribe su nombre, responde lo que pueda y al final toca "Descargar mis respuestas".
4. Te manda el archivo `respuestas__<nombre>.json`. Guardalos en `research/eval-respuestas/`.

## Qué se le pide

- **Parte 1 (60 pares):** dos versiones de la misma pintura; elige cuál colgaría. Puede decir "no puedo decidir".
- **Parte 2 (60 imágenes):** una imagen sola; marca dónde ve algo retocado, o dice que no ve nada raro.

Puede parar cuando quiera: el archivo guarda lo que haya respondido. El orden de los pares y cuál va a la
izquierda se sortean para cada persona, y quedan registrados en su archivo.

## Para quien evalúa conociendo el proyecto

Marilyn conoce los métodos y vio resultados: su evaluación se reporta aparte de la de quienes no saben nada,
y no entra en el acuerdo entre evaluadores "ciegos". Lo ideal es que las otras 2 o 3 personas no sepan
qué métodos se comparan ni que uno es de código y otro de un modelo de imagen.

## Límites de esta página

- Las imágenes están a 1600 px de lado mayor. Los defectos que solo se ven al 100 % (halos de 1 o 2 px)
  no se van a notar; eso favorece a quien los tenga.
- Los pares comparan siempre el mismo número de intento de cada método (intento 1 con intento 1). El
  emparejamiento es nominal: los intentos no comparten nada salvo la pintura.
- Es larga: 120 respuestas. Si alguien abandona, la segunda parte queda con menos datos que la primera.
