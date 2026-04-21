from __future__ import annotations

from pathlib import Path

from packages.exporters.obsidian_exporter import export_obsidian


def test_obsidian_basic_profile_keeps_original_shape(tmp_path: Path):
    out = export_obsidian(
        output_dir=tmp_path,
        collection_name="My Set",
        books=[
            {
                "id": "book-1",
                "summary": "S1",
                "wiki": "W1",
            }
        ],
        profile="basic",
    )

    note = (out / "book-1.md").read_text(encoding="utf-8")
    assert note == "# book-1\n\n## Summary\nS1\n\n## Wiki\nW1"


def test_obsidian_enhanced_frontmatter_and_tags(tmp_path: Path):
    out = export_obsidian(
        output_dir=tmp_path,
        collection_name="My Set",
        books=[
            {
                "id": "book-1",
                "title": "My Book",
                "source_type": "uploaded_pdf",
                "summary": "hello",
                "wiki": "world",
            }
        ],
        profile="enhanced",
    )

    note = (out / "book-1.md").read_text(encoding="utf-8")
    assert note.startswith("---\n")
    assert 'title: "My Book"' in note
    assert 'book_id: "book-1"' in note
    assert 'source_type: "uploaded_pdf"' in note
    assert 'collection: "My Set"' in note
    assert '  - "book-qa-library"' in note
    assert '  - "source/uploaded_pdf"' in note
    assert '  - "collection/my_set"' in note
    assert "aliases:" in note
    assert '  - "My Book"' in note


def test_obsidian_enhanced_preserves_emoji(tmp_path: Path):
    out = export_obsidian(
        output_dir=tmp_path,
        collection_name="Emoji Set",
        books=[
            {
                "id": "book-1",
                "source_type": "uploaded_epub",
                "summary": "Emoji 😀 kept",
                "wiki": "Wiki 🚀 kept",
            }
        ],
        profile="enhanced",
    )

    note = (out / "book-1.md").read_text(encoding="utf-8")
    assert "Emoji 😀 kept" in note
    assert "Wiki 🚀 kept" in note


def test_obsidian_enhanced_copies_local_relative_image_and_rewrites_link(tmp_path: Path):
    artifact_dir = tmp_path / "artifact-src"
    artifact_dir.mkdir(parents=True, exist_ok=True)
    img = artifact_dir / "chart.png"
    img.write_bytes(b"PNGDATA")

    out = export_obsidian(
        output_dir=tmp_path,
        collection_name="Media Set",
        books=[
            {
                "id": "book-1",
                "source_type": "uploaded_pdf",
                "summary": "![chart](chart.png)",
                "wiki": "",
                "summary_path": str(artifact_dir / "summary.md"),
            }
        ],
        profile="enhanced",
    )

    note = (out / "book-1.md").read_text(encoding="utf-8")
    assert "![chart](assets/book-1/chart.png)" in note
    copied = out / "assets" / "book-1" / "chart.png"
    assert copied.exists()
    assert copied.read_bytes() == b"PNGDATA"


def test_obsidian_enhanced_missing_local_image_adds_warning(tmp_path: Path):
    artifact_dir = tmp_path / "artifact-src"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    out = export_obsidian(
        output_dir=tmp_path,
        collection_name="Warn Set",
        books=[
            {
                "id": "book-1",
                "source_type": "uploaded_pdf",
                "summary": "![missing](missing.png)",
                "wiki": "",
                "summary_path": str(artifact_dir / "summary.md"),
            }
        ],
        profile="enhanced",
    )

    note = (out / "book-1.md").read_text(encoding="utf-8")
    assert "![missing](missing.png)" in note
    assert "export_warnings:" in note
    assert "Unresolved local image asset: missing.png" in note


def test_obsidian_enhanced_remote_and_data_images_are_untouched(tmp_path: Path):
    out = export_obsidian(
        output_dir=tmp_path,
        collection_name="Remote Set",
        books=[
            {
                "id": "book-1",
                "source_type": "uploaded_pdf",
                "summary": (
                    "![http](https://cdn.example.com/x.png)\n"
                    '<img src="data:image/png;base64,abc"/>'
                ),
                "wiki": "",
            }
        ],
        profile="enhanced",
    )

    note = (out / "book-1.md").read_text(encoding="utf-8")
    assert "![http](https://cdn.example.com/x.png)" in note
    assert '<img src="data:image/png;base64,abc"/>' in note


def test_obsidian_enhanced_rejects_path_traversal_asset_copy(tmp_path: Path):
    root = tmp_path / "context"
    root.mkdir(parents=True, exist_ok=True)
    outside = tmp_path / "outside.png"
    outside.write_bytes(b"NOPE")

    out = export_obsidian(
        output_dir=tmp_path,
        collection_name="Path Set",
        books=[
            {
                "id": "book-1",
                "source_type": "uploaded_pdf",
                "summary": "![bad](../outside.png)",
                "wiki": "",
                "summary_path": str(root / "summary.md"),
            }
        ],
        profile="enhanced",
    )

    note = (out / "book-1.md").read_text(encoding="utf-8")
    assert "![bad](../outside.png)" in note
    assert "export_warnings:" in note
    assert not (out / "assets" / "book-1" / "outside.png").exists()


def test_obsidian_enhanced_frontmatter_sanitizes_newline_injection(tmp_path: Path):
    out = export_obsidian(
        output_dir=tmp_path,
        collection_name="My Set\ninjected: true",
        books=[
            {
                "id": "book-1",
                "title": 'Real Title"\ninjected: true',
                "source_type": "uploaded_pdf",
                "summary": "ok",
                "wiki": "ok",
            }
        ],
        profile="enhanced",
    )

    note = (out / "book-1.md").read_text(encoding="utf-8")
    assert 'title: "Real Title\\" injected: true"' in note
    assert 'collection: "My Set injected: true"' in note
    assert "\ninjected: true\n" not in note


def test_obsidian_export_rejects_unknown_profile(tmp_path: Path):
    try:
        export_obsidian(
            output_dir=tmp_path,
            collection_name="My Set",
            books=[],
            profile="unexpected",
        )
    except ValueError as exc:
        assert "Unsupported obsidian export profile" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported profile")
