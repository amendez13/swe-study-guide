"""Tests for the standalone study-guide web server."""

from __future__ import annotations

import importlib.util
import io
import sys
from pathlib import Path

from src.quiz_bank import concept_titles


def import_serve_module():
    """Import the repo-root serve.py module for direct testing."""
    repo_root = Path(__file__).resolve().parent.parent
    module_path = repo_root / "serve.py"
    spec = importlib.util.spec_from_file_location("swe_study_guide_serve", module_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


serve_module = import_serve_module()


def _write_topic(content_root: Path, tech: str, topic: str, files: dict[str, str]) -> None:
    topic_dir = content_root / tech / topic
    topic_dir.mkdir(parents=True)
    for name, text in files.items():
        (topic_dir / name).write_text(text, encoding="utf-8")


def test_build_content_index_has_drills_when_drills_md_present(monkeypatch, tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write_topic(
        content,
        "01_Algorithms",
        "01_Complexity",
        {"notes.md": "# Notes\n", "concepts.md": "## Concept\n", "drills.md": "## Drill\n"},
    )
    monkeypatch.setattr(serve_module, "CONTENT_DIR", content)

    topic = serve_module.build_content_index()["technologies"][0]["topics"][0]

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"


def test_build_content_index_has_drills_false_when_drills_md_absent(monkeypatch, tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write_topic(
        content,
        "01_Algorithms",
        "02_Sorting",
        {"notes.md": "# Notes\n", "concepts.md": "## Concept\n"},
    )
    monkeypatch.setattr(serve_module, "CONTENT_DIR", content)

    topic = serve_module.build_content_index()["technologies"][0]["topics"][0]

    assert topic["hasDrills"] is False
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"


def test_build_content_index_excludes_drills_md_from_notes_candidates(monkeypatch, tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write_topic(
        content,
        "01_Algorithms",
        "03_Graphs",
        {"overview.md": "# Overview\n", "concepts.md": "## Concept\n", "drills.md": "## Drill\n"},
    )
    monkeypatch.setattr(serve_module, "CONTENT_DIR", content)

    topic = serve_module.build_content_index()["technologies"][0]["topics"][0]

    assert topic["notesFile"] == "overview.md"
    assert topic["hasDrills"] is True


def test_build_content_index_drills_only_topic_has_no_notes_file(monkeypatch, tmp_path: Path) -> None:
    content = tmp_path / "content"
    _write_topic(content, "01_Algorithms", "04_Heaps", {"drills.md": "## Drill\n"})
    monkeypatch.setattr(serve_module, "CONTENT_DIR", content)

    topic = serve_module.build_content_index()["technologies"][0]["topics"][0]

    assert topic["notesFile"] is None
    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is False


def test_algorithmic_complexity_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "07_Data_Structures_and_Algorithms"
        for item in tech["topics"]
        if item["dir"] == "01_Algorithmic_Complexity"
    )

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"


def test_interview_framework_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "09_System_Design_Interview"
        for item in tech["topics"]
        if item["dir"] == "01_Interview_Framework_and_Process"
    )

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = (
        Path(__file__).resolve().parent.parent
        / "content"
        / "09_System_Design_Interview"
        / "01_Interview_Framework_and_Process"
    )
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## The Four-Step Framework",
        "## Time Allocation",
        "## Back-of-the-Envelope Estimation",
        "## QPS and Storage Estimate",
        "## Choosing the Deep-Dive Focus",
        "## The Wrap-Up Checklist",
    ):
        assert heading in concepts
    assert "Understand & establish scope" in concepts
    assert "Propose high-level design & get buy-in" in concepts
    assert "Design deep dive" in concepts
    assert "2^10" in concepts
    assert "99.999%" in concepts
    assert drills.count("**Answer:**") >= 6
    assert "estimate_load" in notes


def test_scalability_fundamentals_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "09_System_Design_Interview"
        for item in tech["topics"]
        if item["dir"] == "02_Scalability_Fundamentals"
    )

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = (
        Path(__file__).resolve().parent.parent / "content" / "09_System_Design_Interview" / "02_Scalability_Fundamentals"
    )
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## Vertical Scaling",
        "## Horizontal Scaling",
        "## Stateless vs. Stateful Services",
        "## Shared Session Store",
        "## Describing Load",
        "## Describing Performance",
        "## The Scale Cube",
        "## Scaling from Zero to Millions",
    ):
        assert heading in concepts
    assert "Multiple data centers" in concepts
    assert "Logging, metrics, automation" in concepts
    assert "The design lives in Observability" in concepts
    assert "no observability topic yet" not in concepts.lower()
    assert "shared session store" in concepts.lower()
    answers = drills.split("**Answer:**")[1:]
    assert len(answers) >= 8
    assert all("```python" in answer for answer in answers)
    assert "feed_plan" in notes
    assert "Shared session store" in notes
    assert "25_Observability" in notes


