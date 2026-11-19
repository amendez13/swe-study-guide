"""Tests for quiz history storage and the quiz HTTP endpoints (issue #72, ported from aws-sa-course #79)."""

from __future__ import annotations

import json
import sqlite3
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any, Iterator
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

import serve
from src.quiz_bank import QuizSnapshot
from src.quiz_store import MAX_BATCH, QuizRequestError, QuizStore, normalize_timestamp


def _question(key: str, chapter: str, lesson: str, concept: str, answer: list[str], quiz: str = "set-a") -> dict[str, Any]:
    return {
        "key": key,
        "id": key.split("/")[1],
        "quizKey": f"{chapter}/{quiz}",
        "quizId": quiz,
        "quizTitle": quiz.upper(),
        "techDir": chapter,
        "techNum": int(chapter[:2]),
        "techTitle": chapter,
        "topicDir": lesson,
        "topicTitle": lesson,
        "conceptSlug": concept,
        "conceptTitle": concept.title(),
        "conceptRoute": f"{chapter}/{lesson}/concepts/{concept}",
        "choices": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}, {"id": "c", "text": "C"}],
        "answer": answer,
    }


def _snapshot(*questions: dict[str, Any]) -> QuizSnapshot:
    items = list(questions) or [
        _question("01_CH/q1", "01_CH", "01_L", "policy", ["a"]),
        _question("01_CH/q2", "01_CH", "01_L", "policy", ["a", "b"]),
        _question("01_CH/q3", "01_CH", "02_L", "deny", ["c"], quiz="set-b"),
        _question("02_CH/q1", "02_CH", "01_L", "vpc", ["b"]),
    ]
    return QuizSnapshot(questions=items, quizzes=[], issues=[], etag="e", by_key={q["key"]: q for q in items})


def _attempt(n: int, key: str = "01_CH/q1", selected: list[str] | None = None, **extra: Any) -> dict[str, Any]:
    item = {
        "attemptId": f"attempt-{n:04d}",
        "questionKey": key,
        "selected": selected if selected is not None else ["a"],
        "sessionId": "session-0001",
        "answeredAt": f"2026-09-28T10:{n:02d}:00Z",
    }
    item.update(extra)
    return item


@pytest.fixture
def store(tmp_path: Path) -> Iterator[QuizStore]:
    quiz_store = QuizStore(tmp_path / "nested" / "quiz.sqlite3")
    yield quiz_store
    quiz_store.close()


def test_schema_is_created_once(tmp_path: Path) -> None:
    path = tmp_path / "quiz.sqlite3"
    QuizStore(path).close()
    QuizStore(path).close()
    with sqlite3.connect(path) as conn:
        assert conn.execute("SELECT version FROM schema_version").fetchall() == [(1,)]


def test_attempts_are_graded_by_the_server_and_replays_are_idempotent(store: QuizStore) -> None:
    snapshot = _snapshot()
    batch = {"attempts": [_attempt(1, selected=["a"]), _attempt(2, key="01_CH/q2", selected=["a"])]}

    first = store.record_attempts(batch, snapshot)
    replay = store.record_attempts(batch, snapshot)

    assert first == {
        "accepted": [{"attemptId": "attempt-0001", "correct": True}, {"attemptId": "attempt-0002", "correct": False}],
        "rejected": [],
    }
    assert replay == first
    assert store.progress(snapshot)["totals"]["attempts"] == 2


def test_client_correctness_claims_are_ignored(store: QuizStore) -> None:
    result = store.record_attempts({"attempts": [_attempt(1, selected=["b"], correct=True)]}, _snapshot())
    assert result["accepted"] == [{"attemptId": "attempt-0001", "correct": False}]


@pytest.mark.parametrize(
    ("item", "reason"),
    [
        ({"attemptId": "short"}, "invalid attemptId"),
        ("not-an-object", "invalid attemptId"),
        (_attempt(1, key="01_CH/gone"), "unknown question"),
        (_attempt(1, key=5), "unknown question"),
        (_attempt(1, sessionId="bad id!"), "invalid sessionId"),
        (_attempt(1, selected=[]), "invalid selection"),
        (_attempt(1, selected=[1]), "invalid selection"),
        (_attempt(1, selected=["z"]), "invalid selection"),
    ],
)
def test_bad_attempts_are_rejected_individually(store: QuizStore, item: Any, reason: str) -> None:
    result = store.record_attempts({"attempts": [item, _attempt(9)]}, _snapshot())

    assert result["rejected"][0]["reason"] == reason
    assert result["accepted"] == [{"attemptId": "attempt-0009", "correct": True}]


