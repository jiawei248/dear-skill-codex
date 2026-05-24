import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = ROOT / "assets" / "templates" / "poem"
TEMPLATE = TEMPLATE_DIR / "template.json"
CANONICAL = TEMPLATE_DIR / "template-source" / "collage-poem.html"


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


def load_manifest():
    return json.loads(TEMPLATE.read_text(encoding="utf-8"))


def slot_by_id(manifest, slot_id):
    return {slot["id"]: slot for slot in manifest["slots"]}[slot_id]


def extract_runtime_config(html_text):
    match = re.search(
        r"window\.POEM_GIFT_CONFIG\s*=\s*(\{.*?\});\s*</script>",
        html_text,
        re.S,
    )
    assert match, "missing POEM_GIFT_CONFIG script"
    return json.loads(match.group(1))


def sample_slots():
    return {
        "poem_scenes": [
            {
                "id": "shore-letter",
                "title": "山海替你保存一封信",
                "subtitle": "dear you",
                "video": "poem-work/media/bg.mp4",
                "poster": "poem-work/media/poster.jpg",
                "basket": "poem-work/media/basket.png",
                "accent": "#c07a4a",
                "bg": ["#141a25", "#32241d", "#8a6037"],
                "title_color": "rgba(255, 220, 160, 0.94)",
                "subtitle_color": "rgba(255, 225, 176, 0.72)",
                "video_filter": "saturate(0.82) contrast(1.08)",
            }
        ],
        "film_layers": [
            {"src": "poem-work/images/layer1.jpg", "x": 120, "y": 260, "w": 300, "h": 420, "rot": -1},
            {"src": "poem-work/images/layer2.png", "x": 540, "y": 560, "w": 360, "h": 260, "rot": 1},
        ],
        "word_bank": {
            "words": ["山海", "替", "你", "保存", "一封信", "的", "的", "得", "地", "在", "把", "给"]
        },
        "starter_words": [["山海", 266, 342], ["替", 718, 386], ["你", 554, 922]],
        "paper_palette": {
            "paper_paths": ["poem-work/papers/cream.png", "poem-work/papers/blue.png"],
            "paper_colors": ["#151612", "#6f2117", "#fff8e8"],
        },
        "initial_scene_id": "shore-letter",
    }