def test_high_availability_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "09_System_Design_Interview"
        for item in tech["topics"]
        if item["dir"] == "03_High_Availability_and_Reliability"
    )

    assert topic["title"] == "High Availability and Reliability"
    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = (
        Path(__file__).resolve().parent.parent
        / "content"
        / "09_System_Design_Interview"
        / "03_High_Availability_and_Reliability"
    )
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## Availability and the Nines",
        "## MTBF and MTTR",
        "## Redundancy and Replication",
        "## Failover Strategies",
        "## Active-Active vs. Active-Passive",
        "## Multi-DC and Geo Routing",
        "## SLA, SLO, and SLI",
        "## Graceful Degradation",
        "## Circuit Breaker Pattern",
    ):
        assert heading in concepts
    assert concepts.count("## Multi-DC and Geo Routing") == 1
    assert "Residency" in concepts
    assert "Fail closed" in concepts
    assert "commit_ms" in concepts
    answers = drills.split("**Answer:**")[1:]
    assert len(answers) >= 8
    assert all("```python" in answer for answer in answers)
    assert "still_east" in drills
    assert "998001" in drills
    assert "3153" in drills
    assert "local-copy" in notes
    assert "02_Scalability_Fundamentals" in notes
    assert "25_Observability" in notes
    assert "22_Content_Distribution_and_Media" in notes


def test_load_balancing_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "09_System_Design_Interview"
        for item in tech["topics"]
        if item["dir"] == "04_Load_Balancing"
    )

    assert topic["title"] == "Load Balancing"
    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = Path(__file__).resolve().parent.parent / "content" / "09_System_Design_Interview" / "04_Load_Balancing"
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## What a Load Balancer Does",
        "## In Front of the Web Tier",
        "## DNS-Level Load Balancing",
        "## Layer 4 vs. Layer 7 Load Balancing",
        "## TLS Termination",
        "## Load Balancing Algorithms",
        "## Health Checks",
        "## Sticky Sessions (Session Affinity)",
        "## Load Balancer as a Single Point of Failure",
    ):
        assert heading in concepts
    assert "Shared Session Store" in concepts
    assert "02_Scalability_Fundamentals" in concepts
    answers = drills.split("**Answer:**")[1:]
    assert len(answers) >= 8
    assert all("```python" in answer for answer in answers)
    assert "333 500" in drills
    assert "vip-moved" in drills
    assert "pick_door" in notes
    assert "web-b web-c" in notes
    assert "02_Scalability_Fundamentals" in notes
    assert "03_High_Availability_and_Reliability" in notes
    assert "10_Networking_and_Communication" in notes


def test_scalability_multi_dc_pointer_names_the_card() -> None:
    topic_dir = (
        Path(__file__).resolve().parent.parent / "content" / "09_System_Design_Interview" / "02_Scalability_Fundamentals"
    )
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    assert "There is no dedicated multi-data-center card yet." not in notes
    assert "Multi-DC and Geo Routing" in notes
    assert "no dedicated multi-data-center card" not in drills
    assert "Multi-DC and Geo Routing card in High Availability" in drills


