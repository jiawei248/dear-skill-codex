from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify-h5.sh"
DOC = ROOT / "references" / "stage4-visualization.md"


def test_verify_h5_script_exists_and_mentions_browser_flow():
    assert SCRIPT.is_file()
    text = SCRIPT.read_text(encoding="utf-8")

    assert "Usage: verify-h5.sh <index.html>" in text
    assert "Codex browser" in text
    assert "npx playwright" in text
    assert "python3 -m http.server" in text
    assert "console" in text.lower()


def test_stage4_docs_define_codex_browser_h5_flow():
    text = DOC.read_text(encoding="utf-8")

    assert "scripts/verify-h5.sh <index.html>" in text
    assert "Codex" in text
    assert "browser_navigate" in text
    assert "browser_snapshot" in text
    assert "console" in text.lower()


def test_stage4_docs_include_paper_house_checklist():
    text = DOC.read_text(encoding="utf-8")

    for phrase in [
        "page opens",
        "four rooms",
        "hero item",
        "card is readable",
        "music preview",
        "mobile viewport",
        "console",
    ]:
        assert phrase in text
