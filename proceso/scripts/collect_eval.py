"""Evaluation bookkeeping: build the hybrids, make previews, measure every output and write the run log.

    python scripts/collect_eval.py

For each case and seed 1-5:
  code    research/runs/code/<case>__code__s<k>__r<n>.jpg   (the agent's final delivery, from its config "out")
  edit    research/runs/edit/<case>__edit__s<k>.png          (Nano Banana 2, downloaded from Comfy Cloud)
  hybrid  research/runs/hybrid/<case>__hybrid__s<k>.jpg      (edit pasted over the original with the code mask
                                                             of the same seed, scripts/composite.py)
Appends one line per run to research/runs.jsonl (ids e####), skipping ids already present, so it is safe
to re-run. Metrics come from scripts/measure.py; agent tokens and time from research/runs/agent-usage.jsonl;
credits from the Comfy Cloud billing feed copied below.
"""
import json
import os
import subprocess
import sys

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
PY = sys.executable
CASES = ['prato', 'arnolfini', 'baco', 'atenas']
# credits_used per job from get_billing_activity, 2026-11-17 (model gemini-3.1-flash-image)
CREDITS = {('prato', 1): 38.45, ('prato', 2): 38.45, ('prato', 3): 38.45, ('prato', 4): 38.45, ('prato', 5): 38.45,
           ('arnolfini', 1): 38.46, ('arnolfini', 2): 38.46, ('arnolfini', 3): 38.46, ('arnolfini', 4): 38.46,
           ('arnolfini', 5): 38.46, ('baco', 1): 38.52, ('baco', 2): 38.46, ('baco', 3): 38.46, ('baco', 4): 38.46,
           ('baco', 5): 38.46, ('atenas', 1): 38.51, ('atenas', 2): 38.46, ('atenas', 3): 38.46, ('atenas', 4): 38.46,
           ('atenas', 5): 38.46}


def run(args):
    r = subprocess.run([PY] + args, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[-800:] or r.stdout[-800:])
    return r.stdout


def preview(path):
    p = os.path.splitext(path)[0] + '__preview.jpg'
    if not os.path.exists(p):
        im = Image.open(path).convert('RGB'); im.thumbnail((900, 900)); im.save(p, quality=88)
    return p


def measure(case, path):
    return json.loads(run(['scripts/measure.py', case, path, '--json']))['summary']


def main():
    commit = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip()
    usage = {}
    for line in open('research/runs/agent-usage.jsonl', encoding='utf-8'):
        u = json.loads(line); usage[(u['case'], u['seed'])] = u
    jobs = {}
    for line in open('research/runs/edit/jobs.tsv', encoding='utf-8'):
        c, s, j = line.split(); jobs[(c, int(s))] = j
    log = 'research/runs.jsonl'
    seen = {json.loads(l)['id'] for l in open(log, encoding='utf-8') if l.strip()}
    os.makedirs('research/runs/hybrid', exist_ok=True)
    n = 0
    for ci, case in enumerate(CASES):
        src = f'research/sources/work/{case}.jpg'
        for seed in range(1, 6):
            cfg = f'research/runs/code/{case}__code__s{seed}.json'
            out = json.load(open(cfg, encoding='utf-8'))['out']
            code, mask = out + '.jpg', out + '__mask.png'
            edit = f'research/runs/edit/{case}__edit__s{seed}.png'
            hyb = f'research/runs/hybrid/{case}__hybrid__s{seed}'
            ecc = None
            if not os.path.exists(hyb + '.jpg'):
                o = run(['scripts/composite.py', src, edit, mask, hyb])
                for l in o.splitlines():
                    if l.startswith('ECC correlation'):
                        ecc = float(l.split()[2].rstrip(';'))
                open(hyb + '__log.txt', 'w', encoding='utf-8').write(o)
            elif os.path.exists(hyb + '__log.txt'):
                for l in open(hyb + '__log.txt', encoding='utf-8'):
                    if l.startswith('ECC correlation'):
                        ecc = float(l.split()[2].rstrip(';'))
            preview(edit)
            u = usage[(case, seed)]
            rows = [
                ('code', code, {'tokens_total': u['tokens'], 'script_runs': u['script_runs']}, u['time_s'], cfg,
                 u.get('note', '')),
                ('edit', edit, {'credits': CREDITS[(case, seed)]}, None, 'research/briefs/edit-prompts.md',
                 f'Comfy Cloud, GeminiImage2Node, Nano Banana 2, 4K, job {jobs[(case, seed)]}. Tiempo no medido.'),
                ('hybrid', hyb + '.jpg', {'credits': 0.0, 'ecc_correlation': ecc}, None,
                 'scripts/composite.py --grow 6 --feather 5',
                 f'Ropa de edit s{seed} pegada sobre el original con la mascara de code s{seed}. Compuesto en local '
                 f'con registro ECC, no en el pipeline de Comfy Cloud. No suma creditos: reutiliza la edicion.'),
            ]
            for k, (cond, path, extra, t, config, note) in enumerate(rows):
                rid = f'e{ci * 15 + (seed - 1) * 3 + k + 1:04d}'
                if rid in seen:
                    continue
                m = measure(case, path)
                m.update({a: b for a, b in extra.items() if b is not None})
                rec = {'id': rid, 'condition': cond, 'case': case, 'seed': seed, 'view': 'full', 'metrics': m,
                       'time_s': t, 'cost_usd': None, 'status': 'ok', 'commit': commit, 'config': config,
                       'output': path, 'note': note}
                with open(log, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + '\n')
                n += 1
                print(rid, cond, case, seed, {a: round(b, 2) for a, b in m.items() if isinstance(b, float)}, flush=True)
    print('lineas nuevas:', n)


if __name__ == '__main__':
    main()