def test_observability_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "09_System_Design_Interview"
        for item in tech["topics"]
        if item["dir"] == "25_Observability"
    )

    assert topic["title"] == "Observability"
    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = Path(__file__).resolve().parent.parent / "content" / "09_System_Design_Interview" / "25_Observability"
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## Per-Server Logs",
        "## Centralized Logs",
        "## Error Logs",
        "## Host Metrics",
        "## Tier Metrics",
        "## Business Metrics",
        "## Continuous Integration",
        "## Repeatable Deploys",
        "## Fleet Growth",
    ):
        assert heading in concepts
    assert "request id" in concepts.lower()
    assert "data center" in concepts.lower()
    answers = drills.split("**Answer:**")[1:]
    assert len(answers) >= 8
    assert all("```python" in answer for answer in answers)
    assert "31600" in drills
    assert "tier_error_rate" in notes
    assert "01_Interview_Framework_and_Process" in notes
    assert "02_Scalability_Fundamentals" in notes
    assert "03_High_Availability_and_Reliability" in notes


def test_caching_topic_has_no_cdn_card() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "09_System_Design_Interview"
        for item in tech["topics"]
        if item["dir"] == "05_Caching"
    )

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = Path(__file__).resolve().parent.parent / "content" / "09_System_Design_Interview" / "05_Caching"
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## When Caching Helps",
        "## Cache Tier Placement",
        "## Hit Ratio Math",
        "## Cache-Aside (Lazy Loading)",
        "## Read-Through and Write-Through",
        "## Write-Behind (Write-Back)",
        "## Eviction Policies",
        "## TTL Tuning",
        "## Cache Invalidation",
        "## Cache Stampede Protection",
        "## Hot Key Mitigation",
        "## Distributed Cache Architecture",
        "## Cache Failure and Overprovisioning",
        "## Multi-Layer Caching",
    ):
        assert heading in concepts
    for heading in (
        "## Hit Ratio Latency",
        "## Required Hit Ratio",
        "## Stale Read Race",
        "## LRU Trace",
        "## Pick the Write Pattern",
        "## Stampede Fix",
        "## Cache Node Loss",
        "## Hot Key Split",
    ):
        assert heading in drills
    assert len(concepts.split("\n## ")) == 14
    cards = drills.split("\n## ")[1:]
    assert len(cards) == 8
    answer_bodies = [card.split("**Answer:**", 1)[1] for card in cards]
    assert sum("```python" in body for body in answer_bodies) == 7
    assert "```python" not in answer_bodies[4]
    assert "0.8 5 100" in drills
    assert "0.95 20" in drills
    assert "no-second-delete" in drills
    assert "('B', ['C', 'A', 'D'])" in drills
    assert "30 1" in drills
    assert "200 650" in drills
    assert "850 250" in drills
    assert "write_then_delete" in notes
    assert "None 2.4 100 67" in notes
    assert "80–95" not in concepts
    assert "80–95" not in notes
    assert "80-95" not in concepts
    assert "80-95" not in notes
    assert "two sources of truth" not in notes.lower()
    assert "source of truth" in concepts.lower()
    assert "## CDN" not in concepts
    assert "## CDN" not in drills
    assert "Content Delivery Network" not in concepts
    assert "Content Delivery Network" not in drills
    assert "Content Delivery Network" not in notes
    assert "pull" not in notes.lower()
    assert "22_Content_Distribution_and_Media" in notes
    assert "08_Data_Partitioning_and_Consistent_Hashing" in notes
    assert "09_Consistency_and_Replication" in notes


