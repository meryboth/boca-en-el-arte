"""Build labelled contact sheets that document the process, from the files already on disk.

    python scripts/process_sheets.py

Writes research/proceso/*.jpg. Safe to re-run: it rebuilds every sheet from whatever exists, so run it
again after new attempts finish. Nothing here is a result; the sheets only show what was produced.
"""
import glob
import json
import os
import re

from PIL import Image, ImageDraw, ImageFont

Image.MAX_IMAGE_PIXELS = None
OUT = 'research/proceso'
H = 620
PAD = 14
LABEL = 54


def font(size):
    for name in ('arial.ttf', 'DejaVuSans.ttf'):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    return ImageFont.load_default()


F, FT = font(20), font(30)


def sheet(title, items, name, height=H, per_row=None):
    """items: list of (label, path). Missing files are skipped and listed in the footer."""
    tiles, missing = [], []
    for label, path in items:
        if not os.path.exists(path):
            missing.append(label); continue
        im = Image.open(path).convert('RGB')
        im = im.resize((round(im.width * height / im.height), height), Image.LANCZOS)
        tiles.append((label, im))
    if not tiles:
        return
    per_row = per_row or len(tiles)
    rows = [tiles[i:i + per_row] for i in range(0, len(tiles), per_row)]
    width = max(sum(t[1].width for t in r) + PAD * (len(r) + 1) for r in rows)
    total_h = 70 + len(rows) * (height + LABEL + PAD) + (34 if missing else 0)
    sh = Image.new('RGB', (width, total_h), (250, 250, 248))
    d = ImageDraw.Draw(sh)
    d.text((PAD, 18), title, fill=(20, 20, 20), font=FT)
    y = 70
    for r in rows:
        x = PAD
        for label, im in r:
            sh.paste(im, (x, y))
            d.text((x, y + height + 8), label, fill=(40, 40, 40), font=F)
            x += im.width + PAD
        y += height + LABEL + PAD
    if missing:
        d.text((PAD, total_h - 30), 'Falta: ' + ', '.join(missing), fill=(150, 40, 40), font=F)
    os.makedirs(OUT, exist_ok=True)
    sh.save(f'{OUT}/{name}.jpg', quality=86)
    print(name, sh.size, len(tiles), 'imagenes')


def final_preview(case, cond, seed):
    cfg = f'research/runs/{cond}/{case}__{cond}__s{seed}.json'
    if not os.path.exists(cfg):
        return None
    out = json.load(open(cfg, encoding='utf-8')).get('out', '')
    p = out + '__preview.jpg'
    if os.path.exists(p):
        return p
    c = sorted(glob.glob(f'research/runs/{cond}/{case}__{cond}__s{seed}__r*__preview.jpg'))
    return c[-1] if c else None


