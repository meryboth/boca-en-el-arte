# Museo Xeneize · classical paintings in blue and gold, and the room built to hang them

<!-- Generated from report.template.md by scripts/render_report.py with the numbers of report-data.json. Do not edit report.md by hand. -->

*Open R&D · generative art, image-to-3D and a pre-rendered museum · 2026 · unofficial fan project: no crest, no sponsors, no player names.*

Ten public-domain paintings get their clothes repainted in blue and gold, hang in a 3D room built entirely by script, and end at a scale model of the stadium. Along the way one question was tested properly — who repaints a Renaissance robe better, code or an image model? — and the answer was **neither**: across 20 blind pairs the code won 9 and the image model 11, a tie that hides a clean split by painting. The rest is an honest build log: what Claude Fable 5.2 could and could not do as a "generative artist", what Tesseract added, and four attempts at one stadium.

## Results at a glance

| Number | What it is | n | Comes from |
|---|---|---|---|
| 5.2 ΔE00 | How much Nano Banana 2 changes faces, hands and background it was told to leave alone (median; the limit set beforehand was 2.0) | 20 edits | Table 2 |
| 9 – 11 | Code vs. image model in blind pairs: no winner (95 % interval 25.0 % to 65.0 %) | 20 pairs, one evaluator | Table 3 |
| 5 of 20 | Code recolours flagged as "visibly retouched" — all five attempts on one painting; 0 of 20 for the image model | 20 per method | Table 3 |
| 4 | Routes tried for the stadium model: cubes by eye, a ready-made model, two image-to-3D services, a clean model from a building sheet — the one Marilyn accepted | 1 object | Table 5 |
| 1,337 credits + 2.90 M tokens | Everything paid: 77 logged runs, failed and discarded ones included | 77 runs | Table 6 |

## Where it started, and the first thing that failed

The brief was to try two tools on something hostable: **Claude Fable 5.2** as a generative artist and **Tesseract** (Mirage) for 3D. Fable writes code and text, not pixels, so the first pilot had it draw a whole "Renaissance" painting in code. Marilyn's verdict: not realistic, and not what she wanted — she wanted *real* paintings with the shirt added (run `p0001`, kept in the log; protocol v1 is archived).

That rewrote the project. Protocol v2 asks a narrower question: given a real painting, **who should change the clothes** — deterministic code written by an agent, an image-editing model, or both?

## The three methods

- **`edit` (baseline).** Nano Banana 2 (Gemini 3.1 Flash Image) from a Comfy Cloud node, 4K, one frozen prompt per painting, no iteration. It is the naive alternative: hand the picture to a model and ask.
- **`code`.** A fresh Fable 5.2 agent per attempt writes the config for a frozen CIELAB recolouring script (polygons, a colour key per region, levels), looks at the result and corrects it, up to four rounds. Outside the mask every pixel is the original.
- **`hybrid`.** The clothes from the `edit` output pasted onto the original through the mask of the `code` attempt with the same seed, after registering both images. Added after the pilots, at Marilyn's request: the model painted better cloth, the code protected better faces.

