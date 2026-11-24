"""Scale model of the stadium for the museum room. Imported by blender_sala.py.

Built from references, not from a survey: aerial photographs on Wikimedia Commons (Category:Aerial
photographs of La Bombonera in 2025) and a reference render supplied by Marilyn. What it reproduces:

- the plan: a bowl that curves around one long side and both ends, cut flat on the fourth side;
- three tiers, blue, yellow and blue, the upper one the tallest, with aisles and parapets;
- the letters picked out in yellow seats on the upper tier (set LETTERS = "" to leave them out);
- the outer wall: blue base with columns, the yellow band with diagonal braces, blue top with windows;
- the flat side: a thin concrete building with a grid of windows and a tower at each end;
- floodlights on the rim, the scoreboard, and a striped pitch with its markings.

No sponsor logos and no crest. Every piece is a scaled unit cube, so the whole model stays editable by
changing the numbers below.
"""
import math

from mathutils import Matrix

LETTERS = 'CABJ*BOCA'
FONT = {   # 5 x 7, top row first
    'C': ['.###.', '#...#', '#....', '#....', '#....', '#...#', '.###.'],
    'A': ['.###.', '#...#', '#...#', '#####', '#...#', '#...#', '#...#'],
    'B': ['####.', '#...#', '#...#', '####.', '#...#', '#...#', '####.'],
    'J': ['..###', '...#.', '...#.', '...#.', '...#.', '#..#.', '.##..'],
    'O': ['.###.', '#...#', '#...#', '#...#', '#...#', '#...#', '.###.'],
    '*': ['..#..', '..#..', '#####', '.###.', '.###.', '#...#', '.....'],
}
N_EXP = 4.0          # superellipse exponent: 2 is an ellipse, larger is squarer
SAMPLES = 168        # pieces along the bowl, the same on every row so the letters line up


