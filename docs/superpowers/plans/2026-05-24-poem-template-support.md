# Poem Template Support Plan

**Goal:** Add `poem` as a ready rich template alongside `paper-house` and `draw-card`, with a runtime builder, English production docs, asset bundle metadata, registry copy, and tests that lock the integration contract.

**Template principle:** theme-first media. If the user does not provide a theme, infer one from their raw material before finding or generating the background video, tonal image layers, word bank, and paper palette.

## Phase 1 — Template Registry and Documentation

- [x] Create `assets/templates/poem/`.
- [x] Copy the canonical desktop H5 into `template-source/collage-poem.html`.
- [x] Use `~/Desktop/preview_poem.png` for `preview.png` and `demo-preview.png`.
- [x] Add `template.json` with aliases, slot schema, activation disclosure, asset bundle metadata, and build contract.
- [x] Add English `README.md`, `SPEC.md`, and `RELEASE.md`.
- [x] Document the required production rules:
  - infer theme from raw material when no theme is provided
  - background video sets the emotional weather
  - still images must match the video's palette and world
  - theme title must touch real life but stay broad
  - word bank must be abundant and varied
  - function words and particles should repeat
  - paper chips should match the video and images

## Phase 2 — Runtime Builder and Config Hook

- [x] Add `window.POEM_GIFT_CONFIG` support to the canonical H5.
- [x] Support runtime overrides for scenes, film layer sets, word sets, starter sets, paper paths, starter papers, paper colors, fonts, black paper, and initial scene.
- [x] Implement `template-source/build.py`.
- [x] Ensure the builder writes output separately and does not mutate the canonical HTML.
- [x] Inline locally available images, videos, SVGs, and fonts from the build workdir, the fetched `base/` bundle, or `template-source/`.

## Phase 3 — Asset Bundle and GitHub Release

- [x] Stage the bundle from `~/Desktop/poem/assets`.
- [x] Include `assets/generated/`, `assets/scene1/`, `assets/scene2/`, `assets/papers/`, `assets/fonts/`, and `assets/previews/`.
- [x] Exclude `.DS_Store`, `__pycache__/`, `.git/`, local API keys, and source-only generation scripts.
- [x] Zip as `poem-v1.zip`.
- [x] Compute sha256 and update `template.json`.
- [ ] Upload the zip to GitHub Release tag `assets-poem-v1` after `gh` auth is refreshed.
- [ ] Confirm the release asset URL and sha256 digest match `template.json`.

## Phase 4 — Tests, Registry Copy, and Verification

- [x] Add schema tests for the template manifest and docs.
- [x] Add builder tests for runtime config injection, workdir-prefixed asset inlining, static asset inlining, and source immutability.
- [x] Add asset-bundle metadata tests.
- [x] Update `README.md`, `SKILL.md`, and `references/templates.md` so users can discover the template.
- [x] Run focused pytest coverage.
- [ ] Build a sample H5 and verify drag/shuffle/save behavior locally.

## Acceptance Criteria

- `assets/templates/poem/template.json` is valid JSON and references existing local docs/source/preview files.
- `template-source/build.py` can generate an `index.html` from `filled-slots.json`.
- The generated HTML contains `window.POEM_GIFT_CONFIG`.
- The canonical HTML remains unchanged by builds.
- The release bundle is prepared and the manifest hash matches it.
- Docs explicitly require theme inference from raw material, cinematic background video/image selection, abundant word banks, repeated particles/connectors, and matching paper-chip palettes.