def test_relational_databases_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "09_System_Design_Interview"
        for item in tech["topics"]
        if item["dir"] == "06_Databases_Relational"
    )

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = Path(__file__).resolve().parent.parent / "content" / "09_System_Design_Interview" / "06_Databases_Relational"
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    concept_headings = [
        "## Relational Database",
        "## Choosing Relational or NoSQL",
        "## ACID Properties",
        "## Normalization and Denormalization",
        "## Indexing",
        "## Vertical Database Scaling",
        "## Database Replication",
        "## Read Replicas",
        "## Failover and Promotion",
        "## Database Sharding",
        "## Sharding Challenges",
    ]
    drill_headings = [
        "## Replica Count",
        "## Read After Write",
        "## Primary Loss",
        "## Vertical or Shard",
        "## Shard Key Pick",
        "## Hot Shard",
        "## Resharding Cost",
        "## Index Choice",
    ]
    for heading in concept_headings:
        assert heading in concepts
    for heading in drill_headings:
        assert heading in drills
    assert concept_titles(concepts) == [heading.removeprefix("## ") for heading in concept_headings]
    assert concept_titles(drills) == [heading.removeprefix("## ") for heading in drill_headings]
    assert len(concepts.split("\n## ")) == 11
    cards = drills.split("\n## ")[1:]
    assert len(cards) == 8
    answer_bodies = {card.split("\n", 1)[0]: card.split("**Answer:**", 1)[1] for card in cards}
    assert sum("```python" in body for body in answer_bodies.values()) == 6
    assert "```python" not in answer_bodies["Vertical or Shard"]
    assert "```python" not in answer_bodies["Index Choice"]
    assert "12000 8000 True False True" in drills
    assert "False True True True" in drills
    assert "[75, 76, 77, 78, 79, 80] [] [72, 73, 74, 75, 76, 77, 78, 79, 80]" in drills
    assert "1 2 4 8" in drills
    assert "7750 750" in drills
    assert "800 50" in drills
    assert "6 12000 8000" in notes
    assert "Normalization vs. Denormalization" not in concepts
    assert "W + R > N" not in concepts
    assert "W + R > N" not in notes
    assert "W + R > N" not in drills
    assert "zero data loss" not in concepts.lower()
    assert "instant failover" not in concepts.lower()
    assert "07_Databases_NoSQL_and_Specialized" in notes
    assert "08_Data_Partitioning_and_Consistent_Hashing" in notes
    assert "09_Consistency_and_Replication" in notes
    assert "05_Caching" in notes
    assert "03_High_Availability_and_Reliability" in concepts
    assert "02_Scalability_Fundamentals" in concepts


def test_content_distribution_owns_cdn_and_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "09_System_Design_Interview"
        for item in tech["topics"]
        if item["dir"] == "22_Content_Distribution_and_Media"
    )

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = (
        Path(__file__).resolve().parent.parent / "content" / "09_System_Design_Interview" / "22_Content_Distribution_and_Media"
    )
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## Why a CDN",
        "## Edge and Origin",
        "## Cacheable and Dynamic",
        "## CDN TTL",
        "## Purge and Invalidation",
        "## PoPs and Placement",
        "## Origin Shield",
        "## Video Uploading and Transcoding",
        "## Adaptive Bitrate Streaming",
        "## CDN Cost Optimization",
        "## File Sync and Conflict Resolution",
        "## Image Processing and Optimization",
    ):
        assert heading in concepts
    assert concepts.count("A CDN is a set of caches") == 1
    answers = drills.split("**Answer:**")[1:]
    assert len(answers) >= 6
    assert all("```python" in answer for answer in answers)
    assert "origin_fetches_per_sec" in drills
    assert "hit_ratio" in drills
    assert "05_Caching" in notes
    assert "origin shield" in notes.lower()


