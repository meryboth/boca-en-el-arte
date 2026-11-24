"""Paint over the crest and sponsor marks the reconstruction left on the corner towers.

    python scripts/tapar_logos.py <texture.png> <faces.json> <out.png>

Inside the UV triangles listed by blender_glb_caras_esquina.py, every pixel that is not blue (red or green
channel above the blue one) takes the median blue of the same area. Brand decision: no crest, no sponsors.
"""
import json, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

tex, faces, out = sys.argv[1:4]
im = Image.open(tex).convert('RGB'); W, H = im.size
m = Image.new('L', im.size, 0); d = ImageDraw.Draw(m)
for t in json.load(open(faces)):
    d.polygon([(u * W, (1 - v) * H) for u, v in t], fill=255)
m = m.filter(ImageFilter.MaxFilter(5))
a = np.asarray(im).astype(int); mask = np.asarray(m) > 0
r, g, b = a[..., 0], a[..., 1], a[..., 2]
blue = mask & (b > r + 25) & (b > g + 10)
mark = mask & ~blue & ((r > b) | (g > b + 5) | (r + g + b > 480))
fill = np.median(a[blue], axis=0)
a[mark] = fill
Image.fromarray(a.astype(np.uint8)).save(out)
print(f'area {mask.sum()} px, painted {mark.sum()} px with {fill.astype(int).tolist()}')
