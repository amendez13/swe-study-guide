"""Tests for the standalone study-guide web server."""

from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path


def import_serve_module():
    """Import the repo-root serve.py module for direct testing."""
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "serve.py"
    spec = importlib.util.spec_from_file_location("swe_study_guide_serve", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


serve_module = import_serve_module()


def _write_topic(content_root: Path, tech: str, topic: str, files: dict[str, str]) -> None:
    topic_dir = content_root / tech / topic
    topic_dir.mkdir(parents=True)
    for name, text in files.items():
        (topic_dir / name).write_text(text, encoding="utf-8")


def test_build_content_index_has_drills_when_drills_md_present(monkeypatch, tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write_topic(
        content,
        "01_Algorithms",
        "01_Complexity",
        {"notes.md": "# Notes\n", "concepts.md": "## Concept\n", "drills.md": "## Drill\n"},
    )
    monkeypatch.setattr(serve_module, "CONTENT_DIR", content)

    topic = serve_module.build_content_index()["technologies"][0]["topics"][0]

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"


def test_build_content_index_has_drills_false_when_drills_md_absent(monkeypatch, tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write_topic(
        content,
        "01_Algorithms",
        "02_Sorting",
        {"notes.md": "# Notes\n", "concepts.md": "## Concept\n"},
    )
    monkeypatch.setattr(serve_module, "CONTENT_DIR", content)

    topic = serve_module.build_content_index()["technologies"][0]["topics"][0]

    assert topic["hasDrills"] is False
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"


def test_build_content_index_excludes_drills_md_from_notes_candidates(monkeypatch, tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write_topic(
        content,
        "01_Algorithms",
        "03_Graphs",
        {"overview.md": "# Overview\n", "concepts.md": "## Concept\n", "drills.md": "## Drill\n"},
    )
    monkeypatch.setattr(serve_module, "CONTENT_DIR", content)

    topic = serve_module.build_content_index()["technologies"][0]["topics"][0]

    assert topic["notesFile"] == "overview.md"
    assert topic["hasDrills"] is True


def test_build_content_index_drills_only_topic_has_no_notes_file(monkeypatch, tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write_topic(content, "01_Algorithms", "04_Heaps", {"drills.md": "## Drill\n"})
    monkeypatch.setattr(serve_module, "CONTENT_DIR", content)

    topic = serve_module.build_content_index()["technologies"][0]["topics"][0]

    assert topic["notesFile"] is None
    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is False


def test_algorithmic_complexity_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "07_Data_Structures_and_Algorithms"
        for item in tech["topics"]
        if item["dir"] == "01_Algorithmic_Complexity"
    )

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"


def test_arrays_strings_hash_tables_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "07_Data_Structures_and_Algorithms"
        for item in tech["topics"]
        if item["dir"] == "02_Arrays_Strings_and_Hash_Tables"
    )

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"


def test_resolve_under_allows_paths_within_root(tmp_path: Path) -> None:
    root = tmp_path / "content"
    nested_file = root / "topic" / "notes.md"
    nested_file.parent.mkdir(parents=True)
    nested_file.write_text("hello", encoding="utf-8")

    resolved = serve_module.resolve_under(root, "topic/notes.md")

    assert resolved == nested_file.resolve()


def test_resolve_under_rejects_path_traversal(tmp_path: Path) -> None:
    root = tmp_path / "content"
    root.mkdir()
    outside = tmp_path / "README.md"
    outside.write_text("secret", encoding="utf-8")

    resolved = serve_module.resolve_under(root, "../README.md")

    assert resolved is None


def test_build_health_payload_uses_release_info(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        serve_module,
        "get_release_info",
        lambda: {"tag": "v1.2.3", "commit": "abc123", "short_commit": "abc123", "source": "env"},
    )

    payload = serve_module.build_health_payload()

    assert payload == {
        "status": "ok",
        "release": {
            "tag": "v1.2.3",
            "commit": "abc123",
            "short_commit": "abc123",
            "source": "env",
        },
    }


def test_main_binds_requested_host_and_port(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    recorded: dict[str, object] = {}

    class FakeServer:
        def __init__(self, address, handler):  # type: ignore[no-untyped-def]
            recorded["address"] = address
            recorded["handler"] = handler
            self.daemon_threads = False

        def serve_forever(self) -> None:
            raise KeyboardInterrupt()

        def shutdown(self) -> None:
            recorded["shutdown"] = True

    monkeypatch.setattr(
        serve_module.argparse.ArgumentParser,
        "parse_args",
        lambda self: serve_module.argparse.Namespace(host="0.0.0.0", port=9099),
    )
    monkeypatch.setattr(
        serve_module,
        "build_content_index",
        lambda: {"technologies": [{"topics": []}]},
    )
    monkeypatch.setattr(serve_module, "ThreadingHTTPServer", FakeServer)

    serve_module.main()

    captured = capsys.readouterr()
    assert recorded["address"] == ("0.0.0.0", 9099)
    assert recorded["shutdown"] is True
    assert "http://0.0.0.0:9099" in captured.out


def test_send_ok_sets_no_cache_and_skips_body_for_head() -> None:
    handler = serve_module.StudyHandler.__new__(serve_module.StudyHandler)
    recorded: list[tuple[str, str]] = []
    body = b'console.log("study guide");'

    handler.wfile = io.BytesIO()
    handler.send_response = lambda code: recorded.append(("status", str(code)))  # type: ignore[method-assign]
    handler.send_header = lambda key, value: recorded.append((key, value))  # type: ignore[method-assign]
    handler.end_headers = lambda: recorded.append(("end_headers", ""))  # type: ignore[method-assign]

    handler._send_ok(  # type: ignore[attr-defined]
        content_type="application/javascript; charset=utf-8",
        include_body=False,
        body=body,
        cache_control="no-store",
    )

    assert ("status", "200") in recorded
    assert ("Content-Length", str(len(body))) in recorded
    assert ("Cache-Control", "no-store") in recorded
    assert ("Pragma", "no-cache") in recorded
    assert ("Expires", "0") in recorded
    assert handler.wfile.getvalue() == b""


def test_send_ok_sets_cors_for_content_api() -> None:
    handler = serve_module.StudyHandler.__new__(serve_module.StudyHandler)
    recorded: list[tuple[str, str]] = []
    body = b"{}"

    handler.wfile = io.BytesIO()
    handler.send_response = lambda code: recorded.append(("status", str(code)))  # type: ignore[method-assign]
    handler.send_header = lambda key, value: recorded.append((key, value))  # type: ignore[method-assign]
    handler.end_headers = lambda: None  # type: ignore[method-assign]

    handler._send_ok(  # type: ignore[attr-defined]
        content_type="application/json",
        include_body=True,
        body=body,
        allow_cors=True,
        cache_control="no-store",
    )

    assert ("Access-Control-Allow-Origin", "*") in recorded
    assert handler.wfile.getvalue() == body
