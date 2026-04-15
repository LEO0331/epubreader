from __future__ import annotations

from packages.parsing.html_parser import parse_html


def test_html_parser_removes_navigation_noise_and_preserves_structure():
    html = b"""
    <html>
      <head><title>Sample Book</title></head>
      <body>
        <nav>menu</nav>
        <h1>Chapter One</h1>
        <p>Intro paragraph.</p>
        <h2>Section A</h2>
        <p>Useful content.</p>
        <footer>footer text</footer>
      </body>
    </html>
    """

    parsed = parse_html(html)

    assert parsed["metadata"]["title"] == "Sample Book"
    assert len(parsed["sections"]) == 2
    assert parsed["sections"][0]["heading"] == "Chapter One"
    assert parsed["sections"][1]["heading_path"] == ["Chapter One", "Section A"]
