"""Gather every number the final report uses into research/report-data.json.

    python scripts/build_report_data.py

Sources: research/results.json (experiment), research/eval-results.json (blind evaluation),
research/runs.jsonl (credits, mesh sizes), research/runs/agent-usage.jsonl (agent tokens and time),
tesseract/intro/.tesseract-work/export.log (export time), museo/ (frames, site size) and
research/report-extra.json (the few figures that only exist in a written log, each with its source).
render_report.py then fills research/report.template.md from this file, so no number is typed by hand.
"""
import glob
import json
import os
from datetime import datetime

R = 'research'
load = lambda p: json.load(open(p, encoding='utf-8'))
runs = [json.loads(l) for l in open(f'{R}/runs.jsonl', encoding='utf-8')]
cred = lambda pre: round(sum((r['metrics'].get('credits') or 0) for r in runs if r['id'].startswith(pre)), 2)
usage = [json.loads(l) for l in open(f'{R}/runs/agent-usage.jsonl', encoding='utf-8')]
ev = load(f'{R}/eval-results.json')['evaluators']['Mari']
t0, t1 = (datetime.fromisoformat(ev[k].replace('Z', '+00:00')) for k in ('started', 'finished'))
ev['duration_s'] = (t1 - t0).total_seconds()
ev['answers'] = ev['pairs_answered'] + ev['singles_answered']
for p in ev['pairs'].values():
    p['n_pairs'] = p['n_decided'] + p['undecided']
export = [json.loads(l) for l in open('tesseract/intro/.tesseract-work/export.log', encoding='utf-8') if l.strip().startswith('{')]
done = [e for e in export if e.get('type') == 'complete'][-1]
site = [os.path.getsize(f) for f in glob.glob('museo/sitio/**/*', recursive=True) if os.path.isfile(f)]
data = {
    'exp': load(f'{R}/results.json'),
    'eval': ev,
    'agents': {'n': len(usage), 'tokens_total': sum(u['tokens'] for u in usage),
               'tokens_M': sum(u['tokens'] for u in usage) / 1e6, 'time_s_total': sum(u['time_s'] for u in usage),
               'time_h': sum(u['time_s'] for u in usage) / 3600},
    'credits': {'pilots': cred('p'), 'eval_edits': cred('e'), 'second_batch': cred('a'), 'model3d': cred('m'),
                'total': round(cred('p') + cred('e') + cred('a') + cred('m'), 2)},
    'runs': {'total': len(runs), 'pilots': sum(r['id'].startswith('p') for r in runs),
             'eval': sum(r['id'].startswith('e') for r in runs), 'second_batch': sum(r['id'].startswith('a') for r in runs),
             'model3d': sum(r['id'].startswith('m') for r in runs),
             'model3d_failed': sum(r['id'].startswith('m') and r['status'] == 'error' for r in runs)},
    'm': {r['id']: r['metrics'] for r in runs if r['id'].startswith('m')},
    'tess': {'frames': done['total'], 'export_s': done['elapsedSeconds'], 'export_min': done['elapsedSeconds'] / 60,
             'spf': done['elapsedSeconds'] / done['total']},
    'room': {'frames': len(glob.glob('museo/render/frames/*.jpg')), 'works': len(load('museo/seleccion.json').get('obras', load('museo/seleccion.json')))},
    'site': {'frames': len(glob.glob('museo/sitio/frames/*')), 'mb': sum(site) / 1e6},
    'extra': load(f'{R}/report-extra.json'),
}
json.dump(data, open(f'{R}/report-data.json', 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print('report-data.json:', {k: (v if not isinstance(v, dict) or len(str(v)) < 200 else '...') for k, v in data.items() if k not in ('exp', 'eval', 'extra')})
