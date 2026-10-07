#!/bin/bash
# Render the Atlas plates into the two Atlas themes (backgrounds/ + preview.png).
#   build-wallpapers.sh [SOLITUDE_DIR [INK_DIR]]
# Defaults to the installed themes in ~/.config/omarchy/themes (symlinks to the
# theme repos work: the PNGs land in the repo checkouts, ready to commit).
# Needs python3, rsvg-convert (librsvg) and ImageMagick; uses the Iosevka font
# when installed.
set -euo pipefail
HERE="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
THEMES="$HOME/.config/omarchy/themes"
SOLITUDE="${1:-$THEMES/atlas-solitude}"
INK="${2:-$THEMES/atlas-ink}"
OUT=$(mktemp -d)
trap 'rm -rf "$OUT"' EXIT

(cd "$HERE" && python3 render.py "$OUT" >/dev/null)
for pair in "dark:$SOLITUDE" "light:$INK"; do
  pal=${pair%%:*} theme=${pair#*:}
  [[ -d $theme ]] || { echo "No theme folder at $theme" >&2; exit 1; }
  mkdir -p "$theme/backgrounds"
  rm -f "$theme/backgrounds/"*.png
  cp "$OUT/$pal/"*.png "$theme/backgrounds/"
  magick "$OUT/$pal/03-nautilus.png" -resize 1440x900 "$theme/preview.png"
done
echo "Atlas wallpapers rendered into $SOLITUDE and $INK"
