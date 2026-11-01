#!/usr/bin/env python3
"""Render every quiz question as one Markdown document for content review.

Questions are validated exactly as the site serves them (src/quiz_bank.py), so
the dump also lists any content errors. Correct answers are marked with ✅.
Ported from aws-sa-course (issue #72).

Usage:
    python scripts/export_quiz_markdown.py [-o artifacts/quiz_dump.md]
        [--technology 07_Data_Structures_and_Algorithms] [--quiz <techDir>/<quizId>]
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import serve  # noqa: E402
from src.quiz_bank import QuizBank, QuizSnapshot  # noqa: E402


def render(snapshot: QuizSnapshot, technologies: set[str] | None = None, quizzes: set[str] | None = None) -> str:
    questions = [
        q
        for q in snapshot.questions
        if (not technologies or q["techDir"] in technologies) and (not quizzes or q["quizKey"] in quizzes)
    ]
    per_quiz = Counter((q["techDir"], q["quizTitle"]) for q in questions)
    lines: list[str] = ["# Quiz content dump", ""]
    lines.append(
        f"{len(questions)} questions in {len(per_quiz)} quizzes · "
        f"{sum(q['multiple'] for q in questions)} multi-answer · "
        f"{sum(q['placeholder'] for q in questions)} placeholders · "
        f"{len(snapshot.issues)} content issues"
    )
    lines.append("")
    lines.append("| Technology | Quiz | Questions |")
    lines.append("|---|---|---|")
    for (tech_dir, quiz_title), count in per_quiz.items():
        lines.append(f"| {tech_dir} | {quiz_title} | {count} |")
    lines.append("")

    if snapshot.issues:
        lines += ["## Content issues", ""]
        for issue in snapshot.issues:
            lines.append(f"- `{issue['file']}` {issue['question']}: {issue['message']}")
        lines.append("")

    current_tech = current_quiz = current_topic = None
    number = 0
    for question in questions:
        if question["techDir"] != current_tech:
            current_tech, current_quiz, current_topic = question["techDir"], None, None
            lines += [f"## {question['techNum']}. {question['techTitle']}", ""]
        if question["quizKey"] != current_quiz:
            current_quiz, current_topic = question["quizKey"], None
            lines += [f"### Quiz: {question['quizTitle']}", ""]
        if question["topicDir"] != current_topic:
            current_topic = question["topicDir"]
            lines += [f"#### {question['topicNum']}. {question['topicTitle']}", ""]
        number += 1
        lines += _question(number, question)
    return "\n".join(lines).rstrip() + "\n"


def _question(number: int, question: dict[str, Any]) -> list[str]:
    tags = ["multi-answer"] if question["multiple"] else []
    if question["placeholder"]:
        tags.append("placeholder")
    suffix = f" _({', '.join(tags)})_" if tags else ""
    lines = [
        f"##### Q{number} · `{question['id']}`{suffix}",
        "",
        f"**Concept:** {question['conceptTitle']} → `#{question['conceptRoute']}`",
        "",
        question["prompt"],
        "",
    ]
    for choice in question["choices"]:
        mark = "✅" if choice["id"] in question["answer"] else "▫️"
        lines.append(f"- {mark} **{choice['id']}.** {choice['text']}")
    lines.append("")
    if question["explanation"]:
        lines += [f"> {line}" if line else ">" for line in question["explanation"].splitlines()]
        lines.append("")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("-o", "--output", type=Path, help="write to this file instead of stdout")
    parser.add_argument("--technology", action="append", help="limit to a technology dir (repeatable)")
    parser.add_argument("--quiz", action="append", help="limit to a quiz key <techDir>/<quizId> (repeatable)")
    args = parser.parse_args(argv)

    snapshot = QuizBank(serve.CONTENT_DIR, serve.build_content_index()).snapshot()
    markdown = render(
        snapshot,
        set(args.technology) if args.technology else None,
        set(args.quiz) if args.quiz else None,
    )
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(markdown, encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        sys.stdout.write(markdown)
    return 1 if snapshot.issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
