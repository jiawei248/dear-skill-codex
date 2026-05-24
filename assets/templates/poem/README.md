# poem

A film-collage poem H5 with a full-screen cinematic video, two to three tonal image layers, a basket of draggable torn-paper word chips, scene switching, and a live-image save flow.

Best for: poetic notes, friend comfort, movie/book reflections, birthdays, longing, light confessions, and aesthetic memory collages where the recipient should play with words rather than only read a finished message.

## Where to look

| File | What it is |
|---|---|
| `template.json` | Slot schema, asset bundle URL, runtime config contract, and activation disclosure |
| `SPEC.md` | Production rules for theme inference, video/image selection, word-bank writing, paper palette, and verification |
| `RELEASE.md` | How to stage, zip, and publish the asset bundle as a GitHub Release |
| `template-source/collage-poem.html` | Canonical authored H5; read-only source |
| `template-source/build.py` | Runtime builder that injects `window.POEM_GIFT_CONFIG` and writes a standalone output HTML |
| `base/` | Downloaded on first use from GitHub Release; holds default videos, posters, collage images, papers, fonts, and previews |

## Status

- Template authored; canonical HTML is `template-source/collage-poem.html`
- Production + content spec written (`SPEC.md`)
- Slot schema defined (`template.json`)
- Runtime builder implemented (`template-source/build.py`)
- Asset bundle v1 packaged and wired in `template.json`

Before making a gift, read `SPEC.md` end-to-end. The central rule is theme-first media: if the user did not provide a theme, infer it from their raw material before searching or generating a background video, image layers, word bank, and paper palette.
