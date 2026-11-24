"""Cut the stadium out of an aerial photograph, for image-to-3D models that expect one object on a plain ground.

    python scripts/recorte_estadio.py <photo> <out-prefix> [--pad 0.06] [--size 1536]

The stadium is the only large thing in these photographs that is saturated blue, saturated yellow or
pitch green. The mask is those colours, closed with a large kernel so the grey concrete between them joins,
then only the largest blob is kept and its holes filled. The cut-out is placed on white, cropped to a square
around the blob with some padding, and saved as PNG with alpha and as JPEG on white.

It is a colour heuristic, not a segmentation model: blue roofs or pools touching the stadium come along,
and grey parts of the stadium far from any colour (the box building in some views) can be clipped. Look at
every result before using it.
"""
import argparse

import cv2
import numpy as np
from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('photo'); ap.add_argument('out')
    ap.add_argument('--pad', type=float, default=0.06); ap.add_argument('--size', type=int, default=1536)
    ap.add_argument('--close', type=float, default=0.022, help='closing kernel, as a fraction of the image width')
    a = ap.parse_args()
    rgb = np.asarray(Image.open(a.photo).convert('RGB'))
    H, W = rgb.shape[:2]
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    blue = (h > 100) & (h < 125) & (s > 110) & (v > 40)
    yellow = (h > 14) & (h < 32) & (s > 130) & (v > 120)
    green = (h > 35) & (h < 75) & (s > 90) & (v > 70)
    m = (blue | yellow | green).astype(np.uint8)
    k = max(3, int(W * a.close)) | 1
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    big = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    blob = (lab == big).astype(np.uint8)
    cnts, _ = cv2.findContours(blob, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    filled = np.zeros_like(blob); cv2.drawContours(filled, cnts, -1, 1, -1)          # fill holes
    filled = cv2.morphologyEx(filled, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    filled = cv2.dilate(filled, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9)))
    alpha = cv2.GaussianBlur(filled.astype(np.float32), (0, 0), 2.0)
    ys, xs = np.where(filled > 0)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    side = int(max(x1 - x0, y1 - y0) * (1 + 2 * a.pad))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    canvas = np.full((side, side, 4), 255, np.uint8); canvas[..., 3] = 0
    sx0, sy0 = cx - side // 2, cy - side // 2
    ax0, ay0, ax1, ay1 = max(sx0, 0), max(sy0, 0), min(sx0 + side, W), min(sy0 + side, H)
    canvas[ay0 - sy0:ay1 - sy0, ax0 - sx0:ax1 - sx0, :3] = rgb[ay0:ay1, ax0:ax1]
    canvas[ay0 - sy0:ay1 - sy0, ax0 - sx0:ax1 - sx0, 3] = (alpha[ay0:ay1, ax0:ax1] * 255).astype(np.uint8)
    im = Image.fromarray(canvas).resize((a.size, a.size), Image.LANCZOS)
    im.save(a.out + '.png')
    white = Image.new('RGB', im.size, (255, 255, 255)); white.paste(im, mask=im.split()[3])
    white.save(a.out + '.jpg', quality=92)
    print(f'{a.photo}: blob {filled.mean() * 100:.1f} % of the photo, crop {side}px -> {a.size}px')


if __name__ == '__main__':
    main()
