"""Build the museum site from the rendered walkthrough.

    python scripts/build_sitio.py [--step 2] [--width 1280] [--quality 72] [--intro clip.mp4]

Reads museo/render/frames/f_####.jpg and museo/sala.json, writes museo/sitio/ with the frames as WebP
(every --step-th frame) and a single index.html. The site is static: any web host can serve the folder.
"""
import argparse
import glob
import json
import os
import shutil

from PIL import Image


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--step', type=int, default=3); ap.add_argument('--width', type=int, default=1280)
    ap.add_argument('--quality', type=int, default=72)
    ap.add_argument('--intro', default='tesseract/intro/intro.mp4', help='entrance clip shown once over the first frame; skipped if the file is missing')
    a = ap.parse_args()
    sala = json.load(open('museo/sala.json', encoding='utf-8'))
    src = sorted(glob.glob('museo/render/frames/f_*.jpg'))
    if len(src) < sala['frames']:
        raise SystemExit(f'faltan cuadros: hay {len(src)} de {sala["frames"]}')
    out = 'museo/sitio'
    os.makedirs(out + '/frames', exist_ok=True)
    for f in glob.glob(out + '/frames/*.webp'):
        os.remove(f)
    keep = list(range(0, sala['frames'], a.step))
    if keep[-1] != sala['frames'] - 1:
        keep.append(sala['frames'] - 1)
    names, total = [], 0
    for k, i in enumerate(keep):
        im = Image.open(src[i]).convert('RGB')
        if im.width > a.width:
            im = im.resize((a.width, round(im.height * a.width / im.width)), Image.LANCZOS)
        name = f'frames/f_{k:04d}.webp'
        im.save(f'{out}/{name}', 'WEBP', quality=a.quality, method=5)
        total += os.path.getsize(f'{out}/{name}'); names.append(name)

    def idx(frame):                                   # Blender frame (1-based) -> index in the kept list
        return min(range(len(keep)), key=lambda k: abs(keep[k] - (frame - 1)))

    Image.MAX_IMAGE_PIXELS = None
    for d in ('paradas', 'obras'):
        os.makedirs(f'{out}/{d}', exist_ok=True)
        for f in glob.glob(f'{out}/{d}/*.webp'):
            os.remove(f)

    def webp(src_path, dst, width, quality):
        im = Image.open(src_path).convert('RGB')
        if im.width > width:
            im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
        im.save(f'{out}/{dst}', 'WEBP', quality=quality, method=5)
        return os.path.getsize(f'{out}/{dst}')

    paradas, extra = [], 0
    for k, p in enumerate(sala['paradas']):
        q = {'id': p['id'], 'in': idx(p['frame_in']), 'out': idx(p['frame_out'])}
        if 'titulo' in p:
            q.update({'titulo': p['titulo'], 'autor': p['autor']})
        if os.path.exists(p.get('still', '')):          # sharp picture shown while standing at the stop
            q['still'] = f'paradas/p_{k:02d}.webp'; extra += webp(p['still'], q['still'], 2560, 84)
        if 'fuente' in p:                               # the work itself, to look at closely
            q['obra'] = f'obras/o_{k:02d}.webp'; extra += webp(p['fuente'], q['obra'], 2600, 86)
        paradas.append(q)
    total += extra
    data = {'frames': names, 'paradas': paradas}
    if os.path.exists(a.intro):
        shutil.copyfile(a.intro, out + '/intro.mp4'); data['intro'] = 'intro.mp4'; total += os.path.getsize(out + '/intro.mp4')
    elif os.path.exists(out + '/intro.mp4'):
        os.remove(out + '/intro.mp4')
    html = open('scripts/sitio_template.html', encoding='utf-8').read().replace('/*DATA*/', json.dumps(data, ensure_ascii=False))
    open(out + '/index.html', 'w', encoding='utf-8').write(html)
    print(f'{len(names)} cuadros, {total / 1e6:.1f} MB, {len(paradas)} paradas -> {out}/index.html')


if __name__ == '__main__':
    main()
