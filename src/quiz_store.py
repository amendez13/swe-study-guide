"""SQLite-backed quiz history and flags (issue #72, ported from aws-sa-course #79).

Attempts are append-only and keyed by a client-generated ``attempt_id`` so the
browser outbox can replay a batch safely. Every statistic is derived from the
attempt rows; nothing is stored as a counter.
"""

from __future__ import annotations

import json
import re
import sqlite3
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .quiz_bank import QuizSnapshot, grade

SCHEMA_VERSION = 1
MAX_BATCH = 200
TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")

_SCHEMA = """
CREATE TABLE IF NOT EXISTS attempts (
  attempt_id   TEXT PRIMARY KEY,
  question_key TEXT NOT NULL,
  tech_dir  TEXT NOT NULL,
  topic_dir   TEXT NOT NULL,
  concept_slug TEXT NOT NULL,
  selected     TEXT NOT NULL,
  correct      INTEGER NOT NULL,
  session_id   TEXT NOT NULL,
  answered_at  TEXT NOT NULL,
  received_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS attempts_question ON attempts(question_key);
CREATE INDEX IF NOT EXISTS attempts_concept ON attempts(tech_dir, topic_dir, concept_slug);
CREATE TABLE IF NOT EXISTS flags (
  question_key TEXT PRIMARY KEY,
  flagged      INTEGER NOT NULL,
  updated_at   TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS schema_version (version INTEGER NOT NULL);
"""


class QuizRequestError(ValueError):
    """A request body that cannot be processed at all (HTTP 400)."""


def _now() -> str:
    return _format(datetime.now(timezone.utc))


def _format(moment: datetime) -> str:
    # Fixed-width UTC so lexicographic order equals chronological order.
    return moment.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def normalize_timestamp(value: Any) -> str | None:
    """Parse an ISO 8601 timestamp into fixed-width UTC, or return None."""

    if not isinstance(value, str) or not value.strip() or len(value) > 64:
        return None
    text = value.strip()
    if text.endswith(("Z", "z")):
        text = text[:-1] + "+00:00"
    try:
        moment = datetime.fromisoformat(text)
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=timezone.utc)
    return _format(moment)


def _batch(payload: Any, key: str) -> list[Any]:
    if not isinstance(payload, dict) or not isinstance(payload.get(key), list):
        raise QuizRequestError(f"Body must be an object with a '{key}' list")
    items: list[Any] = payload[key]
    if len(items) > MAX_BATCH:
        raise QuizRequestError(f"At most {MAX_BATCH} items per request")
    return items


def _ratio(correct: int, attempts: int) -> float | None:
    return round(correct / attempts, 4) if attempts else None


