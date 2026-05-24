# poem — Template Spec

This document is the source of truth for producing a `poem` gift. The design principle behind every rule: **the recipient should be able to assemble many beautiful, strange, grounded sentences, not just look at a pretty background.**

## 0. What This Template Is

`poem` is a full-screen H5 built around a film-collage surface:

- a looping cinematic background video
- two to three image layers positioned like film stills, documents, objects, or visual memories
- a title and subtitle/fragments
- a basket of draggable torn-paper word chips
- starter chips already placed on the canvas
- scene switching
- a save flow that exports a still or live WebM

The canonical output is `template-source/collage-poem.html`. The builder reads `filled-slots.json`, injects `window.POEM_GIFT_CONFIG`, inlines available local assets, and writes a separate gift `index.html`.

## 1. Ready Scope

The ready version supports:

- using the bundled grass and letter scenes, generated paper chips, fonts, posters, videos, and still images
- overriding scenes, background videos, posters, baskets, title/subtitle copy, colors, and filters
- replacing film image layers and their 1080x1350-stage coordinates
- replacing word banks or per-scene word sets
- replacing starter word sets and paper palettes
- building a single output HTML without modifying the canonical HTML

It does not automatically search the web or call a video-generation model. The agent is responsible for inferring the theme, finding or generating media, staging those assets in `poem-work/`, and verifying that the final H5 renders.

## 2. The 8 Production Rules

### Rule 1 — Infer the theme before media search

If the user has not supplied a theme, inspect their raw material first. Pull the strongest motif from photos, screenshots, notes, filenames, quoted phrases, places, objects, time of day, weather, or emotional situation. Only after that should you search for or generate media.

Good theme titles connect to real life while staying roomy:

- `山海替你保存一封信`
- `夏天把风寄存在草地`
- `夜班车把心事开慢一点`
- `雨把便利店照得很亮`
- `旧收据里还有一个春天`

Weak themes:

- `思念`
- `治愈`
- `美好回忆`
- `高级感拼贴`

### Rule 2 — Background video sets the weather

The background video is the emotional weather of the page. If no video is provided, find or generate a beautiful HD film-textured video based on the inferred theme. Prefer landscape, real-world, or lightly abstract scenes: shore moonlight, moving grass, wet streetlights, train windows, dusk buildings, old-paper shadows, harbor light, kitchen steam.

Keep motion gentle. The word chips need to stay readable.

### Rule 3 — Image layers must share one world

Pick two to three images whose palette and subject logic match the video. They can be film stills, landscape details, documents, flowers, receipts, windows, objects, or slightly abstract atmosphere. They should feel collected from the same memory, not pulled from unrelated mood boards.

Use opacity, filter, and placement to leave air for the word chips.

### Rule 4 — Theme titles need reality and room

The title should touch something concrete from life, but leave enough space for many possible poems. `山海替你保存一封信` works because it carries sea, distance, letter, memory, and tenderness. `给阿嬷的情书电影二创` is too narrow for a reusable word basket.

### Rule 5 — The word bank must be abundant

A thin basket makes the collage hard. Aim for 120-220 tokens per theme when possible. Mix:

- theme nouns: moon, bus stop, envelope, tide, grass, receipt
- real-life objects: slippers, hot water bottle, red light, plastic stool, convenience store
- verbs: save, return, pass by, hide, wait, rewrite
- adjectives/adverbs: soft, damp, ordinary, serious, quietly
- grounded names/places when the user provided them
- emotional words: longing, bright, awkward, brave
- strange but realistic words: moonlight customer service, memory pinned, sadness half-sugar, harbor zoning out
- everyday funny phrases: takeout arrived, forgot umbrella, change coins, phone on mute

### Rule 6 — Function words should repeat

Do not force every chip to be unique. Collage poetry needs glue. Include and repeat common particles and connectors, especially in Chinese:

`的`, `的`, `的`, `地`, `得`, `在`, `在`, `把`, `把`, `给`, `给`, `从`, `向`, `和`, `与`, `或`, `而`, `但是`, `因为`, `所以`, `如果`, `然后`, `后来`, `之前`, `之后`, `里面`, `旁边`.

This is not filler; it lets the recipient build complete sentences.

### Rule 7 — Paper chips must match the palette

Paper colors should harmonize with the video and image layers. Warm moon/letter scenes can use cream, kraft, black, muted blue, and old-paper textures. Grass scenes can use off-white, cream, grid, kraft, and soft blue. Avoid rainbow paper unless the theme is intentionally playful or chaotic.

Always check text contrast on each paper color.

### Rule 8 — Verify the H5 in a browser

Before delivery:

- build into a separate gift folder
- open the output with a local server or `scripts/verify-h5.sh`
- confirm the background video or poster appears
- switch scenes when more than one exists
- drag words out of the basket, rotate/delete one chip, and return one to the basket
- click shuffle and confirm the basket refills without overlap
- click save and confirm PNG/WebM fallback behavior
- inspect mobile width for title, basket, and word-chip overlap
- inspect console output for failed local assets

If browser verification is blocked by local video autoplay or codec support, report that limitation directly.

## 3. Slot Mapping Contract

