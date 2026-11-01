"""Load and validate per-technology quiz files (issue #72).

A technology may carry any number of quiz sets under
``content/<TECH>/quizzes/<quiz-id>.yaml`` (plus an optional legacy
``content/<TECH>/quiz.yaml`` whose quiz id is ``quiz``). Every question links
to one concept card: a ``## <Title>`` heading in ``<TOPIC>/concepts.md``.

The bank never raises for bad content: invalid questions are excluded and
reported under ``issues`` so the site keeps working, while the test suite
rejects any committed issue.

Ported from the aws-sa-course quiz (aws-sa-course #79).
"""

from __future__ import annotations

import hashlib
import re
import threading
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

import yaml

QUIZ_DIR = "quizzes"
LEGACY_QUIZ_FILE = "quiz.yaml"
QUIZ_FORMAT_VERSION = 1
QUESTION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
QUIZ_ID_RE = re.compile(r"^[a-z0-9][a-z0-9_-]{0,79}$")
CHOICE_ID_RE = re.compile(r"^[a-z0-9]{1,8}$")
_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_BULLET_RE = re.compile(r"^\s*-\s+(.+?)\s*$", re.MULTILINE)


def slugify(value: str) -> str:
    """Normalize a concept title into a stable lowercase slug.

    Must stay in sync with ``slugify`` in ``site/app.js``.
    """

    decomposed = unicodedata.normalize("NFD", value)
    without_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    hyphenated = re.sub(r"[^a-z0-9]+", "-", without_accents.lower())
    return hyphenated.strip("-")


@dataclass(frozen=True)
class QuizSnapshot:
    """An immutable, validated view of every quiz file at one point in time."""

    questions: list[dict[str, Any]]
    quizzes: list[dict[str, Any]]
    issues: list[dict[str, str]]
    etag: str
    by_key: dict[str, dict[str, Any]] = field(default_factory=dict)

    def payload(self) -> dict[str, Any]:
        return {
            "version": QUIZ_FORMAT_VERSION,
            "quizzes": self.quizzes,
            "questions": self.questions,
            "issues": self.issues,
        }


def concept_titles(markdown: str) -> list[str]:
    """Return concept titles exactly as ``parseConcepts`` in ``site/app.js`` does."""

    headings = _HEADING_RE.findall(markdown)
    if headings:
        return [title.strip() for title in headings if title.strip()]
    return [title.strip() for title in _BULLET_RE.findall(markdown) if title.strip()]


def _is_text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def quiz_files(tech_path: Path) -> list[tuple[str, Path]]:
    """Return ``(quiz_id, path)`` for every quiz file of one technology, sorted."""

    found: list[tuple[str, Path]] = []
    legacy = tech_path / LEGACY_QUIZ_FILE
    if legacy.is_file():
        found.append(("quiz", legacy))
    quiz_dir = tech_path / QUIZ_DIR
    if quiz_dir.is_dir():
        for path in sorted(quiz_dir.iterdir()):
            if path.is_file() and path.suffix in (".yaml", ".yml"):
                found.append((path.stem, path))
    return found