def main():
    P = 'research/pilots/'
    sheet('01 · Piloto: obra entera dibujada por codigo (descartado por falta de realismo)',
          [('La creacion de Adan, una pasada, canvas 2D', 'research/outputs/fable-5-2__oneshot__adan__s0-piloto.png')],
          '01_piloto-obra-por-codigo', height=520)
    sheet('02 · Julio II: las cuatro versiones del recoloreo por codigo',
          [('Original', P + '_preview_src.jpg'),
           ('v1: plano y saturado', P + 'julio2__code-recolor__v1__preview.jpg'),
           ('v2: manchas por un bug', P + 'julio2__code-recolor__v2__preview.jpg'),
           ('v3: tine la barba', P + 'julio2__code-recolor__v3__preview.jpg'),
           ('v4: final', P + 'julio2__code-recolor__v4__preview.jpg')], '02_julio2-versiones-codigo')
    sheet('03 · Julio II: los tres metodos sobre la misma pintura',
          [('Original', P + '_preview_src.jpg'),
           ('Codigo (Fable 5.2)', P + 'julio2__code-recolor__v4__preview.jpg'),
           ('Nano Banana 2 solo', P + 'julio2__edit-nb2__s1-piloto__preview.jpg'),
           ('Combinado (local)', P + 'julio2__hybrid__v1__preview.jpg'),
           ('Combinado (Comfy Cloud)', P + 'julio2__hybrid-comfy__s1b__preview.jpg')], '03_julio2-tres-metodos')
    sheet('04 · Julio II al 100 %: borde de la barba',
          [('Codigo', P + 'julio2__code-recolor__v4__crop100.jpg'),
           ('Nano Banana 2 solo', P + 'julio2__edit-nb2__s1-piloto__crop100.jpg'),
           ('Combinado (local)', P + 'julio2__hybrid__v1__crop100.jpg'),
           ('Combinado (Comfy Cloud)', P + 'julio2__hybrid-comfy__s1b__crop100.jpg')], '04_julio2-detalle-100')
    sheet('05 · Zonas de medicion (verde: no debe cambiar; magenta: ropa)',
          [(c, f'research/zones/{c}__zonas.jpg') for c in ('prato', 'arnolfini', 'baco', 'atenas')],
          '05_zonas-de-medicion', height=560)
    n = 6
    for case in ('prato', 'arnolfini', 'baco', 'atenas'):
        items = [('Original', f'{P}_preview_{case}.jpg')]
        for s in range(1, 6):
            p = final_preview(case, 'code', s)
            runs = len(glob.glob(f'research/runs/code/{case}__code__s{s}__r*__preview.jpg'))
            items.append((f'Intento {s} ({runs} corridas)', p or f'falta-{case}-s{s}'))
        sheet(f'{n:02d} · {case}: los cinco intentos independientes del recoloreo por codigo', items,
              f'{n:02d}_{case}-cinco-intentos', height=520, per_row=3 if case in ('baco', 'atenas') else 6)
        n += 1
    for case, s in (('arnolfini', 1), ('atenas', 2)):
        rounds = sorted(glob.glob(f'research/runs/code/{case}__code__s{s}__r*__preview.jpg'),
                        key=lambda p: int(re.search(r'__r(\d+)__', p).group(1)))
        sheet(f'{n:02d} · {case}, intento {s}: como corrige el agente de una corrida a la siguiente',
              [(f'Corrida {i + 1}', p) for i, p in enumerate(rounds)], f'{n:02d}_{case}-s{s}-rondas',
              height=520, per_row=2 if case == 'atenas' else 4)
        n += 1
    for case in ('prato', 'arnolfini', 'baco', 'atenas'):
        wide = case in ('baco', 'atenas')
        sheet(f'{n:02d} · {case}: los tres metodos, intento 1',
              [('Original', f'{P}_preview_{case}.jpg'),
               ('Codigo (Fable 5.2)', final_preview(case, 'code', 1) or 'falta'),
               ('Nano Banana 2 solo', f'research/runs/edit/{case}__edit__s1__preview.jpg'),
               ('Combinado', f'research/runs/hybrid/{case}__hybrid__s1__preview.jpg')],
              f'{n:02d}_{case}-tres-metodos', height=560, per_row=2 if wide else 4)
        n += 1
        sheet(f'{n:02d} · {case}: las cinco ediciones de Nano Banana 2 (mismo prompt, semillas 1 a 5)',
              [(f'Semilla {k}', f'research/runs/edit/{case}__edit__s{k}__preview.jpg') for k in range(1, 6)],
              f'{n:02d}_{case}-cinco-ediciones-nb2', height=480, per_row=3 if wide else 5)
        n += 1
    sheet(f'{n:02d} · Tesseract: prueba minima de render',
          [('Raster', 'tesseract/smoke/smoke-raster.png'), ('Path tracer, 16 muestras', 'tesseract/smoke/smoke-pt16.png')],
          f'{n:02d}_tesseract-prueba', height=520)


if __name__ == '__main__':
    main()
