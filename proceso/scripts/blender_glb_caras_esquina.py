"""List the UV triangles of the faces on the lower panel of the four corner towers of the reconstructed stadium.

    blender --background --python scripts/blender_glb_caras_esquina.py -- <model.glb> <out.json>

The reconstruction put a crest and a sponsor mark there; tapar_logos.py paints them over.
A face is taken when it lies within 5 degrees of a corner diagonal, on the outer surface, in the lower band.
"""
import json, math, os, sys
import bpy

glb, out = [os.path.abspath(p) for p in sys.argv[sys.argv.index('--') + 1:][:2]]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
ob = next(o for o in bpy.context.scene.objects if o.type == 'MESH')
me, M = ob.data, ob.matrix_world
uv = me.uv_layers.active.data
cs = [M @ p.center for p in me.polygons]
diag = [math.atan2(sy * 0.457, sx * 0.5) for sx in (-1, 1) for sy in (-1, 1)]
def near(c):
    a = math.atan2(c.y, c.x)
    return min(abs((a - d + math.pi) % (2 * math.pi) - math.pi) for d in diag) < math.radians(5)
cand = [i for i, c in enumerate(cs) if near(c) and -0.075 < c.z < -0.012]
rmax = max(math.hypot(cs[i].x, cs[i].y) for i in cand)
tris = [[list(uv[l].uv) for l in me.polygons[i].loop_indices] for i in cand
        if math.hypot(cs[i].x, cs[i].y) > rmax - 0.05]
json.dump(tris, open(out, 'w'))
print('CARAS', len(tris), 'rmax', round(rmax, 3))
