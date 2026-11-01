"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const {
  buildSession,
  computeRollups,
  grade,
  matchesFilter,
  mergeProgress,
  parseRoute,
  selectQuestions,
  shuffle,
  techGroups,
  unitKey,
  weakConcepts,
} = require("../../site/quiz.js");

function question(key, lesson, concept, answer, quiz = "set-a") {
  const [techDir] = key.split("/");
  return {
    key,
    quizKey: `${techDir}/${quiz}`,
    quizId: quiz,
    quizTitle: quiz.toUpperCase(),
    techDir,
    techNum: Number(techDir.slice(0, 2)),
    techTitle: techDir,
    topicDir: lesson,
    topicTitle: lesson,
    conceptSlug: concept,
    conceptTitle: concept,
    conceptRoute: `${techDir}/${lesson}/concepts/${concept}`,
    choices: [{ id: "a" }, { id: "b" }, { id: "c" }],
    answer,
  };
}

const QUESTIONS = [
  question("01_CH/q1", "01_L", "policy", ["a"]),
  question("01_CH/q2", "01_L", "policy", ["a", "b"]),
  question("01_CH/q3", "02_L", "deny", ["c"], "set-b"),
  question("02_CH/q1", "01_L", "vpc", ["b"]),
];
const BY_KEY = Object.fromEntries(QUESTIONS.map((q) => [q.key, q]));

function seeded(seed) {
  let value = seed;
  return () => {
    value = (value * 16807) % 2147483647;
    return (value - 1) / 2147483646;
  };
}

test("grade requires the exact answer set, regardless of order", () => {
  assert.equal(grade(BY_KEY["01_CH/q2"], ["b", "a"]), true);
  assert.equal(grade(BY_KEY["01_CH/q2"], ["a"]), false);
  assert.equal(grade(BY_KEY["01_CH/q2"], ["a", "b", "c"]), false);
  assert.equal(grade(BY_KEY["01_CH/q1"], ["b"]), false);
});

test("pending outbox attempts merge on top of server progress", () => {
  const server = {
    questions: { "01_CH/q1": { attempts: 1, correct: 0, wrong: 1, lastCorrect: false, lastAnsweredAt: "2026-09-28T10:00:00.000000Z", flagged: false } },
    flags: {},
  };
  const pending = [
    { attemptId: "p2", questionKey: "01_CH/q1", selected: ["a"], answeredAt: "2026-09-28T11:00:00.000Z" },
    { attemptId: "p1", questionKey: "01_CH/q3", selected: ["a"], answeredAt: "2026-09-28T10:30:00.000Z" },
    { attemptId: "gone", questionKey: "09_CH/removed", selected: ["a"], answeredAt: "2026-09-28T10:30:00.000Z" },
  ];

  const stats = mergeProgress(server, pending, [], BY_KEY);

  assert.deepEqual(stats["01_CH/q1"], {
    attempts: 2,
    correct: 1,
    wrong: 1,
    lastCorrect: true,
    lastAnsweredAt: "2026-09-28T11:00:00.000Z",
    flagged: false,
  });
  assert.equal(stats["01_CH/q3"].wrong, 1);
  assert.equal(stats["09_CH/removed"], undefined);
});

test("an older pending attempt does not replace the latest result", () => {
  const server = {
    questions: { "01_CH/q1": { attempts: 1, correct: 1, wrong: 0, lastCorrect: true, lastAnsweredAt: "2026-09-28T12:00:00.000000Z" } },
  };
  const stats = mergeProgress(server, [{ questionKey: "01_CH/q1", selected: ["b"], answeredAt: "2026-09-28T09:00:00.000Z" }], [], BY_KEY);
  assert.equal(stats["01_CH/q1"].lastCorrect, true);
  assert.equal(stats["01_CH/q1"].wrong, 1);
});

test("pending flags win only when newer than the server copy", () => {
  const server = {
    questions: { "01_CH/q1": { attempts: 0, correct: 0, wrong: 0, flagged: true } },
    flags: {
      "01_CH/q1": { flagged: true, updatedAt: "2026-09-28T10:00:00.000000Z" },
      "01_CH/q2": { flagged: true, updatedAt: "2026-09-28T12:00:00.000000Z" },
    },
  };
  const pending = [
    { questionKey: "01_CH/q1", flagged: false, updatedAt: "2026-09-28T11:00:00.000Z" },
    { questionKey: "01_CH/q2", flagged: false, updatedAt: "2026-09-28T11:00:00.000Z" },
    { questionKey: "01_CH/q3", flagged: true, updatedAt: "2026-09-28T11:00:00.000Z" },
    { questionKey: "nope/q", flagged: true, updatedAt: "2026-09-28T11:00:00.000Z" },
  ];
  const stats = mergeProgress(server, [], pending, BY_KEY);
  assert.equal(stats["01_CH/q1"].flagged, false);
  assert.equal(stats["01_CH/q2"], undefined);
  assert.equal(stats["01_CH/q3"].flagged, true);
  assert.equal(stats["nope/q"], undefined);
  assert.deepEqual(mergeProgress(null, null, null, BY_KEY), {});
});