class QuizStore:
    """Thread-safe wrapper around one SQLite connection."""

    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(str(path), check_same_thread=False, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA busy_timeout=5000")
            self._conn.executescript(_SCHEMA)
            row = self._conn.execute("SELECT version FROM schema_version").fetchone()
            if row is None:
                self._conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # ── writes ──────────────────────────────────────────────────

    def record_attempts(self, payload: Any, snapshot: QuizSnapshot) -> dict[str, Any]:
        """Insert attempts idempotently; the server grades against ``snapshot``."""

        items = _batch(payload, "attempts")
        accepted: list[dict[str, Any]] = []
        rejected: list[dict[str, str]] = []
        received_at = _now()

        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                for item in items:
                    attempt_id = item.get("attemptId") if isinstance(item, dict) else None
                    if not isinstance(attempt_id, str) or not TOKEN_RE.match(attempt_id):
                        rejected.append({"attemptId": str(attempt_id or ""), "reason": "invalid attemptId"})
                        continue
                    existing = self._conn.execute(
                        "SELECT correct FROM attempts WHERE attempt_id = ?", (attempt_id,)
                    ).fetchone()
                    if existing is not None:
                        # A replay of a stored attempt: acknowledge, never duplicate.
                        accepted.append({"attemptId": attempt_id, "correct": bool(existing["correct"])})
                        continue
                    reason = self._attempt_problem(item, snapshot)
                    if reason:
                        rejected.append({"attemptId": attempt_id, "reason": reason})
                        continue
                    question = snapshot.by_key[item["questionKey"]]
                    selected = sorted(set(item["selected"]))
                    correct = grade(question, selected)
                    answered_at = normalize_timestamp(item.get("answeredAt")) or received_at
                    self._conn.execute(
                        "INSERT INTO attempts (attempt_id, question_key, tech_dir, topic_dir, concept_slug,"
                        " selected, correct, session_id, answered_at, received_at)"
                        " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            attempt_id,
                            question["key"],
                            question["techDir"],
                            question["topicDir"],
                            question["conceptSlug"],
                            json.dumps(selected),
                            int(correct),
                            item["sessionId"],
                            answered_at,
                            received_at,
                        ),
                    )
                    accepted.append({"attemptId": attempt_id, "correct": correct})
                self._conn.execute("COMMIT")
            except BaseException:
                self._conn.execute("ROLLBACK")
                raise
        return {"accepted": accepted, "rejected": rejected}

    @staticmethod
    def _attempt_problem(item: dict[str, Any], snapshot: QuizSnapshot) -> str:
        key = item.get("questionKey")
        question = snapshot.by_key.get(key) if isinstance(key, str) else None
        if question is None:
            return "unknown question"
        session_id = item.get("sessionId")
        if not isinstance(session_id, str) or not TOKEN_RE.match(session_id):
            return "invalid sessionId"
        selected = item.get("selected")
        if not isinstance(selected, list) or not selected or not all(isinstance(choice, str) for choice in selected):
            return "invalid selection"
        choice_ids = {choice["id"] for choice in question["choices"]}
        if any(choice not in choice_ids for choice in selected):
            return "invalid selection"
        return ""

    def set_flags(self, payload: Any, snapshot: QuizSnapshot) -> dict[str, Any]:
        """Upsert flags; the newest client ``updatedAt`` wins."""

        items = _batch(payload, "flags")
        results: list[dict[str, Any]] = []
        rejected: list[dict[str, str]] = []
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                for item in items:
                    key = item.get("questionKey") if isinstance(item, dict) else None
                    if not isinstance(key, str) or key not in snapshot.by_key:
                        rejected.append({"questionKey": str(key or ""), "reason": "unknown question"})
                        continue
                    updated_at = normalize_timestamp(item.get("updatedAt"))
                    if updated_at is None or not isinstance(item.get("flagged"), bool):
                        rejected.append({"questionKey": key, "reason": "invalid flag"})
                        continue
                    self._conn.execute(
                        "INSERT INTO flags (question_key, flagged, updated_at) VALUES (?, ?, ?)"
                        " ON CONFLICT(question_key) DO UPDATE SET flagged = excluded.flagged, updated_at = excluded.updated_at"
                        " WHERE excluded.updated_at >= flags.updated_at",
                        (key, int(item["flagged"]), updated_at),
                    )
                    row = self._conn.execute("SELECT flagged, updated_at FROM flags WHERE question_key = ?", (key,)).fetchone()
                    results.append({"questionKey": key, "flagged": bool(row["flagged"]), "updatedAt": row["updated_at"]})
                self._conn.execute("COMMIT")
            except BaseException:
                self._conn.execute("ROLLBACK")
                raise
        return {"flags": results, "rejected": rejected}

    # ── reads ───────────────────────────────────────────────────

    def progress(self, snapshot: QuizSnapshot) -> dict[str, Any]:
        """Per-question stats plus concept and technology roll-ups for current questions."""

        with self._lock:
            attempt_rows = self._conn.execute(
                "SELECT question_key, correct, answered_at FROM attempts ORDER BY answered_at, received_at, rowid"
            ).fetchall()
            flag_rows = self._conn.execute("SELECT question_key, flagged, updated_at FROM flags").fetchall()

        per_question, flags = _question_stats(attempt_rows, flag_rows, snapshot)
        return {"questions": per_question, "flags": flags, **_rollups(snapshot, per_question)}


