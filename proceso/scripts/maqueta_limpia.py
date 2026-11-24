"""Clean model of the stadium, built from a building sheet (research/maqueta3d/ficha_edificio.md).

Imported by blender_sala.py (build), or run on its own to look at it:

    blender --background --python scripts/maqueta_limpia.py -- <out-prefix>

Unlike maqueta_bombonera.py (unit cubes placed by eye), every surface here is swept along the plan of
the building: a path with two straight ends, two quarter-circle corners and one straight long side, open
on the fourth side where the box building stands. Tiers, parapets and the outer wall are the same path
at different distances from the wall, so they stay parallel and meet cleanly.

All numbers in F are metres. Where each comes from is in the building sheet; none is a survey.
No crest, no sponsor marks, no lettering.
"""
import math

import bpy
from mathutils import Matrix, Vector

F = {
    'pitch': (105.0, 68.0),
    'depth': 50.0,          # touchline (or goal line) to the outer wall, measured on the ground in photograph 08
    'corner_radius': 52.0,  # of the outer wall; read off the plan of the Rodin model
    'flat_side': 5.0,       # far touchline to the foot of the low stand on the side of the boxes
    'top': 34.0,            # rim of the upper tier (Rodin model, scaled by the pitch)
    # tiers: name, distance from the pitch at the front and at the back, height at the front and at the back, rows, seats
    'tiers': [('baja', 6.0, 17.0, 1.2, 5.5, 10, 'azul'),
              ('media', 15.0, 29.0, 8.0, 15.5, 12, 'oro'),
              ('alta', 27.0, 48.0, 18.0, 33.0, 18, 'azul')],
    # outer wall, bottom to top: height where the layer ends, material, how far it steps back from the wall line
    'wall': [(11.0, 'azul', 0.0), (18.0, 'oro', 0.0), (22.0, 'azul_oscuro', 1.2), (34.0, 'azul', 0.0)],
    'bay': 4,               # one pilaster every this many path steps
    'boxes': {'depth': 9.0, 'height': 27.0, 'floors': 8, 'tower': 31.0},
}
N_END, N_ARC, N_SIDE = 24, 40, 64      # path steps: each straight end, each corner, the long side


