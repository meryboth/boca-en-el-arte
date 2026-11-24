"""Build the museum room in Blender from the selection of works, and render stills or the walkthrough.

    blender --background --python scripts/blender_sala.py -- [--seleccion museo/seleccion.json]
            [--stills] [--anim] [--res 1600x900] [--samples 64] [--step 1]

Reads the selection (falls back to a provisional one), hangs each work on alternating side walls with the
widest one on the end wall, lights each with a ceiling spot, and animates a camera that stops in front of
every work. Always saves museo/sala.blend (textures packed) and museo/sala.json (layout and frame ranges
of each stop, for the web page). --stills renders one frame per stop to museo/render/stills/;
--anim renders the frame sequence to museo/render/frames/.
"""
import argparse
import json
import math
import os
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = os.getcwd()
TITLES = {'prato': ('Madonna del Prato', 'Rafael, 1505–06'), 'arnolfini': ('Matrimonio Arnolfini', 'Jan van Eyck, 1434'),
          'baco': ('Baco y Ariadna', 'Tiziano, 1520–23'), 'atenas': ('La escuela de Atenas', 'Rafael, 1509–11'),
          'julio2': ('Retrato de Julio II', 'Rafael, 1511'), 'armino': ('La dama del armiño', 'Leonardo da Vinci, c. 1490'),
          'gioconda': ('La Gioconda', 'Leonardo da Vinci, c. 1503–19'), 'enrique8': ('Enrique VIII', 'Taller de Hans Holbein el Joven, c. 1540–47'), 'castiglione': ('Retrato de Baltasar Castiglione', 'Rafael, c. 1515'),
          'eleonora': ('Eleonora de Toledo con su hijo', 'Bronzino, c. 1545'), 'embajadores': ('Los embajadores', 'Hans Holbein el Joven, 1533')}
METHOD = {'code': 'Recoloreo por código (Fable 5.2)', 'edit': 'Edición con Nano Banana 2', 'hybrid': 'Combinado'}
W_ROOM, H_ROOM = 7.0, 4.2          # metres
SPACING, MARGIN = 5.6, 3.6
EYE = 1.6
HOLD, TRAVEL, FPS = 36, 96, 24
FLOOR_ROT = 90                       # degrees; 90 turns the boards across the room


def provisional():
    key = json.load(open(os.path.join(ROOT, 'research/eval-key.json'), encoding='utf-8'))['images']
    want = [('prato', 'hybrid', 1), ('arnolfini', 'hybrid', 1), ('baco', 'code', 1), ('atenas', 'code', 1)]
    obras = []
    for iid, v in key.items():
        if (v['case'], v['condition'], v['seed']) in want:
            obras.append({'id': iid, 'pintura': v['case'], 'metodo': v['condition'], 'fuente': v['source']})
    obras.append({'id': 'julio2__hybrid-a__sin-sillon', 'pintura': 'julio2', 'metodo': 'hybrid',
                  'fuente': 'museo/obras/julio2__hybrid-a__sin-sillon.jpg'})
    return obras


def mat(name, color, rough=0.6, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    return m


def box(name, center, size, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=center)
    o = bpy.context.active_object; o.name = name; o.scale = size; o.data.materials.append(material)
    return o


def quad(name, c, right, w, h, material):
    up = Vector((0, 0, 1)); r = Vector(right)
    v = [c - r * w / 2 - up * h / 2, c + r * w / 2 - up * h / 2, c + r * w / 2 + up * h / 2, c - r * w / 2 + up * h / 2]
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(p) for p in v], [], [(0, 1, 2, 3)])
    uv = me.uv_layers.new(name='UVMap')
    for i, co in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[i].uv = co
    me.update(); me.materials.append(material)
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o)
    return o


def image_mat(name, path):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = bpy.data.images.load(path)
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.55
    return m, tex.image


# Scanned frames from Poly Haven (CC0). Model axes: X right, Z up, front faces -Y. Sizes in the model's metres.
MARCOS = {
    'fancy_picture_frame_02': {'open': (0.392, 0.4995), 'centre': (0.0, -0.00415), 'outer': (0.6606, 0.771),
                               'y_back': -0.0013, 'y_canvas': -0.0093},
    'fancy_picture_frame_01': {'open': (0.5394, 0.4003), 'centre': (-0.0004, -0.001), 'outer': (0.603, 0.4641),
                               'y_back': -0.0019, 'y_canvas': -0.0066},
}
_MARCO_MESH = {}


