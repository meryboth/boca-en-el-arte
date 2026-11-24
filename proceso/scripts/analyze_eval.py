"""Analyse blind-evaluation answers against the key.

    python scripts/analyze_eval.py [--out research/eval-results.json]

Reads every research/eval-respuestas/respuestas__*.json and research/eval-key.json.

Part 1 (pairs). For each comparison "A vs B" (hybrid vs edit, hybrid vs code, code vs edit): wins of A,
wins of B, undecided, win rate of A over decided pairs, and a bootstrap 95 % interval of that rate
resampling pairs (10 000 resamples, fixed seed). Verdict: a winner only if the interval excludes 0.5
and there are at least 5 decided pairs. Also broken down by painting (n = 5 pairs each: described, never
called). Left/right bias and answer times are reported because they say how much to trust the data.

Part 2 (singles). Share of images of each method flagged as "something looks off", with the same bootstrap.

With one evaluator the interval reflects variation between attempts and paintings, not between people.
"""
import argparse
import glob
import json
import random
import statistics

COMPARISONS = [('hybrid', 'edit'), ('hybrid', 'code'), ('code', 'edit')]
CASES = ['prato', 'arnolfini', 'baco', 'atenas']


def boot(xs, reps=10000, seed=7):
    if not xs:
        return None, None
    rng = random.Random(seed)
    m = sorted(sum(xs[rng.randrange(len(xs))] for _ in xs) / len(xs) for _ in range(reps))
    return m[int(0.025 * reps)], m[int(0.975 * reps)]


def rate_block(wins):
    """wins: list of 1 (first method chosen) / 0 (second chosen), decided pairs only."""
    n = len(wins)
    if n == 0:
        return {'n_decided': 0}
    lo, hi = boot(wins)
    r = sum(wins) / n
    verdict = 'sin ganador'
    if n >= 5 and lo > 0.5:
        verdict = 'gana el primero'
    elif n >= 5 and hi < 0.5:
        verdict = 'gana el segundo'
    return {'n_decided': n, 'wins_first': sum(wins), 'wins_second': n - sum(wins), 'rate_first': round(r, 3),
            'ci95': [round(lo, 3), round(hi, 3)], 'verdict': verdict}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='research/eval-results.json')
    a = ap.parse_args()
    key = json.load(open('research/eval-key.json', encoding='utf-8'))
    img = key['images']
    res = {'evaluators': {}}
    for f in sorted(glob.glob('research/eval-respuestas/respuestas__*.json')):
        d = json.load(open(f, encoding='utf-8'))
        ev = {'file': f, 'pairs_answered': len(d['answers1']), 'singles_answered': len(d['answers2']),
              'started': d.get('started'), 'finished': d.get('finished')}
        t1 = [x['ms'] for x in d['answers1']]; t2 = [x['ms'] for x in d['answers2']]
        ev['pairs_ms_median'] = statistics.median(t1) if t1 else None
        ev['singles_ms_median'] = statistics.median(t2) if t2 else None
        ev['singles_under_1s'] = sum(1 for t in t2 if t < 1000)
        dec = [x for x in d['answers1'] if x['choice'] != 'none']
        ev['chose_left'] = sum(1 for x in dec if x['choice'] == 'left')
        ev['chose_right'] = len(dec) - ev['chose_left']
        ev['undecided'] = len(d['answers1']) - len(dec)

        comp = {}
        for A, B in COMPARISONS:
            rows = []
            for x in d['answers1']:
                l, r = img[x['left']], img[x['right']]
                if {l['condition'], r['condition']} != {A, B}:
                    continue
                chosen = None if x['choice'] == 'none' else (l if x['choice'] == 'left' else r)['condition']
                rows.append((l['case'], chosen))
            block = rate_block([1 if c == A else 0 for _, c in rows if c])
            block['undecided'] = sum(1 for _, c in rows if c is None)
            block['by_case'] = {}
            for case in CASES:
                cs = [c for k, c in rows if k == case]
                block['by_case'][case] = {'first': sum(1 for c in cs if c == A), 'second': sum(1 for c in cs if c == B),
                                          'undecided': sum(1 for c in cs if c is None)}
            comp[f'{A}_vs_{B}'] = block
        ev['pairs'] = comp

        sing = {}
        for cond in ('code', 'edit', 'hybrid'):
            xs = [0 if x['nothing'] else 1 for x in d['answers2'] if img[x['image']]['condition'] == cond]
            lo, hi = boot(xs)
            sing[cond] = {'n': len(xs), 'flagged': sum(xs), 'rate': round(sum(xs) / len(xs), 3) if xs else None,
                          'ci95': [round(lo, 3), round(hi, 3)] if xs else None,
                          'flagged_images': [f"{img[x['image']]['case']} s{img[x['image']]['seed']}"
                                             for x in d['answers2']
                                             if not x['nothing'] and img[x['image']]['condition'] == cond]}
        ev['singles'] = sing
        res['evaluators'][d['evaluator']] = ev
    json.dump(res, open(a.out, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)

    for name, ev in res['evaluators'].items():
        print(f"== {name}: {ev['pairs_answered']} pares, {ev['singles_answered']} sueltas; "
              f"izq {ev['chose_left']} / der {ev['chose_right']} / sin decidir {ev['undecided']}; "
              f"mediana {ev['pairs_ms_median']:.0f} ms por par, {ev['singles_ms_median']:.0f} ms por suelta "
              f"({ev['singles_under_1s']} sueltas en menos de 1 s)")
        for k, b in ev['pairs'].items():
            print(f"  {k:15s} {b.get('wins_first')}-{b.get('wins_second')} (sin decidir {b['undecided']}) "
                  f"tasa {b.get('rate_first')} IC95 {b.get('ci95')} -> {b.get('verdict')}")
            print('     ' + '  '.join(f"{c}: {v['first']}-{v['second']}" + (f" ({v['undecided']} s/d)" if v['undecided'] else '')
                                      for c, v in b['by_case'].items()))
        for k, s in ev['singles'].items():
            print(f"  raro en {k:7s} {s['flagged']}/{s['n']} IC95 {s['ci95']}  {s['flagged_images']}")


if __name__ == '__main__':
    main()
