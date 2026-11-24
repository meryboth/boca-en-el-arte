"""Teaser of the museum, path-traced in Tesseract: six shots, one project each, joined with ffmpeg.

    python scripts/tesseract_teaser.py build            # one .tsrct per shot in tesseract/teaser/
    python scripts/tesseract_teaser.py preview          # one frame per shot (middle of the shot) -> Previews/
    python scripts/tesseract_teaser.py export [--only 3]  # path tracer, 48 samples, 24 fps, 1080p; skips shots already done
    python scripts/tesseract_teaser.py join             # teaser.mp4

One project per shot because a cut is then just a file boundary: no camera switching to get wrong, a failed
shot can be exported again alone, and every shot keeps its own log. The room, the lights and their powers
are the ones of the first entrance clip (tesseract/intro/.tesseract-work/scene.json); only the camera changes.
Positions are written in Blender metres (x across, y along the room, z up) and converted like the first clip.
"""
import argparse
import json
import math
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'tesseract', 'teaser')
WORK = os.path.join(OUT, '.tesseract-work')
TSRCT = os.path.join(os.environ['LOCALAPPDATA'], 'Tesseract', 'bin', 'tsrct.cmd')
MODEL = os.path.join(ROOT, 'museo', 'sala_ligera.blend')
BASE = os.path.join(ROOT, 'tesseract', 'intro', '.tesseract-work', 'scene.json')
FPS, SAMPLES, P = 24, 48, 100
STALL = 600                                              # seconds without a new frame before an export is killed
L = 38.6; YT = L - 6.0                                  # room length, table position


def S(x, y, z):
    return [round(x * P, 2), round(-z * P, 2), round(y * P, 2)]


def orbit(a0, a1, r, z, n=7):                           # arc around the table, angles from the entrance side
    return [(r * math.sin(math.radians(a0 + (a1 - a0) * k / (n - 1))), YT - r * math.cos(math.radians(a0 + (a1 - a0) * k / (n - 1))), z) for k in range(n)]


# name, seconds, field of view, camera path (2+ points, even spacing in time), point the camera looks at
SHOTS = [
    ('1_tunel',    3.0, 68, [(0, -4.6, 1.6), (0, -1.0, 1.6)],            (0, L, 1.75)),
    ('2_pared',    3.5, 62, [(-2.35, 1.6, 1.5), (-2.35, 8.2, 1.5)],       (-3.44, 15.5, 1.7)),
    ('3_julio2',   3.0, 58, [(0.45, 11.1, 1.62), (1.05, 11.7, 1.66)],    (3.44, 12.0, 1.75)),
    # ('4_vigas' out of the cut on 2026-11-20: Marilyn, "no suman nada", too much ceiling; 4_vigas.mp4 is kept)
    # ('4_vigas',    3.0, 72, [(0.9, 15.0, 0.9), (0.9, 19.5, 0.9)],        (-0.6, 28.0, 5.6)),
    ('5_maqueta',  4.0, 52, orbit(-62, 12, 2.9, 1.9),                    (0, YT, 0.98)),
    ('6_sala',     3.5, 68, [(0, 1.2, 1.6), (0, 4.4, 1.6)],              (0, L, 1.75)),
]
TITLE = '6_sala'


def tsrct(*args, cwd=OUT, out=None, err=None):
    r = subprocess.run(['cmd', '/c', TSRCT, *args], cwd=cwd, stdout=out or subprocess.PIPE, stderr=err or subprocess.PIPE, text=out is None)
    if r.returncode:
        raise SystemExit(f'tsrct {" ".join(args[:3])} failed: {(r.stderr or r.stdout or "")[-600:] if out is None else "see log"}')
    return r.stdout if out is None else ''