def run_poem_builder(tmp_path, slots):
    workdir = tmp_path / "poem-work"
    (workdir / "media").mkdir(parents=True)
    (workdir / "images").mkdir(parents=True)
    (workdir / "papers").mkdir(parents=True)
    (workdir / "media" / "bg.mp4").write_bytes(b"fake-mp4")
    (workdir / "media" / "poster.jpg").write_bytes(b"fake-jpeg")
    (workdir / "media" / "basket.png").write_bytes(PNG_1X1)
    (workdir / "images" / "layer1.jpg").write_bytes(b"fake-jpeg")
    (workdir / "images" / "layer2.png").write_bytes(PNG_1X1)
    (workdir / "papers" / "cream.png").write_bytes(PNG_1X1)
    (workdir / "papers" / "blue.png").write_bytes(PNG_1X1)
    slots_path = workdir / "filled-slots.json"
    slots_path.write_text(json.dumps(slots, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "index.html"

    result = subprocess.run(
        [
            "python3",
            str(TEMPLATE_DIR / "template-source" / "build.py"),
            "--slots",
            str(slots_path),
            "--workdir",
            str(workdir),
            "--out",
            str(out),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return out, workdir, result


def test_poem_template_manifest_and_files_exist():
    manifest = load_manifest()

    assert manifest["id"] == "poem"
    assert "collage-poem" in manifest["aliases"]
    assert "拼贴诗" in manifest["aliases"]
    assert manifest["status"] == "ready"
    assert manifest["preview"] == "preview.png"
    assert (TEMPLATE_DIR / manifest["preview"]).is_file()
    assert (TEMPLATE_DIR / "demo-preview.png").is_file()
    assert manifest["canonical_html_reference"] == "template-source/collage-poem.html"
    assert (TEMPLATE_DIR / manifest["canonical_html_reference"]).is_file()
    assert manifest["build_script"] == "template-source/build.py"
    assert (TEMPLATE_DIR / manifest["build_script"]).is_file()
    assert (TEMPLATE_DIR / "README.md").is_file()
    assert (TEMPLATE_DIR / "SPEC.md").is_file()
    assert (TEMPLATE_DIR / "RELEASE.md").is_file()
    assert (TEMPLATE_DIR / "base" / ".gitkeep").is_file()


def test_poem_asset_bundle_metadata_matches_release_contract():
    bundle = load_manifest()["asset_bundle"]

    assert bundle["local_path"] == "base/"
    assert bundle["url"].endswith("/assets-poem-v1/poem-v1.zip")
    assert bundle["sha256"] == "e50e60ccd2a930335692eb653f0267bae14da18056fb5f0693a290b44fd59d36"
    assert len(bundle["sha256"]) == 64
    assert bundle["size_mb"] == 50
    assert bundle["contents"] == [
        "assets/generated/",
        "assets/scene1/",
        "assets/scene2/",
        "assets/papers/",
        "assets/fonts/",
        "assets/previews/",
    ]


def test_poem_base_gitkeep_is_allowed_but_bundle_contents_are_ignored():
    gitkeep = TEMPLATE_DIR / "base" / ".gitkeep"

    assert gitkeep.is_file()
    keep_result = subprocess.run(
        ["git", "check-ignore", "-q", "assets/templates/poem/base/.gitkeep"],
        cwd=ROOT,
    )
    assert keep_result.returncode == 1

    bundle_result = subprocess.run(
        ["git", "check-ignore", "-q", "assets/templates/poem/base/assets"],
        cwd=ROOT,
    )
    assert bundle_result.returncode == 0


def test_poem_slots_capture_theme_first_media_and_word_bank_rules():
    manifest = load_manifest()

    recipient = slot_by_id(manifest, "recipient_material")
    assert recipient["type"] == "user_context"
    assert "infer one from the strongest concrete motifs" in recipient["grounding_rules"][0]

    plan = slot_by_id(manifest, "poem_theme_plan")
    assert plan["type"] == "ai_text"
    assert "background_video_prompt" in plan["output_fields"]
    assert "word_bank_strategy" in plan["output_fields"]
    assert "Start from user material" in plan["rules"][0]

    video = slot_by_id(manifest, "background_video")
    assert video["type"] == "ai_generated_video"
    assert "beautiful, cinematic, HD, film-grain background video" in video["selection_rules"][1]

    layers = slot_by_id(manifest, "film_image_layers")
    assert layers["count_range"] == [2, 3]
    assert "one visual world" in layers["style_rules"][3]

    words = slot_by_id(manifest, "word_bank")
    assert words["count_range"] == [120, 220]
    assert "function words and connectors" in words["rules"][2]
    assert "Repeat especially useful particles/connectors" in words["rules"][3]

    paper = slot_by_id(manifest, "paper_palette")
    assert "harmonizes with the selected video and still images" in paper["purpose"]


def test_poem_docs_describe_four_phase_plan_and_user_requested_rules():
    spec = (TEMPLATE_DIR / "SPEC.md").read_text(encoding="utf-8")
    plan = (ROOT / "docs" / "superpowers" / "plans" / "2026-05-24-poem-template-support.md").read_text(
        encoding="utf-8"
    )
    release = (TEMPLATE_DIR / "RELEASE.md").read_text(encoding="utf-8")

    for phrase in [
        "Infer the theme before media search",
        "Background video sets the weather",
        "Image layers must share one world",
        "The word bank must be abundant",
        "Function words should repeat",
        "Paper chips must match the palette",
        "canonical output is `template-source/collage-poem.html`",
    ]:
        assert phrase in spec

    for phase in [
        "Phase 1 — Template Registry and Documentation",
        "Phase 2 — Runtime Builder and Config Hook",
        "Phase 3 — Asset Bundle and GitHub Release",
        "Phase 4 — Tests, Registry Copy, and Verification",
    ]:
        assert phase in plan

    assert "assets-poem-v1" in release
    assert "poem-v1.zip" in release
    assert "shasum -a 256" in release


def test_poem_registry_copy_is_discoverable():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    templates = (ROOT / "references" / "templates.md").read_text(encoding="utf-8")

    for text in [readme, skill, templates]:
        assert "--template poem" in text

    assert "assets/templates/poem/preview.png" in readme
    assert "Film Collage Word Basket" in templates
    assert "scripts/fetch-asset-bundle.sh --template poem" in templates
    assert "背景视频、同色调图片和一篮可拖拽纸条词语" in readme


def test_poem_builder_injects_runtime_config_inlines_assets_and_preserves_source(tmp_path):
    before = hashlib.sha256(CANONICAL.read_bytes()).hexdigest()

    out, workdir, _ = run_poem_builder(tmp_path, sample_slots())
    html_text = out.read_text(encoding="utf-8")
    config = extract_runtime_config(html_text)

    assert out.is_file()
    assert config["template"] == "poem"
    assert config["scenes"][0]["title"] == "山海替你保存一封信"
    assert config["scenes"][0]["titleColor"] == "rgba(255, 220, 160, 0.94)"
    assert config["scenes"][0]["video"].startswith("data:video/mp4;base64,")
    assert config["scenes"][0]["poster"].startswith("data:image/jpeg;base64,")
    assert config["scenes"][0]["basket"].startswith("data:image/png;base64,")
    assert config["filmLayerSets"][0][0]["src"].startswith("data:image/jpeg;base64,")
    assert config["filmLayerSets"][0][1]["src"].startswith("data:image/png;base64,")
    assert config["words"].count("的") == 2
    assert config["starterSets"][0][0] == ["山海", 266, 342]
    assert config["paperPaths"][0].startswith("data:image/png;base64,")
    assert config["paperColors"] == ["#151612", "#6f2117", "#fff8e8"]
    assert config["initialSceneId"] == "shore-letter"
    assert "window.POEM_GIFT_CONFIG" in html_text
    assert "const POEM_CONFIG = window.POEM_GIFT_CONFIG || {};" in html_text
    assert "poem-work/media/bg.mp4" not in html_text

    staged = json.loads((workdir / "runtime_config.json").read_text(encoding="utf-8"))
    assert staged == config
    after = hashlib.sha256(CANONICAL.read_bytes()).hexdigest()
    assert after == before


def test_poem_builder_accepts_manifest_theme_plan_slot(tmp_path):
    slots = {
        "poem_theme_plan": {
            "theme_id": "slow-bus",
            "theme_title": "夜班车把心事开慢一点",
            "theme_subtitle": "slow route",
            "title_color": "rgba(255, 245, 210, 0.92)",
        },
        "background_media": {
            "video": "poem-work/media/bg.mp4",
            "poster": "poem-work/media/poster.jpg",
            "basket": "poem-work/media/basket.png",
        },
        "word_bank": ["夜班车", "把", "心事", "的", "的", "在"],
    }

    out, _, _ = run_poem_builder(tmp_path, slots)
    config = extract_runtime_config(out.read_text(encoding="utf-8"))

    assert config["scenes"][0]["id"] == "slow-bus"
    assert config["scenes"][0]["title"] == "夜班车把心事开慢一点"
    assert config["scenes"][0]["subtitle"] == "slow route"
    assert config["scenes"][0]["titleColor"] == "rgba(255, 245, 210, 0.92)"
    assert config["scenes"][0]["video"].startswith("data:video/mp4;base64,")
