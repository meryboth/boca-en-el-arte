"""Render a reconstructed GLB from four angles, to look at it before it goes into the room.

    blender --background --python scripts/blender_preview_glb.py -- <model.glb> <out-prefix>

Prints the bounding box, vertex and face counts and the texture sizes, and writes
<out-prefix>__{frente,dorso,costado,planta}.jpg (1280x960, EEVEE, neutral light).
"""
import math
import os
import sys

import bpy
from mathutils import Vector

glb, out = [os.path.abspath(p) for p in sys.argv[sys.argv.index('--') + 1:][:2]]   # Blender resolves relative paths from the drive root
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
pts = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
lo = Vector([min(p[i] for p in pts) for i in range(3)])
hi = Vector([max(p[i] for p in pts) for i in range(3)])
size, mid = hi - lo, (hi + lo) / 2
print('BBOX size', [round(v, 3) for v in size], 'min', [round(v, 3) for v in lo])
print('MESHES', len(meshes), 'verts', sum(len(o.data.vertices) for o in meshes),
      'faces', sum(len(o.data.polygons) for o in meshes))
for im in bpy.data.images:
    print('IMAGE', im.name, tuple(im.size))

sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 1280, 960
sc.render.image_settings.file_format = 'JPEG'
world = bpy.data.worlds.new('W'); sc.world = world; world.use_nodes = True
world.node_tree.nodes['Background'].inputs[0].default_value = (0.75, 0.75, 0.75, 1)
world.node_tree.nodes['Background'].inputs[1].default_value = 1.0
sun = bpy.data.objects.new('Sol', bpy.data.lights.new('Sol', 'SUN')); sc.collection.objects.link(sun)
sun.data.energy = 3.0; sun.rotation_euler = (math.radians(45), 0, math.radians(30))
cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
cam.data.lens = 50
r = max(size) * 1.9
views = {'frente': (0, -r * 0.8, r * 0.55), 'dorso': (0, r * 0.8, r * 0.55),
         'costado': (r * 0.8, 0, r * 0.55), 'planta': (0, -0.001, r * 1.05)}
for name, off in views.items():
    cam.location = mid + Vector(off)
    cam.rotation_euler = (mid - cam.location).to_track_quat('-Z', 'Y').to_euler()
    sc.render.filepath = f'{out}__{name}.jpg'
    bpy.ops.render.render(write_still=True)