def test_scalability_cdn_pointer_targets_content_distribution() -> None:
    topic_dir = (
        Path(__file__).resolve().parent.parent / "content" / "09_System_Design_Interview" / "02_Scalability_Fundamentals"
    )
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    assert "Foundational CDN behavior stays in Caching" not in concepts
    assert "Foundational CDN and media pipelines both live in Content Distribution." in concepts
    assert "Basic CDN stays in Caching" not in notes
    assert "22_Content_Distribution_and_Media" in notes
    assert '"CDN basics": "Content Distribution"' in drills
    assert '"CDN basics": "Caching"' not in drills


CODING_PROBLEMS_TOPICS = (
    "01_Math_and_Logic_Puzzles",
    "02_Object-Oriented_Design",
    "03_Testing",
    "04_Databases_and_SQL",
    "05_Threads_and_Locks",
    "06_Moderate_Problems",
    "07_Hard_Problems",
)


def _coding_problems_tech() -> dict:
    index = serve_module.build_content_index()
    return next(tech for tech in index["technologies"] if tech["dir"] == "11_Coding_Problems")


def test_coding_problems_section_is_indexed_in_order() -> None:
    tech = _coding_problems_tech()

    assert tech["num"] == 11
    assert tech["title"] == "Coding Problems"
    assert tech["hasTechnologyConcepts"] is False
    assert [topic["dir"] for topic in tech["topics"]] == list(CODING_PROBLEMS_TOPICS)
    assert [topic["title"] for topic in tech["topics"]] == [
        "Math and Logic Puzzles",
        "Object-Oriented Design",
        "Testing",
        "Databases and SQL",
        "Threads and Locks",
        "Moderate Problems",
        "Hard Problems",
    ]


def test_math_and_logic_puzzles_topic_exposes_drills() -> None:
    tech = _coding_problems_tech()
    topic = next(item for item in tech["topics"] if item["dir"] == "01_Math_and_Logic_Puzzles")

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = Path(__file__).resolve().parent.parent / "content" / "11_Coding_Problems" / "01_Math_and_Logic_Puzzles"
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## Divisibility",
        "## Checking for primality",
        "## Sieve of Eratosthenes",
        "## Probability of A and B",
        "## Probability of A or B",
        "## Independence",
        "## Mutual exclusivity",
        "## Start talking",
        "## Develop rules and patterns",
        "## Worst case shifting",
        "## Algorithm approaches",
        "## GCD and LCM",
        "## Modular arithmetic",
        "## Fast exponentiation",
        "## Overflow awareness",
    ):
        assert heading in concepts
    answers = drills.split("**Answer:**")[1:]
    assert len(answers) >= 12
    assert all("```python" in answer for answer in answers)
    assert "math.isqrt" in concepts
    assert "mod_pow" in notes


def test_object_oriented_design_topic_exposes_drills() -> None:
    tech = _coding_problems_tech()
    topic = next(item for item in tech["topics"] if item["dir"] == "02_Object-Oriented_Design")

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = Path(__file__).resolve().parent.parent / "content" / "11_Coding_Problems" / "02_Object-Oriented_Design"
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## Handle ambiguity",
        "## Define the core objects",
        "## Analyze relationships",
        "## Investigate actions",
        "## Encapsulation",
        "## Inheritance",
        "## Polymorphism",
        "## Composition over inheritance",
        "## Interfaces vs abstract classes",
        "## SOLID",
        "## Singleton",
        "## Factory method",
        "## Strategy",
        "## Observer",
        "## Decorator and Adapter",
        "## State machines",
    ):
        assert heading in concepts
    answers = drills.split("**Answer:**")[1:]
    assert len(answers) >= 12
    assert all("```python" in answer for answer in answers)
    assert "FeePolicy" in concepts or "price" in concepts
    assert "BikeCage" in notes