def actions(name, secs, fov, path, look):
    ms = round(secs * 1000)
    A = []
    for a in json.load(open(BASE)):
        it = a.get('item', {})
        if a['type'] in ('setFxAnimator', 'setFxScene3DActiveCamera') or it.get('type') == 'Camera3D':
            continue
        if a['type'] == 'createFxScene3DLayer':
            a['activeRange'] = {'start': 0, 'duration': ms}
        A.append(a)
    aim = {'constraints': [{'type': 'aim', 'id': 80, 'target': {'id': 81, 'target': {'type': 'world'}, 'offset': S(*look), 'offsetSpace': 'local'},
                            'up': [0, 1, 0], 'upSpace': 'world', 'forwardAxis': 'positiveZ', 'influence': 1}]}
    cam = {'type': 'Camera3D', 'id': 3, 'parentId': None, 'name': 'Camara', 'transform': {'position': S(*path[0]), 'relationships': aim},
           'lens': {'type': 'angle', 'projection': {'type': 'perspective', 'angleOfView': fov}}}
    A.insert(2, {'type': 'addFxScene3DLayer', 'compositionId': 'main', 'layerId': 1, 'item': cam})
    A.insert(3, {'type': 'setFxScene3DActiveCamera', 'compositionId': 'main', 'layerId': 1, 'cameraItemId': 3})
    keys = [{'id': f'cam-{k}', 'layerTime': round(ms * k / (len(path) - 1)), 'value': {'type': 'vector3', 'value': S(*p)}, 'easing': {'type': 'linear'}} for k, p in enumerate(path)]
    A.append({'type': 'setFxAnimator', 'compositionId': 'main', 'target': {'type': 'styleProperty', 'layerId': 1, 'itemId': 3, 'propertyName': 'position'},
              'animator': {'type': 'keyframes', 'enabled': True, 'keyframes': keys}, 'dependencies': [], 'layerRefBindings': []})
    return A


def titles(secs):
    ms = round(secs * 1000)
    def txt(lid, name, text, style, size, color, y):
        return {'type': 'createFxTextLayer', 'compositionId': 'main', 'insertIndex': 0, 'layerId': lid, 'name': name, 'activeRange': {'start': 0, 'duration': ms},
                'transform': {'anchorPoint': [0, 0], 'position': [112, y], 'scale': [100, 100], 'rotation': 0, 'opacity': 100},
                'sourceText': {'text': text, 'fontFamily': 'Georgia', 'fontStyle': style, 'fontSize': size, 'fillColor': color, 'justification': 'left', 'boxText': False}}
    B = [txt(30, 'Titulo', 'Museo Xeneize', 'Regular', 132, [0.96, 0.95, 0.92, 1], 840), txt(31, 'Bajada', 'La pintura clásica, de azul y oro', 'Italic', 46, [0.953, 0.698, 0.161, 1], 915)]
    for lid, d in ((30, 0), (31, 200)):
        B.append({'type': 'setFxPropertyKeyframes', 'compositionId': 'main', 'property': {'layerId': lid, 'propertyType': 'opacity'}, 'keyframes': [
            {'id': f't{lid}-a', 'layerTime': 300 + d, 'value': {'type': 'float', 'value': 0}, 'easing': {'type': 'linear'}},
            {'id': f't{lid}-b', 'layerTime': 1200 + d, 'value': {'type': 'float', 'value': 100}, 'easing': {'type': 'cubicBezier', 'x1': 0.2, 'y1': 0, 'x2': 0.2, 'y2': 1}}]})
    return B


def build(only):
    os.makedirs(WORK, exist_ok=True); os.makedirs(os.path.join(OUT, 'Previews'), exist_ok=True)
    print(tsrct('telemetry', 'status').strip())
    for name, secs, fov, path, look in SHOTS:
        if only and only not in name:
            continue
        proj = f'{name}.tsrct'
        if os.path.exists(os.path.join(OUT, proj)):
            os.remove(os.path.join(OUT, proj))
        tsrct('project', 'create', '--project', proj)
        ed = os.path.join(WORK, f'{name}__editable.json')
        tsrct('project', 'checkout', '--project', proj, '--output', ed)
        j = json.load(open(ed)); j['dimensions'] = {'width': 1920, 'height': 1080}; j['duration'] = secs
        json.dump(j, open(ed, 'w'))
        tsrct('project', 'commit', '--project', proj, '--file', ed)
        tsrct('project', 'import-asset', '--project', proj, '--file', MODEL, '--asset-id', 'sala', '--kind', 'model3d')
        af = os.path.join(WORK, f'{name}__scene.json'); json.dump(actions(name, secs, fov, path, look), open(af, 'w'))
        r = json.loads(tsrct('project', 'apply', '--project', proj, '--actions', af))
        msg = f'{name}: {r.get("appliedActions")} actions, warnings {r.get("warnings")}'
        if name == TITLE:
            for f in ('georgia.ttf', 'georgiai.ttf'):
                tsrct('project', 'import-font', '--project', proj, '--file', f'C:/Windows/Fonts/{f}')
            tf = os.path.join(WORK, f'{name}__titles.json'); json.dump(titles(secs), open(tf, 'w'))
            msg += f', titles {json.loads(tsrct("project", "apply", "--project", proj, "--actions", tf)).get("appliedActions")}'
        print(msg)


