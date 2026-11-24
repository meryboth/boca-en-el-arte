Mensaje con que se lanza cada agente (CASO, COND y K cambian):

Trabajás en el repo C:\Users\mboth\OneDrive\Desktop\teserract. Leé primero estos dos archivos y seguilos al pie de la letra, incluidas las reglas de independencia y el máximo de 4 corridas del script:

1. research/briefs/code-agent-brief.md (el brief)
2. research/briefs/cases/CASO.md (los datos del caso: pintura fuente y cambios de color pedidos)

Datos de esta corrida:
- Config a escribir: research/runs/COND/CASO__COND__sK.json
- Prefijo de salida de cada corrida: research/runs/COND/CASO__COND__sK__r1, luego __r2, etc. (campo "out" de la config; cambialo antes de cada corrida).
- Tus vistas previas y archivos auxiliares van en research/runs/COND/_tmp_CASO_sK/.

Otros agentes trabajan a la vez en la misma carpeta con otros nombres de archivo: no leas ni toques ningún archivo que no sea de esta corrida (CASO, sK), ni los briefs de otros casos. La máquina tiene poca memoria libre: corré el script de a una vez, nunca dos en paralelo. No leas research/pilots/, research/outputs/ ni research/zones/, no modifiques scripts/recolor.py, y respondé al final solo lo que pide el brief.

Solo en la condición code-sinclave se agrega este párrafo:
Restricción de esta corrida: la clave de color va apagada. Usá exactamente esta clave global y ninguna clave por región: "key": {"c_lo": -2, "c_hi": -1, "hue_min": -180, "hue_max": 180}. Con eso el script recolorea todo lo que cae dentro de tus polígonos, así que los polígonos tienen que seguir el borde de cada prenda. No uses "everything_else" ni "fill".
