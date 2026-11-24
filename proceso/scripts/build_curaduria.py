"""Build the curation page: every candidate work, labelled, to pick what hangs in the museum.

    python scripts/build_curaduria.py

Writes museo/curaduria/index.html. Unlike the blind evaluation, this page says which method made each
image. It reuses the 1600 px images in research/eval/img and makes its own for the Julius II variants.
The page downloads seleccion.json; save it as museo/seleccion.json.
"""
import json
import os

from PIL import Image

Image.MAX_IMAGE_PIXELS = None
OUT = 'museo/curaduria'
TITLES = {'prato': 'Madonna del Prato — Rafael', 'arnolfini': 'Matrimonio Arnolfini — Van Eyck',
          'baco': 'Baco y Ariadna — Tiziano', 'atenas': 'La escuela de Atenas — Rafael',
          'julio2': 'Retrato de Julio II — Rafael'}
METHOD = {'code': 'Código (Fable 5.2)', 'edit': 'Nano Banana 2', 'hybrid': 'Combinado'}


def main():
    os.makedirs(OUT + '/img', exist_ok=True)
    key = json.load(open('research/eval-key.json', encoding='utf-8'))['images']
    items = []
    for iid, v in key.items():
        items.append({'id': iid, 'case': v['case'], 'method': v['condition'], 'label': f"{METHOD[v['condition']]} · intento {v['seed']}",
                      'img': f'../../research/eval/img/{iid}.jpg', 'source': v['source']})
    for name, method, label in (('julio2__code__sin-sillon', 'code', 'Código (Fable 5.2)'),
                                ('julio2__hybrid-a__sin-sillon', 'hybrid', 'Combinado · edición A (franja bordada)'),
                                ('julio2__hybrid-b__sin-sillon', 'hybrid', 'Combinado · edición B (franja lisa)')):
        src = f'museo/obras/{name}.jpg'
        dst = f'{OUT}/img/{name}.jpg'
        if not os.path.exists(dst):
            im = Image.open(src).convert('RGB'); im.thumbnail((1600, 1600), Image.LANCZOS); im.save(dst, quality=88)
        items.append({'id': name, 'case': 'julio2', 'method': method, 'label': label, 'img': f'img/{name}.jpg', 'source': src})
    order = {'hybrid': 0, 'edit': 1, 'code': 2}
    items.sort(key=lambda x: (list(TITLES).index(x['case']), order[x['method']], x['label']))
    html = TEMPLATE.replace('/*DATA*/', json.dumps({'titles': TITLES, 'items': items}, ensure_ascii=False))
    open(OUT + '/index.html', 'w', encoding='utf-8').write(html)
    print(len(items), 'candidatas ->', OUT + '/index.html')


