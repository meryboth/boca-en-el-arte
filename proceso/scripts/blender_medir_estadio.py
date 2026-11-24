"""Measure a reconstructed stadium mesh, to write the building sheet the clean model is built from.

    blender --background --python scripts/blender_medir_estadio.py -- <model.glb> <out.json>

Every vertex takes the colour of the diffuse texture at its UV and is classed as pitch (green), yellow,
blue or other. The pitch gives the origin, the axes and the scale (its long side is taken as 105 m).
In that frame (x along the pitch, y across it, metres) the script writes:

- pitch: length and width as measured, and the scale used;
- outline: outer radius of the building every 3 degrees around the pitch centre;
- inner: radius where the stands start (first point 1.5 m above the pitch), same angles;
- sections: for 8 directions, the highest surface in 1 m steps from the centre outwards (height, colour);
- heights: top of the building per direction, and the height range of the yellow on the outer wall.

It measures a generated mesh, not the building: the numbers carry that model's errors.
"""
import json
import math
import os
import sys

import bpy
import numpy as np

glb, out = [os.path.abspath(p) for p in sys.argv[sys.argv.index('--') + 1:][:2]]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
ob = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
me = ob.data
n = len(me.vertices)
co = np.empty(n * 3, np.float32); me.vertices.foreach_get('co', co); co = co.reshape(n, 3)
M = np.array(ob.matrix_world); co = co @ M[:3, :3].T + M[:3, 3]

nl = len(me.loops)
lv = np.empty(nl, np.int32); me.loops.foreach_get('vertex_index', lv)
uv = np.empty(nl * 2, np.float32); me.uv_layers.active.data.foreach_get('uv', uv); uv = uv.reshape(nl, 2)
vuv = np.zeros((n, 2), np.float32); vuv[lv] = uv
img = next(i for i in bpy.data.images if 'diffuse' in i.name.lower() or i.name.startswith('Color'))
W, H = img.size
px = np.array(img.pixels[:], np.float32).reshape(H, W, 4)
col = px[np.clip((vuv[:, 1] % 1 * H).astype(int), 0, H - 1), np.clip((vuv[:, 0] % 1 * W).astype(int), 0, W - 1), :3]
r, g, b = col[:, 0], col[:, 1], col[:, 2]
green = (g > r * 1.15) & (g > b * 1.15) & (g > 0.12)
yellow = (r > b * 1.5) & (g > b * 1.25) & (r > 0.35)
blue = (b > r * 1.3) & (b > g * 1.05)
kind = np.where(green, 1, np.where(yellow, 2, np.where(blue, 3, 0)))

# pitch frame: centre and axes from the green vertices that lie low
gz = np.median(co[green, 2])
pitch = green & (np.abs(co[:, 2] - gz) < 0.02 * np.ptp(co[:, 2]) + 0.01)
P = co[pitch, :2]; c = np.median(P, axis=0)
_, _, vt = np.linalg.svd(P - c, full_matrices=False)
ax = vt[0] / np.linalg.norm(vt[0]); ay = np.array([-ax[1], ax[0]])
u = (P - c) @ ax; v = (P - c) @ ay
lo_u, hi_u = np.percentile(u, [1, 99]); lo_v, hi_v = np.percentile(v, [1, 99])
c = c + ax * (lo_u + hi_u) / 2 + ay * (lo_v + hi_v) / 2
k = 105.0 / (hi_u - lo_u)                                   # metres per model unit
X = ((co[:, :2] - c) @ ax) * k; Y = ((co[:, :2] - c) @ ay) * k; Z = (co[:, 2] - gz) * k
R = np.hypot(X, Y); A = np.degrees(np.arctan2(Y, X)) % 360

res = {'source': os.path.basename(glb), 'scale_m_per_unit': round(float(k), 3),
       'pitch': {'length_m': 105.0, 'width_m_measured': round(float((hi_v - lo_v) * k), 1)},
       'bbox_m': {'x': [round(float(X.min()), 1), round(float(X.max()), 1)],
                  'y': [round(float(Y.min()), 1), round(float(Y.max()), 1)], 'z_max': round(float(Z.max()), 1)},
       'outline': [], 'inner': [], 'top': [], 'sections': {}}
for a in range(0, 360, 3):
    m = np.abs((A - a + 180) % 360 - 180) < 1.5
    if not m.any():
        res['outline'].append(None); res['inner'].append(None); res['top'].append(None); continue
    res['outline'].append(round(float(np.percentile(R[m], 99.5)), 1))
    up = m & (Z > 1.5)
    res['inner'].append(round(float(np.percentile(R[up], 0.5)), 1) if up.any() else None)
    res['top'].append(round(float(np.percentile(Z[m], 99.5)), 1))
names = {0: '-', 1: 'G', 2: 'Y', 3: 'B'}
for a in range(0, 360, 45):
    m = np.abs((A - a + 180) % 360 - 180) < 4
    prof = []
    for rr in range(0, 140):
        s = m & (R >= rr) & (R < rr + 1)
        if not s.any():
            prof.append(None); continue
        top = s & (Z >= np.percentile(Z[s], 90))
        prof.append([round(float(np.percentile(Z[s], 95)), 1), names[int(np.bincount(kind[top], minlength=4).argmax())]])
    while prof and prof[-1] is None:
        prof.pop()
    res['sections'][str(a)] = prof
wall = yellow & (R > np.interp(A, np.arange(0, 360, 3), [o or 0 for o in res['outline']]) - 4)
if wall.any():
    res['yellow_on_outer_wall_z'] = [round(float(v), 1) for v in np.percentile(Z[wall], [5, 50, 95])]
res['axis_note'] = 'x along the pitch, y across; angle 0 = +x (one end), 90 = +y'
json.dump(res, open(out, 'w'), indent=1)
print('MEDIDO', res['scale_m_per_unit'], res['pitch'], res['bbox_m'])
