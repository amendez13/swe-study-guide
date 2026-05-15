"""Tests for the standalone study-guide web server."""

from __future__ import annotations

import importlib.util
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
