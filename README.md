# Atlas

The generator behind the **Atlas** themes for [Omarchy](https://omarchy.org)
([Atlas Solitude](https://github.com/PhyAMR/omarchy-atlas-solitude), dark, and
[Atlas Ink](https://github.com/PhyAMR/omarchy-atlas-ink), light e-ink), plus the
birds screensaver.

- **Wallpapers:** eleven procedural "plates", technical drawings of the world
  (engine, fern, nautilus, dragonfly, turbofan, flower, fish, earth, tree,
  beetle, radiolarian), each drawn once as SVG and rendered in both palettes at
  2880×1800. Rendering is deterministic: the same code gives byte-identical PNGs.
- **Screensaver:** a murmuration of starlings in thin braille strokes (boids),
  coloured by the current Omarchy theme. It opens the same window class as
  Omarchy's screensaver, so the idle service's dismiss/lock logic keeps working.

You don't need this repo to *use* the themes: they ship their rendered
wallpapers. You need it to change the plates or to get the screensaver.

## Requirements

`python3` (standard library only), `rsvg-convert` (librsvg), ImageMagick
(`magick`), and the Iosevka Nerd Font for the labels (falls back to any
monospace font).

## Screensaver

```bash
make install          # links ~/.local/bin/atlas-screensaver
atlas-screensaver force
```

To use it as the idle screensaver, set it in `~/.config/omarchy/shell.json`
with [Idle Plus](https://github.com/PhyAMR/omarchy-idle):

```json
"idle": { "screensaverCommand": "$HOME/.local/bin/atlas-screensaver" }
```

`ATLAS_SCREENSAVER_FONT_SIZE` (default 9) sets the terminal font size; smaller
is finer.

## Wallpapers

```bash
make wallpapers                                  # into the installed themes
make wallpapers SOLITUDE=~/code/omarchy-atlas-solitude INK=~/code/omarchy-atlas-ink
python3 render.py /tmp/out fern tree             # just some plates, both palettes
```

`make wallpapers` replaces each theme's `backgrounds/*.png` and `preview.png`;
commit them in the theme repos. Palettes are in `atlas.py` (`PALETTES`), plates
in `plate_*.py`, and their order in `plates.py`.

## License

MIT, see [LICENSE](LICENSE).