def preview(only, samples):
    for name, secs, *_ in SHOTS:
        if only and only not in name:
            continue
        r = json.loads(tsrct('preview', '--project', f'{name}.tsrct', '--time', str(round(secs * 0.6, 2)), '--output', f'Previews/{name}.png', '--renderer', 'path-tracer', '--samples', str(samples)))
        print(name, round(r['renderSeconds'], 1), 's')


def export(only):
    for name, secs, *_ in SHOTS:
        mp4 = os.path.join(OUT, f'{name}.mp4')
        if (only and only not in name) or (os.path.exists(mp4) and os.path.exists(os.path.join(WORK, f'{name}__export.out'))):
            continue
        t = time.time(); log = os.path.join(WORK, f'{name}__export.log'); tmp = os.path.join(WORK, f'{name}__export.tmp')
        with open(tmp, 'w') as o, open(log, 'a') as e:   # append: a failed attempt stays in the log
            start = e.tell()
            pr = subprocess.Popen(['cmd', '/c', TSRCT, 'export', '--project', f'{name}.tsrct', '--output', f'{name}.mp4', '--renderer', 'path-tracer', '--samples', str(SAMPLES),
                                   '--fps', str(FPS), '--resolution', '1080p', '--json'], cwd=OUT, stdout=o, stderr=e)
            done, moved = -1, time.time()
            while pr.poll() is None:                     # watchdog: the export once sat 40 h on one frame, still printing progress
                time.sleep(30)
                with open(log, 'rb') as f:
                    f.seek(max(start, os.path.getsize(log) - 4000)); m = re.findall(rb'"completed":(\d+)', f.read())
                if m and int(m[-1]) != done:
                    done, moved = int(m[-1]), time.time()
                if time.time() - moved > STALL:
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(pr.pid)], capture_output=True); pr.wait()
                    raise SystemExit(f'{name}: no new frame in {STALL} s (stuck at {done}), killed')
        if pr.returncode:
            raise SystemExit(f'{name}: tsrct export failed, see log')
        os.replace(tmp, os.path.join(WORK, f'{name}__export.out'))   # the .out exists only for a finished shot
        print(f'{name}: {round(secs * FPS)} frames in {time.time() - t:.0f} s', flush=True)


def join():
    lst = os.path.join(WORK, 'concat.txt')
    open(lst, 'w').write(''.join(f"file '{os.path.join(OUT, n + '.mp4').replace(os.sep, '/')}'\n" for n, *_ in SHOTS))
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', lst, '-c:v', 'libx264', '-crf', '21', '-preset', 'slow', '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart', '-an', os.path.join(OUT, 'teaser.mp4')], check=True)
    print('teaser.mp4', os.path.getsize(os.path.join(OUT, 'teaser.mp4')), 'bytes')


if __name__ == '__main__':
    ap = argparse.ArgumentParser(); ap.add_argument('step', choices=['build', 'preview', 'export', 'join'])
    ap.add_argument('--only', default=''); ap.add_argument('--samples', type=int, default=SAMPLES)
    a = ap.parse_args()
    {'build': lambda: build(a.only), 'preview': lambda: preview(a.only, a.samples), 'export': lambda: export(a.only), 'join': join}[a.step]()
