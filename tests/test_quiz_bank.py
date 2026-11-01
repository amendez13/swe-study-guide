"""Tests for quiz file loading and validation (issue #72, ported from aws-sa-course #79)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

import pytest
import yaml

from src.quiz_bank import QuizBank, concept_titles, grade, quiz_files, slugify
from tests.test_serve import serve_module

TECH = "01_Algorithms"

VALID_QUESTION: dict[str, Any] = {
    "id": "q-one",
    "topic": "01_Complexity",
    "concept": "Big O notation",
    "prompt": "Which one?",
    "choices": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}, {"id": "c", "text": "C"}],
    "answer": ["b"],
    "explanation": "Because.",
    "placeholder": True,
}


def _content(tmp_path: Path) -> tuple[Path, dict[str, Any]]:
    content = tmp_path / "content"
    topic = content / TECH / "01_Complexity"
    topic.mkdir(parents=True)
    (topic / "concepts.md").write_text("## Big O notation\n\nBody.\n\n## Loop bounds that aren’t N\n\nBody.\n")
    other = content / TECH / "02_Bullets"
    other.mkdir()
    (other / "concepts.md").write_text("- Bullet Concept\n- Another\n")
    (content / "02_Other" / "01_Topic").mkdir(parents=True)
    (content / "02_Other" / "01_Topic" / "concepts.md").write_text("## Thing\n")
    index = {
        "technologies": [
            {
                "num": 1,
                "dir": TECH,
                "title": "Algorithms",
                "topics": [
                    {"num": 1, "dir": "01_Complexity", "title": "Complexity"},
                    {"num": 2, "dir": "02_Bullets", "title": "Bullets"},
                ],
            },
            {"num": 2, "dir": "02_Other", "title": "Other", "topics": [{"num": 1, "dir": "01_Topic", "title": "Topic"}]},
        ]
    }
    return content, index


def _write_quiz(content: Path, name: str, questions: list[Any] | None = None, raw: str | None = None, tech: str = TECH, **meta: Any) -> Path:
    if name == "quiz.yaml":
        path = content / tech / name
    else:
        path = content / tech / "quizzes" / name
        path.parent.mkdir(parents=True, exist_ok=True)
    if raw is not None:
        path.write_text(raw)
    else:
        path.write_text(yaml.safe_dump({"version": 1, **meta, "questions": questions or []}, allow_unicode=True))
    return path


def _question(**overrides: Any) -> dict[str, Any]:
    question = json.loads(json.dumps(VALID_QUESTION))
    question.update(overrides)
    return question


def test_valid_question_is_resolved_to_a_concept_route(tmp_path: Path) -> None:
    content, index = _content(tmp_path)
    _write_quiz(
        content,
        "basics.yaml",
        [_question(answer="b"), _question(id="q-two", topic="02_Bullets", concept="Another")],
        title="Basics",
        description="Intro set",
    )

    snapshot = QuizBank(content, index).snapshot()

    assert snapshot.issues == []
    first = snapshot.by_key[f"{TECH}/q-one"]
    assert first["conceptRoute"] == f"{TECH}/01_Complexity/concepts/big-o-notation"
    assert first["conceptTitle"] == "Big O notation"
    assert first["answer"] == ["b"]
    assert first["multiple"] is False
    assert first["placeholder"] is True
    assert first["quizKey"] == f"{TECH}/basics"
    assert first["quizTitle"] == "Basics"
    assert first["techTitle"] == "Algorithms"
    assert first["topicNum"] == 1
    assert snapshot.by_key[f"{TECH}/q-two"]["conceptSlug"] == "another"
    payload = snapshot.payload()
    assert payload["questions"] == snapshot.questions
    assert payload["quizzes"] == [
        {
            "key": f"{TECH}/basics",
            "id": "basics",
            "techDir": TECH,
            "title": "Basics",
            "description": "Intro set",
            "file": f"{TECH}/quizzes/basics.yaml",
            "questions": 2,
        }
    ]


def test_many_quiz_sets_per_technology_and_legacy_file(tmp_path: Path) -> None:
    content, index = _content(tmp_path)
    _write_quiz(content, "quiz.yaml", [_question(id="legacy")])
    _write_quiz(content, "b-second.yml", [_question(id="second", answer=["c", "a"])])
    _write_quiz(content, "a_first.yaml", [_question(id="first", concept="loop bounds that aren't n")])
    _write_quiz(content, "other.yaml", [_question(id="first", topic="01_Topic", concept="Thing")], tech="02_Other")
    (content / TECH / "quizzes" / "notes.txt").write_text("ignored")

    snapshot = QuizBank(content, index).snapshot()

    assert snapshot.issues == []
    assert [quiz["key"] for quiz in snapshot.quizzes] == [
        f"{TECH}/quiz",
        f"{TECH}/a_first",
        f"{TECH}/b-second",
        "02_Other/other",
    ]
    assert [quiz["title"] for quiz in snapshot.quizzes][:3] == ["Quiz", "A first", "B second"]
    # Same id in different technologies is fine: keys are <techDir>/<id>.
    assert {f"{TECH}/first", "02_Other/first"} <= set(snapshot.by_key)
    assert snapshot.by_key[f"{TECH}/first"]["conceptTitle"] == "Loop bounds that aren’t N"
    assert snapshot.by_key[f"{TECH}/second"]["answer"] == ["a", "c"]
    assert snapshot.by_key[f"{TECH}/second"]["multiple"] is True


def test_duplicate_ids_across_quiz_files_of_one_technology_are_not_served(tmp_path: Path) -> None:
    content, index = _content(tmp_path)
    _write_quiz(content, "one.yaml", [_question(id="dup"), _question(id="keep-one")])
    _write_quiz(content, "two.yaml", [_question(id="dup"), _question(id="keep-two")])

    snapshot = QuizBank(content, index).snapshot()

    assert sorted(snapshot.by_key) == [f"{TECH}/keep-one", f"{TECH}/keep-two"]
    assert sorted(issue["file"] for issue in snapshot.issues) == [f"{TECH}/quizzes/one.yaml", f"{TECH}/quizzes/two.yaml"]
    assert all("Duplicate question id 'dup'" in issue["message"] for issue in snapshot.issues)
    assert {quiz["key"]: quiz["questions"] for quiz in snapshot.quizzes} == {f"{TECH}/one": 1, f"{TECH}/two": 1}


@pytest.mark.parametrize(
    ("overrides", "message"),
    [
        ({"id": "Bad Id"}, "'id' must match"),
        ({"topic": "99_Missing"}, "Unknown topic"),
        ({"concept": ""}, "'concept' is required"),
        ({"concept": "Nope"}, "is not a '## ' heading"),
        ({"prompt": "  "}, "'prompt' is required"),
        ({"choices": [{"id": "a", "text": "A"}]}, "at least 2"),
        ({"choices": ["a", "b"]}, "must be a mapping"),
        ({"choices": [{"id": "A!", "text": "x"}, {"id": "b", "text": "y"}]}, "Choice 'id'"),
        ({"choices": [{"id": "a", "text": ""}, {"id": "b", "text": "y"}]}, "needs 'text'"),
        ({"choices": [{"id": "a", "text": "x"}, {"id": "a", "text": "y"}]}, "Duplicate choice"),
        ({"answer": []}, "non-empty list"),
        ({"answer": ["b", "b"]}, "non-empty list"),
        ({"answer": ["z"]}, "unknown choice ids"),
        ({"explanation": 5}, "'explanation' must be text"),
    ],
)
def test_invalid_questions_are_excluded_and_reported(tmp_path: Path, overrides: dict[str, Any], message: str) -> None:
    content, index = _content(tmp_path)
    _write_quiz(content, "set.yaml", [_question(**overrides), _question(id="q-ok")])

    snapshot = QuizBank(content, index).snapshot()

    assert [question["id"] for question in snapshot.questions] == ["q-ok"]
    assert len(snapshot.issues) == 1
    assert snapshot.issues[0]["file"] == f"{TECH}/quizzes/set.yaml"
    assert message in snapshot.issues[0]["message"]


def test_duplicate_ids_in_one_file_and_non_mapping_questions_are_reported(tmp_path: Path) -> None:
    content, index = _content(tmp_path)
    _write_quiz(content, "set.yaml", [_question(), _question(), "not a mapping", _question(id="q-x", explanation=None)])

    snapshot = QuizBank(content, index).snapshot()

    assert [question["id"] for question in snapshot.questions] == ["q-one", "q-x"]
    assert snapshot.by_key[f"{TECH}/q-x"]["explanation"] == ""
    messages = [issue["message"] for issue in snapshot.issues]
    assert any("Duplicate question id" in message for message in messages)
    assert any(issue["question"] == "#3" for issue in snapshot.issues)


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("questions: [unclosed", "Cannot parse file"),
        ("- just a list\n", "must be a mapping"),
        ("version: 2\nquestions: []\n", "Unsupported version"),
        ("title: 5\nquestions: []\n", "'title' must be text"),
        ("description: [1]\nquestions: []\n", "'description' must be text"),
    ],
)
def test_broken_files_do_not_break_other_quiz_sets(tmp_path: Path, raw: str, message: str) -> None:
    content, index = _content(tmp_path)
    _write_quiz(content, "broken.yaml", raw=raw)
    _write_quiz(content, "good.yaml", [_question()])

    snapshot = QuizBank(content, index).snapshot()

    assert list(snapshot.by_key) == [f"{TECH}/q-one"]
    assert [quiz["id"] for quiz in snapshot.quizzes] == ["good"]
    assert message in snapshot.issues[0]["message"]


def test_bad_quiz_file_names_are_reported(tmp_path: Path) -> None:
    content, index = _content(tmp_path)
    _write_quiz(content, "Bad Name.yaml", [_question()])

    snapshot = QuizBank(content, index).snapshot()

    assert snapshot.questions == []
    assert "Quiz file name" in snapshot.issues[0]["message"]


def test_snapshot_is_cached_until_an_input_file_changes(tmp_path: Path) -> None:
    content, index = _content(tmp_path)
    quiz = _write_quiz(content, "set.yaml", [_question()])
    bank = QuizBank(content, lambda: index)

    first = bank.snapshot()
    assert bank.snapshot() is first

    quiz.write_text(yaml.safe_dump({"questions": [_question(), _question(id="q-two")]}))
    stat = quiz.stat()
    os.utime(quiz, ns=(stat.st_atime_ns, stat.st_mtime_ns + 1_000_000))

    second = bank.snapshot()
    assert second is not first
    assert second.etag != first.etag
    assert len(second.questions) == 2

    index["technologies"][0]["topics"][0]["title"] = "Renamed"
    third = bank.snapshot()
    assert third is not second
    assert third.by_key[f"{TECH}/q-one"]["topicTitle"] == "Renamed"


def test_unreadable_concepts_file_makes_the_concept_unknown(tmp_path: Path) -> None:
    content, index = _content(tmp_path)
    _write_quiz(content, "set.yaml", [_question()])
    (content / TECH / "01_Complexity" / "concepts.md").write_bytes(b"\xff\xfe\x00bad")

    snapshot = QuizBank(content, index).snapshot()

    assert snapshot.questions == []
    assert "is not a '## ' heading" in snapshot.issues[0]["message"]


def test_index_entries_without_a_dir_are_ignored(tmp_path: Path) -> None:
    content, index = _content(tmp_path)
    _write_quiz(content, "set.yaml", [_question()])
    index["technologies"].insert(0, {"title": "no dir"})

    assert len(QuizBank(content, index).snapshot().questions) == 1


def test_quiz_files_lists_legacy_then_sorted_sets(tmp_path: Path) -> None:
    content, _ = _content(tmp_path)
    assert quiz_files(content / TECH) == []
    _write_quiz(content, "z.yaml", [])
    _write_quiz(content, "quiz.yaml", [])
    assert [quiz_id for quiz_id, _ in quiz_files(content / TECH)] == ["quiz", "z"]


def test_concept_titles_mirror_the_site_parser() -> None:
    assert concept_titles("## One\ntext\n### Not a concept\n##  Two  \n") == ["One", "Two"]
    assert concept_titles("- First\n  - Second\ntext\n") == ["First", "Second"]
    assert concept_titles("plain text") == []


def test_slugify_matches_the_site() -> None:
    assert slugify("Loop bounds that aren’t N") == "loop-bounds-that-aren-t-n"
    assert slugify("  Café — Größe ") == "cafe-gro-e"
    assert slugify("Multi-part algorithms: add vs. multiply") == "multi-part-algorithms-add-vs-multiply"


def test_grade_requires_the_exact_answer_set() -> None:
    question = {"answer": ["a", "c"]}
    assert grade(question, ["c", "a"]) is True
    assert grade(question, ["a"]) is False
    assert grade(question, ["a", "b", "c"]) is False


def test_every_committed_quiz_file_is_valid() -> None:
    """CI guard: committed quiz content must reference real topics and concepts."""

    index = serve_module.build_content_index()
    snapshot = QuizBank(serve_module.CONTENT_DIR, index).snapshot()

    assert snapshot.issues == []
    committed = list(serve_module.CONTENT_DIR.glob("*/quizzes/*.y*ml")) + list(serve_module.CONTENT_DIR.glob("*/quiz.yaml"))
    assert committed, "expected at least one committed quiz file"
    assert snapshot.questions
    assert len(snapshot.quizzes) == len(committed)