class QuizBank:
    """Builds :class:`QuizSnapshot` objects, rebuilding only when inputs change."""

    def __init__(self, content_dir: Path, content_index: dict[str, Any] | Callable[[], dict[str, Any]]) -> None:
        self.content_dir = content_dir
        self._content_index = content_index
        self._lock = threading.Lock()
        self._fingerprint: str | None = None
        self._snapshot: QuizSnapshot | None = None

    def _index(self) -> dict[str, Any]:
        return self._content_index() if callable(self._content_index) else self._content_index

    def _input_files(self) -> list[Path]:
        patterns = (
            f"*/{LEGACY_QUIZ_FILE}",
            f"*/{QUIZ_DIR}/*.yaml",
            f"*/{QUIZ_DIR}/*.yml",
            "*/*/concepts.md",
        )
        files: list[Path] = []
        for pattern in patterns:
            files.extend(self.content_dir.glob(pattern))
        return sorted(files)

    def _compute_fingerprint(self) -> str:
        digest = hashlib.sha256()
        for path in self._input_files():
            try:
                stat = path.stat()
            except OSError:
                continue
            digest.update(f"{path.relative_to(self.content_dir)}:{stat.st_mtime_ns}:{stat.st_size}\n".encode())
        for tech in self._index().get("technologies", []):
            digest.update(f"{tech.get('dir')}|{tech.get('title')}\n".encode())
            for topic in tech.get("topics", []):
                digest.update(f"  {topic.get('dir')}|{topic.get('title')}\n".encode())
        return digest.hexdigest()[:32]

    def snapshot(self) -> QuizSnapshot:
        fingerprint = self._compute_fingerprint()
        with self._lock:
            if self._snapshot is None or fingerprint != self._fingerprint:
                self._snapshot = self._build(fingerprint)
                self._fingerprint = fingerprint
            return self._snapshot

    # ── building ────────────────────────────────────────────────

    def _build(self, etag: str) -> QuizSnapshot:
        questions: list[dict[str, Any]] = []
        quizzes: list[dict[str, Any]] = []
        issues: list[dict[str, str]] = []
        concept_cache: dict[Path, dict[str, str]] = {}

        for tech in self._index().get("technologies", []):
            if isinstance(tech.get("dir"), str):
                self._build_technology(tech, questions, quizzes, issues, concept_cache)

        counts: dict[str, int] = {}
        for question in questions:
            counts[question["quizKey"]] = counts.get(question["quizKey"], 0) + 1
        for quiz in quizzes:
            quiz["questions"] = counts.get(str(quiz["key"]), 0)

        by_key = {question["key"]: question for question in questions}
        return QuizSnapshot(questions=questions, quizzes=quizzes, issues=issues, etag=etag, by_key=by_key)

    def _build_technology(
        self,
        tech: dict[str, Any],
        questions: list[dict[str, Any]],
        quizzes: list[dict[str, Any]],
        issues: list[dict[str, str]],
        concept_cache: dict[Path, dict[str, str]],
    ) -> None:
        """Load every quiz set of one technology, appending to the shared lists."""

        tech_dir = tech["dir"]
        tech_questions: list[dict[str, Any]] = []
        for quiz_id, path in quiz_files(self.content_dir / tech_dir):
            quiz = self._build_quiz_set(tech, quiz_id, path, tech_questions, issues, concept_cache)
            if quiz is not None:
                quizzes.append(quiz)

        # Question keys are <techDir>/<id>, so ids must be unique across all
        # of a technology's quiz files. Serve neither copy of a duplicate.
        id_files: dict[str, list[str]] = {}
        for question in tech_questions:
            id_files.setdefault(question["id"], []).append(question["file"])
        duplicates = {qid: files for qid, files in id_files.items() if len(files) > 1}
        for qid, files in duplicates.items():
            for rel_file in files:
                others = ", ".join(sorted(f for f in set(files) if f != rel_file)) or rel_file
                issues.append(
                    {
                        "file": rel_file,
                        "question": qid,
                        "message": f"Duplicate question id '{qid}' in technology {tech_dir} (also in {others})",
                    }
                )
        for question in tech_questions:
            question.pop("file")
            if question["id"] not in duplicates:
                questions.append(question)

    def _build_quiz_set(
        self,
        tech: dict[str, Any],
        quiz_id: str,
        path: Path,
        tech_questions: list[dict[str, Any]],
        issues: list[dict[str, str]],
        concept_cache: dict[Path, dict[str, str]],
    ) -> dict[str, Any] | None:
        """Validate one quiz file; return its quiz-set entry, or None if unusable."""

        rel_file = path.relative_to(self.content_dir).as_posix()
        if not QUIZ_ID_RE.match(quiz_id):
            issues.append({"file": rel_file, "question": "", "message": "Quiz file name must match [a-z0-9][a-z0-9_-]*"})
            return None
        try:
            meta, raw_questions = self._load_file(path)
        except ValueError as exc:
            issues.append({"file": rel_file, "question": "", "message": str(exc)})
            return None

        quiz: dict[str, Any] = {
            "key": f"{tech['dir']}/{quiz_id}",
            "id": quiz_id,
            "techDir": tech["dir"],
            "title": meta["title"],
            "description": meta["description"],
            "file": rel_file,
            "questions": 0,
        }
        seen_ids: set[str] = set()
        for position, raw in enumerate(raw_questions, start=1):
            label = raw.get("id") if isinstance(raw, dict) and isinstance(raw.get("id"), str) else f"#{position}"
            try:
                question = self._validate_question(tech, quiz, raw, seen_ids, concept_cache)
            except ValueError as exc:
                issues.append({"file": rel_file, "question": str(label), "message": str(exc)})
                continue
            # Temporary marker for duplicate detection; removed before serving.
            question["file"] = rel_file
            tech_questions.append(question)
        return quiz

    @staticmethod
    def _load_file(path: Path) -> tuple[dict[str, str], list[Any]]:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, yaml.YAMLError) as exc:
            raise ValueError(f"Cannot parse file: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("questions"), list):
            raise ValueError("File must be a mapping with a 'questions' list")
        if data.get("version", QUIZ_FORMAT_VERSION) != QUIZ_FORMAT_VERSION:
            raise ValueError(f"Unsupported version {data.get('version')!r}")
        title = data.get("title")
        description = data.get("description", "")
        if title is not None and not _is_text(title):
            raise ValueError("'title' must be text")
        if description is not None and not isinstance(description, str):
            raise ValueError("'description' must be text")
        stem = path.stem.replace("-", " ").replace("_", " ").strip()
        meta = {
            "title": str(title).strip() if title else (stem[:1].upper() + stem[1:]),
            "description": (description or "").strip(),
        }
        questions: list[Any] = data["questions"]
        return meta, questions

    def _concepts_for(self, topic_path: Path, cache: dict[Path, dict[str, str]]) -> dict[str, str]:
        if topic_path not in cache:
            try:
                titles = concept_titles((topic_path / "concepts.md").read_text(encoding="utf-8"))
            except (OSError, UnicodeDecodeError):
                titles = []
            slugs: dict[str, str] = {}
            for title in titles:
                slugs.setdefault(slugify(title), title)
            cache[topic_path] = slugs
        return cache[topic_path]

    def _validate_question(
        self,
        tech: dict[str, Any],
        quiz: dict[str, Any],
        raw: Any,
        seen_ids: set[str],
        concept_cache: dict[Path, dict[str, str]],
    ) -> dict[str, Any]:
        if not isinstance(raw, dict):
            raise ValueError("Question must be a mapping")

        qid = raw.get("id")
        if not isinstance(qid, str) or not QUESTION_ID_RE.match(qid):
            raise ValueError("'id' must match [a-z0-9][a-z0-9-]* (max 80 chars)")
        if qid in seen_ids:
            raise ValueError(f"Duplicate question id '{qid}' in quiz file")
        seen_ids.add(qid)

        topic, concept_slug, concept_title = self._resolve_concept(tech, raw, concept_cache)
        prompt = raw.get("prompt")
        if not _is_text(prompt):
            raise ValueError("'prompt' is required")
        choices = _validate_choices(raw.get("choices"))
        answer = _validate_answer(raw.get("answer"), choices)
        explanation = raw.get("explanation", "")
        if explanation is None:
            explanation = ""
        if not isinstance(explanation, str):
            raise ValueError("'explanation' must be text")

        tech_dir = tech["dir"]
        return {
            "key": f"{tech_dir}/{qid}",
            "id": qid,
            "quizKey": quiz["key"],
            "quizId": quiz["id"],
            "quizTitle": quiz["title"],
            "techDir": tech_dir,
            "techNum": tech.get("num"),
            "techTitle": tech.get("title", tech_dir),
            "topicDir": topic["dir"],
            "topicNum": topic.get("num"),
            "topicTitle": topic.get("title", topic["dir"]),
            "conceptTitle": concept_title,
            "conceptSlug": concept_slug,
            "conceptRoute": f"{tech_dir}/{topic['dir']}/concepts/{concept_slug}",
            "prompt": str(prompt).strip(),
            "choices": choices,
            "answer": answer,
            "multiple": len(answer) > 1,
            "explanation": explanation.strip(),
            "placeholder": bool(raw.get("placeholder", False)),
        }

    def _resolve_concept(
        self, tech: dict[str, Any], raw: dict[str, Any], concept_cache: dict[Path, dict[str, str]]
    ) -> tuple[dict[str, Any], str, str]:
        topic_dir = raw.get("topic")
        topic = next(
            (entry for entry in tech.get("topics", []) if isinstance(topic_dir, str) and entry.get("dir") == topic_dir),
            None,
        )
        if topic is None:
            raise ValueError(f"Unknown topic {topic_dir!r} in technology {tech['dir']}")

        concepts = self._concepts_for(self.content_dir / tech["dir"] / topic["dir"], concept_cache)
        concept = raw.get("concept")
        if not _is_text(concept):
            raise ValueError("'concept' is required")
        concept_slug = slugify(str(concept))
        if concept_slug not in concepts:
            raise ValueError(f"Concept {concept!r} is not a '## ' heading in {tech['dir']}/{topic['dir']}/concepts.md")
        return topic, concept_slug, concepts[concept_slug]


def _validate_choices(raw_choices: Any) -> list[dict[str, str]]:
    if not isinstance(raw_choices, list) or len(raw_choices) < 2:
        raise ValueError("'choices' must list at least 2 options")
    choices: list[dict[str, str]] = []
    for choice in raw_choices:
        if not isinstance(choice, dict):
            raise ValueError("Each choice must be a mapping with 'id' and 'text'")
        cid, text = choice.get("id"), choice.get("text")
        if not isinstance(cid, str) or not CHOICE_ID_RE.match(cid):
            raise ValueError("Choice 'id' must be 1-8 lowercase letters or digits")
        if not _is_text(text):
            raise ValueError(f"Choice {cid!r} needs 'text'")
        if any(existing["id"] == cid for existing in choices):
            raise ValueError(f"Duplicate choice id {cid!r}")
        choices.append({"id": cid, "text": str(text).strip()})
    return choices


def _validate_answer(answer: Any, choices: list[dict[str, str]]) -> list[str]:
    if isinstance(answer, str):
        answer = [answer]
    if (
        not isinstance(answer, list)
        or not answer
        or not all(isinstance(item, str) for item in answer)
        or len(set(answer)) != len(answer)
    ):
        raise ValueError("'answer' must be a non-empty list of distinct choice ids")
    order = [choice["id"] for choice in choices]
    unknown = [item for item in answer if item not in order]
    if unknown:
        raise ValueError(f"'answer' references unknown choice ids {unknown}")
    return sorted(answer, key=order.index)


def grade(question: dict[str, Any], selected: list[str]) -> bool:
    """Exact-set grading; multi-answer questions have no partial credit."""

    return set(selected) == set(question["answer"])