def build(brick, cx, cy, z0, mats):
    """brick(name, matrix, material_name, mats) places a unit cube. Returns the height of the model."""
    a, b = 0.5, 0.325                                  # half pitch (105 x 68 m)
    y_cut = -b - 0.03                                  # the bowl stops here; beyond it is the building of boxes

    def put(name, x, y, z, sx, sy, sz, rot, material, tilt=0.0):
        # mirrored in y: the building of boxes stands on the far side and faces the visitor
        M = (Matrix.Translation((cx + x, cy - y, z0 + z)) @ Matrix.Rotation(-rot, 4, 'Z')
             @ Matrix.Rotation(tilt, 4, 'Y') @ Matrix.Diagonal((sx, sy, sz, 1)))
        brick(name, M, material, mats)

    def curve(d):
        """SAMPLES points (x, y, tangent angle, piece length) of the bowl at distance d from its inner edge."""
        A, B = a * 1.2 + d, b * 1.2 + d
        e = 2.0 / N_EXP
        t0 = -math.asin(min(1.0, (abs(y_cut) / B)) ** (N_EXP / 2))
        raw = []
        for k in range(SAMPLES + 1):
            t = t0 + (math.pi - 2 * t0) * k / SAMPLES
            c, s = math.cos(t), math.sin(t)
            raw.append((A * math.copysign(abs(c) ** e, c), B * math.copysign(abs(s) ** e, s)))
        pts = []
        for k in range(SAMPLES):
            (x0, y0), (x1, y1) = raw[k], raw[k + 1]
            pts.append(((x0 + x1) / 2, (y0 + y1) / 2, math.atan2(y1 - y0, x1 - x0), math.hypot(x1 - x0, y1 - y0)))
        return pts

    base = 0.02
    put('Base', 0, 0.1, base / 2, 1.98, 1.5, base, 0, 'hormigon')

    # pitch: mowing stripes, lines, centre circle, penalty areas and goals
    stripes = 14
    put('Borde', 0, 0, base + 0.003, 2 * a + 0.09, 2 * b + 0.09, 0.006, 0, 'cesped2')
    for k in range(stripes):
        put('Franja', -a + (k + 0.5) * 2 * a / stripes, 0, base + 0.004, 2 * a / stripes, 2 * b, 0.008, 0,
            'cesped' if k % 2 == 0 else 'cesped2')
    zl, lw = base + 0.0085, 0.004
    for x in (-a, 0, a):
        put('Linea', x, 0, zl, lw, 2 * b, 0.002, 0, 'blanco')
    for y in (-b, b):
        put('Linea', 0, y, zl, 2 * a, lw, 0.002, 0, 'blanco')
    for k in range(28):
        ang = k * 2 * math.pi / 28
        put('Circulo', 0.087 * math.cos(ang), 0.087 * math.sin(ang), zl, 0.021, lw, 0.002, ang + math.pi / 2, 'blanco')
    for sx in (-1, 1):
        for depth, half in ((0.157, 0.192), (0.052, 0.087)):            # penalty area, goal area
            put('Area', sx * (a - depth), 0, zl, lw, 2 * half, 0.002, 0, 'blanco')
            for sy in (-1, 1):
                put('Area', sx * (a - depth / 2), sy * half, zl, depth, lw, 0.002, 0, 'blanco')
        put('Arco', sx * (a + 0.012), 0, base + 0.02, 0.004, 0.07, 0.004, 0, 'blanco')
        for sy in (-1, 1):
            put('Arco', sx * (a + 0.012), sy * 0.035, base + 0.012, 0.004, 0.004, 0.022, 0, 'blanco')

    # where each glyph sits along the bowl: centred on the long side, 5 pieces wide, 3 apart
    glyph_at = {}
    span = len(LETTERS) * 8 - 3
    start = (SAMPLES - span) // 2
    for g, ch in enumerate(LETTERS):
        for col in range(5):
            glyph_at[start + g * 8 + col] = (ch, col)                    # the mirrored curve runs left to right for the viewer

    # three tiers: (rows, step out, step up, seats, aisles, rise of the wall in front, aisle every n pieces)
    tiers = [(6, 0.012, 0.0075, 'azul', 'oro', 0.018, 12), (8, 0.012, 0.0125, 'oro', 'azul', 0.026, 0),
             (10, 0.0125, 0.0165, 'azul', 'oro', 0.03, 8)]
    d, h = 0.0, base
    for ti, (rows, s_out, s_up, seats, aisle, front, every) in enumerate(tiers):
        h += front
        for x, y, rot, ln in curve(d - s_out * 0.5):                     # parapet in front of the tier
            put('Baranda', x, y, h / 2 + 0.002, ln * 1.12, 0.004, h + 0.004, rot, 'blanco')
        for r in range(rows):
            h += s_up
            for k, (x, y, rot, ln) in enumerate(curve(d)):
                colour = seats
                if every and k % every == 0 and not (ti == 2 and start - 2 <= k <= start + span + 1):
                    colour = aisle
                if ti == 2 and k in glyph_at and 1 <= r <= 7:
                    ch, col = glyph_at[k]
                    colour = 'oro' if FONT[ch][7 - r][col] == '#' else 'azul'
                put('Grada', x, y, h / 2, ln * 1.12, s_out * 1.08, h, rot, colour)
            d += s_out
    top, d_out = h, d + 0.004

    # outer wall: blue base with columns, the yellow band with its diagonal braces, blue top with windows
    lo, hi = top * 0.34, top * 0.6
    wall = curve(d_out)
    for k, (x, y, rot, ln) in enumerate(wall):
        put('MuroBajo', x, y, lo / 2, ln * 1.1, 0.012, lo, rot, 'azul')
        put('MuroFranja', x, y, (lo + hi) / 2, ln * 1.1, 0.008, hi - lo, rot, 'oro')
        put('Tornapunta', x, y, (lo + hi) / 2, ln * 0.3, 0.013, (hi - lo) * 1.08, rot, 'azul', 0.5 if k % 2 == 0 else -0.5)
        put('MuroAlto', x, y, (hi + top) / 2, ln * 1.1, 0.012, top - hi, rot, 'azul')
        put('Cornisa', x, y, hi, ln * 1.1, 0.018, 0.006, rot, 'blanco')
        put('Cornisa', x, y, lo, ln * 1.1, 0.018, 0.006, rot, 'blanco')
        put('Remate', x, y, top + 0.004, ln * 1.1, 0.018, 0.008, rot, 'hormigon')
        if k % 2 == 0:
            for row in range(3):
                put('Ventana', x, y, hi + (top - hi) * (0.22 + 0.27 * row), ln * 0.55, 0.014, (top - hi) * 0.13, rot, 'vidrio')
        if k % 4 == 0:
            put('Columna', x, y, lo / 2, ln * 0.28, 0.02, lo, rot, 'hormigon')

    # floodlights along the rim, and the scoreboard on its legs above one end
    rim = curve(d_out - 0.01)
    for k in range(10, SAMPLES - 5, 14):
        x, y, rot, ln = rim[k]
        put('Mastil', x, y, top + 0.03, 0.006, 0.006, 0.06, rot, 'hormigon')
        put('Reflector', x, y, top + 0.066, 0.05, 0.01, 0.022, rot, 'blanco')
    x, y, rot, ln = rim[SAMPLES // 7]
    for off in (-0.045, 0.045):
        put('MarcadorPata', x + off * math.cos(rot), y + off * math.sin(rot), top + 0.03, 0.008, 0.008, 0.06, rot, 'hormigon')
    put('Marcador', x, y, top + 0.085, 0.13, 0.014, 0.06, rot, 'vidrio')
    put('MarcadorLuz', x, y, top + 0.122, 0.12, 0.012, 0.012, rot, 'blanco')

    # the flat side: a thin concrete building with a grid of windows, a tower at each end and two masts
    ends = curve(d_out)
    half_w = abs(ends[0][0]) - 0.03
    wy, bh = y_cut - 0.065, top * 0.8
    put('PalcosGrada', 0, y_cut - 0.012, base + 0.03, 2 * a + 0.1, 0.05, 0.06, 0, 'azul')          # low stand in front
    put('Palcos', 0, wy, bh / 2 + base, 2 * half_w, 0.07, bh, 0, 'hormigon_claro')
    floors, cols = 8, 36
    for r in range(floors):
        for c in range(cols):
            for face in (0.036, -0.036):                                 # windows towards the pitch and towards the street
                put('VentanaPalco', -half_w + 0.03 + c * (2 * half_w - 0.06) / (cols - 1), wy + face,
                    base + 0.075 + r * (bh - 0.1) / (floors - 1), (2 * half_w - 0.06) / cols * 0.62, 0.004,
                    (bh - 0.1) / floors * 0.55, 0, 'vidrio')
    put('PalcosTecho', 0, wy + 0.004, bh + base + 0.005, 2 * half_w + 0.02, 0.09, 0.01, 0, 'hormigon')
    for sx in (-1, 1):
        put('Torre', sx * (half_w + 0.02), wy, (top * 0.95) / 2 + base, 0.085, 0.095, top * 0.95, 0, 'hormigon_claro')
        for r in range(6):
            put('TorreLosa', sx * (half_w + 0.02), wy + 0.03, base + 0.06 + r * top * 0.15, 0.09, 0.05, 0.006, 0, 'hormigon')
        put('MastilTorre', sx * (half_w + 0.02), wy, top * 0.95 + base + 0.09, 0.005, 0.005, 0.18, 0, 'blanco')
        put('ReflectorTorre', sx * (half_w + 0.02), wy + 0.004, top * 0.95 + base + 0.17, 0.04, 0.008, 0.03, 0, 'blanco')
    return top + 0.2
