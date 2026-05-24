# poem Asset Bundle Release

The runtime bundle is intentionally not committed to the repo. It is published as a GitHub Release asset and fetched on first use by:

```bash
scripts/fetch-asset-bundle.sh --template poem
```

The aliases `collage-poem`, `poem-collage`, `word-basket`, and `拼贴诗` are accepted by the skill manifest and by `fetch-asset-bundle.sh`, but the release folder id is `poem`.

## Bundle v1

- Release tag: `assets-poem-v1`
- Asset name: `poem-v1.zip`
- Manifest URL: `https://github.com/jiawei248/dear-skill/releases/download/assets-poem-v1/poem-v1.zip`
- Manifest sha256: `e50e60ccd2a930335692eb653f0267bae14da18056fb5f0693a290b44fd59d36`
- Approx extracted size: `65 MB`
- Approx zip size: `50 MB`

Expected extracted layout:

```text
base/
└── assets/
    ├── generated/
    │   ├── papers/
    │   ├── scene1/
    │   └── scene2/
    ├── scene1/
    ├── scene2/
    ├── papers/
    ├── fonts/
    └── previews/
```

Excluded from the bundle:

- `.DS_Store`
- `__pycache__/`
- `.git/`
- local API keys or environment files
- source-only generation scripts that are not part of the runtime bundle

## Release Steps

From the staged bundle directory:

```bash
zip -r -X poem-v1.zip assets -x '*/.DS_Store' -x '*/__pycache__/*' -x '*.pyc'
shasum -a 256 poem-v1.zip
gh release create assets-poem-v1 poem-v1.zip --title "poem assets v1" --notes "Asset bundle for the dear poem template."
```

After upload, update `template.json` with the sha256 and zip size. The test suite locks these values so accidental bundle drift is visible.
