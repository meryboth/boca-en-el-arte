"""Recolour garments of a painting to blue and gold, keeping the original shading and brushwork.

    python scripts/recolor.py research/pilots/julio2.json

The config names the source image, the preview width its coordinates refer to, and a list of regions.
Each region has polygons drawn by hand (loose is fine) and is refined by a colour key in CIELAB: only
pixels whose hue and chroma match the source garment colour are changed. The key is the top-level "key"
or a per-region "key": {"a_lo","a_hi"} (gate on a*, for reds) or {"c_lo","c_hi"} (gate on chroma, any hue),
plus {"hue_min","hue_max"} in degrees of atan2(b*, a*); hue_min > hue_max wraps through +-180.
Region options: "fill": {"erode","l_lo","l_hi","red_guard": true} recolours everything well inside the
polygon except light neutral paint (red_guard keeps greenish pixels out; set false for non-red garments);
"fill_exclude": polygons kept out of the fill; "exclude"; "band"; "everything_else": true takes every keyed
pixel outside the earlier polygons. Earlier regions win where they overlap. Lightness detail (folds,
craquelure) is kept; only its level is shifted, and hue and chroma are replaced.

Writes <out>.jpg, a 900 px preview and a mask image. Prints timing and the share of changed pixels.
"""
import json
import sys
import time

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from skimage import color


def smooth(x, lo, hi):
    t = np.clip((x - lo) / (hi - lo), 0, 1)
    return t * t * (3 - 2 * t)


def poly_mask(size, polys, scale, feather):
    m = Image.new('L', size, 0)
    d = ImageDraw.Draw(m)
    for p in polys:
        d.polygon([(x * scale, y * scale) for x, y in p], fill=255)
    if feather:
        m = m.filter(ImageFilter.GaussianBlur(feather * scale))
    return np.asarray(m, dtype=np.float32) / 255


def main():
    cfg = json.load(open(sys.argv[1], encoding='utf-8'))
    t0 = time.time()
    src = Image.open(cfg['source']).convert('RGB')
    W, H = src.size
    S = W / cfg['coord_width']
    lab = color.rgb2lab(np.asarray(src, dtype=np.float32) / 255).astype(np.float32)
    L, a, b = lab[..., 0], lab[..., 1], lab[..., 2]
    C = np.hypot(a, b)
    hue = np.degrees(np.arctan2(b, a))

    def key_weight(key):
        # Chroma gate on C (not a*) so garments of any source hue can be keyed, then a hue window.
        # hue_min > hue_max means the window wraps through +-180 degrees.
        cw = smooth(C, key['c_lo'], key['c_hi']) if 'c_lo' in key else smooth(a, key['a_lo'], key['a_hi'])
        lo, hi = key['hue_min'], key['hue_max']
        if lo <= hi:
            hw = smooth(hue, lo - 8, lo) * (1 - smooth(hue, hi, hi + 8))
        else:
            hw = np.maximum(smooth(hue, lo - 8, lo), 1 - smooth(hue, hi, hi + 8))
        return cw * hw

    out = lab.copy()
    total = np.zeros((H, W), np.float32)
    taken = np.zeros((H, W), np.float32)
    for r in cfg['regions']:
        if r.get('everything_else'):
            geo = 1 - np.clip(taken, 0, 1)
        else:
            geo = poly_mask((W, H), r['polygons'], S, r.get('feather', 1.5))
        for ex in r.get('exclude', []):
            geo = geo * (1 - poly_mask((W, H), [ex], S, 1.5))
        w = geo * key_weight(r.get('key', cfg.get('key')))
        if r.get('fill'):
            # Well inside the polygon everything is garment except light neutral paint (fur trim, beard).
            core = poly_mask((W // 4, H // 4), r['polygons'], S / 4, 0)
            core = Image.fromarray((core * 255).astype(np.uint8)).filter(
                ImageFilter.MinFilter(int(r['fill']['erode'] * S / 4) * 2 + 1)).resize((W, H), Image.BILINEAR)
            core = np.asarray(core, dtype=np.float32) / 255
            for ex in r.get('fill_exclude', []):
                core = core * (1 - poly_mask((W, H), [ex], S, 2))
            light_neutral = smooth(L, r['fill']['l_lo'], r['fill']['l_hi']) * (1 - smooth(C, 12, 22))
            guard = smooth(a, -3, 2) if r['fill'].get('red_guard', True) else 1.0
            w = np.maximum(w, core * (1 - light_neutral) * guard)
        if 'band' in r:
            bd = r['band']
            xs = np.arange(W, dtype=np.float32)[None, :] / S
            ys = np.arange(H, dtype=np.float32)[:, None] / S
            Lb = np.asarray(Image.fromarray(np.clip(L * 2.55, 0, 255).astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(6 * S)), dtype=np.float32) / 2.55
            yc = bd['y'] + bd['sag'] * (xs - bd['x0']) ** 2 + bd['fold'] * (Lb - float(np.median(Lb[w > .5])))
            w = w * (1 - smooth(np.abs(ys - yc), bd['half'] - 1.2, bd['half'] + 1.2))
        if not r.get('everything_else'):
            taken = np.maximum(taken, poly_mask((W, H), r['polygons'], S, 3))
        sel = w > 0.5
        if not sel.any():
            print(r['name'], 'empty'); continue
        Lm, Cm = float(np.median(L[sel])), float(np.median(C[sel]))
        tl, ta, tb = color.rgb2lab(np.array([[[int(r['target'][i:i + 2], 16) / 255 for i in (1, 3, 5)]]]))[0, 0]
        tc, th = float(np.hypot(ta, tb)), float(np.arctan2(tb, ta))
        # Multiplicative: keeps the relative depth of folds when the level is raised or lowered.
        Ln = r['l_median'] * (np.maximum(L, 0.5) / Lm) ** r.get('gamma', 1.0)
        top = r.get('l_max', 92)
        Ln = np.where(Ln > top - 15, top - 15 * np.exp(-(Ln - (top - 15)) / 15), Ln)
        Cn = r.get('chroma', tc) * np.clip(C / max(Cm, 1e-3), 0.25, 1.35) * np.clip(Ln / 14, 0, 1)
        new = np.stack([Ln, Cn * np.cos(th), Cn * np.sin(th)], -1)
        w = w * (1 - total)                      # earlier regions win where they overlap
        out = out * (1 - w[..., None]) + new * w[..., None]
        total = np.clip(total + w, 0, 1)
        print(f"{r['name']}: {sel.mean() * 100:.2f} % of pixels, source L median {Lm:.1f}, C median {Cm:.1f}")

    rgb = np.clip(color.lab2rgb(out) * 255 + 0.5, 0, 255).astype(np.uint8)
    rgb[total == 0] = np.asarray(src)[total == 0]   # untouched pixels stay bit-identical before encoding
    res = Image.fromarray(rgb)
    res.save(cfg['out'] + '.jpg', quality=95, subsampling=0)
    Image.fromarray((total * 255).astype(np.uint8)).save(cfg['out'] + '__mask.png')
    pv = res.copy(); pv.thumbnail((900, 900)); pv.save(cfg['out'] + '__preview.jpg', quality=88)
    print(f"changed pixels (w>0): {(total > 0).mean() * 100:.2f} %  time {time.time() - t0:.1f} s  size {W}x{H}")


if __name__ == '__main__':
    main()
