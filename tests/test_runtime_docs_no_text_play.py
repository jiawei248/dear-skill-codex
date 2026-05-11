from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

TEXT_PLAY_FORBIDDEN = [
    "text-play",
    "text_play",
    "text play",
    "Interactive text-play",
    "互动文字游戏",
    "互动文字礼物",
    "文字游戏",
    "live-chat gift",
    "live chat interactions",
]


def test_runtime_references_do_not_expose_text_play_as_supported_format():
    scanned_roots = [
        ROOT / "CHANGELOG.md",
        ROOT / "CONTRIBUTING.md",
        ROOT / "README.md",
        ROOT / "SKILL.md",
        ROOT / "gift-history.example.json",
        ROOT / "gift-history.schema.json",
        ROOT / "references",
    ]
    offenders = []
    for root in scanned_roots:
        paths = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
        for path in paths:
            if path.suffix.lower() not in {".md", ".json", ".py"}:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for token in TEXT_PLAY_FORBIDDEN:
                if token in text:
                    offenders.append(f"{path.relative_to(ROOT)} contains {token}")

    assert offenders == []