def test_replay_of_a_stored_attempt_is_accepted_after_its_question_is_removed(store: QuizStore) -> None:
    store.record_attempts({"attempts": [_attempt(1, key="02_CH/q1", selected=["b"])]}, _snapshot())
    remaining = _snapshot(_question("01_CH/q1", "01_CH", "01_L", "policy", ["a"]))

    result = store.record_attempts({"attempts": [_attempt(1, key="02_CH/q1", selected=["b"])]}, remaining)

    assert result == {"accepted": [{"attemptId": "attempt-0001", "correct": True}], "rejected": []}
    progress = store.progress(remaining)
    assert progress["questions"] == {}
    assert progress["totals"]["attempts"] == 0


@pytest.mark.parametrize("payload", [{}, {"attempts": "x"}, [], {"attempts": [_attempt(1)] * (MAX_BATCH + 1)}])
def test_malformed_batches_raise(store: QuizStore, payload: Any) -> None:
    with pytest.raises(QuizRequestError):
        store.record_attempts(payload, _snapshot())


def test_write_failures_roll_back_the_whole_batch(store: QuizStore, monkeypatch: pytest.MonkeyPatch) -> None:
    def explode(question: Any, selected: Any) -> bool:
        raise RuntimeError("boom")

    monkeypatch.setattr("src.quiz_store.grade", explode)
    with pytest.raises(RuntimeError):
        store.record_attempts({"attempts": [_attempt(1)]}, _snapshot())
    monkeypatch.undo()
    assert store.progress(_snapshot())["totals"]["attempts"] == 0
    assert store.record_attempts({"attempts": [_attempt(1)]}, _snapshot())["accepted"]


def test_missing_answered_at_falls_back_to_server_time(store: QuizStore) -> None:
    store.record_attempts({"attempts": [_attempt(1, answeredAt="nonsense")]}, _snapshot())
    last = store.progress(_snapshot())["questions"]["01_CH/q1"]["lastAnsweredAt"]
    assert last.endswith("Z") and not last.startswith("2026-09-28T10:01")


def test_progress_rolls_up_by_question_concept_technology_and_quiz(store: QuizStore) -> None:
    snapshot = _snapshot()
    store.record_attempts(
        {
            "attempts": [
                _attempt(1, selected=["b"]),  # q1 wrong
                _attempt(2, selected=["a"]),  # q1 right (latest)
                _attempt(3, key="01_CH/q2", selected=["a", "b"]),  # q2 right
                _attempt(4, key="01_CH/q2", selected=["a"]),  # q2 wrong (latest)
                _attempt(5, key="01_CH/q3", selected=["a"]),  # q3 wrong
            ]
        },
        snapshot,
    )
    store.set_flags({"flags": [{"questionKey": "02_CH/q1", "flagged": True, "updatedAt": "2026-09-28T11:00:00Z"}]}, snapshot)

    progress = store.progress(snapshot)

    assert progress["questions"]["01_CH/q1"] == {
        "attempts": 2,
        "correct": 1,
        "wrong": 1,
        "lastCorrect": True,
        "lastAnsweredAt": "2026-09-28T10:02:00.000000Z",
        "flagged": False,
    }
    assert progress["questions"]["02_CH/q1"]["flagged"] is True
    assert progress["questions"]["02_CH/q1"]["attempts"] == 0

    policy = next(c for c in progress["concepts"] if c["conceptSlug"] == "policy")
    assert policy["questions"] == 2
    assert policy["attempted"] == 2
    assert policy["attempts"] == 4
    assert policy["correct"] == 2
    assert policy["wrong"] == 2
    assert policy["accuracy"] == 0.5
    assert policy["lastCorrect"] == 1
    assert policy["conceptRoute"] == "01_CH/01_L/concepts/policy"

    techs = {tech["techDir"]: tech for tech in progress["technologies"]}
    assert techs["01_CH"]["attempts"] == 5
    assert techs["01_CH"]["accuracy"] == 0.4
    assert techs["02_CH"]["accuracy"] is None
    assert techs["02_CH"]["flagged"] == 1

    quizzes = {quiz["quizKey"]: quiz for quiz in progress["quizzes"]}
    assert set(quizzes) == {"01_CH/set-a", "01_CH/set-b", "02_CH/set-a"}
    assert quizzes["01_CH/set-a"]["questions"] == 2
    assert quizzes["01_CH/set-a"]["attempts"] == 4
    assert quizzes["01_CH/set-b"]["wrong"] == 1
    assert quizzes["01_CH/set-b"]["accuracy"] == 0.0
    assert progress["totals"] == {
        "questions": 4,
        "attempted": 3,
        "attempts": 5,
        "correct": 2,
        "wrong": 3,
        "flagged": 1,
        "lastCorrect": 1,
        "accuracy": 0.4,
    }


