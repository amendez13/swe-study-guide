#!/usr/bin/env python3
"""Local SWE study guide server.

Scans the content/ directory, builds a JSON index of technologies and topics,
then serves the site/ frontend and content/ assets.

Usage:
    python serve.py [--port 8080]
"""

import argparse
import json
import os
import re
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

from src.quiz_bank import QuizBank, quiz_files
from src.quiz_store import QuizRequestError, QuizStore
from src.release_info import get_release_info

ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content"
SITE_DIR = ROOT / "site"
# These files have their own tabs and must not be picked up as the notes document.
NOTES_FILE_EXCLUSIONS = frozenset({"concepts.md", "drills.md"})
# Quiz history lives in SQLite; the container points this at /data (issue #72).
QUIZ_DB_ENV = "SWE_STUDY_GUIDE_QUIZ_DB"
DEFAULT_QUIZ_DB = ROOT / ".local" / "quiz.sqlite3"
MAX_QUIZ_BODY_BYTES = 256 * 1024


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
                    f.name
                    for f in topic_dir.iterdir()
                    if f.is_file() and f.suffix == ".md" and f.name not in NOTES_FILE_EXCLUSIONS
                ]
                notes_file = md_files[0] if md_files else None

            has_concepts = (topic_dir / "concepts.md").exists()
            has_drills = (topic_dir / "drills.md").exists()

            topics.append(
                {
                    "num": topic_num,
                    "dir": topic_dir.name,
                    "title": topic_title,
                    "notesFile": notes_file,
                    "hasConcepts": has_concepts,
                    "hasDrills": has_drills,
                }
            )

        technologies.append(
            {
                "num": tech_num,
                "dir": tech_dir.name,
                "title": tech_title,
                "hasTechnologyConcepts": has_technology_concepts,
                "quizCount": len(quiz_files(tech_dir)),
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


def quiz_db_path() -> Path:
    """Return the SQLite path for quiz history (env override, else .local/)."""
    configured = os.environ.get(QUIZ_DB_ENV, "").strip()
    return Path(configured) if configured else DEFAULT_QUIZ_DB


class StudyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, content_index=None, quiz_bank=None, quiz_store=None, **kwargs):
        self.content_index = content_index
        self.quiz_bank = quiz_bank
        self.quiz_store = quiz_store
        super().__init__(*args, **kwargs)

    def do_GET(self):
        self._handle_request(include_body=True)

    def do_HEAD(self):
        self._handle_request(include_body=False)

    def do_POST(self):
        path = unquote(urlsplit(self.path).path)
        if path == "/api/quiz/attempts":
            self._handle_quiz_write("attempts")
            return
        self.send_error(404, "Not found")

    def do_PUT(self):
        path = unquote(urlsplit(self.path).path)
        if path == "/api/quiz/flags":
            self._handle_quiz_write("flags")
            return
        self.send_error(404, "Not found")

    # ── quiz (issue #72) ─────────────────────────────────────

    def _send_json(self, payload: Any, status: int = 200, include_body: bool = True) -> None:
        body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def _read_json_body(self, max_bytes: int) -> dict:
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        if length > max_bytes:
            # Drain a moderately oversized body so the client reliably reads
            # the 400 instead of seeing a connection reset mid-upload.
            if length <= max_bytes * 4:
                self.rfile.read(length)
            raise ValueError("Request body too large")
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("Invalid JSON body") from exc
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def _handle_quiz_get(self, path: str, include_body: bool) -> None:
        if self.quiz_bank is None or self.quiz_store is None:
            self._send_json({"error": "Quiz is not configured"}, status=503, include_body=include_body)
            return
        snapshot = self.quiz_bank.snapshot()
        if path == "/api/quiz/progress":
            self._send_json(self.quiz_store.progress(snapshot), include_body=include_body)
            return
        quoted_etag = f'"{snapshot.etag}"'
        if self.headers.get("If-None-Match") == quoted_etag:
            self.send_response(304)
            self.send_header("ETag", quoted_etag)
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            return
        body = json.dumps(snapshot.payload(), ensure_ascii=False, separators=(",", ":")).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("ETag", quoted_etag)
        self.end_headers()
        if include_body:
            self.wfile.write(body)

    def _handle_quiz_write(self, kind: str) -> None:
        if self.quiz_bank is None or self.quiz_store is None:
            self._send_json({"error": "Quiz is not configured"}, status=503)
            return
        try:
            payload = self._read_json_body(max_bytes=MAX_QUIZ_BODY_BYTES)
            snapshot = self.quiz_bank.snapshot()
            if kind == "attempts":
                result = self.quiz_store.record_attempts(payload, snapshot)
            else:
                result = self.quiz_store.set_flags(payload, snapshot)
        except (ValueError, QuizRequestError) as exc:
            self._send_json({"error": str(exc)}, status=400)
            return
        self._send_json(result)

    def _handle_request(self, include_body: bool):
        path = unquote(urlsplit(self.path).path)

        if path in ("/api/quiz/questions", "/api/quiz/progress"):
            self._handle_quiz_get(path, include_body)
            return

        if path == "/api/content":
            payload = json.dumps(self.content_index).encode()
            self._send_ok(
                content_type="application/json",
                include_body=include_body,
                body=payload,
                allow_cors=True,
                cache_control="no-store",
            )
            return

        if path == "/health":
            payload = json.dumps(build_health_payload()).encode()
            self._send_ok(
                content_type="application/json",
                include_body=include_body,
                body=payload,
                cache_control="no-store",
            )
            return

        if path.startswith("/content/"):
            rel = path[len("/content/") :]
            file_path = resolve_under(CONTENT_DIR, rel)
            if file_path and file_path.is_file():
                self._send_ok(
                    content_type=self._guess_type(file_path),
                    include_body=include_body,
                    body=file_path.read_bytes(),
                    allow_cors=True,
                    cache_control="no-store",
                )
            else:
                self.send_error(404, f"Not found: {rel}")
            return

        if path == "/":
            path = "/index.html"

        file_path = resolve_under(SITE_DIR, path)
        if file_path and file_path.is_file():
            self._send_ok(
                content_type=self._guess_type(file_path),
                include_body=include_body,
                body=file_path.read_bytes(),
                cache_control="no-store",
            )
        else:
            self.send_error(404, f"Not found: {path}")

    def _send_ok(
        self,
        *,
        content_type: str,
        include_body: bool,
        body: bytes,
        allow_cors: bool = False,
        cache_control: str | None = None,
    ) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        if allow_cors:
            self.send_header("Access-Control-Allow-Origin", "*")
        if cache_control:
            self.send_header("Cache-Control", cache_control)
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        self.end_headers()
        if include_body:
            self.wfile.write(body)

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

    quiz_bank = QuizBank(CONTENT_DIR, index)
    quiz_store = QuizStore(quiz_db_path())
    snapshot = quiz_bank.snapshot()
    print(f"Quiz: {len(snapshot.questions)} questions in {len(snapshot.quizzes)} quiz sets, {len(snapshot.issues)} issues")
    print(f"Quiz history: {quiz_store.path}")

    def handler_factory(*args, **kwargs):
        return StudyHandler(*args, content_index=index, quiz_bank=quiz_bank, quiz_store=quiz_store, **kwargs)

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