### `recipient_material`

Use this to extract the recipient, relationship, occasion, language habit, concrete imagery, color palette, and theme candidates.

### `poem_theme_plan`

Produce one compact plan with:

- `theme_title`
- `theme_subtitle`
- `real_life_anchors`
- `visual_mood`
- `background_video_prompt`
- `image_search_or_generation_plan`
- `word_bank_strategy`
- `paper_palette`

The plan prevents the template from turning into generic aesthetic wallpaper.

### `background_video`

Maps to `window.POEM_GIFT_CONFIG.scenes[].video`. Values may be staged in `poem-work/media/`:

```json
{
  "poem_scenes": [
    {
      "id": "shore-letter",
      "title": "山海替你保存一封信",
      "subtitle": "dear you, from every shore that remembered home",
      "video": "poem-work/media/shore-letter-background.mp4",
      "poster": "poem-work/media/shore-letter-poster.jpg",
      "basket": "poem-work/media/letter-box.png",
      "accent": "#c07a4a",
      "bg": ["#141a25", "#32241d", "#8a6037"],
      "titleColor": "rgba(255, 220, 160, 0.94)",
      "subtitleColor": "rgba(255, 225, 176, 0.72)",
      "videoFilter": "saturate(0.82) contrast(1.08) brightness(0.78) sepia(0.08)"
    }
  ]
}
```

The builder strips the `poem-work/` prefix and inlines files from the workdir or fetched bundle.

### `film_image_layers`

Maps to `window.POEM_GIFT_CONFIG.filmLayerSets`:

```json
{
  "film_layers": [
    {"src": "poem-work/images/shore-letter/01.jpg", "x": 594, "y": 266, "w": 348, "h": 464, "rot": -1, "opacity": 0.78},
    {"src": "poem-work/images/shore-letter/02.png", "x": 116, "y": 468, "w": 410, "h": 318, "rot": 0, "opacity": 0.62}
  ]
}
```

Coordinates use the 1080x1350 stage coordinate system.

### `word_bank`

Maps to `window.POEM_GIFT_CONFIG.words` or `wordSets`. The builder accepts:

```json
{
  "word_bank": {
    "words": ["山海", "替", "你", "保存", "一封信", "的", "的", "在", "把", "给"]
  }
}
```

For multiple scenes:

```json
{
  "word_bank": {
    "word_sets": [
      ["夏天", "草地", "把", "风", "寄存", "的", "的"],
      ["山海", "信封", "替", "你", "保存", "得", "地"]
    ]
  }
}
```

### `starter_words`

Maps to `window.POEM_GIFT_CONFIG.starterSets`. Each item is `[word, x, y]` in stage coordinates:

```json
{
  "starter_words": [
    ["把", 220, 382],
    ["月光", 450, 505],
    ["寄给", 650, 680],
    ["你", 520, 920]
  ]
}
```

### `paper_palette`

Maps to `paperPaths`, `starterPapers`, `paperColors`, `fontOptions`, and `blackPaper`:

```json
{
  "paper_palette": {
    "paper_paths": [
      "assets/generated/papers/paper-white-wide.png",
      "assets/generated/papers/paper-kraft-strip.png",
      "assets/generated/papers/paper-blue-strip.png"
    ],
    "paper_colors": ["#151612", "#6f2117", "#fff8e8"]
  }
}
```

### `poem_runtime_overrides`

Use this for advanced edits: `scenes`, `filmLayerSets`, `wordSets`, `starterSets`, `paperPaths`, `starterPapers`, `paperColors`, `fontOptions`, `blackPaper`, `initialSceneId`, and `initialSceneIndex`.

## 4. Runtime Builder Contract

Command:

```bash
python3 assets/templates/poem/template-source/build.py \
  --slots ./gifts/<date>-<recipient>/poem-work/filled-slots.json \
  --workdir ./gifts/<date>-<recipient>/poem-work \
  --out ./gifts/<date>-<recipient>/index.html
```

The builder:

1. reads `filled-slots.json`
2. normalizes scenes, media, film layers, word sets, starter words, paper palette, and override groups
3. resolves assets from the workdir, `assets/templates/poem/base/`, or `template-source/`
4. injects `window.POEM_GIFT_CONFIG`
5. writes `poem-work/runtime_config.json`
6. writes the final `index.html`

It does not modify `template-source/collage-poem.html`.

Asset paths may be written either relative to the workdir (`media/bg.mp4`) or with the documented workdir prefix (`poem-work/media/bg.mp4`). The builder strips the `poem-work/` prefix before inlining.

## 5. Per-Gift Checklist

- [ ] Theme was inferred from user material or explicitly provided by the user.
- [ ] Background video is cinematic, HD, film-textured, and gentle enough for reading.
- [ ] Two to three image layers share one palette and subject world with the video.
- [ ] Theme title connects to real life and remains broad enough for many poems.
- [ ] Word bank is abundant and varied, including repeated function words.
- [ ] Paper chip palette matches the video and images.
- [ ] Starter words invite continuation rather than finishing the poem.
- [ ] The final H5 opens, switches scenes, drags/shuffles words, and saves output.