def marco_mesh(name):
    if name not in _MARCO_MESH:
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=os.path.join(ROOT, f'museo/assets/marcos/{name}/{name}.gltf'))
        for ob in set(bpy.data.objects) - before:
            if ob.type == 'MESH' and not ob.name.endswith('_canvas'):
                _MARCO_MESH[name] = ob.data
            bpy.data.objects.remove(ob)
    return _MARCO_MESH[name]


def scanned_frame(o, c, n, r, which):
    """Hang a scanned frame around the work. The frame is scaled so its opening matches the canvas; when the
    work is closer to the frame turned on its side, it is rotated 90 degrees. Returns outer width, outer
    height, the point where the canvas goes, and what was done (for the layout file)."""
    up = Vector((0, 0, 1)); f = MARCOS[which]
    ow, oh = f['open']
    a = o['w'] / o['h']
    turned = abs(math.log(a / (oh / ow))) < abs(math.log(a / (ow / oh)))
    from mathutils import Matrix
    if not turned:
        sx, sz = o['w'] / ow, o['h'] / oh
        cols = (r * sx, None, up * sz); outer = (f['outer'][0] * sx, f['outer'][1] * sz)
        centre = Vector((f['centre'][0], 0, f['centre'][1]))
    else:
        s1, s2 = o['h'] / ow, o['w'] / oh            # model X runs up the wall, model Z runs along it
        cols = (up * s1, None, -r * s2); outer = (f['outer'][1] * s2, f['outer'][0] * s1)
        sx, sz = s1, s2
        centre = Vector((f['centre'][0], 0, f['centre'][1]))
    sy = (sx + sz) / 2
    X, Z = cols[0], cols[2]; Y = -n * sy
    M = Matrix(((X.x, Y.x, Z.x, 0), (X.y, Y.y, Z.y, 0), (X.z, Y.z, Z.z, 0), (0, 0, 0, 1)))
    wall = c - n * 0.06
    origin = wall - (M.to_3x3() @ Vector((centre.x, f['y_back'], centre.z)))
    M.translation = origin
    ob = bpy.data.objects.new('Marco_' + o['id'], marco_mesh(which)); bpy.context.collection.objects.link(ob)
    ob.matrix_world = M
    canvas_at = wall + n * ((f['y_back'] - f['y_canvas']) * sy + 0.003)
    info = {'modelo': which, 'girado': turned, 'estirado': round(max(sx, sz) / min(sx, sz), 3)}
    return outer[0], outer[1], canvas_at, info


_CUBE = {}


def brick(name, matrix, material_name, mats):
    """A unit cube placed by a matrix, sharing one mesh per material: cheap for the hundreds of pieces of the model."""
    if material_name not in _CUBE:
        bpy.ops.mesh.primitive_cube_add(size=1)
        base = bpy.context.active_object; me = base.data; me.materials.append(mats[material_name])
        bpy.data.objects.remove(base); _CUBE[material_name] = me
    o = bpy.data.objects.new(name, _CUBE[material_name]); bpy.context.collection.objects.link(o)
    o.matrix_world = matrix
    return o