TEMPLATE = r"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Curaduría del museo</title>
<style>
  :root { --bg:#f6f4ef; --fg:#1d1b18; --muted:#6a655c; --line:#d9d4c8; --card:#fff; --accent:#103f79; --gold:#c98f0c; }
  @media (prefers-color-scheme: dark) { :root { --bg:#171614; --fg:#eeeae2; --muted:#a39d91; --line:#3a3731; --card:#211f1c; --accent:#6ea0e6; --gold:#f3b229; } }
  * { box-sizing:border-box; } body { margin:0; background:var(--bg); color:var(--fg); font:16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif; }
  main { max-width:1500px; margin:0 auto; padding:20px 16px 110px; }
  h1 { font-size:1.5rem; margin:0 0 6px; } h2 { font-size:1.15rem; margin:28px 0 10px; } p { margin:6px 0; max-width:70ch; } .muted { color:var(--muted); }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(230px,1fr)); gap:12px; }
  .tile { border:3px solid var(--line); border-radius:10px; background:var(--card); padding:0; overflow:hidden; cursor:pointer; text-align:left; color:inherit; font:inherit; }
  .tile img { display:block; width:100%; aspect-ratio:1; object-fit:contain; background:#111; }
  .tile span { display:block; padding:8px 10px; font-size:.9rem; }
  .tile[aria-pressed=true] { border-color:var(--gold); box-shadow:0 0 0 2px var(--gold); }
  .tile:focus-visible, button:focus-visible { outline:3px solid var(--accent); outline-offset:2px; }
  .zoom { float:right; font-size:.8rem; color:var(--accent); text-decoration:underline; }
  footer { position:fixed; left:0; right:0; bottom:0; background:var(--card); border-top:1px solid var(--line); padding:12px 16px; display:flex; gap:14px; align-items:center; flex-wrap:wrap; }
  button.primary { font:inherit; padding:10px 18px; border-radius:8px; border:0; background:var(--accent); color:#fff; cursor:pointer; } button.primary:disabled { opacity:.45; cursor:default; }
  dialog { border:0; padding:0; background:#000; max-width:98vw; max-height:98vh; } dialog img { display:block; max-width:98vw; max-height:96vh; } dialog::backdrop { background:#000c; }
</style></head><body><main>
<h1>Curaduría del museo</h1>
<p>Tocá las obras que querés colgar. Podés elegir las que quieras, varias de la misma pintura si te gustan. "Ampliar" abre la imagen grande sin seleccionarla.</p>
<p class="muted">Dentro de cada pintura van primero las combinadas, después las de Nano Banana 2 y al final las de código.</p>
<div id="groups"></div></main>
<footer><strong id="count">0 obras elegidas</strong><button class="primary" id="dl" disabled>Descargar mi selección</button><span class="muted">Guardá el archivo como <code>museo/seleccion.json</code>.</span></footer>
<dialog id="zoom"><img id="zoomimg" alt="Obra ampliada"></dialog>
<script>
const DATA = /*DATA*/; const sel = new Set(); const $ = id => document.getElementById(id);
const groups = $('groups');
for (const c of Object.keys(DATA.titles)) {
  const h = document.createElement('h2'); h.textContent = DATA.titles[c]; groups.appendChild(h);
  const g = document.createElement('div'); g.className = 'grid'; groups.appendChild(g);
  for (const it of DATA.items.filter(x => x.case === c)) {
    const b = document.createElement('button'); b.className = 'tile'; b.setAttribute('aria-pressed', 'false');
    const img = document.createElement('img'); img.src = it.img; img.loading = 'lazy'; img.alt = DATA.titles[c] + ', ' + it.label;
    const s = document.createElement('span'); s.textContent = it.label;
    const z = document.createElement('a'); z.className = 'zoom'; z.textContent = 'Ampliar'; z.href = '#';
    z.onclick = e => { e.preventDefault(); e.stopPropagation(); $('zoomimg').src = it.img; $('zoom').showModal(); };
    s.appendChild(z); b.append(img, s);
    b.onclick = () => { sel.has(it.id) ? sel.delete(it.id) : sel.add(it.id); b.setAttribute('aria-pressed', sel.has(it.id)); update(); };
    g.appendChild(b);
  }
}
function update() { $('count').textContent = sel.size + (sel.size === 1 ? ' obra elegida' : ' obras elegidas'); $('dl').disabled = sel.size === 0; }
$('zoom').onclick = () => $('zoom').close();
$('dl').onclick = () => {
  const out = { fecha: new Date().toISOString(), obras: DATA.items.filter(x => sel.has(x.id)).map(x => ({ id: x.id, pintura: x.case, metodo: x.method, etiqueta: x.label, fuente: x.source })) };
  const a = document.createElement('a'); a.href = URL.createObjectURL(new Blob([JSON.stringify(out, null, 1)], { type: 'application/json' }));
  a.download = 'seleccion.json'; document.body.appendChild(a); a.click(); a.remove();
};
</script></body></html>
"""

if __name__ == '__main__':
    main()
