#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "template-source" / "collage-poem.html"
CONFIG_MARKER = "</head>"
ASSET_PREFIXES = ("assets/",)
WORKDIR_ASSET_PREFIX = "poem-work/"
MEDIA_SUFFIXES = {
    ".apng",
    ".avif",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mp4",
    ".otf",
    ".png",
    ".svg",
    ".ttf",
    ".webm",
    ".webp",
    ".woff",
    ".woff2",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--slots", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    return parser.parse_args()


def read_slots(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, dict):
        for key in ("items", "selected", "resolved", "layers", "scenes", "words", "lines"):
            if isinstance(value.get(key), list):
                return value[key]
    return []


def normalize_source_list(value: Any) -> list[str]:
    result: list[str] = []
    for item in as_list(value):
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict):
            src = item.get("src") or item.get("path") or item.get("resolved_path")
            if src:
                result.append(str(src))
    return result


def strip_workdir_prefix(workdir: Path, src_path: Path) -> Path | None:
    parts = src_path.parts
    if parts and parts[0] in {workdir.name, "poem-work"} and len(parts) > 1:
        return workdir.joinpath(*parts[1:])
    return None


def strip_asset_suffix(src: str) -> str:
    return re.split(r"[?#]", src, maxsplit=1)[0]


def resolve_asset_path(workdir: Path, src: str) -> Path | None:
    if not src or src.startswith(("data:", "http:", "https:", "file:", "blob:")):
        return None
    src_path = Path(strip_asset_suffix(src))
    if src_path.is_absolute():
        return src_path if src_path.is_file() else None
    workdir_relative_path = strip_workdir_prefix(workdir, src_path)
    candidates = [
        *([workdir_relative_path] if workdir_relative_path else []),
        workdir / src,
        ROOT / "base" / src,
        ROOT / "template-source" / src,
    ]
    return next((path for path in candidates if path.is_file()), None)


