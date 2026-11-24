"""Combined method without a hand-drawn mask: keep from the AI edit only what it clearly recoloured.

    python scripts/auto_hybrid.py <original> <edited> <out-prefix> [--thr 14] [--min-area 0.0008]

The edit is resized and registered to the original (same ECC as composite.py, estimated on the whole
picture at quarter size). The mask is where hue/chroma moved more than --thr in CIELAB (a*, b* distance,
ignoring lightness, on a slightly blurred copy so paint grain does not vote), cleaned by closing and
opening, dropping specks smaller than --min-area of the picture and filling small holes. Then it calls the
same paste as composite.py: grown 6 px, feathered 5 px. Outside the mask the result is the original.

Writes <out>.jpg, <out>__preview.jpg and <out>__mask.png. Faster and cheaper than drawing the mask, but it
trusts the model: whatever the edit recoloured by mistake outside the garments comes through.
"""
import argparse
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image
from skimage import color

Image.MAX_IMAGE_PIXELS = None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('original'); ap.add_argument('edited'); ap.add_argument('out')
    ap.add_argument('--thr', type=float, default=14); ap.add_argument('--min-area', type=float, default=0.0008)
    a = ap.parse_args()
    src = np.asarray(Image.open(a.original).convert('RGB'))
    H, W = src.shape[:2]
    ed = np.asarray(Image.open(a.edited).convert('RGB').resize((W, H), Image.LANCZOS))
    q = 4
    g0 = cv2.cvtColor(cv2.resize(src, (W // q, H // q), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    g1 = cv2.cvtColor(cv2.resize(ed, (W // q, H // q), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
    warp = np.eye(2, 3, dtype=np.float32)
    try:
        cc, warp = cv2.findTransformECC(g0, g1, warp, cv2.MOTION_AFFINE,
                                        (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), None, 5)
        warp[:, 2] *= q
        ed = cv2.warpAffine(ed, warp, (W, H), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REFLECT)
        print(f'ECC correlation {cc:.4f}')
    except cv2.error as e:
        print('ECC failed, using the resized edit as is:', str(e)[:80])
    s = 2                                             # measure the colour move at half size
    sm = lambda im: cv2.GaussianBlur(cv2.resize(im, (W // s, H // s), interpolation=cv2.INTER_AREA), (0, 0), 2.0)
    l0 = color.rgb2lab(sm(src).astype(np.float32) / 255); l1 = color.rgb2lab(sm(ed).astype(np.float32) / 255)
    d = np.hypot(l1[..., 1] - l0[..., 1], l1[..., 2] - l0[..., 2])
    m = (d > a.thr).astype(np.uint8)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    m = cv2.morphologyEx(cv2.morphologyEx(m, cv2.MORPH_CLOSE, k), cv2.MORPH_OPEN, k)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    area = m.size * a.min_area
    keep = np.zeros_like(m)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] >= area:
            keep[lab == i] = 1
    inv = 1 - keep                                    # fill holes smaller than the same area
    n, lab, stats, _ = cv2.connectedComponentsWithStats(inv, 8)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] < area:
            keep[lab == i] = 1
    mask = cv2.resize(keep * 255, (W, H), interpolation=cv2.INTER_LINEAR)
    Image.fromarray(mask).save(a.out + '__mask.png')
    print(f'mask covers {keep.mean() * 100:.2f} % of the picture')
    r = subprocess.run([sys.executable, 'scripts/composite.py', a.original, a.edited, a.out + '__mask.png', a.out],
                       capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr[-400:])


if __name__ == '__main__':
    main()
