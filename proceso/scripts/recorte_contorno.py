"""Cut the stadium out of the aerial photographs along hand-traced outlines.

    python scripts/recorte_contorno.py

Reads research/maqueta3d/contornos.json (outlines traced on 960x540 copies) and the photographs in
research/maqueta3d/fuentes/, and writes for each a square 1536 px JPEG on white in
research/maqueta3d/recortes_mano/, plus a contact sheet. This replaced the colour heuristic of
recorte_estadio.py, which clipped shaded stands and the grey box building.
"""
import json
import os

from PIL import Image, ImageDraw, ImageFilter

BASE = 'research/maqueta3d'


def main():
    outlines = json.load(open(f'{BASE}/contornos.json', encoding='utf-8'))
    os.makedirs(f'{BASE}/recortes_mano', exist_ok=True)
    tiles = []
    for i, poly in outlines.items():
        if i.startswith('_'):
            continue
        im = Image.open(f'{BASE}/fuentes/bombonera_aerea_{i}.jpg').convert('RGB')
        k = im.width / 960
        m = Image.new('L', im.size, 0)
        ImageDraw.Draw(m).polygon([(x * k, y * k) for x, y in poly], fill=255)
        m = m.filter(ImageFilter.GaussianBlur(1.2))
        xs = [x * k for x, _ in poly]; ys = [y * k for _, y in poly]
        side = int(max(max(xs) - min(xs), max(ys) - min(ys)) * 1.1)
        cx, cy = (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2
        out = Image.new('RGB', (side, side), (255, 255, 255))
        out.paste(im, (int(side / 2 - cx), int(side / 2 - cy)), m)
        out = out.resize((1536, 1536), Image.LANCZOS)
        out.save(f'{BASE}/recortes_mano/recorte_{i}.jpg', quality=93)
        tiles.append(out.resize((480, 480)))
    sheet = Image.new('RGB', (480 * len(tiles), 480), (200, 200, 200))
    for n, t in enumerate(tiles):
        sheet.paste(t, (n * 480, 0))
    sheet.save(f'{BASE}/hoja_recortes_mano.jpg', quality=85)
    print(len(tiles), 'recortes')


if __name__ == '__main__':
    main()