def aim(obj, target):
    obj.rotation_euler = (Vector(target) - obj.location).to_track_quat('-Z', 'Y').to_euler()


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument('--seleccion', default='museo/seleccion.json')
    ap.add_argument('--stills', action='store_true'); ap.add_argument('--anim', action='store_true')
    ap.add_argument('--res', default='1600x900'); ap.add_argument('--res-stills', default='2880x1620'); ap.add_argument('--samples', type=int, default=64)
    ap.add_argument('--step', type=int, default=1)
    ap.add_argument('--tex-max', type=int, default=0, help='shrink every texture to this many px on its long side (for renderers short of memory)')
    ap.add_argument('--blend-out', default='museo/sala.blend')
    ap.add_argument('--piso', default='cemento', choices=['cemento', 'cemento-oscuro', 'cemento-claro', 'deck'])
    ap.add_argument('--solo', default='', help='render only the stills whose id contains this text')
    ap.add_argument('--sufijo', default='')
    ap.add_argument('--maqueta', default='limpia', choices=['limpia', 'tripo', 'codigo'], help='clean model from the building sheet, reconstructed GLB, or the first model built from cubes')
    ap.add_argument('--maqueta-giro', type=float, default=180.0, help='turn of the reconstructed model about the vertical, in degrees')
    a = ap.parse_args(argv)

    sel_path = os.path.join(ROOT, a.seleccion)
    if os.path.exists(sel_path):
        obras = json.load(open(sel_path, encoding='utf-8'))['obras']; origen = a.seleccion
    else:
        obras = provisional(); origen = 'provisional (no hay museo/seleccion.json)'
    print('SALA seleccion:', origen, len(obras), 'obras')

    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    try:                                           # sharper textures at grazing angles and in the paintings
        bpy.context.preferences.system.anisotropic_filter = 'FILTER_16'
    except Exception as e:
        print('SALA aviso anisotropico', e)
    world = bpy.data.worlds.new('Mundo'); sc.world = world; world.use_nodes = True
    bg = world.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.75, 0.78, 0.85, 1)
    bg.inputs['Strength'].default_value = 0.1

    m_wall = mat('Pared', (0.55, 0.53, 0.5), 0.92); m_ceil = mat('Techo', (0.9, 0.9, 0.88), 0.95)
    m_floor = mat('Piso', (0.19, 0.12, 0.075), 0.32); m_skirt = mat('Zocalo', (0.07, 0.065, 0.06), 0.5)
    m_gold = mat('Marco', (0.62, 0.43, 0.15), 0.38, 1.0); m_liner = mat('Filete', (0.05, 0.04, 0.035), 0.6); m_bench = mat('Banco', (0.11, 0.1, 0.095), 0.6)
    m_card = mat('Cartel', (0.93, 0.92, 0.9), 0.8)
    try:                                           # fine grain on the gilding so it does not read as plastic
        gt = m_gold.node_tree; gb = gt.nodes['Principled BSDF']
        noise = gt.nodes.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 90.0
        noise.inputs['Detail'].default_value = 6.0
        bump = gt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.22
        gt.links.new(noise.outputs['Fac'], bump.inputs['Height']); gt.links.new(bump.outputs['Normal'], gb.inputs['Normal'])
    except Exception as e:
        print('SALA aviso dorado', e)
    # Boca: blue #103F79 and gold #F3B229 in scene-linear values; bare concrete as in a stadium
    m_blue = mat('Azul', (0.0052, 0.0497, 0.1912), 0.7); m_oro = mat('Oro', (0.8963, 0.4452, 0.0222), 0.55)
    m_conc = mat('Hormigon', (0.3, 0.3, 0.29), 0.95); m_seat = mat('Butaca', (0.0052, 0.0497, 0.1912), 0.35)
    m_led = mat('Led', (0.6, 0.75, 1.0), 0.5)
    try:
        lb = m_led.node_tree.nodes['Principled BSDF']
        lb.inputs['Emission Color'].default_value = (0.6, 0.78, 1.0, 1); lb.inputs['Emission Strength'].default_value = 8.0
    except Exception as e:
        print('SALA aviso led', e)
    nt = m_floor.node_tree; b = nt.nodes['Principled BSDF']
    if a.piso == 'deck':
        # wood deck from a scanned texture (Poly Haven, CC0), laid along the room and repeated every 2 m
        pdir = os.path.join(ROOT, 'museo/assets/piso/wood_floor_deck')
        geo = nt.nodes.new('ShaderNodeNewGeometry'); mp = nt.nodes.new('ShaderNodeMapping')
        mp.inputs['Scale'].default_value = (0.5, 0.5, 0.5); mp.inputs['Rotation'].default_value = (0, 0, math.radians(FLOOR_ROT))
        nt.links.new(geo.outputs['Position'], mp.inputs['Vector'])

        def tex(name, non_color):
            n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(os.path.join(pdir, name))
            if non_color:
                n.image.colorspace_settings.name = 'Non-Color'
            nt.links.new(mp.outputs['Vector'], n.inputs['Vector'])
            return n

        td = tex('wood_floor_deck_diff_2k.jpg', False); tr = tex('wood_floor_deck_rough_2k.jpg', True)
        tn = tex('wood_floor_deck_nor_gl_2k.jpg', True)
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = 1.0
        nt.links.new(td.outputs['Color'], b.inputs['Base Color']); nt.links.new(tr.outputs['Color'], b.inputs['Roughness'])
        nt.links.new(tn.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], b.inputs['Normal'])
    else:
        # smooth polished concrete: large soft mottling, fine grain, and gloss that varies with it
        big = nt.nodes.new('ShaderNodeTexNoise'); big.inputs['Scale'].default_value = 0.9
        big.inputs['Detail'].default_value = 8.0; big.inputs['Roughness'].default_value = 0.62
        fine = nt.nodes.new('ShaderNodeTexNoise'); fine.inputs['Scale'].default_value = 55.0; fine.inputs['Detail'].default_value = 4.0
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        tone = {'cemento': ((0.2, 0.2, 0.195, 1), (0.34, 0.335, 0.325, 1)), 'cemento-oscuro': ((0.07, 0.07, 0.072, 1), (0.14, 0.14, 0.142, 1)),
                'cemento-claro': ((0.42, 0.41, 0.39, 1), (0.6, 0.59, 0.56, 1))}[a.piso]
        ramp.color_ramp.elements[0].position = 0.3; ramp.color_ramp.elements[0].color = tone[0]
        ramp.color_ramp.elements[1].position = 0.75; ramp.color_ramp.elements[1].color = tone[1]
        rr = nt.nodes.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.16; rr.inputs['To Max'].default_value = 0.36
        bump = nt.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = 0.04
        nt.links.new(big.outputs['Fac'], ramp.inputs['Fac']); nt.links.new(ramp.outputs['Color'], b.inputs['Base Color'])
        nt.links.new(big.outputs['Fac'], rr.inputs['Value']); nt.links.new(rr.outputs['Result'], b.inputs['Roughness'])
        nt.links.new(fine.outputs['Fac'], bump.inputs['Height']); nt.links.new(bump.outputs['Normal'], b.inputs['Normal'])

    # sizes from the image files, then layout: widest work on the end wall, the rest alternate sides
    for o in obras:
        mt, img = image_mat('Obra_' + o['id'], os.path.join(ROOT, o['fuente']))
        o['_mat'] = mt; o['aspect'] = img.size[0] / img.size[1]
        h = 1.2; w = h * o['aspect']
        if w > 3.4:
            w = 3.4; h = w / o['aspect']
        o['w'], o['h'] = w, h
    end = max(obras, key=lambda o: o['aspect']) if len(obras) > 2 else None
    if end:
        end['h'] = 2.3; end['w'] = end['h'] * end['aspect']
        if end['w'] > 4.0:
            end['w'] = 4.0; end['h'] = end['w'] / end['aspect']
    side = [o for o in obras if o is not end]
    n_side = len(side)
    L = MARGIN * 2 + SPACING * max(n_side - 1, 1) / 1 * 0.5 + 2.5
    L = max(L, 10.0) + 6.5                       # room at the end for the model of the stadium
    yT = L - 6.0
    cz = 1.75
    for i, o in enumerate(side):
        left = i % 2 == 0
        y = MARGIN + i * SPACING * 0.5
        o['wall'] = 'izquierda' if left else 'derecha'
        o['c'] = Vector((-W_ROOM / 2 + 0.06 if left else W_ROOM / 2 - 0.06, y, cz))
        o['right'] = (0, 1, 0) if left else (0, -1, 0); o['n'] = Vector((1, 0, 0)) if left else Vector((-1, 0, 0))
    if end:
        end['wall'] = 'fondo'; end['c'] = Vector((0, L - 0.06, cz + 0.3)); end['right'] = (1, 0, 0); end['n'] = Vector((0, -1, 0))
    order = sorted(side, key=lambda o: o['c'].y) + ([end] if end else [])

    t = 0.2
    box('Piso', (0, L / 2, -t / 2), (W_ROOM + 2 * t, L + 2 * t, t), m_floor)
    box('Techo', (0, L / 2, H_ROOM + t / 2), (W_ROOM + 2 * t, L + 2 * t, t), m_ceil)
    box('ParedIzq', (-W_ROOM / 2 - t / 2, L / 2, H_ROOM / 2), (t, L + 2 * t, H_ROOM), m_wall)
    box('ParedDer', (W_ROOM / 2 + t / 2, L / 2, H_ROOM / 2), (t, L + 2 * t, H_ROOM), m_wall)
    box('ParedFondo', (0, L + t / 2, H_ROOM / 2), (W_ROOM, t, H_ROOM), m_blue)       # end wall: blue with the gold band
    box('FranjaFondo', (0, L - 0.012, 0.56), (W_ROOM, 0.024, 0.12), m_oro)
    # players' tunnel: the visit starts inside it and comes out into the room
    TW, TH, TL = 2.6, 2.7, 5.0
    side_w = (W_ROOM - TW) / 2
    for sx in (-1, 1):
        box('ParedEntrada', (sx * (TW / 2 + side_w / 2), -t / 2, H_ROOM / 2), (side_w, t, H_ROOM), m_wall)
        box('TunelPared', (sx * (TW / 2 + t / 2), -TL / 2, TH / 2), (t, TL, TH), m_blue)
        box('TunelLed', (sx * (TW / 2 - 0.08), -TL / 2, TH - 0.06), (0.05, TL - 0.4, 0.05), m_led)
    box('ParedEntradaDintel', (0, -t / 2, (H_ROOM + TH) / 2), (TW, t, H_ROOM - TH), m_wall)
    box('TunelPiso', (0, -TL / 2, -t / 2), (TW, TL, t), m_conc)
    box('TunelTecho', (0, -TL / 2, TH + t / 2), (TW + 2 * t, TL, t), m_conc)
    box('TunelFondo', (0, -TL - t / 2, TH / 2), (TW + 2 * t, t, TH), m_conc)
    for ty in (-1.2, -3.6):
        tl = bpy.data.lights.new('TunelLuz', 'AREA'); tl.energy = 55; tl.size = 1.2; tl.color = (0.7, 0.82, 1.0)
        to = bpy.data.objects.new('TunelLuz', tl); bpy.context.collection.objects.link(to); to.location = (0, ty, TH - 0.05)
    # the shirt as architecture: blue base with the gold band running along both side walls
    for sx in (-1, 1):
        box('BaseAzul', (sx * (W_ROOM / 2 - 0.012), L / 2, 0.25), (0.024, L, 0.5), m_blue)
        box('FranjaOro', (sx * (W_ROOM / 2 - 0.014), L / 2, 0.56), (0.028, L, 0.12), m_oro)
    # stadium structure: concrete beams across the ceiling and pilasters between the works
    y = MARGIN - SPACING * 0.25
    while y < L - 0.8:
        box('Viga', (0, y, H_ROOM - 0.19), (W_ROOM, 0.32, 0.38), m_conc)
        for sx in (-1, 1):
            box('Pilastra', (sx * (W_ROOM / 2 - 0.07), y, H_ROOM / 2), (0.14, 0.32, H_ROOM), m_conc)
        y += SPACING * 0.5
    # benches as rows of stand seats on a concrete step
    for k, y in enumerate([MARGIN + 1.1 + j * 4.4 for j in range(int((L - 2 * MARGIN) // 4.4) + 1)]):
        if y > yT - 2.6:
            continue
        face = 1 if k % 2 == 0 else -1
        box('Grada', (0, y, 0.15), (0.62, 1.9, 0.3), m_conc)
        for j in (-1, 0, 1):
            box('Butaca', (0.03 * face, y + j * 0.6, 0.345), (0.46, 0.5, 0.09), m_seat)
            box('Respaldo', (-0.22 * face, y + j * 0.6, 0.56), (0.07, 0.5, 0.42), m_seat)
            box('ButacaFilo', (-0.22 * face, y + j * 0.6, 0.785), (0.075, 0.5, 0.03), m_oro)

    for o in order:
        c, n, r = o['c'], o['n'], Vector(o['right'])
        fw, fh, canvas_at, o['marco'] = scanned_frame(o, c, n, r, 'fancy_picture_frame_01' if o is end else 'fancy_picture_frame_02')
        o['fw'], o['fh'] = fw, fh
        quad('Lienzo_' + o['id'], canvas_at, r, o['w'], o['h'], o['_mat'])
        cc = c + r * (fw / 2 + 0.22) + Vector((0, 0, -o['h'] / 2 + 0.12)) - n * 0.05
        box('Cartel_' + o['id'], cc, (0.012, 0.2, 0.13) if abs(n.x) > 0 else (0.2, 0.012, 0.13), m_card)
        ld = bpy.data.lights.new('Spot_' + o['id'], 'SPOT'); ld.energy = 620; ld.spot_size = math.radians(52)
        ld.spot_blend = 0.75; ld.color = (1.0, 0.93, 0.84); ld.shadow_soft_size = 0.12
        lo = bpy.data.objects.new('Spot_' + o['id'], ld); bpy.context.collection.objects.link(lo)
        lo.location = c + n * 1.9 + Vector((0, 0, H_ROOM - 0.25 - c.z)); aim(lo, c)
    # one skylight per bay, so the room keeps the same light however long it gets
    y = MARGIN
    while y < L - 0.5:
        sky = bpy.data.lights.new('Lucernario', 'AREA'); sky.energy = 60; sky.shape = 'RECTANGLE'
        sky.size = 1.6; sky.size_y = 1.5; sky.color = (0.92, 0.95, 1.0)
        try:
            sky.use_shadow = False              # soft fill light; keeps the shadow budget for the spots
        except Exception:
            pass
        so = bpy.data.objects.new('Lucernario', sky); bpy.context.collection.objects.link(so)
        so.location = (0, y, H_ROOM - 0.42)
        y += SPACING * 0.5

    # the model of the stadium, on a table near the end of the room, with its own light
    m_table = mat('Mesa', (0.035, 0.03, 0.028), 0.45); m_grass = mat('Cesped', (0.03, 0.2, 0.04), 0.9)
    m_white = mat('Blanco', (0.8, 0.8, 0.78), 0.6)
    box('MesaTapa', (0, yT, 0.86), (2.2, 1.75, 0.06), m_table)
    box('MesaPie', (0, yT, 0.42), (1.7, 1.3, 0.83), m_table)
    m_grass2 = mat('Cesped2', (0.022, 0.15, 0.03), 0.9); m_glass = mat('Vidrio', (0.004, 0.012, 0.035), 0.12)
    sys.path.insert(0, os.path.join(ROOT, 'scripts'))
    glb = os.path.join(ROOT, 'research/maqueta3d/modelo/bombonera__tripo__frente-nb2__s42__sin-logos.glb')
    if a.maqueta == 'limpia':
        # the clean model built from the building sheet (scripts/maqueta_limpia.py)
        import maqueta_limpia
        maqueta_limpia.build(0, yT, 0.89, 1.95, {
            'azul': m_blue, 'oro': m_oro, 'blanco': m_white, 'cesped': m_grass, 'cesped2': m_grass2,
            'hormigon': m_conc, 'vidrio': m_glass, 'azul_claro': mat('AzulClaro', (0.035, 0.1, 0.3), 0.6),
            'azul_oscuro': mat('AzulOscuro', (0.006, 0.016, 0.055), 0.5)}, a.maqueta_giro)
    elif a.maqueta == 'tripo' and os.path.exists(glb):
        # the model reconstructed from images (research/maqueta3d/BITACORA.md), scaled to 1.9 m on its long side
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=glb)
        new = [o for o in bpy.data.objects if o not in before]
        pts = [o.matrix_world @ Vector(c) for o in new if o.type == 'MESH' for c in o.bound_box]
        lo = Vector([min(p[i] for p in pts) for i in range(3)]); hi = Vector([max(p[i] for p in pts) for i in range(3)])
        k = 1.9 / max(hi.x - lo.x, hi.y - lo.y)
        pivot = bpy.data.objects.new('Maqueta', None); bpy.context.collection.objects.link(pivot)
        for o in new:
            if o.parent is None:
                o.parent = pivot
        pivot.scale = (k, k, k); pivot.rotation_euler = (0, 0, math.radians(a.maqueta_giro))
        pivot.location = (0, yT, 0.91 - lo.z * k)
        rot = Matrix.Rotation(math.radians(a.maqueta_giro), 4, 'Z')
        ext = [rot @ Vector((sx * (hi.x - lo.x) / 2 * k, sy * (hi.y - lo.y) / 2 * k, 0)) for sx in (-1, 1) for sy in (-1, 1)]
        box('MaquetaBase', (0, yT, 0.9), (2 * max(abs(v.x) for v in ext) + 0.08, 2 * max(abs(v.y) for v in ext) + 0.08, 0.02), m_conc)
    else:
        import maqueta_bombonera
        maqueta_bombonera.build(brick, 0, yT + 0.1, 0.89, {'azul': m_blue, 'oro': m_oro, 'blanco': m_white,
                                'cesped': m_grass, 'cesped2': m_grass2, 'hormigon': m_conc, 'vidrio': m_glass,
                                'hormigon_claro': mat('HormigonClaro', (0.5, 0.49, 0.46), 0.9)})
    for sx in (-1, 1):
        ml = bpy.data.lights.new('MaquetaLuz', 'SPOT'); ml.energy = 380; ml.spot_size = math.radians(60); ml.spot_blend = 0.6
        ml.color = (1.0, 0.95, 0.88)
        mo = bpy.data.objects.new('MaquetaLuz', ml); bpy.context.collection.objects.link(mo)
        mo.location = (sx * 1.2, yT - 0.6, H_ROOM - 0.5); aim(mo, (0, yT, 0.95))

    cam_d = bpy.data.cameras.new('Camara'); cam_d.lens = 24; cam_d.sensor_width = 36
    cam = bpy.data.objects.new('Camara', cam_d); bpy.context.collection.objects.link(cam); sc.camera = cam
    body = bpy.data.objects.new('Visitante', None); bpy.context.collection.objects.link(body); cam.parent = body
    tgt = bpy.data.objects.new('Mirada', None); bpy.context.collection.objects.link(tgt)
    con = cam.constraints.new('TRACK_TO'); con.target = tgt; con.track_axis = 'TRACK_NEGATIVE_Z'; con.up_axis = 'UP_Y'

    stops = [{'id': 'tunel', 'cam': Vector((0, -4.2, EYE)), 'tgt': Vector((0, L, EYE + 0.15))},
             {'id': 'entrada', 'cam': Vector((0, 1.4, EYE)), 'tgt': Vector((0, L, EYE + 0.15))}]
    for o in order:
        if o is end:
            stops.append({'id': 'maqueta', 'cam': Vector((-1.75, yT + 1.75, 2.0)), 'tgt': Vector((0.1, yT - 0.05, 1.08)),
                          'keep_x': True, 'titulo': 'La Bombonera', 'autor': 'Maqueta'})
        dist = max(2.6, o['fw'] * 0.95)
        dist = min(dist, (W_ROOM - 0.9) if abs(o['n'].x) > 0 else 6.5)
        p = o['c'] + o['n'] * dist; p.z = EYE
        stops.append({'id': o['id'], 'cam': p, 'tgt': o['c'].copy()})
    def key(fr, c, g):
        body.location = c; tgt.location = g
        body.keyframe_insert('location', frame=fr); tgt.keyframe_insert('location', frame=fr)

    def bob(fr, dz):
        cam.location = (0, 0, dz); cam.keyframe_insert('location', frame=fr)

    f = 1
    for i, s in enumerate(stops):
        s['frame_in'] = f
        key(f, s['cam'], s['tgt']); key(f + HOLD, s['cam'], s['tgt'])
        bob(f, 0.0); bob(f + HOLD, 0.0)
        s['frame_out'] = f + HOLD
        if i + 1 < len(stops):
            # walk like a visitor: turn away from the work, look down the room, walk, then turn to the next one
            A, B = s, stops[i + 1]
            dy = B['cam'].y - A['cam'].y
            ahead = Vector((0, B['cam'].y + 6.0, EYE - 0.1))
            c1 = Vector((A['cam'].x * 0.3, A['cam'].y + dy * 0.3, EYE))
            c2 = Vector((B['cam'].x * 0.3, A['cam'].y + dy * 0.72, EYE))
            if A.get('keep_x'):                    # leave the table by its side instead of across it
                c1 = Vector((A['cam'].x, A['cam'].y + dy * 0.45, EYE)); c2 = Vector((A['cam'].x * 0.55, A['cam'].y + dy * 0.8, EYE))
            if B.get('keep_x'):                    # and arrive at it from the same side
                c2 = Vector((B['cam'].x, A['cam'].y + dy * 0.7, EYE))
            key(f + HOLD + TRAVEL // 3, c1, ahead)
            key(f + HOLD + 2 * TRAVEL // 3, c2, ahead.lerp(B['tgt'], 0.5))
            steps = 8                              # footsteps: a small rise and fall while walking, none while standing
            for k in range(1, steps):
                bob(f + HOLD + round(k * TRAVEL / steps), 0.022 if k % 2 else -0.012)
        f += HOLD + TRAVEL
    sc.frame_start = 1; sc.frame_end = stops[-1]['frame_out']; sc.render.fps = FPS

    rw, rh = (int(v) for v in a.res.split('x'))
    sc.render.engine = 'BLENDER_EEVEE'; sc.render.resolution_x = rw; sc.render.resolution_y = rh
    ee = sc.eevee
    for attr, val in (('shadow_pool_size', '1024'), ('taa_render_samples', a.samples), ('use_raytracing', True), ('use_shadows', True),
                      ('use_gtao', True), ('use_soft_shadows', True)):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except Exception as e:
                print('SALA aviso eevee', attr, e)
    try:
        sc.view_settings.look = 'AgX - Medium High Contrast'
    except Exception as e:
        print('SALA aviso look', e)

    os.makedirs(os.path.join(ROOT, 'museo/render/stills'), exist_ok=True)
    os.makedirs(os.path.join(ROOT, 'museo/render/frames'), exist_ok=True)
    layout = {'seleccion': origen, 'sala': {'ancho_m': W_ROOM, 'largo_m': round(L, 2), 'alto_m': H_ROOM},
              'fps': FPS, 'frames': sc.frame_end, 'resolucion': a.res, 'paradas': []}
    for s in stops:
        o = next((x for x in order if x['id'] == s['id']), None)
        p = {'id': s['id'], 'frame_in': s['frame_in'], 'frame_out': s['frame_out'],
             'still': f'museo/render/stills/parada_{stops.index(s):02d}_{s["id"]}.jpg'}
        if s.get('titulo'):
            p.update({'titulo': s['titulo'], 'autor': s['autor']})
        if o:
            ti = TITLES.get(o['pintura'], (o['pintura'], ''))
            p.update({'titulo': ti[0], 'autor': ti[1], 'metodo': METHOD.get(o['metodo'], o['metodo']), 'pared': o['wall'],
                      'ancho_m': round(o['w'], 2), 'alto_m': round(o['h'], 2), 'fuente': o['fuente'], 'marco': o['marco']})
        layout['paradas'].append(p)
    json.dump(layout, open(os.path.join(ROOT, 'museo/sala.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    if a.tex_max:
        for im in bpy.data.images:
            w, h = im.size
            if max(w, h) > a.tex_max:
                k = a.tex_max / max(w, h); im.scale(max(1, round(w * k)), max(1, round(h * k)))
                # write the small copy to disk and point the image at it, so that is what gets packed
                os.makedirs(os.path.join(ROOT, 'museo/_tex_ligera'), exist_ok=True)
                im.filepath_raw = os.path.join(ROOT, 'museo/_tex_ligera', ''.join(ch if ch.isalnum() else '_' for ch in im.name) + '.jpg')
                im.file_format = 'JPEG'; im.save()
    try:
        bpy.ops.file.pack_all()
    except Exception as e:
        print('SALA aviso pack', e)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ROOT, a.blend_out))
    print('SALA guardada: largo', round(L, 2), 'm, frames', sc.frame_end, 'paradas', len(stops))

    import time
    if a.stills:
        sw, sh = (int(v) for v in a.res_stills.split('x'))
        sc.render.resolution_x = sw; sc.render.resolution_y = sh
        sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 93
        for i, s in enumerate(stops):
            if a.solo and a.solo not in s['id']:
                continue
            sc.frame_set(s['frame_in'] + HOLD // 2)
            sc.render.filepath = os.path.join(ROOT, f'museo/render/stills/parada_{i:02d}_{s["id"]}{a.sufijo}.jpg')
            t0 = time.time(); bpy.ops.render.render(write_still=True)
            print(f'SALA still {i} {s["id"]} {time.time() - t0:.1f} s')
    if a.anim:
        sc.render.resolution_x = rw; sc.render.resolution_y = rh
        sc.render.image_settings.file_format = 'JPEG'; sc.render.image_settings.quality = 88
        sc.frame_step = a.step
        sc.render.filepath = os.path.join(ROOT, 'museo/render/frames/f_')
        t0 = time.time(); bpy.ops.render.render(animation=True)
        print(f'SALA anim {sc.frame_end} frames (paso {a.step}) {time.time() - t0:.1f} s')


if __name__ == '__main__':
    main()
