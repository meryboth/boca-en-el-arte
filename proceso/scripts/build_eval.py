"""Build the blind evaluation page: anonymised images + one self-contained index.html.

    python scripts/build_eval.py

Writes research/eval/ (index.html and img/<id>.jpg at 1600 px) and research/eval-key.json, the only place
that says which method produced each image. The key is NOT inside research/eval/, so the folder can be
handed to evaluators as is. Image ids come from a fixed seed, so re-running gives the same ids.

Part 1 (pairs): same painting and seed, two methods, "which one would you hang?". 3 comparisons x 4
paintings x 5 seeds = 60 pairs. Part 2 (singles): each of the 60 images alone, "mark anything that looks
digitally retouched, or say nothing looks off". Order and left/right are shuffled per evaluator in the page.
"""
import json
import os
import random

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
CASES = ['prato', 'arnolfini', 'baco', 'atenas']
TITLES = {'prato': 'Madonna del Prato', 'arnolfini': 'Matrimonio Arnolfini', 'baco': 'Baco y Ariadna',
          'atenas': 'La escuela de Atenas'}
COMPARISONS = [('code', 'edit'), ('hybrid', 'edit'), ('hybrid', 'code')]
OUT = 'research/eval'


def path_of(case, cond, seed):
    if cond == 'code':
        return json.load(open(f'research/runs/code/{case}__code__s{seed}.json', encoding='utf-8'))['out'] + '.jpg'
    if cond == 'edit':
        return f'research/runs/edit/{case}__edit__s{seed}.png'
    return f'research/runs/hybrid/{case}__hybrid__s{seed}.jpg'


def main():
    rng = random.Random(20261117)
    os.makedirs(OUT + '/img', exist_ok=True)
    ids = rng.sample(range(1000, 9999), 60)
    key, images, k = {}, {}, 0
    for case in CASES:
        for seed in range(1, 6):
            for cond in ('code', 'edit', 'hybrid'):
                iid = f'im{ids[k]}'; k += 1
                src = path_of(case, cond, seed)
                dst = f'{OUT}/img/{iid}.jpg'
                if not os.path.exists(dst):
                    im = Image.open(src).convert('RGB'); im.thumbnail((1600, 1600), Image.LANCZOS)
                    im.save(dst, quality=88)
                key[iid] = {'case': case, 'condition': cond, 'seed': seed, 'source': src}
                images[(case, cond, seed)] = iid
    pairs = []
    for case in CASES:
        for seed in range(1, 6):
            for a, b in COMPARISONS:
                pairs.append({'id': f'p{len(pairs) + 1:02d}', 'case': case, 'a': images[(case, a, seed)],
                              'b': images[(case, b, seed)]})
    key_pairs = {p['id']: {'case': p['case'], 'a': key[p['a']]['condition'], 'b': key[p['b']]['condition'],
                           'seed': key[p['a']]['seed']} for p in pairs}
    json.dump({'images': key, 'pairs': key_pairs}, open('research/eval-key.json', 'w', encoding='utf-8'), indent=1)
    singles = [{'id': i, 'case': v['case']} for i, v in key.items()]
    data = {'titles': TITLES, 'pairs': pairs, 'singles': singles}
    html = open('scripts/eval_template.html', encoding='utf-8').read().replace('/*DATA*/', json.dumps(data))
    open(OUT + '/index.html', 'w', encoding='utf-8').write(html)
    size = sum(os.path.getsize(f'{OUT}/img/{f}') for f in os.listdir(OUT + '/img')) / 1e6
    print(f'{len(pairs)} pares, {len(singles)} imagenes, {size:.1f} MB en {OUT}/img')


if __name__ == '__main__':
    main()
