"""Hybrid: paste only the garment area of an AI-edited painting over the untouched original.

    python scripts/composite.py <original> <edited> <garment-mask.png> <out-prefix> [--grow PX] [--feather PX]

The edited image is resized to the original, then registered to it with an affine transform estimated
(ECC, on a quarter-size grey image) only on the area outside the mask, where both should still match.
The mask is the one scripts/recolor.py writes (white = garment). It is grown and feathered so the seam
falls just outside the garment edge. Outside the grown mask the output is the original, bit for bit
before encoding. Writes <out>.jpg and a 900 px preview; prints the transform and timing.
"""
import argparse
import time

import cv2
import numpy as np
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('original'); ap.add_argument('edited'); ap.add_argument('mask'); ap.add_argument('out')
    ap.add_argument('--grow', type=float, default=6, help='grow the mask by this many px (original scale)')
    ap.add_argument('--feather', type=float, default=5, help='gaussian sigma of the seam, px')
    ap.add_argument('--no-register', action='store_true')
    a = ap.parse_args()
    t0 = time.time()

    src = np.asarray(Image.open(a.original).convert('RGB'))
    H, W = src.shape[:2]
    ed_im = Image.open(a.edited).convert('RGB')
    print(f'edited {ed_im.size[0]}x{ed_im.size[1]} -> {W}x{H}')
    ed = np.asarray(ed_im.resize((W, H), Image.LANCZOS))
    m = np.asarray(Image.open(a.mask).convert('L').resize((W, H), Image.BILINEAR), dtype=np.float32) / 255

    warp = np.eye(2, 3, dtype=np.float32)
    if not a.no_register:
        q = 4
        g0 = cv2.cvtColor(cv2.resize(src, (W // q, H // q), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
        g1 = cv2.cvtColor(cv2.resize(ed, (W // q, H // q), interpolation=cv2.INTER_AREA), cv2.COLOR_RGB2GRAY)
        keep = (cv2.resize(m, (W // q, H // q)) < 0.05).astype(np.uint8)
        keep = cv2.erode(keep, np.ones((9, 9), np.uint8))
        crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-7)
        cc, warp = cv2.findTransformECC(g0, g1, warp, cv2.MOTION_AFFINE, crit, keep, 5)
        warp[:, 2] *= q
        print(f'ECC correlation {cc:.4f}; affine {np.round(warp, 5).tolist()}')
        ed = cv2.warpAffine(ed, warp, (W, H), flags=cv2.INTER_LANCZOS4 | cv2.WARP_INVERSE_MAP,
                            borderMode=cv2.BORDER_REFLECT)

    hard = (m > 0.35).astype(np.uint8)
    k = int(round(a.grow)) * 2 + 1
    if k > 1:
        hard = cv2.dilate(hard, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    w = cv2.GaussianBlur(hard.astype(np.float32), (0, 0), a.feather) if a.feather > 0 else hard.astype(np.float32)
    w[w < 0.004] = 0
    out = (src * (1 - w[..., None]) + ed * w[..., None] + 0.5).astype(np.uint8)
    out[w == 0] = src[w == 0]

    res = Image.fromarray(out)
    res.save(a.out + '.jpg', quality=95, subsampling=0)
    pv = res.copy(); pv.thumbnail((900, 900)); pv.save(a.out + '__preview.jpg', quality=88)
    print(f'pasted area {(w > 0).mean() * 100:.2f} %  time {time.time() - t0:.1f} s')


if __name__ == '__main__':
    main()