def test_flags_use_last_write_wins_by_client_time(store: QuizStore) -> None:
    snapshot = _snapshot()

    def put(flagged: bool, at: str) -> dict[str, Any]:
        return store.set_flags({"flags": [{"questionKey": "01_CH/q1", "flagged": flagged, "updatedAt": at}]}, snapshot)

    assert put(True, "2026-09-28T10:00:00Z")["flags"][0]["flagged"] is True
    assert put(False, "2026-09-28T09:00:00+00:00")["flags"][0]["flagged"] is True  # older write loses
    newer = put(False, "2026-09-28T12:30:00+02:00")  # 10:30 UTC
    assert newer["flags"] == [{"questionKey": "01_CH/q1", "flagged": False, "updatedAt": "2026-09-28T10:30:00.000000Z"}]
    progress = store.progress(snapshot)
    assert progress["flags"]["01_CH/q1"]["flagged"] is False
    assert "01_CH/q1" not in progress["questions"]


def test_invalid_flags_are_rejected(store: QuizStore) -> None:
    result = store.set_flags(
        {
            "flags": [
                {"questionKey": "nope/q", "flagged": True, "updatedAt": "2026-09-28T10:00:00Z"},
                {"questionKey": "01_CH/q1", "flagged": "yes", "updatedAt": "2026-09-28T10:00:00Z"},
                {"questionKey": "01_CH/q1", "flagged": True, "updatedAt": "later"},
                "junk",
            ]
        },
        _snapshot(),
    )
    assert [item["reason"] for item in result["rejected"]] == [
        "unknown question",
        "invalid flag",
        "invalid flag",
        "unknown question",
    ]
    assert result["flags"] == []


def test_flags_for_removed_questions_are_hidden(store: QuizStore) -> None:
    store.set_flags(
        {"flags": [{"questionKey": "02_CH/q1", "flagged": True, "updatedAt": "2026-09-28T10:00:00Z"}]}, _snapshot()
    )
    remaining = _snapshot(_question("01_CH/q1", "01_CH", "01_L", "policy", ["a"]))
    assert store.progress(remaining)["flags"] == {}


def test_flag_write_failures_roll_back(store: QuizStore, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("src.quiz_store.normalize_timestamp", lambda value: (_ for _ in ()).throw(RuntimeError("boom")))
    with pytest.raises(RuntimeError):
        store.set_flags({"flags": [{"questionKey": "01_CH/q1", "flagged": True, "updatedAt": "x"}]}, _snapshot())


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("2026-09-28T10:00:00Z", "2026-09-28T10:00:00.000000Z"),
        ("2026-09-28T10:00:00.5z", "2026-09-28T10:00:00.500000Z"),
        ("2026-09-28T10:00:00", "2026-09-28T10:00:00.000000Z"),
        ("2026-09-28T12:00:00+02:00", "2026-09-28T10:00:00.000000Z"),
        ("", None),
        (None, None),
        ("x" * 65, None),
        ("yesterday", None),
    ],
)
def test_normalize_timestamp(value: Any, expected: str | None) -> None:
    assert normalize_timestamp(value) == expected


# ── HTTP endpoints ────────────────────────────────────────────


