#!/usr/bin/env bash
# Download mentor headshots from Drive into assets/img/mentors/ and square them.
#
# The Drive files are private, so this only works once the two Google Form
# "File responses" folders are shared as "anyone with the link can view".
# Revoke that again afterwards — the images live in the repo from then on.
#
#   bash tools/fetch_headshots.sh
#
# Ids come from data/headshot-sources.local.json, which is gitignored.
set -uo pipefail
cd "$(dirname "$0")/.."

SRC=data/headshot-sources.local.json
OUT=assets/img/mentors
[ -f "$SRC" ] || { echo "missing $SRC"; exit 1; }
mkdir -p "$OUT"

ok=0; fail=0
while IFS=$'\t' read -r name id; do
  slug=$(printf '%s' "$name" | tr '[:upper:]' '[:lower:]' | sed -e 's/[^a-z0-9]\+/-/g' -e 's/^-//' -e 's/-$//')
  tmp=$(mktemp)
  curl -sL "https://drive.usercontent.google.com/download?id=${id}&export=download" -o "$tmp"
  if [ "$(file -b --mime-type "$tmp")" != "image/jpeg" ] && [ "$(file -b --mime-type "$tmp")" != "image/png" ]; then
    echo "  SKIP  $name — not an image (folder still private?)"
    rm -f "$tmp"; fail=$((fail+1)); continue
  fi
  python3 - "$tmp" "$OUT/$slug.jpg" <<'PY'
import sys
from PIL import Image, ImageOps
src, dst = sys.argv[1], sys.argv[2]
im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
# centre square crop, biased slightly up so faces are not cut at the chin
s = min(im.size)
left = (im.width - s) // 2
top = max(0, int((im.height - s) * 0.35))
im.crop((left, top, left + s, top + s)).resize((320, 320), Image.LANCZOS)\
  .save(dst, "JPEG", quality=82, optimize=True, progressive=True)
PY
  echo "  ok    $name -> $OUT/$slug.jpg ($(du -h "$OUT/$slug.jpg" | cut -f1))"
  rm -f "$tmp"; ok=$((ok+1))
done < <(python3 -c "
import json
d = json.load(open('$SRC'))['sources']
for k, v in d.items(): print('%s\t%s' % (k, v))
")

echo
echo "  downloaded $ok, skipped $fail"
[ $ok -gt 0 ] && echo "  now run: python3 tools/build_mentors.py"