test("roll-ups match the server algorithm (see test_quiz_store.py)", () => {
  const stats = mergeProgress(
    { questions: {}, flags: {} },
    [
      { questionKey: "01_CH/q1", selected: ["b"], answeredAt: "2026-09-28T10:01:00Z" },
      { questionKey: "01_CH/q1", selected: ["a"], answeredAt: "2026-09-28T10:02:00Z" },
      { questionKey: "01_CH/q2", selected: ["a", "b"], answeredAt: "2026-09-28T10:03:00Z" },
      { questionKey: "01_CH/q2", selected: ["a"], answeredAt: "2026-09-28T10:04:00Z" },
      { questionKey: "01_CH/q3", selected: ["a"], answeredAt: "2026-09-28T10:05:00Z" },
    ],
    [{ questionKey: "02_CH/q1", flagged: true, updatedAt: "2026-09-28T11:00:00Z" }],
    BY_KEY
  );

  const rollups = computeRollups(QUESTIONS, stats);

  const policy = rollups.concepts.find((c) => c.conceptSlug === "policy");
  assert.equal(policy.questions, 2);
  assert.equal(policy.attempted, 2);
  assert.equal(policy.attempts, 4);
  assert.equal(policy.accuracy, 0.5);
  assert.equal(policy.lastCorrect, 1);
  const techs = Object.fromEntries(rollups.technologies.map((c) => [c.techDir, c]));
  assert.equal(techs["01_CH"].accuracy, 0.4);
  assert.equal(techs["02_CH"].accuracy, null);
  assert.equal(techs["02_CH"].flagged, 1);
  const quizzes = Object.fromEntries(rollups.quizzes.map((q) => [q.quizKey, q]));
  assert.deepEqual(Object.keys(quizzes).sort(), ["01_CH/set-a", "01_CH/set-b", "02_CH/set-a"]);
  assert.equal(quizzes["01_CH/set-a"].attempts, 4);
  assert.equal(quizzes["01_CH/set-b"].accuracy, 0);
  assert.deepEqual(rollups.totals, {
    questions: 4,
    attempted: 3,
    attempts: 5,
    correct: 2,
    wrong: 3,
    flagged: 1,
    lastCorrect: 1,
    accuracy: 0.4,
  });

  const weak = weakConcepts(rollups.concepts);
  assert.deepEqual(
    weak.map((c) => c.conceptSlug),
    ["deny", "policy"]
  );
});

test("filters select unanswered, wrong, wrong-last and flagged questions", () => {
  assert.equal(matchesFilter(undefined, "unanswered"), true);
  assert.equal(matchesFilter({ attempts: 1, wrong: 1, lastCorrect: true }, "wrong"), true);
  assert.equal(matchesFilter({ attempts: 1, wrong: 1, lastCorrect: true }, "wrong-last"), false);
  assert.equal(matchesFilter({ attempts: 0, flagged: true }, "flagged"), true);
  assert.equal(matchesFilter(undefined, "all"), true);

  const stats = { "01_CH/q1": { attempts: 1, wrong: 1, lastCorrect: false, flagged: true } };
  assert.deepEqual(
    selectQuestions(QUESTIONS, stats, { units: ["01_CH/set-a/01_L"], filter: "all" }).map((q) => q.key),
    ["01_CH/q1", "01_CH/q2"]
  );
  assert.deepEqual(
    selectQuestions(QUESTIONS, stats, { units: null, filter: "flagged" }).map((q) => q.key),
    ["01_CH/q1"]
  );
  assert.deepEqual(
    selectQuestions(QUESTIONS, stats, { units: null, concept: "01_CH/02_L/concepts/deny", filter: "unanswered" }).map(
      (q) => q.key
    ),
    ["01_CH/q3"]
  );
});

test("sessions honour limit and shuffle options", () => {
  const ordered = buildSession(QUESTIONS, { shuffleQuestions: false, shuffleChoices: false, limit: 2 });
  assert.deepEqual(ordered.keys, ["01_CH/q1", "01_CH/q2"]);
  assert.deepEqual(ordered.choiceOrder["01_CH/q1"], ["a", "b", "c"]);
  assert.equal(ordered.index, 0);
  assert.deepEqual(ordered.answers, {});
  assert.ok(ordered.id);

  const shuffled = buildSession(QUESTIONS, {}, seeded(7));
  assert.equal(shuffled.keys.length, 4);
  assert.deepEqual([...shuffled.keys].sort(), QUESTIONS.map((q) => q.key).sort());
  assert.deepEqual([...shuffled.choiceOrder["01_CH/q3"]].sort(), ["a", "b", "c"]);
  assert.deepEqual(shuffle([1, 2, 3, 4, 5], seeded(3)).sort(), [1, 2, 3, 4, 5]);
});

test("routes parse quiz views and presets", () => {
  assert.deepEqual(parseRoute("#_quiz"), { view: "builder", params: {} });
  assert.deepEqual(parseRoute("#_quiz/run"), { view: "run", params: {} });
  assert.deepEqual(parseRoute("#_quiz?concept=01_CH%2F01_L%2Fconcepts%2Fpolicy&filter=wrong"), {
    view: "builder",
    params: { concept: "01_CH/01_L/concepts/policy", filter: "wrong" },
  });
  assert.equal(parseRoute("#01_CH/01_L"), null);
});

test("techGroups nests technologies, quiz sets and topic units", () => {
  const groups = techGroups(QUESTIONS, [{ key: "01_CH/set-a", description: "First set" }]);
  assert.deepEqual(
    groups.map((tech) => [tech.dir, tech.quizzes.map((quiz) => quiz.key)]),
    [
      ["01_CH", ["01_CH/set-a", "01_CH/set-b"]],
      ["02_CH", ["02_CH/set-a"]],
    ]
  );
  const first = groups[0];
  assert.equal(first.quizzes[0].description, "First set");
  assert.equal(first.quizzes[1].description, "");
  assert.deepEqual(first.quizzes[0].units.map((unit) => [unit.key, unit.questions.length]), [["01_CH/set-a/01_L", 2]]);
  assert.deepEqual(first.units.map((unit) => unit.key), ["01_CH/set-a/01_L", "01_CH/set-b/02_L"]);
  assert.equal(unitKey(QUESTIONS[2]), "01_CH/set-b/02_L");
});
