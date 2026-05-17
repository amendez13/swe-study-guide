#!/usr/bin/env python3
"""Local SWE study guide server.

Scans the content/ directory, builds a JSON index of technologies and topics,
then serves the site/ frontend and content/ assets.

Usage:
    python serve.py [--port 8080]
"""

import argparse
import json
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote

from src.release_info import get_release_info

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
SITE_DIR = ROOT / "site"


def natural_sort_key(s: str):
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", s)]


def build_content_index() -> dict:
    technologies = []
    tech_dirs = sorted(
        [d for d in CONTENT_DIR.iterdir() if d.is_dir()],
        key=lambda d: natural_sort_key(d.name),
    )
    for tech_dir in tech_dirs:
        match = re.match(r"^(\d+)_(.+)$", tech_dir.name)
        if not match:
            continue
        tech_num = int(match.group(1))
        tech_title = match.group(2).replace("_", " ")

        has_technology_concepts = (tech_dir / "technology_concepts.md").exists()

        topics = []
        topic_dirs = sorted(
            [d for d in tech_dir.iterdir() if d.is_dir()],
            key=lambda d: natural_sort_key(d.name),
        )
        for topic_dir in topic_dirs:
            topic_match = re.match(r"^(\d+)_(.+)$", topic_dir.name)
            if not topic_match:
                continue
            topic_num = int(topic_match.group(1))
            topic_title = topic_match.group(2).replace("_", " ")

            notes_file = None
            if (topic_dir / "notes.md").exists():
                notes_file = "notes.md"
            else:
                md_files = [
                    f.name for f in topic_dir.iterdir() if f.is_file() and f.suffix == ".md" and f.name not in ("concepts.md",)
                ]
                notes_file = md_files[0] if md_files else None

            has_concepts = (topic_dir / "concepts.md").exists()

            topics.append(
                {
                    "num": topic_num,
                    "dir": topic_dir.name,
                    "title": topic_title,
                    "notesFile": notes_file,
                    "hasConcepts": has_concepts,
                }
            )

        technologies.append(
            {
                "num": tech_num,
                "dir": tech_dir.name,
                "title": tech_title,
                "hasTechnologyConcepts": has_technology_concepts,
                "topics": topics,
            }
        )

    return {"technologies": technologies}


def resolve_under(root: Path, relative_path: str) -> Path | None:
    """Resolve a path only when it stays within the expected root."""
    root_resolved = root.resolve()
    candidate = (root_resolved / relative_path.lstrip("/")).resolve()
    try:
        candidate.relative_to(root_resolved)
    except ValueError:
        return None
    return candidate


def build_health_payload() -> dict[str, Any]:
    """Return a cheap liveness payload with release metadata."""
    return {
        "status": "ok",
        "release": get_release_info(),
    }


class StudyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, content_index=None, **kwargs):
        self.content_index = content_index
        super().__init__(*args, **kwargs)

    def do_GET(self):
        path = unquote(self.path)

        if path == "/api/content":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(self.content_index).encode())
            return

        if path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(build_health_payload()).encode())
            return

        if path.startswith("/content/"):
            rel = path[len("/content/") :]
            file_path = resolve_under(CONTENT_DIR, rel)
            if file_path and file_path.is_file():
                self.send_response(200)
                ct = self._guess_type(file_path)
                self.send_header("Content-Type", ct)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(file_path.read_bytes())
            else:
                self.send_error(404, f"Not found: {rel}")
            return

        if path == "/":
            path = "/index.html"

        file_path = resolve_under(SITE_DIR, path)
        if file_path and file_path.is_file():
            self.send_response(200)
            ct = self._guess_type(file_path)
            self.send_header("Content-Type", ct)
            self.end_headers()
            self.wfile.write(file_path.read_bytes())
        else:
            self.send_error(404, f"Not found: {path}")

    def _guess_type(self, path: Path) -> str:
        ext = path.suffix.lower()
        return {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json",
            ".md": "text/plain; charset=utf-8",
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".gif": "image/gif",
            ".svg": "image/svg+xml",
        }.get(ext, "application/octet-stream")

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description="SWE Study Guide Server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    print("Scanning content directory...")
    index = build_content_index()
    total_topics = sum(len(t["topics"]) for t in index["technologies"])
    print(f"Found {len(index['technologies'])} technologies, {total_topics} topics")

    def handler_factory(*args, **kwargs):
        return StudyHandler(*args, content_index=index, **kwargs)

    server = ThreadingHTTPServer((args.host, args.port), handler_factory)
    server.daemon_threads = True
    print("\n  SWE Study Guide")
    print(f"  http://{args.host}:{args.port}\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