def test_testing_topic_exposes_drills() -> None:
    tech = _coding_problems_tech()
    topic = next(item for item in tech["topics"] if item["dir"] == "03_Testing")

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = Path(__file__).resolve().parent.parent / "content" / "11_Coding_Problems" / "03_Testing"
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## What the interviewer is looking for",
        "## Testing a real-world object",
        "## Manual vs automated",
        "## Black-box vs white-box",
        "## Testing a function",
        "## Unit, integration, and end-to-end",
        "## The test pyramid",
        "## Equivalence classes",
        "## Boundary values",
        "## Edge and error cases",
        "## Stubs, fakes, and mocks",
        "## Property-based testing",
        "## Flaky tests and determinism",
        "## Load and security basics",
        "## Troubleshooting questions",
        "## A troubleshooting sequence",
    ):
        assert heading in concepts
    answers = drills.split("**Answer:**")[1:]
    assert len(answers) >= 12
    assert all("```python" in answer for answer in answers)
    assert "locker_fee" in notes


def test_databases_and_sql_topic_exposes_drills() -> None:
    tech = _coding_problems_tech()
    topic = next(item for item in tech["topics"] if item["dir"] == "04_Databases_and_SQL")

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"

    topic_dir = Path(__file__).resolve().parent.parent / "content" / "11_Coding_Problems" / "04_Databases_and_SQL"
    concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
    drills = (topic_dir / "drills.md").read_text(encoding="utf-8")
    notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
    for heading in (
        "## Explicit and implicit joins",
        "## Inner, left, and full joins",
        "## Self joins and anti-joins",
        "## SELECT, INSERT, UPDATE, DELETE",
        "## WHERE, GROUP BY, and HAVING",
        "## NULL",
        "## Subqueries and CTEs",
        "## Window functions",
        "## First through third normal form",
        "## Keys and constraints",
        "## Indexes",
        "## Transactions, ACID, and isolation",
        "## When to denormalize",
        "## Handle ambiguity",
        "## Core tables, relationships, and actions",
        "## Large database design",
    ):
        assert heading in concepts
    answers = drills.split("**Answer:**")[1:]
    assert len(answers) >= 12
    assert all("```sql" in answer for answer in answers)
    assert "potters" in notes


def test_coding_problems_scaffolds_render_without_drills() -> None:
    tech = _coding_problems_tech()
    root = Path(__file__).resolve().parent.parent / "content" / "11_Coding_Problems"
    finished = {
        "01_Math_and_Logic_Puzzles",
        "02_Object-Oriented_Design",
        "03_Testing",
        "04_Databases_and_SQL",
    }
    scaffolds = [item for item in tech["topics"] if item["dir"] not in finished]

    assert [item["dir"] for item in scaffolds] == list(CODING_PROBLEMS_TOPICS[4:])
    for topic in scaffolds:
        assert topic["hasDrills"] is False
        assert topic["hasConcepts"] is True
        assert topic["notesFile"] == "notes.md"
        topic_dir = root / topic["dir"]
        assert not (topic_dir / "drills.md").exists()
        concepts = (topic_dir / "concepts.md").read_text(encoding="utf-8")
        notes = (topic_dir / "notes.md").read_text(encoding="utf-8")
        assert concepts.startswith("## ")
        assert concepts.count("\n## ") >= 5
        assert notes.startswith("# ")
        assert "## Key Points" in notes
        assert "## Example" in notes


def test_arrays_strings_hash_tables_topic_exposes_drills() -> None:
    index = serve_module.build_content_index()
    topic = next(
        item
        for tech in index["technologies"]
        if tech["dir"] == "07_Data_Structures_and_Algorithms"
        for item in tech["topics"]
        if item["dir"] == "02_Arrays_Strings_and_Hash_Tables"
    )

    assert topic["hasDrills"] is True
    assert topic["hasConcepts"] is True
    assert topic["notesFile"] == "notes.md"


def test_resolve_under_allows_paths_within_root(tmp_path: Path) -> None:
    root = tmp_path / "content"
    nested_file = root / "topic" / "notes.md"
    nested_file.parent.mkdir(parents=True)
    nested_file.write_text("hello", encoding="utf-8")

    resolved = serve_module.resolve_under(root, "topic/notes.md")

    assert resolved == nested_file.resolve()


