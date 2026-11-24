#!/usr/bin/env bash
# Publishes ONLY museo/sitio/ (plus scripts/sitio_README.md as README.md and museo/readme/ as readme/) to the public repo, at its root.
#
#     bash scripts/publicar_sitio.sh "mensaje del commit"          # builds the commit, shows it, does not push
#     bash scripts/publicar_sitio.sh "mensaje del commit" --push   # and pushes it to main
#
# Since 2026-11-24 it also publishes the process record under proceso/ (see the list below).
# Nothing else goes there: the commit is built from a temporary index that only sees
# museo/sitio, so the project's own branch, index and working tree are not touched.
set -euo pipefail
REMOTE=https://github.com/meryboth/boca-en-el-arte.git
MSG=${1:?falta el mensaje del commit}
cd "$(git rev-parse --show-toplevel)"

export GIT_INDEX_FILE=$(git rev-parse --absolute-git-dir)/index.sitio
rm -f "$GIT_INDEX_FILE"
git --work-tree=museo/sitio add -A .
git update-index --add --cacheinfo 100644,"$(git hash-object -w scripts/sitio_README.md)",README.md
for f in museo/readme/*; do   # images of the README, published under readme/
  git update-index --add --cacheinfo 100644,"$(git hash-object -w "$f")",readme/"$(basename "$f")"
done

# The process record, under proceso/: documents, data, process sheets and code. Never anything git ignores.
# Left out on purpose: full-size images, 3D models, the aerial photos and their cut-outs, the first pilot image.
{ git ls-files research comfy scripts museo
  git ls-files -o --exclude-standard research comfy scripts museo/BITACORA.md museo/render/stills museo/render/pisos museo/seleccion.json
} | sort -u | grep -v -E '^research/(outputs|maqueta3d/(modelo|fuentes|vistas|recortes|recortes_mano)|eval-respuestas)/|^research/maqueta3d/(hoja_fotos_aereas|hoja_recortes|_grilla)|^research/proceso/(01_|12_tesseract)|adan|__pycache__|^museo/(sitio|readme|obras|assets|curaduria)/|\.blend' > "$GIT_INDEX_FILE.list"
git hash-object -w --stdin-paths < "$GIT_INDEX_FILE.list" | paste - "$GIT_INDEX_FILE.list" | while IFS=$'	' read -r h f; do
  printf '100644 %s	proceso/%s
' "$h" "$f"
done | git update-index --add --index-info
git update-index --add --cacheinfo 100644,"$(git hash-object -w scripts/proceso_README.md)",proceso/README.md
git update-index --add --cacheinfo 100644,"$(printf '' | git hash-object -w --stdin)",.nojekyll   # Pages serves the files as they are
rm -f "$GIT_INDEX_FILE.list"
TREE=$(git write-tree)
rm -f "$GIT_INDEX_FILE"; unset GIT_INDEX_FILE

PARENT=$(git ls-remote "$REMOTE" refs/heads/main | cut -f1)
if [ -n "$PARENT" ]; then
  git fetch -q "$REMOTE" refs/heads/main
  [ "$(git rev-parse "$PARENT^{tree}")" = "$TREE" ] && { echo "sin cambios respecto de lo publicado ($PARENT)"; exit 0; }
  COMMIT=$(git commit-tree "$TREE" -p "$PARENT" -m "$MSG")
else
  COMMIT=$(git commit-tree "$TREE" -m "$MSG")
fi
git update-ref refs/sitio/main "$COMMIT"
echo "commit $COMMIT"
git ls-tree -r --long "$COMMIT" | awk '{n++; s+=$4} END{printf "%d archivos, %.1f MB\n", n, s/1e6}'
git ls-tree --name-only "$COMMIT"

if [ "${2:-}" = "--push" ]; then
  git push "$REMOTE" "$COMMIT:refs/heads/main"
else
  echo "no se subió nada (falta --push)"
fi