def _empty_stats() -> dict[str, Any]:
    return {"attempts": 0, "correct": 0, "wrong": 0, "lastCorrect": None, "lastAnsweredAt": None, "flagged": False}


def _question_stats(
    attempt_rows: list[sqlite3.Row], flag_rows: list[sqlite3.Row], snapshot: QuizSnapshot
) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """Fold chronologically ordered attempt rows and flag rows into per-question stats."""

    per_question: dict[str, dict[str, Any]] = {}
    for row in attempt_rows:
        key = row["question_key"]
        if key not in snapshot.by_key:
            continue  # history kept, but removed questions leave the roll-ups
        stats = per_question.setdefault(key, _empty_stats())
        stats["attempts"] += 1
        if row["correct"]:
            stats["correct"] += 1
        else:
            stats["wrong"] += 1
        stats["lastCorrect"] = bool(row["correct"])
        stats["lastAnsweredAt"] = row["answered_at"]

    flags: dict[str, dict[str, Any]] = {}
    for row in flag_rows:
        key = row["question_key"]
        if key not in snapshot.by_key:
            continue
        flags[key] = {"flagged": bool(row["flagged"]), "updatedAt": row["updated_at"]}
        if row["flagged"]:
            per_question.setdefault(key, _empty_stats())["flagged"] = True
    return per_question, flags


def _rollups(snapshot: QuizSnapshot, per_question: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Concept, technology, quiz-set and total roll-ups over the questions that still exist."""

    concepts: dict[tuple[str, str, str], dict[str, Any]] = {}
    technologies: dict[str, dict[str, Any]] = {}
    quizzes: dict[str, dict[str, Any]] = {}
    totals: dict[str, Any] = {
        "questions": 0,
        "attempted": 0,
        "attempts": 0,
        "correct": 0,
        "wrong": 0,
        "flagged": 0,
        "lastCorrect": 0,
    }

    for question in snapshot.questions:
        key = question["key"]
        stats = per_question.get(key)
        concept = concepts.setdefault(
            (question["techDir"], question["topicDir"], question["conceptSlug"]),
            {
                "techDir": question["techDir"],
                "techTitle": question["techTitle"],
                "topicDir": question["topicDir"],
                "topicTitle": question["topicTitle"],
                "conceptSlug": question["conceptSlug"],
                "conceptTitle": question["conceptTitle"],
                "conceptRoute": question["conceptRoute"],
                **{name: 0 for name in totals},
            },
        )
        tech = technologies.setdefault(
            question["techDir"],
            {
                "techDir": question["techDir"],
                "techNum": question["techNum"],
                "techTitle": question["techTitle"],
                **{name: 0 for name in totals},
            },
        )
        quiz = quizzes.setdefault(
            question["quizKey"],
            {
                "quizKey": question["quizKey"],
                "quizId": question["quizId"],
                "quizTitle": question["quizTitle"],
                "techDir": question["techDir"],
                "techTitle": question["techTitle"],
                **{name: 0 for name in totals},
            },
        )
        for bucket in (concept, tech, quiz, totals):
            bucket["questions"] += 1
            if stats is None:
                continue
            bucket["attempts"] += stats["attempts"]
            bucket["correct"] += stats["correct"]
            bucket["wrong"] += stats["wrong"]
            bucket["attempted"] += 1 if stats["attempts"] else 0
            bucket["flagged"] += 1 if stats["flagged"] else 0
            bucket["lastCorrect"] += 1 if stats["lastCorrect"] else 0

    for bucket in (*concepts.values(), *technologies.values(), *quizzes.values(), totals):
        bucket["accuracy"] = _ratio(bucket["correct"], bucket["attempts"])

    return {
        "concepts": list(concepts.values()),
        "technologies": list(technologies.values()),
        "quizzes": list(quizzes.values()),
        "totals": totals,
    }
