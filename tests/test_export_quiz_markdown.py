"""Tests for scripts/export_quiz_markdown.py (issue #72)."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

from src.quiz_bank import QuizSnapshot

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "export_quiz_markdown.py"
_spec = importlib.util.spec_from_file_location("export_quiz_markdown", SCRIPT)
assert _spec and _spec.loader
export = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(export)


def _question(key: str, topic: str, answer: list[str], quiz: str = "basics", **extra: object) -> dict[str, object]:
    tech, qid = key.split("/")
    question: dict[str, object] = {
        "key": key,
        "id": qid,
        "quizKey": f"{tech}/{quiz}",
        "quizTitle": quiz.title(),
        "techDir": tech,
        "techNum": int(tech[:2]),
        "techTitle": tech[3:],
        "topicDir": topic,
        "topicNum": int(topic[:2]),
        "topicTitle": topic[3:],
        "conceptTitle": "Big O",
        "conceptRoute": f"{tech}/{topic}/concepts/big-o",
        "prompt": "Which one?",
        "choices": [{"id": "a", "text": "A"}, {"id": "b", "text": "B"}],
        "answer": answer,
        "multiple": len(answer) > 1,
        "explanation": "Line one.\n\nLine two.",
        "placeholder": False,
    }
    question.update(extra)
    return question


def _snapshot() -> QuizSnapshot:
    questions = [
        _question("01_ALG/q1", "01_Intro", ["b"]),
        _question("01_ALG/q2", "02_More", ["a", "b"], quiz="advanced", placeholder=True, explanation=""),
        _question("02_NEXT/q1", "01_Intro", ["a"]),
    ]
    return QuizSnapshot(
        questions=questions,
        quizzes=[],
        issues=[{"file": "03_X/quizzes/x.yaml", "question": "bad", "message": "Unknown topic"}],
        etag="e",
        by_key={q["key"]: q for q in questions},  # type: ignore[misc]
    )


def test_render_groups_by_technology_quiz_and_topic_and_marks_answers() -> None:
    markdown = export.render(_snapshot())

    assert "3 questions in 3 quizzes · 1 multi-answer · 1 placeholders · 1 content issues" in markdown
    assert "- `03_X/quizzes/x.yaml` bad: Unknown topic" in markdown
    assert markdown.count("## 1. ALG") == 1
    assert "### Quiz: Advanced" in markdown
    assert "#### 2. More" in markdown
    assert "##### Q2 · `q2` _(multi-answer, placeholder)_" in markdown
    assert "- ▫️ **a.** A\n- ✅ **b.** B" in markdown
    assert "> Line one.\n>\n> Line two." in markdown
    assert "`#01_ALG/01_Intro/concepts/big-o`" in markdown

    only_second = export.render(_snapshot(), {"02_NEXT"})
    assert "1 questions in 1 quizzes" in only_second
    assert "## 1. ALG" not in only_second

    only_quiz = export.render(_snapshot(), quizzes={"01_ALG/advanced"})
    assert "1 questions in 1 quizzes" in only_quiz
    assert "### Quiz: Basics" not in only_quiz


def test_main_exports_committed_content(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    out = tmp_path / "dump.md"
    assert export.main(["-o", str(out), "--technology", "07_Data_Structures_and_Algorithms"]) == 0
    assert "Algorithmic Complexity" in out.read_text(encoding="utf-8")
    assert export.main(["--quiz", "07_Data_Structures_and_Algorithms/complexity-code-analysis"]) == 0
    assert "Analyse the Code" in capsys.readouterr().out