class Parts:
    """Collects quads by material; one mesh object per material at the end."""

    def __init__(self):
        self.q = {}

    def quad(self, material, a, b, c, d):
        self.q.setdefault(material, []).append((a, b, c, d))

    def box(self, material, centre, size, yaw=0.0, tilt=0.0):
        M = (Matrix.Translation(centre) @ Matrix.Rotation(yaw, 4, 'Z') @ Matrix.Rotation(tilt, 4, 'Y')
             @ Matrix.Diagonal((size[0] / 2, size[1] / 2, size[2] / 2, 1)))
        v = [tuple(M @ Vector(p)) for p in ((-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
                                            (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1))]
        for f in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
            self.quad(material, *(v[i] for i in f))

    def objects(self, name, M, mats):
        made = []
        for material, quads in self.q.items():
            verts, faces = [], []
            for q in quads:
                faces.append(tuple(range(len(verts), len(verts) + 4)))
                verts.extend(tuple(M @ Vector(p)) for p in q)
            me = bpy.data.meshes.new(f'{name}_{material}')
            me.from_pydata(verts, [], faces); me.validate(); me.update()
            me.materials.append(mats.get(material) or mats['azul'])
            ob = bpy.data.objects.new(f'{name}_{material}', me)
            bpy.context.collection.objects.link(ob)
            made.append(ob)
        return made


def path(s):
    """Points (x, y, heading) of the plan, s metres inside the outer wall. Same number of points for every s."""
    L, W = F['pitch']; D, R = F['depth'], F['corner_radius']
    A, B, yF = L / 2 + D, W / 2 + D, W / 2 + F['flat_side']
    pts = []
    for k in range(N_END):                                   # straight end on the -x side, from the flat side down
        t = k / N_END
        pts.append((-(A - s), yF + (-(B - R) - yF) * t, -math.pi / 2))
    for k in range(N_ARC):
        a = math.pi + (math.pi / 2) * k / N_ARC
        pts.append((-(A - R) + (R - s) * math.cos(a), -(B - R) + (R - s) * math.sin(a), a + math.pi / 2))
    for k in range(N_SIDE):
        pts.append((-(A - R) + 2 * (A - R) * k / N_SIDE, -(B - s), 0.0))
    for k in range(N_ARC):
        a = 1.5 * math.pi + (math.pi / 2) * k / N_ARC
        pts.append((A - R + (R - s) * math.cos(a), -(B - R) + (R - s) * math.sin(a), a + math.pi / 2))
    for k in range(N_END + 1):
        t = k / N_END
        pts.append((A - s, -(B - R) + (yF + (B - R)) * t, math.pi / 2))
    return pts


def sweep(parts, profile, material_of, close_ends=True):
    """profile: list of (s, z). Sweeps it along the plan; material_of(i, j) names the material of each quad."""
    rails = [path(s) for s, _ in profile]
    n = len(rails[0])
    for i in range(len(profile) - 1):
        z0, z1 = profile[i][1], profile[i + 1][1]
        for j in range(n - 1):
            a, b = rails[i][j], rails[i][j + 1]; c, d = rails[i + 1][j + 1], rails[i + 1][j]
            parts.quad(material_of(i, j), (a[0], a[1], z0), (b[0], b[1], z0), (c[0], c[1], z1), (d[0], d[1], z1))
        if close_ends:                                       # the cut ends on the flat side, down to the ground
            for j in (0, n - 1):
                a, d = rails[i][j], rails[i + 1][j]
                parts.quad(material_of(i, -1), (a[0], a[1], z0), (d[0], d[1], z1), (d[0], d[1], 0), (a[0], a[1], 0))


def build_parts():
    P = Parts()
    L, W = F['pitch']; D = F['depth']
    A, B, yF = L / 2 + D, W / 2 + D, W / 2 + F['flat_side']
    bx = F['boxes']

    # ground slab and the apron around the pitch
    P.box('hormigon', (0, (yF + bx['depth'] - B) / 2, -0.6), (2 * A + 8, B + yF + bx['depth'] + 8, 1.2))
    P.box('azul_oscuro', (0, (yF - W / 2 - 7) / 2, 0.05), (L + 14, W / 2 + 7 + yF, 0.1))      # only inside the bowl

    # pitch: mowing stripes and markings
    stripes = 18
    for k in range(stripes):
        P.box('cesped' if k % 2 == 0 else 'cesped2', (-L / 2 - 3 + (k + 0.5) * (L + 6) / stripes, 0, 0.12),
              ((L + 6) / stripes, W + 6, 0.12))
    z, lw = 0.2, 0.35
    for x in (-L / 2, 0, L / 2):
        P.box('blanco', (x, 0, z), (lw, W, 0.06))
    for y in (-W / 2, W / 2):
        P.box('blanco', (0, y, z), (L + lw, lw, 0.06))
    for k in range(48):
        a = k * 2 * math.pi / 48
        P.box('blanco', (9.15 * math.cos(a), 9.15 * math.sin(a), z), (1.25, lw, 0.06), a + math.pi / 2)
    P.box('blanco', (0, 0, z), (0.7, 0.7, 0.06))
    for sx in (-1, 1):
        for depth, half in ((16.5, 20.16), (5.5, 9.16)):
            P.box('blanco', (sx * (L / 2 - depth), 0, z), (lw, 2 * half, 0.06))
            for sy in (-1, 1):
                P.box('blanco', (sx * (L / 2 - depth / 2), sy * half, z), (depth, lw, 0.06))
        P.box('blanco', (sx * (L / 2 - 11), 0, z), (0.6, 0.6, 0.06))
        for k in range(-5, 6):                                # penalty arc
            a = k * math.radians(53) / 5.5
            P.box('blanco', (sx * (L / 2 - 11 - 9.15 * math.cos(a)), 9.15 * math.sin(a), z), (lw, 1.7, 0.06), -sx * a)
        P.box('blanco', (sx * (L / 2 + 1.0), 0, 2.44), (0.15, 7.32, 0.15))
        for sy in (-1, 1):
            P.box('blanco', (sx * (L / 2 + 0.1), sy * 3.66, 1.22), (0.15, 0.15, 2.44))
            P.box('blanco', (sx * (L / 2 + 1.0), sy * 3.66, 1.22), (1.9, 0.08, 2.44))

    # tiers: stepped rows swept along the plan, a parapet in front and a dark wall behind each
    for name, d0, d1, z0, z1, rows, seats in F['tiers']:
        prof = [(D - d0, z0 - 1.6), (D - d0, z0 + 1.0), (D - d0 - 0.35, z0 + 1.0), (D - d0 - 0.35, z0)]
        n_front = len(prof) - 1
        for r in range(rows):
            dd = d0 + 0.35 + (d1 - d0 - 0.35) * r / rows
            zz = z0 + (z1 - z0) * r / rows
            prof.append((D - dd - (d1 - d0 - 0.35) / rows, zz))      # tread
            prof.append((D - dd - (d1 - d0 - 0.35) / rows, zz + (z1 - z0) / rows))   # riser
        aisle = 'blanco' if seats == 'oro' else 'azul_claro'

        def mat(i, j, n_front=n_front, seats=seats, aisle=aisle):
            if i < n_front:
                return 'blanco' if i == 1 else 'azul'
            return aisle if (j >= 0 and j % 12 == 6) else seats
        sweep(P, prof, mat)
        sweep(P, [(D - d1, 0.0), (D - d1, z1)], lambda i, j: 'azul_oscuro')

    # outer wall in layers, and its flat top
    prof, z = [], 0.0
    for top, material, back in F['wall']:
        prof += [(back, z), (back, top)]; z = top
    layers = [m for _, m, _ in F['wall']]
    sweep(P, prof, lambda i, j: layers[i // 2] if i % 2 == 0 else 'azul')
    sweep(P, [(0.0, F['top']), (D - F['tiers'][-1][2], F['top'])], lambda i, j: 'hormigon')
    sweep(P, [(D - F['tiers'][-1][2], F['top'] + 1.1), (D - F['tiers'][-1][2], F['tiers'][-1][4])], lambda i, j: 'blanco')

    # pilasters, braces on the yellow band, windows on the base and on the top band
    rail, y_lo, y_hi = path(-0.45), F['wall'][0][0], F['wall'][1][0]
    n = len(rail)
    for j in range(0, n, F['bay']):
        x, y, h = rail[j]
        P.box('azul', (x, y, F['top'] / 2), (0.9, 1.3, F['top']), h)
        if j + F['bay'] < n:
            x2, y2, h2 = rail[j + F['bay']]
            mx, my, hm = (x + x2) / 2, (y + y2) / 2, math.atan2(y2 - y, x2 - x)
            span = math.hypot(x2 - x, y2 - y)
            lean = math.atan2(y_hi - y_lo, span) * (1 if (j // F['bay']) % 2 == 0 else -1)
            P.box('azul', (mx, my, (y_lo + y_hi) / 2), (math.hypot(span, y_hi - y_lo) * 0.96, 0.7, 0.9), hm, -lean)
            for zc in (3.2, 6.6, 9.2):
                P.box('vidrio', (mx, my, zc), (span * 0.62, 0.5, 1.5), hm)
            for zc in (25.0, 28.5, 31.6):
                P.box('vidrio', (mx, my, zc), (span * 0.7, 0.5, 1.3), hm)
    for zc in (y_lo, y_hi, F['wall'][2][0]):
        sweep(P, [(-0.25, zc - 0.35), (-0.25, zc + 0.35)], lambda i, j: 'blanco', close_ends=False)

    # stair towers on the two corners
    for j in (N_END + N_ARC // 2, N_END + N_ARC + N_SIDE + N_ARC // 2):
        x, y, h = path(-2.2)[j]
        P.box('azul', (x, y, (F['top'] + 2) / 2), (9.0, 5.5, F['top'] + 2), h)
        P.box('vidrio', (x - 2.9 * math.sin(h) * -1, y - 2.9 * math.cos(h), 20.0), (2.0, 0.5, 3.0), h)

    # floodlights on the rim
    rim = path(1.5)
    for j in range(8, len(rim) - 8, 16):
        x, y, h = rim[j]
        P.box('hormigon', (x, y, F['top'] + 2.5), (0.5, 0.5, 5.0), h)
        P.box('blanco', (x, y, F['top'] + 5.6), (5.0, 0.8, 1.6), h)

    # flat side: low stand, the thin building of boxes with its floors, a tower at each end
    half = L / 2 + 6
    rows = 8
    for r in range(rows):
        P.box('azul', (0, yF + (r + 0.5) * 0.9, 0.6 + r * 0.45), (2 * half, 0.9, 1.2 + r * 0.9))
    y0 = yF + rows * 0.9
    yc = y0 + bx['depth'] / 2
    P.box('azul_oscuro', (0, yc, bx['height'] / 2), (2 * half, bx['depth'], bx['height']))
    P.box('hormigon', (0, yc, bx['height'] + 0.3), (2 * half + 1, bx['depth'] + 1, 0.6))
    for f in range(bx['floors']):
        zc = 5.0 + f * (bx['height'] - 6.0) / bx['floors']
        for face in (y0 - 0.15, y0 + bx['depth'] + 0.15):
            P.box('vidrio', (0, face, zc + 1.2), (2 * half - 1, 0.3, 1.9))
            P.box('blanco', (0, face - 0.1 if face < yc else face + 0.1, zc), (2 * half, 0.4, 0.3))
    for k in range(-13, 14):
        P.box('hormigon', (k * 2 * half / 27, y0 - 0.25, bx['height'] / 2 + 2), (0.35, 0.4, bx['height'] - 4))
    for sx in (-1, 1):
        P.box('azul', (sx * (half + 4.5), yc - 1, bx['tower'] / 2), (9.0, bx['depth'] + 4, bx['tower']))
        P.box('hormigon', (sx * (half + 4.5), yc - 1, bx['tower'] + 0.3), (9.6, bx['depth'] + 4.6, 0.6))
        for f in range(6):
            P.box('vidrio', (sx * (half + 4.5), yc - 1 - (bx['depth'] + 4) / 2 - 0.1, 5 + f * 4.2), (5.0, 0.3, 1.6))

    # scoreboard above the upper tier at one end, on its frame
    sx_, sy_ = -(A - 9), yF - 26
    for off in (-7, 7):
        P.box('azul', (sx_, sy_ + off, F['top'] + 3.0), (0.8, 0.8, 6.0))
    P.box('azul', (sx_, sy_, F['top'] + 10.5), (1.6, 19.0, 10.0))
    P.box('vidrio', (sx_ + 0.9, sy_, F['top'] + 10.5), (0.3, 17.0, 8.4))
    return P


def build(cx, cy, z0, long_side, mats, turn_deg=0.0):
    """Places the model with its centre at (cx, cy), standing on z0, its long side `long_side` metres. Returns the objects."""
    A = F['pitch'][0] / 2 + F['depth']
    k = long_side / (2 * A + 8)
    yc = (F['pitch'][1] / 2 + F['flat_side'] + F['boxes']['depth'] - (F['pitch'][1] / 2 + F['depth'])) / 2
    M = (Matrix.Translation((cx, cy, z0 + 1.2 * k)) @ Matrix.Rotation(math.radians(turn_deg), 4, 'Z')
         @ Matrix.Scale(k, 4) @ Matrix.Translation((0, -yc, 0)))
    return build_parts().objects('Maqueta', M, mats)


if __name__ == '__main__':
    import os
    import sys
    out = os.path.abspath(sys.argv[sys.argv.index('--') + 1])
    bpy.ops.wm.read_factory_settings(use_empty=True)

    def m(name, rgb, rough=0.6):
        mt = bpy.data.materials.new(name); mt.use_nodes = True
        b = mt.node_tree.nodes['Principled BSDF']
        b.inputs['Base Color'].default_value = (*rgb, 1); b.inputs['Roughness'].default_value = rough
        return mt
    mats = {'azul': m('azul', (0.012, 0.05, 0.19)), 'azul_claro': m('azul_claro', (0.05, 0.13, 0.36)),
            'azul_oscuro': m('azul_oscuro', (0.006, 0.018, 0.06)), 'oro': m('oro', (0.9, 0.45, 0.02)),
            'blanco': m('blanco', (0.8, 0.8, 0.78)), 'cesped': m('cesped', (0.03, 0.2, 0.04), 0.9),
            'cesped2': m('cesped2', (0.022, 0.15, 0.03), 0.9), 'hormigon': m('hormigon', (0.35, 0.35, 0.34), 0.9),
            'vidrio': m('vidrio', (0.004, 0.012, 0.035), 0.15)}
    obs = build(0, 0, 0, 2.0, mats)
    print('MAQUETA', len(obs), 'objetos,', sum(len(o.data.polygons) for o in obs), 'caras')
    sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = 1600, 900
    sc.render.image_settings.file_format = 'JPEG'
    w = bpy.data.worlds.new('W'); sc.world = w; w.use_nodes = True
    w.node_tree.nodes['Background'].inputs[0].default_value = (0.8, 0.8, 0.8, 1)
    sun = bpy.data.objects.new('Sol', bpy.data.lights.new('Sol', 'SUN')); sc.collection.objects.link(sun)
    sun.data.energy = 3.5; sun.rotation_euler = (math.radians(48), 0, math.radians(35))
    cam = bpy.data.objects.new('Cam', bpy.data.cameras.new('Cam')); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 50
    for name, pos in {'aerea-curva': (0.9, -2.3, 1.5), 'aerea-palcos': (-1.0, 2.2, 1.5), 'fachada': (1.6, -2.2, 0.35),
                      'planta': (0, -0.01, 3.4)}.items():
        cam.location = pos
        cam.rotation_euler = (Vector((0, 0, 0.1)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
        sc.render.filepath = f'{out}__{name}.jpg'
        bpy.ops.render.render(write_still=True)
