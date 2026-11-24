"""Print what is inside a frame model: objects, materials and the bounding box of the faces of each material.

    blender --background --python scripts/blender_inspect_marco.py -- museo/assets/marcos/<name>/<name>.gltf
"""
import sys

import bpy
from mathutils import Vector

path = sys.argv[sys.argv.index('--') + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=path)
for o in bpy.context.scene.objects:
    print('MARCO obj', o.name, o.type, 'loc', [round(v, 3) for v in o.location], 'rot', [round(v, 3) for v in o.rotation_euler],
          'scale', [round(v, 3) for v in o.scale], 'parent', o.parent.name if o.parent else None)
    if o.type != 'MESH':
        continue
    mw = o.matrix_world
    by = {}
    for p in o.data.polygons:
        m = o.data.materials[p.material_index].name if o.data.materials else '-'
        b = by.setdefault(m, [Vector((1e9,) * 3), Vector((-1e9,) * 3), 0])
        for vi in p.vertices:
            w = mw @ o.data.vertices[vi].co
            for k in range(3):
                b[0][k] = min(b[0][k], w[k]); b[1][k] = max(b[1][k], w[k])
        b[2] += 1
    for m, (lo, hi, n) in by.items():
        print('MARCO   mat', m, 'caras', n, 'min', [round(v, 4) for v in lo], 'max', [round(v, 4) for v in hi],
              'tam', [round(hi[k] - lo[k], 4) for k in range(3)])
