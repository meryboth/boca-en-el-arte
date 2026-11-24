"""Take the colour texture out of a GLB, or put an edited one back in.

    blender --background --python scripts/blender_glb_textura.py -- extraer <model.glb> <texture.png>
    blender --background --python scripts/blender_glb_textura.py -- poner <model.glb> <texture.png> <out.glb>

Used to paint over marks the reconstruction model copied or invented (crests, sponsor logos).
"""
import os
import sys

import bpy

args = sys.argv[sys.argv.index('--') + 1:]
mode, glb, tex = args[0], os.path.abspath(args[1]), os.path.abspath(args[2])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
colour = next(im for im in bpy.data.images if im.name.startswith('Color'))
if mode == 'extraer':
    colour.filepath_raw = tex; colour.file_format = 'PNG'; colour.save()
    print('TEXTURA', tuple(colour.size), tex)
else:
    new = bpy.data.images.load(tex); new.pack()
    for m in bpy.data.materials:
        if m.use_nodes:
            for n in m.node_tree.nodes:
                if n.type == 'TEX_IMAGE' and n.image == colour:
                    n.image = new
    bpy.ops.export_scene.gltf(filepath=os.path.abspath(args[3]), export_format='GLB')
    print('GLB', args[3])