Only fabric is touched — no chairs, no objects (a rule Marilyn set during the pilots). Four evaluation paintings, five seeds each, 60 runs; a fifth painting (Raphael's *Julius II*) was used only to develop the script.

![One calibration painting, three methods](proceso/03_julio2-tres-metodos.jpg)

**Table 1 — conditions.** Same source file (long side 4500 px) for all three.

| Condition | Who paints | Iterates | Cost per image |
|---|---|---|---|
| `edit` | Nano Banana 2 | no (frozen prompt) | 38.46 credits |
| `code` | recolour script, config by a Fable agent | up to 4 rounds (median 4) | 133,900 tokens, 512 s (medians) |
| `hybrid` | model inside the mask, original outside | no | reuses both of the above |

## What the metrics say

Three automatic metrics on small frozen patches drawn before any run: **alteration** (median CIEDE2000 against the original inside protected patches — faces, hands, background; lower is better), **hue error** (median hue-angle distance to the brand blue or gold in clothing patches, degrees; lower is better) and **folds** (Pearson correlation of L* with the original in clothing patches; higher is better). None of them is a gate.

**Table 2 — medians per painting, n = 5 seeds per cell.**

| Painting | Alteration `edit` | `code` | `hybrid` | Hue error `edit` | `code` | `hybrid` | Folds `edit` | `code` | `hybrid` |
|---|---|---|---|---|---|---|---|---|---|
| Madonna del Prato | 4.31 | 0.00 | 0.00 | 12.0° | 0.7° | 12.0° | 0.86 | 0.92 | 0.86 |
| Arnolfini Portrait | 5.74 | 0.00 | 0.00 | 5.4° | 1.2° | 5.3° | 0.82 | 0.99 | 0.82 |
| Bacchus and Ariadne | 5.28 | 0.00 | 0.00 | 13.8° | 0.9° | 13.7° | 0.83 | 0.83 | 0.85 |
| The School of Athens | 4.59 | 0.34 | 0.34 | 14.2° | 0.7° | 14.0° | 0.80 | 0.75 | 0.90 |
| **All four** (n = 20) | **5.19** | **0.00** | **0.00** | **12.7°** | **0.9°** | **12.6°** | **0.83** | **0.91** | **0.85** |

> Runs `e0001`–`e0060` in `runs.jsonl`, seeds 1–5, measured with `scripts/measure.py` on the frozen patches of `zones/zones.json`. `edit` outputs resized to the original before measuring. Paired by seed against `edit`: alteration -5.19 for `code` (95 % interval -5.64 to -4.34); hue error -11.8° for `code` (-13.1 to -8.2) and -0.02° for `hybrid` (-0.07 to 0.00: no winner).

How to read it, including what is true by construction:

- **The image model does touch what it should not** (H2, confirmed): 5.2 ΔE00 against a limit of 2.0, worst patch in any edit 12.5. It also returns a different size (0.92× to 1.67× the original pixels).
- `code` and `hybrid` score ~0 on alteration **because they copy the original outside the mask**. That is the design, not a finding.
- `hybrid` matches `edit` on hue for the same reason in reverse: it *is* the model's cloth.
- The code hits the brand hue far better (0.9° vs 12.7°) — and that turned out not to be what a viewer rewards.

## What a person preferred

Blind page, random order, no labels: 60 pairs ("which would you hang?") and 60 single images ("does anything look retouched?").

**Table 3 — pairs won, by painting.** First number is the first method named.

| Pair | Prato | Arnolfini | Bacchus | Athens | Total | 95 % interval for the first | Verdict |
|---|---|---|---|---|---|---|---|
| `code` vs `edit` | 0–5 | 0–5 | 4–1 | 5–0 | 9–11 | 25.0 % – 65.0 % | no winner |
| `hybrid` vs `code` | 5–0 | 5–0 | 1–4 | 0–5 | 11–9 | 35.0 % – 75.0 % | no winner |
| `hybrid` vs `edit` | 5–0 | 3–2 | 2–0 | 1–3 | 11–5 (4 undecided) | 43.8 % – 87.5 % | no winner |

> One evaluator (Marilyn), 20 pairs per comparison, bootstrap intervals over attempts. "Visibly retouched": `code` 5/20, `edit` 0/20, `hybrid` 0/20. Source: `eval-results.json`.

- **H1 (people prefer the code): not confirmed.** 9–11 overall. But the tie is two opposite landslides: on the two paintings with a few large garments the image model won every pair; on the two with many figures or cloth tangled with skin the code won nine of ten. With one painting per level this is a case study, not a law.
- **H4 (the hybrid beats both): not confirmed.** Against the code it repeats the model's pattern: it wins Prato and Arnolfini and loses the other two. Against the model itself it is 11–5 with 4 pairs she could not tell apart, and the interval still includes 50 %.
- **H3 (the colour key matters): not tested.** The ablation was dropped to stay inside the token budget after the first half cost 2.90 M tokens.
- All five code attempts on the Arnolfini were flagged as retouched: recolouring a dark green velvet towards blue leaves it flat. The metric that should see that (folds) gave those images its *best* score (0.99). The metric is wrong for dark cloth.

![Arnolfini: three methods](proceso/14_arnolfini-tres-metodos.jpg)
![School of Athens: three methods](proceso/18_atenas-tres-metodos.jpg)

What hangs in the museum follows that split, not a single method: hybrid for three paintings, code for *The School of Athens*. Five more paintings were added later with an automatic variant (the mask derived from where the model changed hue, no agent). That variant **was never measured or evaluated**; it is in the room because Marilyn asked for more paintings using what had worked best. One of the five, the Mona Lisa, was later taken down: her dress was already dark and her sleeves ochre, so the repaint barely showed (Marilyn: it "doesn't look like it was changed for Boca"). A workshop-of-Holbein *Henry VIII* replaced it — one attempt, 38.46 credits, checked by eye only — and the walkthrough was rendered again.

![Henry VIII: source, result and the pasted area](proceso/27_enrique8-original-combinado-mascara.jpg)

## The room and the site

The room is a Blender scene with no hand-edited file: one script builds walls, tunnel, beams, skylights, frames, camera path and the stops, and renders 1,621 frames. The site is static: a canvas that scrubs 541 WebP frames with the scroll, a high-resolution still at each of the 10 paintings, 43 MB in total.

Almost every part was replaced after Marilyn looked at it, and those corrections are the useful record (`museo/BITACORA.md`): procedural frame ornaments "don't look realistic" → scanned CC0 frames from Poly Haven; a floor she disliked twice → polished concrete; a camera pan that felt "strange" → a body that walks, bobs and turns to face each painting; pixelated canvases → 3840 px sources and 2880 px stills.

![Floor options](../museo/render/pisos/opciones-cemento.jpg)

The final walkthrough, with the clean stadium model on the table, rendered in 85 minutes (3.1 s per frame, one run, from the file times of the first and last frame) with no errors in the log. The rebuilt site was opened in a desktop browser and scrolled to the model stop: the frame loads and the console is clean. That is the whole of the check — no phone, no load-time measurement.

![The last stop of the walkthrough, final render](../museo/render/stills/parada_11_maqueta.jpg)
![The same stop in the site, narrow browser pane](proceso/23_sitio-parada-maqueta.jpg)

## What Tesseract was for

Honest answer to a question Marilyn asked half-way ("what is Tesseract helping with if we haven't used it?"): the room is Blender; Tesseract made the **192-frame path-traced intro video**. Importing the `.blend` lost the area lights, the procedural materials and the camera constraint, so lights were rebuilt in physical watts (17, 34 and 95 W). The path tracer ran out of memory on the 6 GB card until every texture was shrunk to 1280 px.

**Table 4 — one 1080p frame, path tracer with denoise** (one measurement each).

| Samples | Seconds |
|---|---|
| 16 | 22.4 |
| 48 | 37.5 |
| 128 | 75.2 |

The export took 110 minutes (34.5 s per frame, from the CLI log). The bounced light is clearly better than EEVEE; the boxes are still boxes. Other people get hyper-real results from Tesseract because their models and materials are, not because of the renderer.

![Intro video, one frame per second](proceso/22_tesseract-intro-hoja.jpg)

That first clip was one slow push down the room, and on the site it was hard to tell from the first frame of the walkthrough. Marilyn asked for a teaser with several viewpoints instead: 5 shots, 408 frames, 17 seconds, one Tesseract project per shot joined with ffmpeg. It plays once on the site's cover, muted, and fades into the walkthrough. 6 shots were rendered; a low-angle one of the ceiling beams was cut after Marilyn saw it ("they add nothing" — there is no artwork up there).

Exporting it was the least reliable step of the project. The 6 shots that finished (the cut one included) took 4.3 hours in total (28.1–35.9 s per frame). The third shot failed twice first: once with "GPU device lost" at frame 29 of 72, and once by hanging at frame 61 for about 40 hours while still printing progress lines, which the retry loop could not see because nothing errored. A watchdog that kills the export after 600 s without a new frame fixed the loop; the cause of either failure is unknown (the laptop may have gone to sleep).

![The teaser, twelve frames](proceso/30_teaser-sin-vigas-12-cuadros.jpg)

## Four attempts at one stadium

The room ends at a scale model of the stadium on a table. It took four routes, and the order matters.

**Table 5 — the stadium model.**

| Route | Input | Result | Marilyn's verdict | Cost |
|---|---|---|---|---|
| 1. Cubes placed by code, 3 versions | memory, then aerial photos, then a reference render | recognisable, proportions by eye | "very basic", then "I don't see the reconstruction being precise" | 0 |
| 2. A ready-made model | three found online | none both free and reusable (one at US$ 65 with an editorial licence) | not used | 0 |
| 3a. Normalise views with Nano Banana 2, then Tripo multiview | 4 hand-cut aerial photos | 167,744 vertices; crisp, but the plan and the far side are invented | "we need a better 3D model" | 38.9 + 63.3 credits |
| 3b. Rodin Gen-2.5 on the real photos | the same 4 cut-outs | 600,556 vertices; truer plan and pitch, soft tiers, washed colour, ragged edges | asked for clean modelling instead | 158.25 credits |
| 4. Clean model from a building sheet | measurements of 3b + one rectified real photo + reading the 12 photos | 23,902 faces in 9 objects, swept along the plan | "I like it, let's use that one" | 0 |

What went wrong on the way, all logged:

- Cutting the stadium out of the photos by colour failed on 5 of 7; the outlines were traced by hand.
- The "normalised views" step only half worked: a good front, a rotated middle panel, and a plan view instead of the back. The back fed to Tripo was the front **mirrored**, so that model has no real information about its far side.
- Two of 5 3D runs failed on mistakes Fable made wiring the graph, before reaching the service (2 runs, no charge recorded).
- Tripo painted a crest and a kit-maker's mark on four corner towers, against the prompt and against the brand rule. They were painted over in the texture (11,746 px); a faint outline remains.

![Tripo above, Rodin below, same four angles](maqueta3d/hoja_comparacion__tripo-arriba__rodin-abajo.jpg)

The fourth route is the one worth describing. Instead of asking a model for geometry, the generated mesh was **measured**: every vertex takes its texture colour, the green ones give the pitch — origin, axes and scale (105 m) — and from there come the outline every 3°, eight section cuts and the rim height (~34 m). A sanity check exposes the source: Rodin's pitch is 72.1 m wide instead of 68. One real photo was rectified from the four pitch corners (check: the centre spot lands 1.7 m off) and gives about 50 m from touchline to outer wall. Heights could not be measured from the photo: the camera calibration did not close. Everything went into a sheet with a source and a confidence for each number (`maqueta3d/ficha_edificio.md`) — most are "low" — and Blender swept tiers, parapets and wall along that plan.

![The clean model](maqueta3d/limpia/hoja_v4a.jpg)

### What the comparison says

One object, one run per route and one person judging, so this holds for this case and is not a rule.

| | Tripo (normalised views) | Rodin (real photos) | Blender from the sheet |
|---|---|---|---|
| What decides the shape | the model, from one generated view and its mirror | the model, from 4 oblique photos | explicit measurements, each with a source |
| Surfaces | crisp from afar, melted up close | soft, ragged edges, bits of the neighbourhood | clean edges, parallel parts |
| Unrequested marks | added a crest and a kit-maker's logo | not checked up close | none: only what was modelled exists |
| Fixing one part | regenerate everything | regenerate everything | change one number in the sheet |
| Cost | 38.9 + 63.3 credits | 158.25 credits | 0 |

- **For a building, image-to-3D did not give a usable model.** Both return something recognisable in minutes, but a stadium is regular, repeated geometry — rows, pilasters, bands — and every soft surface and invented part shows. Neither passed.
- **They were useful as a measuring instrument.** Rodin's plan and sections, scaled by the pitch, are what turned a model built by eye (rejected three times) into one with justified proportions. The 158 credits bought measurements, not the final mesh.
- **What changed the outcome was the context, not the tool.** Routes 1 and 4 use the same Blender and the same language model. The fourth starts from a sheet of measurements and a way of building (sweeping profiles along the plan) instead of cubes arranged while looking at photos.
- **Normalising the views with a generative model is unproven**: one good view out of three, and the run that would show whether it helps (Tripo on the raw photos) was not done. Nor can the two services be ranked: one run each, different inputs.
- **The accepted model is cleaner and more controllable, not more accurate in a strict sense.** Its heights still come from a generated mesh that is ~6 % off.

## What it cost

**Table 6 — from the billing feed and the agents' end-of-run notices.**

| Stage | Backend | Runs | Cost |
|---|---|---|---|
| Pilots | Nano Banana 2 (Comfy Cloud) and local code | 6 | 76.99 credits |
| Evaluation: `edit` | Nano Banana 2, 4K | 20 | 769.26 credits |
| Evaluation: `code` | 20 Fable 5.2 agents | 20 | 2,898,475 tokens, 3.6 h of agent time |
| Evaluation: `hybrid` | local composite | 20 | 0 |
| Five more paintings and one replacement | Nano Banana 2 + local mask | 6 | 230.72 credits |
| Stadium, image-to-3D | Nano Banana 2, Tripo, Rodin | 5 (2 failed) | 260.45 credits |
| Room, video, site, clean model | Blender and Tesseract on a laptop | — | 0 |
| **Total** | | **77** | **1337.42 credits + 2.90 M tokens** |

> Credits are Comfy Cloud's own figure per job, not an invoiced amount; no dollar conversion is available. Tokens for the conversation that directed all of this are not counted. The five later paintings were logged from the billing feed a day late, and which job made which painting was not written down; the replacement (*Henry VIII*) was logged when it ran.

## Honest limits

- **One evaluator, who is the author, and fast.** 120 answers in 259 seconds; 33 of the 60 single-image answers took under a second. She knew the methods and had seen results unblinded. The plan was three or four evaluators and an agreement score. *Closes it:* three people who have not seen the project, same page.
- **The baseline was not allowed to iterate; the code was** (up to four rounds). That favours the code, and it still did not win. *Closes it:* give the model four attempts and pick by the same rule.
- **Seeds pair only nominally**, and Nano Banana 2 does not return the same image for the same seed.
- **The folds metric fails on dark cloth** and the alteration metric is trivially zero for two of three methods. Neither was validated against a person before use.
- **Four paintings, one per difficulty level.** The split by painting is a pattern to test, not a result.
- **Half the museum is unmeasured**: the automatic hybrid was never evaluated.
- **The stadium is not a survey.** Its heights come from a generated mesh that is ~6 % off on the one dimension that could be checked. No plans were found. *Closes it:* drawings of the building, or photogrammetry with more than twelve photos.
- **The room is not photoreal**, the teaser has no sound and was checked on a twelve-frame sheet and one desktop playback, the site was not tested on phones, and Tesseract's two-critic review was skipped to save tokens.
- **Times are single measurements** on one machine.

## Reproduce it

- Hardware: Ryzen 9 4900HS, RTX 2060 Max-Q (6 GB), 15.4 GB RAM, Windows 11. Blender 5.1.2, Tesseract CLI 0.7.0.
- Models: Claude Fable 5.2 (agents and direction); Nano Banana 2 (Gemini 3.1 Flash Image), Tripo v3.1 multiview and Rodin Gen-2.5 through Comfy Cloud nodes.
- Experiment: protocol frozen at commit `032ee07`, evaluation at `bf7f79b`. `research/PROTOCOL.md` (with its change log), `runs.jsonl`, `results.json`, `eval-results.json`, raw outputs in `research/runs/`.
- Room and site: `scripts/blender_sala.py --stills --anim`, then `scripts/build_sitio.py`.
- Stadium: `scripts/blender_medir_estadio.py`, `research/maqueta3d/ficha_edificio.md`, `scripts/maqueta_limpia.py`.
- This report: `scripts/build_report_data.py`, then `render_report.py research/report.template.md research/report-data.json research/report.md`.
- Sources and licences: paintings in the public domain via Wikimedia Commons (`research/sources/README.md`, with hashes); aerial photographs by ProtoplasmaKid, CC BY-SA 4.0 — the 3D models derived from them carry the same terms; frames from Poly Haven, CC0.