def test_resolve_under_rejects_path_traversal(tmp_path: Path) -> None:
    root = tmp_path / "content"
    root.mkdir()
    outside = tmp_path / "README.md"
    outside.write_text("secret", encoding="utf-8")

    resolved = serve_module.resolve_under(root, "../README.md")

    assert resolved is None


def test_build_health_payload_uses_release_info(monkeypatch) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setattr(
        serve_module,
        "get_release_info",
        lambda: {"tag": "v1.2.3", "commit": "abc123", "short_commit": "abc123", "source": "env"},
    )

    payload = serve_module.build_health_payload()

    assert payload == {
        "status": "ok",
        "release": {
            "tag": "v1.2.3",
            "commit": "abc123",
            "short_commit": "abc123",
            "source": "env",
        },
    }


def test_main_binds_requested_host_and_port(monkeypatch, capsys) -> None:  # type: ignore[no-untyped-def]
    recorded: dict[str, object] = {}

    class FakeServer:
        def __init__(self, address, handler):  # type: ignore[no-untyped-def]
            recorded["address"] = address
            recorded["handler"] = handler
            self.daemon_threads = False

        def serve_forever(self) -> None:
            raise KeyboardInterrupt()

        def shutdown(self) -> None:
            recorded["shutdown"] = True

    monkeypatch.setattr(
        serve_module.argparse.ArgumentParser,
        "parse_args",
        lambda self: serve_module.argparse.Namespace(host="0.0.0.0", port=9099),
    )
    monkeypatch.setattr(
        serve_module,
        "build_content_index",
        lambda: {"technologies": [{"topics": []}]},
    )
    monkeypatch.setattr(serve_module, "ThreadingHTTPServer", FakeServer)

    serve_module.main()

    captured = capsys.readouterr()
    assert recorded["address"] == ("0.0.0.0", 9099)
    assert recorded["shutdown"] is True
    assert "http://0.0.0.0:9099" in captured.out


def test_send_ok_sets_no_cache_and_skips_body_for_head() -> None:
    handler = serve_module.StudyHandler.__new__(serve_module.StudyHandler)
    recorded: list[tuple[str, str]] = []
    body = b'console.log("study guide");'

    handler.wfile = io.BytesIO()
    handler.send_response = lambda code: recorded.append(("status", str(code)))  # type: ignore[method-assign]
    handler.send_header = lambda key, value: recorded.append((key, value))  # type: ignore[method-assign]
    handler.end_headers = lambda: recorded.append(("end_headers", ""))  # type: ignore[method-assign]

    handler._send_ok(  # type: ignore[attr-defined]
        content_type="application/javascript; charset=utf-8",
        include_body=False,
        body=body,
        cache_control="no-store",
    )

    assert ("status", "200") in recorded
    assert ("Content-Length", str(len(body))) in recorded
    assert ("Cache-Control", "no-store") in recorded
    assert ("Pragma", "no-cache") in recorded
    assert ("Expires", "0") in recorded
    assert handler.wfile.getvalue() == b""


def test_send_ok_sets_cors_for_content_api() -> None:
    handler = serve_module.StudyHandler.__new__(serve_module.StudyHandler)
    recorded: list[tuple[str, str]] = []
    body = b"{}"

    handler.wfile = io.BytesIO()
    handler.send_response = lambda code: recorded.append(("status", str(code)))  # type: ignore[method-assign]
    handler.send_header = lambda key, value: recorded.append((key, value))  # type: ignore[method-assign]
    handler.end_headers = lambda: None  # type: ignore[method-assign]

    handler._send_ok(  # type: ignore[attr-defined]
        content_type="application/json",
        include_body=True,
        body=body,
        allow_cors=True,
        cache_control="no-store",
    )

    assert ("Access-Control-Allow-Origin", "*") in recorded
    assert handler.wfile.getvalue() == body
