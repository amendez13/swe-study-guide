#!/usr/bin/env python3
"""Build text-only NotebookLM source bundles from local study-guide material."""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp", ".tiff", ".svg"}
MEDIA_OR_METADATA_EXTENSIONS = IMAGE_EXTENSIONS | {".json"}


@dataclass(frozen=True)
class SourceEntry:
    source: Path
    target_name: str
    role: str


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def relative_to_repo(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def clean_display_name(name: str) -> str:
    text = re.sub(r"^\d+_", "", name)
    text = text.replace("_", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return text or name


def technology_title(technology_dir: Path) -> str:
    return clean_display_name(technology_dir.name)


def topic_title(topic_dir: Path) -> str:
    return clean_display_name(topic_dir.name)


def is_topic_dir(path: Path) -> bool:
    if not path.is_dir():
        return False
    if path.name == "research":
        return False
    return any((path / filename).exists() for filename in ("concepts.md", "notes.md"))


def target_name(prefix: int, label: str, source: Path) -> str:
    safe_label = re.sub(r"[^a-z0-9]+", "_", label.lower()).strip("_")
    return f"{prefix:02d}_{safe_label}{source.suffix.lower()}"


def collect_sources(topic_dir: Path) -> list[SourceEntry]:
    sources: list[SourceEntry] = []
    prefix = 1

    topic_concepts = topic_dir / "concepts.md"
    if topic_concepts.exists():
        sources.append(
            SourceEntry(
                topic_concepts,
                target_name(prefix, "topic_concepts", topic_concepts),
                "Primary topic concept cards rendered by the study site.",
            )
        )
        prefix += 1

    topic_notes = topic_dir / "notes.md"
    if topic_notes.exists():
        sources.append(
            SourceEntry(
                topic_notes,
                target_name(prefix, "topic_notes", topic_notes),
                "Topic-level narrative notes and examples.",
            )
        )
        prefix += 1

    technology_dir = topic_dir.parent
    technology_concepts = technology_dir / "technology_concepts.md"
    if technology_concepts.exists():
        sources.append(
            SourceEntry(
                technology_concepts,
                target_name(prefix, "technology_concepts", technology_concepts),
                "Technology-level concept map for the surrounding domain.",
            )
        )
        prefix += 1

    research_dir = technology_dir / "research"
    research_concepts = research_dir / "concepts.md"
    if research_concepts.exists():
        sources.append(
            SourceEntry(
                research_concepts,
                target_name(prefix, "research_concepts", research_concepts),
                "Upstream curriculum concepts that shaped the study topic.",
            )
        )
        prefix += 1

    course_outlines = research_dir / "course_outlines.md"
    if course_outlines.exists():
        sources.append(
            SourceEntry(
                course_outlines,
                target_name(prefix, "course_outlines", course_outlines),
                "Course-outline research used to scope the technology.",
            )
        )

    return sources


def bundle_dir_for_topic(topic_dir: Path, repo_root: Path, output_root: Path) -> Path:
    content_root = repo_root / "content"
    return output_root / topic_dir.relative_to(content_root)


def write_readme(bundle_dir: Path, topic_dir: Path, repo_root: Path, sources: list[SourceEntry]) -> None:
    technology_name = technology_title(topic_dir.parent)
    name = topic_title(topic_dir)
    notebook_name = f"SWE Study Guide - {technology_name} - {name}"
    source_lines = "\n".join(f"{idx}. `sources/{entry.target_name}`" for idx, entry in enumerate(sources, start=1))
    canonical_lines = "\n".join(
        f"- `sources/{entry.target_name}` from `{relative_to_repo(entry.source, repo_root)}`: {entry.role}"
        for entry in sources
    )

    readme = f"""# NotebookLM Setup: {name}

Scope: `{relative_to_repo(topic_dir, repo_root)}`

Use this NotebookLM notebook for the study-guide topic **{name}** in
technology **{technology_name}**. This bundle deliberately excludes site
assets, screenshots, image files, and non-text metadata.

## Upload Sources

Upload these text sources to NotebookLM:

{source_lines}

Do not upload:

- `site/`
- screenshots or exported images
- any `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`, or other image file
- any `.json` or other media metadata file

## Source Roles

{canonical_lines}

## Suggested Notebook Name

{notebook_name}

## Initial Notebook Instruction

Paste this into NotebookLM as the first note or first chat instruction:

```text
Use only the uploaded study-guide sources when answering. Treat the topic
concepts as the primary source of truth, the topic notes as the narrative
companion, the technology concepts as the broader concept map, and the
research files as upstream curriculum context.

Explain topics like a strong software engineer tutoring another engineer:
concise, concrete, and grounded in the uploaded files. Favor precise
definitions, practical examples, tradeoffs, and common misunderstandings over
generic summaries.

When I ask for study help, prefer concise but complete answers, produce
active-recall questions when useful, and clearly separate source-grounded
statements from broader inferences.
```

## Useful Starting Prompts

```text
Create a study guide for this topic with the main concepts, practical rules, and common mistakes.
```

```text
Turn this topic into active recall questions with short model answers.
```

```text
Explain the most important tradeoffs, abstractions, and design decisions in this topic.
```

```text
Compare the central ideas in this topic to related concepts from the same technology.
```

## Refresh Note

NotebookLM stores static copies of uploaded sources. If the study-guide files
change, rerun the source refresh and re-upload the changed files.
"""
    (bundle_dir / "README.md").write_text(readme, encoding="utf-8")


def clean_sources_dir(sources_dir: Path) -> None:
    if not sources_dir.exists():
        sources_dir.mkdir(parents=True)
        return
    for child in sources_dir.iterdir():
        if child.is_file() or child.is_symlink():
            child.unlink()
        elif child.is_dir():
            shutil.rmtree(child)


def build_bundle(topic_dir: Path, repo_root: Path, output_root: Path, dry_run: bool) -> tuple[Path, int]:
    sources = collect_sources(topic_dir)
    if not sources:
        raise ValueError(f"No text sources found for {relative_to_repo(topic_dir, repo_root)}")

    bundle_dir = bundle_dir_for_topic(topic_dir, repo_root, output_root)
    sources_dir = bundle_dir / "sources"

    if dry_run:
        return bundle_dir, len(sources)

    bundle_dir.mkdir(parents=True, exist_ok=True)
    clean_sources_dir(sources_dir)

    for entry in sources:
        if entry.source.suffix.lower() in MEDIA_OR_METADATA_EXTENSIONS:
            raise ValueError(f"Refusing to copy non-text source: {entry.source}")
        shutil.copy2(entry.source, sources_dir / entry.target_name)

    write_readme(bundle_dir, topic_dir, repo_root, sources)
    return bundle_dir, len(sources)


def discover_all_topics(repo_root: Path) -> list[Path]:
    content_root = repo_root / "content"
    topics: list[Path] = []
    for technology_dir in sorted(p for p in content_root.iterdir() if p.is_dir()):
        for topic_dir in sorted(p for p in technology_dir.iterdir() if is_topic_dir(p)):
            topics.append(topic_dir)
    return topics


def discover_technology_topics(technology_dir: Path) -> list[Path]:
    return sorted(p for p in technology_dir.iterdir() if is_topic_dir(p))


def discover_existing_bundle_topics(repo_root: Path, output_root: Path) -> list[Path]:
    if not output_root.exists():
        return []
    topics: list[Path] = []
    for candidate in sorted(output_root.glob("*/*")):
        if not candidate.is_dir():
            continue
        topic_dir = repo_root / "content" / candidate.relative_to(output_root)
        if is_topic_dir(topic_dir):
            topics.append(topic_dir)
    return topics


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root", type=Path, default=default_repo_root(), help="Repository root. Defaults to this script's repository."
    )
    parser.add_argument(
        "--output-root", type=Path, default=None, help="NotebookLM output root. Defaults to <repo-root>/notebooklm."
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Print the bundles that would be generated without writing files."
    )

    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--topic", type=Path, help="Study-guide topic folder to package.")
    scope.add_argument("--technology", type=Path, help="Technology folder; all topic folders inside it are packaged.")
    scope.add_argument(
        "--all-existing", action="store_true", help="Refresh topic bundles that already exist under the output root."
    )
    scope.add_argument(
        "--all-topics", action="store_true", help="Create or refresh bundles for every topic with local text sources."
    )
    return parser.parse_args(argv)


def resolve_content_path(path: Path, repo_root: Path) -> Path:
    if path.is_absolute():
        return path
    return repo_root / path


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    output_root = (args.output_root or (repo_root / "notebooklm")).resolve()

    if args.topic:
        topic = resolve_content_path(args.topic, repo_root).resolve()
        if not is_topic_dir(topic):
            print(f"Not a topic folder with local text sources: {topic}", file=sys.stderr)
            return 2
        topics = [topic]
    elif args.technology:
        technology = resolve_content_path(args.technology, repo_root).resolve()
        if not technology.is_dir():
            print(f"Technology folder does not exist: {technology}", file=sys.stderr)
            return 2
        topics = discover_technology_topics(technology)
    elif args.all_existing:
        topics = discover_existing_bundle_topics(repo_root, output_root)
    else:
        topics = discover_all_topics(repo_root)

    if not topics:
        print("No topic bundles matched the requested scope.", file=sys.stderr)
        return 1

    for topic in topics:
        bundle_dir, source_count = build_bundle(topic, repo_root, output_root, args.dry_run)
        action = "Would update" if args.dry_run else "Updated"
        print(f"{action} {relative_to_repo(bundle_dir, repo_root)} ({source_count} sources)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
