"""Tests for the NotebookLM source bundle helper."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "ai-skills"
    / "swe-study-guide-notebooklm-source-creator"
    / "scripts"
    / "build_notebooklm_sources.py"
)
MODULE_SPEC = importlib.util.spec_from_file_location("build_notebooklm_sources", MODULE_PATH)
assert MODULE_SPEC is not None
assert MODULE_SPEC.loader is not None
build_notebooklm_sources = importlib.util.module_from_spec(MODULE_SPEC)
sys.modules[MODULE_SPEC.name] = build_notebooklm_sources
MODULE_SPEC.loader.exec_module(build_notebooklm_sources)


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_is_topic_dir_requires_local_text_sources(tmp_path: Path) -> None:
    repo_root = tmp_path
    topic_dir = repo_root / "content" / "01_FastAPI" / "01_Framework_Foundations"
    topic_dir.mkdir(parents=True)
    assert not build_notebooklm_sources.is_topic_dir(topic_dir)

    write_text(topic_dir / "concepts.md", "## Concept\n")
    assert build_notebooklm_sources.is_topic_dir(topic_dir)

    research_dir = repo_root / "content" / "01_FastAPI" / "research"
    research_dir.mkdir(parents=True)
    write_text(research_dir / "concepts.md", "# Research\n")
    assert not build_notebooklm_sources.is_topic_dir(research_dir)


def test_collect_sources_orders_topic_then_technology_context(tmp_path: Path) -> None:
    topic_dir = tmp_path / "content" / "01_FastAPI" / "03_Path_Operations_and_Routing"
    write_text(topic_dir / "concepts.md", "## Path operations\n")
    write_text(topic_dir / "notes.md", "# Notes\n")
    write_text(topic_dir.parent / "technology_concepts.md", "# FastAPI tech concepts\n")
    write_text(topic_dir.parent / "research" / "concepts.md", "# Research concepts\n")
    write_text(topic_dir.parent / "research" / "course_outlines.md", "# Course outlines\n")

    sources = build_notebooklm_sources.collect_sources(topic_dir)

    assert [entry.target_name for entry in sources] == [
        "01_topic_concepts.md",
        "02_topic_notes.md",
        "03_technology_concepts.md",
        "04_research_concepts.md",
        "05_course_outlines.md",
    ]


def test_build_bundle_writes_expected_files(tmp_path: Path) -> None:
    repo_root = tmp_path
    topic_dir = repo_root / "content" / "01_FastAPI" / "03_Path_Operations_and_Routing"
    output_root = repo_root / "notebooklm"
    write_text(topic_dir / "concepts.md", "## Path operations\n")
    write_text(topic_dir / "notes.md", "# Notes\n")
    write_text(topic_dir.parent / "technology_concepts.md", "# FastAPI tech concepts\n")

    bundle_dir, source_count = build_notebooklm_sources.build_bundle(topic_dir, repo_root, output_root, dry_run=False)

    assert bundle_dir == output_root / "01_FastAPI" / "03_Path_Operations_and_Routing"
    assert source_count == 3
    assert (bundle_dir / "README.md").exists()
    assert (bundle_dir / "sources" / "01_topic_concepts.md").read_text(encoding="utf-8") == "## Path operations\n"
    assert "SWE Study Guide - FastAPI - Path Operations and Routing" in (bundle_dir / "README.md").read_text(encoding="utf-8")


def test_main_supports_all_existing_scope(tmp_path: Path, capsys) -> None:
    repo_root = tmp_path
    topic_dir = repo_root / "content" / "01_FastAPI" / "03_Path_Operations_and_Routing"
    output_root = repo_root / "notebooklm"
    write_text(topic_dir / "concepts.md", "## Path operations\n")
    write_text(topic_dir.parent / "technology_concepts.md", "# FastAPI tech concepts\n")
    (output_root / "01_FastAPI" / "03_Path_Operations_and_Routing").mkdir(parents=True)

    exit_code = build_notebooklm_sources.main(
        [
            "--repo-root",
            str(repo_root),
            "--output-root",
            str(output_root),
            "--all-existing",
            "--dry-run",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Would update notebooklm/01_FastAPI/03_Path_Operations_and_Routing" in captured.out