def encode_asset(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{data}"


def looks_like_asset_path(value: str, workdir: Path) -> bool:
    if value.startswith(ASSET_PREFIXES):
        return True
    if value.startswith(f"{workdir.name}/") or value.startswith(WORKDIR_ASSET_PREFIX):
        return True
    path = Path(strip_asset_suffix(value))
    return path.suffix.lower() in MEDIA_SUFFIXES and not re.search(r"\s", value)


def inline_config_assets(value: Any, workdir: Path) -> Any:
    if isinstance(value, dict):
        return {key: inline_config_assets(item, workdir) for key, item in value.items()}
    if isinstance(value, list):
        return [inline_config_assets(item, workdir) for item in value]
    if isinstance(value, str) and looks_like_asset_path(value, workdir):
        path = resolve_asset_path(workdir, value)
        if path:
            return encode_asset(path)
    return value


def normalize_scene(raw: dict[str, Any]) -> dict[str, Any]:
    key_map = {
        "title_color": "titleColor",
        "subtitle_color": "subtitleColor",
        "video_filter": "videoFilter",
        "subtitle_fragments": "subtitleFragments",
        "caption_fragments": "captionFragments",
        "initial_scene_id": "initialSceneId",
    }
    scene: dict[str, Any] = {}
    for key, value in raw.items():
        if value is None:
            continue
        scene[key_map.get(key, key)] = value
    return scene


def normalize_scenes(slots: dict[str, Any]) -> list[dict[str, Any]]:
    raw = slots.get("poem_scenes") or slots.get("scenes") or slots.get("theme_scenes")
    scenes = [normalize_scene(item) for item in as_list(raw) if isinstance(item, dict)]
    if scenes:
        return scenes

    plan = slots.get("poem_theme_plan") or slots.get("poem_story_plan") or slots.get("theme_plan") or {}
    media = slots.get("background_media") or slots.get("poem_media") or {}
    if not isinstance(plan, dict):
        plan = {}
    if not isinstance(media, dict):
        media = {}
    title = plan.get("theme_title") or plan.get("title")
    if not title:
        return []
    scene = {
        "id": str(plan.get("theme_id") or plan.get("id") or "custom"),
        "title": str(title),
    }
    optional_pairs = {
        "subtitle": plan.get("theme_subtitle") or plan.get("subtitle"),
        "ambient": plan.get("ambient") or plan.get("caption"),
        "accent": plan.get("accent"),
        "bg": plan.get("background_gradient") or plan.get("bg"),
        "titleColor": plan.get("title_color") or plan.get("titleColor"),
        "subtitleColor": plan.get("subtitle_color") or plan.get("subtitleColor"),
        "videoFilter": plan.get("video_filter") or plan.get("videoFilter"),
        "video": media.get("video") or media.get("background_video"),
        "poster": media.get("poster") or media.get("background_poster"),
        "basket": media.get("basket") or media.get("basket_image"),
    }
    scene.update({key: value for key, value in optional_pairs.items() if value})
    return [scene]


def normalize_film_layer(raw: dict[str, Any]) -> dict[str, Any]:
    layer: dict[str, Any] = {}
    for key in ("src", "x", "y", "w", "h", "rot", "opacity", "filter", "z"):
        if raw.get(key) is not None:
            layer[key] = raw[key]
    if "path" in raw and "src" not in layer:
        layer["src"] = raw["path"]
    if "resolved_path" in raw and "src" not in layer:
        layer["src"] = raw["resolved_path"]
    return layer


def normalize_layer_sets(slots: dict[str, Any]) -> list[list[dict[str, Any]]]:
    raw = slots.get("film_layer_sets") or slots.get("film_layers") or slots.get("collage_images")
    if isinstance(raw, dict) and isinstance(raw.get("sets"), list):
        raw = raw["sets"]
    if isinstance(raw, list) and raw and all(isinstance(item, dict) for item in raw):
        return [[normalize_film_layer(item) for item in raw if isinstance(item, dict)]]
    sets: list[list[dict[str, Any]]] = []
    for item in as_list(raw):
        if isinstance(item, list):
            sets.append([normalize_film_layer(layer) for layer in item if isinstance(layer, dict)])
        elif isinstance(item, dict):
            layers = as_list(item)
            if layers:
                sets.append([normalize_film_layer(layer) for layer in layers if isinstance(layer, dict)])
    return [item for item in sets if item]


def normalize_word_sets(slots: dict[str, Any]) -> dict[str, Any]:
    raw = slots.get("word_bank") or slots.get("theme_words") or slots.get("words")
    if isinstance(raw, dict):
        if isinstance(raw.get("word_sets"), list):
            return {"wordSets": raw["word_sets"]}
        if isinstance(raw.get("wordSets"), list):
            return {"wordSets": raw["wordSets"]}
        if isinstance(raw.get("per_scene"), list):
            return {"wordSets": raw["per_scene"]}
        if isinstance(raw.get("words"), list):
            return {"words": raw["words"]}
    if isinstance(raw, list):
        if raw and all(isinstance(item, list) for item in raw):
            return {"wordSets": raw}
        return {"words": [str(item) for item in raw]}
    return {}


def normalize_starter_sets(slots: dict[str, Any]) -> list[Any]:
    raw = slots.get("starter_sets") or slots.get("starter_words")
    if isinstance(raw, dict):
        if isinstance(raw.get("sets"), list):
            return raw["sets"]
        if isinstance(raw.get("items"), list):
            return [raw["items"]]
    if isinstance(raw, list):
        if raw and all(isinstance(item, list) and item and isinstance(item[0], list) for item in raw):
            return raw
        return [raw]
    return []


def normalize_paper_palette(slots: dict[str, Any]) -> dict[str, Any]:
    raw = slots.get("paper_palette") or slots.get("paper_style") or {}
    if not isinstance(raw, dict):
        return {}
    key_map = {
        "paper_paths": "paperPaths",
        "starter_papers": "starterPapers",
        "paper_colors": "paperColors",
        "black_paper": "blackPaper",
        "font_options": "fontOptions",
    }
    config: dict[str, Any] = {}
    for key, value in raw.items():
        if value:
            config[key_map.get(key, key)] = value
    return config


def normalize_runtime_overrides(slots: dict[str, Any]) -> dict[str, Any]:
    raw = slots.get("poem_runtime_overrides") or slots.get("runtime_overrides") or {}
    return raw if isinstance(raw, dict) else {}


def build_runtime_config(slots: dict[str, Any], workdir: Path) -> dict[str, Any]:
    config: dict[str, Any] = {"template": "poem"}

    scenes = normalize_scenes(slots)
    if scenes:
        config["scenes"] = scenes

    layer_sets = normalize_layer_sets(slots)
    if layer_sets:
        config["filmLayerSets"] = layer_sets

    config.update(normalize_word_sets(slots))

    starter_sets = normalize_starter_sets(slots)
    if starter_sets:
        config["starterSets"] = starter_sets

    paper_palette = normalize_paper_palette(slots)
    if paper_palette:
        config.update(paper_palette)

    initial_scene_id = slots.get("initial_scene_id") or slots.get("initialSceneId")
    if initial_scene_id:
        config["initialSceneId"] = initial_scene_id
    if isinstance(slots.get("initial_scene_index"), int):
        config["initialSceneIndex"] = slots["initial_scene_index"]

    config.update(normalize_runtime_overrides(slots))
    return inline_config_assets(config, workdir)


def inline_css_urls(html_text: str, workdir: Path) -> str:
    pattern = re.compile(r"url\((?P<quote>['\"]?)(?P<src>assets/[^'\")]+)(?P=quote)\)")

    def replace(match: re.Match[str]) -> str:
        src = match.group("src")
        path = resolve_asset_path(workdir, src)
        if not path:
            return match.group(0)
        return f'url("{encode_asset(path)}")'

    return pattern.sub(replace, html_text)


def inline_quoted_asset_paths(html_text: str, workdir: Path) -> str:
    pattern = re.compile(r"(?P<quote>['\"])(?P<src>assets/[^'\"]+)(?P=quote)")

    def replace(match: re.Match[str]) -> str:
        quote = match.group("quote")
        src = match.group("src")
        path = resolve_asset_path(workdir, src)
        if not path:
            return match.group(0)
        return f"{quote}{encode_asset(path)}{quote}"

    return pattern.sub(replace, html_text)


def inject_config(html_text: str, config: dict[str, Any]) -> str:
    payload = json.dumps(config, ensure_ascii=False, separators=(",", ":"))
    injection = f"<script>window.POEM_GIFT_CONFIG = {payload};</script>"
    if CONFIG_MARKER in html_text:
        return html_text.replace(CONFIG_MARKER, f"  {injection}\n{CONFIG_MARKER}", 1)
    return injection + "\n" + html_text


def main() -> int:
    args = parse_args()
    slots = read_slots(args.slots)
    args.workdir.mkdir(parents=True, exist_ok=True)
    config = build_runtime_config(slots, args.workdir)
    (args.workdir / "runtime_config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")

    html_text = CANONICAL.read_text(encoding="utf-8")
    html_text = inline_css_urls(html_text, args.workdir)
    html_text = inline_quoted_asset_paths(html_text, args.workdir)
    html_text = inject_config(html_text, config)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(html_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