class _Bank:
    def __init__(self, snapshot: QuizSnapshot) -> None:
        self._snapshot = snapshot

    def snapshot(self) -> QuizSnapshot:
        return self._snapshot


@pytest.fixture
def server_url(store: QuizStore) -> Iterator[str]:
    handler = partial(serve.StudyHandler, content_index={"technologies": []}, quiz_bank=_Bank(_snapshot()), quiz_store=store)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()


def _call(url: str, method: str = "GET", body: Any = None, headers: dict[str, str] | None = None) -> tuple[int, Any]:
    data = json.dumps(body).encode() if body is not None else None
    request = Request(url, data=data, method=method, headers={"Content-Type": "application/json", **(headers or {})})
    try:
        with urlopen(request, timeout=2) as response:
            raw = response.read()
            return response.status, (json.loads(raw) if raw else None)
    except HTTPError as error:
        raw = error.read()
        return error.code, (json.loads(raw) if raw and raw.startswith(b"{") else None)


def test_questions_endpoint_supports_etag(server_url: str) -> None:
    with urlopen(f"{server_url}/api/quiz/questions", timeout=2) as response:
        payload = json.loads(response.read())
        etag = response.headers["ETag"]
    assert etag == '"e"'
    assert [question["key"] for question in payload["questions"]][0] == "01_CH/q1"
    assert payload["issues"] == []

    status, _ = _call(f"{server_url}/api/quiz/questions", headers={"If-None-Match": etag})
    assert status == 304


def test_attempts_flags_and_progress_round_trip(server_url: str) -> None:
    status, result = _call(f"{server_url}/api/quiz/attempts", "POST", {"attempts": [_attempt(1)]})
    assert status == 200
    assert result["accepted"][0]["correct"] is True

    status, result = _call(
        f"{server_url}/api/quiz/flags",
        "PUT",
        {"flags": [{"questionKey": "01_CH/q1", "flagged": True, "updatedAt": "2026-09-28T10:00:00Z"}]},
    )
    assert status == 200
    assert result["flags"][0]["flagged"] is True

    status, progress = _call(f"{server_url}/api/quiz/progress")
    assert status == 200
    assert progress["questions"]["01_CH/q1"]["flagged"] is True
    assert progress["totals"]["attempts"] == 1


def test_bad_requests_return_400(server_url: str) -> None:
    status, body = _call(f"{server_url}/api/quiz/attempts", "POST", {"attempts": "nope"})
    assert status == 400
    assert "attempts" in body["error"]

    request = Request(f"{server_url}/api/quiz/flags", data=b"{not json", method="PUT")
    request.add_header("Content-Type", "application/json")
    with pytest.raises(HTTPError) as error:
        urlopen(request, timeout=2)
    assert error.value.code == 400

    status, body = _call(f"{server_url}/api/quiz/attempts", "POST", {"attempts": [], "pad": "x" * (300 * 1024)})
    assert status == 400
    assert body["error"] == "Request body too large"

    status, _ = _call(f"{server_url}/api/quiz/unknown", "PUT", {})
    assert status == 404


def test_quiz_endpoints_report_when_unconfigured() -> None:
    handler = partial(serve.StudyHandler, content_index={"technologies": []})
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        assert _call(f"{base}/api/quiz/questions")[0] == 503
        assert _call(f"{base}/api/quiz/attempts", "POST", {"attempts": []})[0] == 503
    finally:
        server.shutdown()


def test_head_on_quiz_endpoints_sends_no_body(server_url: str) -> None:
    with urlopen(Request(f"{server_url}/api/quiz/progress", method="HEAD"), timeout=2) as response:
        assert response.status == 200
        assert response.read() == b""
    with urlopen(Request(f"{server_url}/api/quiz/questions", method="HEAD"), timeout=2) as response:
        assert response.headers["ETag"] == '"e"'
        assert response.read() == b""


def test_quiz_get_ignores_query_strings(server_url: str) -> None:
    status, payload = _call(f"{server_url}/api/quiz/progress?t=1")
    assert status == 200
    assert "totals" in payload


def test_unknown_post_returns_404(server_url: str) -> None:
    assert _call(f"{server_url}/api/nope", "POST", {})[0] == 404
