from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_homepage_override_normalizes_material_root_font_size() -> None:
    override = (ROOT / "overrides" / "main.html").read_text()

    assert "html { font-size: 16px; }" in override
    assert "body { font-size: 15.5px; }" in override


def test_landing_css_keeps_portfolio_body_baseline() -> None:
    landing_css = (ROOT / "docs" / "assets" / "landing.css").read_text()

    assert "font-size: 15.5px;" in landing_css
