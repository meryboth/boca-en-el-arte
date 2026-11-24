"""Automatic metrics of one intervened painting against its original, on the frozen patches.

    python scripts/measure.py <case> <output-image> [--zones research/zones/zones.json] [--json]

Patches come from zones.json (preview coordinates). The output is resized to the original size with
Lanczos before measuring; no registration is done, so a model that shifts the picture is penalised.

  alteracion  median CIEDE2000 per protected patch, pixel by pixel against the original.  Lower is better.
  tono        median hue-angle error (CIELAB, degrees) per garment patch against blue #103F79 or gold
              #F3B229 (the patch says which; "cualquiera" takes the nearer one per pixel), over pixels
              with chroma >= 8 so near-neutral shadows do not vote.  Lower is better.
  pliegues    Pearson correlation of L* between output and original per garment patch.  Higher is better.

Prints one line per patch and the three summary numbers (median over patches); --json prints a dict.
"""
import argparse
import json

import numpy as np
from PIL import Image
from skimage import color

Image.MAX_IMAGE_PIXELS = None
TARGETS = {'azul': '#103F79', 'oro': '#F3B229'}


def hue_of(hexcode):
    rgb = np.array([[[int(hexcode[i:i + 2], 16) / 255 for i in (1, 3, 5)]]])
    lab = color.rgb2lab(rgb)[0, 0]
    return float(np.degrees(np.arctan2(lab[2], lab[1])))


def hue_diff(h, target):
    return np.abs((h - target + 180) % 360 - 180)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('case'); ap.add_argument('output')
    ap.add_argument('--zones', default='research/zones/zones.json')
    ap.add_argument('--json', action='store_true')
    a = ap.parse_args()
    z = json.load(open(a.zones, encoding='utf-8'))[a.case]
    src = Image.open(z['source']).convert('RGB')
    W, H = src.size
    S = W / z['coord_width']
    out_im = Image.open(a.output).convert('RGB')
    ratio = out_im.size[0] * out_im.size[1] / (W * H)
    out = out_im if out_im.size == (W, H) else out_im.resize((W, H), Image.LANCZOS)
    hues = {k: hue_of(v) for k, v in TARGETS.items()}

    def crop(im, r):
        b = tuple(int(round(v * S)) for v in r)
        return color.rgb2lab(np.asarray(im.crop(b), dtype=np.float32) / 255)

    res = {'alteracion': {}, 'tono': {}, 'pliegues': {}}
    for name, r in z['protegidas'].items():
        res['alteracion'][name] = float(np.median(color.deltaE_ciede2000(crop(src, r), crop(out, r))))
    for name, g in z['ropa'].items():
        a0, a1 = crop(src, g['rect']), crop(out, g['rect'])
        h = np.degrees(np.arctan2(a1[..., 2], a1[..., 1]))
        c = np.hypot(a1[..., 1], a1[..., 2])
        if g['color'] == 'cualquiera':
            err = np.minimum(hue_diff(h, hues['azul']), hue_diff(h, hues['oro']))
        else:
            err = hue_diff(h, hues[g['color']])
        ok = c >= 8
        res['tono'][name] = float(np.median(err[ok])) if ok.mean() > 0.05 else float('nan')
        res['pliegues'][name] = float(np.corrcoef(a0[..., 0].ravel(), a1[..., 0].ravel())[0, 1])
    summary = {k: float(np.nanmedian(list(v.values()))) for k, v in res.items()}
    summary['alteracion_max'] = float(max(res['alteracion'].values()))
    summary['tono_max'] = float(np.nanmax(list(res['tono'].values())))
    summary['resolucion'] = float(ratio)
    if a.json:
        print(json.dumps({'summary': summary, 'patches': res}))
        return
    for k, v in res.items():
        for n, x in v.items():
            print(f'{k:11s} {n:18s} {x:7.2f}')
    print({k: round(v, 3) for k, v in summary.items()})


if __name__ == '__main__':
    main()
