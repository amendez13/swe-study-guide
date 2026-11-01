/* Central quiz (issue #72, ported from aws-sa-course #79): concept-linked
 * multiple-choice questions with server-side history, weak-spot roll-ups,
 * flags, and an IndexedDB outbox. A technology can hold many quiz sets.
 *
 * Pure logic (filtering, grading, merging, roll-ups) is exported for
 * node:test; the UI mounts on window.SweStudyQuiz and is driven by app.js.
 */
(() => {
  "use strict";

  const SESSION_KEY = "swe-study-guide-quiz-session";
  const BUILDER_KEY = "swe-study-guide-quiz-builder";
  const OUTBOX_DB = "swe-study-guide-quiz-v1";
  const OUTBOX_VERSION = 1;
  const MAX_BATCH = 200;
  const FILTERS = [
    { id: "all", label: "All questions" },
    { id: "unanswered", label: "Unanswered" },
    { id: "wrong", label: "Previously wrong" },
    { id: "wrong-last", label: "Wrong last time" },
    { id: "flagged", label: "Flagged" },
  ];

  // ── Pure logic ─────────────────────────────────────────────

  function grade(question, selected) {
    const want = new Set(question.answer);
    const got = new Set(selected);
    if (want.size !== got.size) return false;
    for (const id of got) if (!want.has(id)) return false;
    return true;
  }

  function emptyStats() {
    return { attempts: 0, correct: 0, wrong: 0, lastCorrect: null, lastAnsweredAt: null, flagged: false };
  }

  /** Server progress + pending outbox items → per-question stats and flags. */
  function mergeProgress(serverProgress, pendingAttempts, pendingFlags, questionsByKey) {
    const stats = {};
    const server = (serverProgress && serverProgress.questions) || {};
    for (const [key, value] of Object.entries(server)) {
      if (questionsByKey[key]) stats[key] = { ...emptyStats(), ...value };
    }
    const sortedAttempts = [...(pendingAttempts || [])].sort((a, b) =>
      String(a.answeredAt).localeCompare(String(b.answeredAt))
    );
    for (const attempt of sortedAttempts) {
      const question = questionsByKey[attempt.questionKey];
      if (!question) continue;
      const entry = (stats[attempt.questionKey] = stats[attempt.questionKey] || emptyStats());
      const correct = grade(question, attempt.selected);
      entry.attempts += 1;
      if (correct) entry.correct += 1;
      else entry.wrong += 1;
      if (!entry.lastAnsweredAt || String(attempt.answeredAt) >= String(entry.lastAnsweredAt)) {
        entry.lastCorrect = correct;
        entry.lastAnsweredAt = attempt.answeredAt;
      }
    }
    const serverFlags = (serverProgress && serverProgress.flags) || {};
    for (const flag of pendingFlags || []) {
      if (!questionsByKey[flag.questionKey]) continue;
      const known = serverFlags[flag.questionKey];
      if (known && String(known.updatedAt) > String(flag.updatedAt)) continue;
      const entry = (stats[flag.questionKey] = stats[flag.questionKey] || emptyStats());
      entry.flagged = Boolean(flag.flagged);
    }
    return stats;
  }

  function ratio(correct, attempts) {
    return attempts ? Math.round((correct / attempts) * 10000) / 10000 : null;
  }

  /** Same roll-up algorithm as QuizStore.progress on the server. */
  function computeRollups(questions, stats) {
    const concepts = new Map();
    const technologies = new Map();
    const quizzes = new Map();
    const blank = () => ({ questions: 0, attempted: 0, attempts: 0, correct: 0, wrong: 0, flagged: 0, lastCorrect: 0 });
    const totals = blank();
    for (const question of questions) {
      const s = stats[question.key];
      const conceptKey = `${question.techDir}/${question.topicDir}/${question.conceptSlug}`;
      if (!concepts.has(conceptKey)) {
        concepts.set(conceptKey, {
          techDir: question.techDir,
          techTitle: question.techTitle,
          topicDir: question.topicDir,
          topicTitle: question.topicTitle,
          conceptSlug: question.conceptSlug,
          conceptTitle: question.conceptTitle,
          conceptRoute: question.conceptRoute,
          ...blank(),
        });
      }
      if (!technologies.has(question.techDir)) {
        technologies.set(question.techDir, {
          techDir: question.techDir,
          techNum: question.techNum,
          techTitle: question.techTitle,
          ...blank(),
        });
      }
      if (!quizzes.has(question.quizKey)) {
        quizzes.set(question.quizKey, {
          quizKey: question.quizKey,
          quizId: question.quizId,
          quizTitle: question.quizTitle,
          techDir: question.techDir,
          techTitle: question.techTitle,
          ...blank(),
        });
      }
      const buckets = [concepts.get(conceptKey), technologies.get(question.techDir), quizzes.get(question.quizKey), totals];
      for (const bucket of buckets) {
        bucket.questions += 1;
        if (!s) continue;
        bucket.attempts += s.attempts;
        bucket.correct += s.correct;
        bucket.wrong += s.wrong;
        if (s.attempts) bucket.attempted += 1;
        if (s.flagged) bucket.flagged += 1;
        if (s.lastCorrect) bucket.lastCorrect += 1;
      }
    }
    for (const bucket of [...concepts.values(), ...technologies.values(), ...quizzes.values(), totals]) {
      bucket.accuracy = ratio(bucket.correct, bucket.attempts);
    }
    return {
      concepts: [...concepts.values()],
      technologies: [...technologies.values()],
      quizzes: [...quizzes.values()],
      totals,
    };
  }

  function weakConcepts(concepts) {
    return concepts
      .filter((concept) => concept.attempts > 0)
      .sort(
        (a, b) =>
          a.accuracy - b.accuracy ||
          b.wrong - a.wrong ||
          a.conceptTitle.localeCompare(b.conceptTitle)
      );
  }

  function matchesFilter(stat, filter) {
    const s = stat || emptyStats();
    if (filter === "unanswered") return s.attempts === 0;
    if (filter === "wrong") return s.wrong > 0;
    if (filter === "wrong-last") return s.lastCorrect === false;
    if (filter === "flagged") return Boolean(s.flagged);
    return true;
  }

  /** A builder selection unit: one topic inside one quiz set. */
  function unitKey(question) {
    return `${question.quizKey}/${question.topicDir}`;
  }

  /** criteria: { units: ["tech/quiz/topic", ...] | null, concept, filter } */
  function selectQuestions(questions, stats, criteria) {
    const units = criteria.units ? new Set(criteria.units) : null;
    return questions.filter((question) => {
      if (units && !units.has(unitKey(question))) return false;
      if (criteria.concept && question.conceptRoute !== criteria.concept) return false;
      return matchesFilter(stats[question.key], criteria.filter || "all");
    });
  }

  function shuffle(items, random = Math.random) {
    const copy = [...items];
    for (let i = copy.length - 1; i > 0; i -= 1) {
      const j = Math.floor(random() * (i + 1));
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  function buildSession(questions, options = {}, random = Math.random) {
    let ordered = options.shuffleQuestions === false ? [...questions] : shuffle(questions, random);
    if (options.limit && options.limit > 0) ordered = ordered.slice(0, options.limit);
    const choiceOrder = {};
    for (const question of ordered) {
      const ids = question.choices.map((choice) => choice.id);
      choiceOrder[question.key] = options.shuffleChoices === false ? ids : shuffle(ids, random);
    }
    return {
      id: newId(),
      keys: ordered.map((question) => question.key),
      choiceOrder,
      index: 0,
      answers: {},
      startedAt: new Date().toISOString(),
      finishedAt: null,
    };
  }

  function parseRoute(hash) {
    const raw = String(hash || "").replace(/^#/, "");
    const [path, query = ""] = raw.split("?");
    const parts = path.split("/").filter(Boolean);
    if (parts[0] !== "_quiz") return null;
    const params = {};
    for (const pair of query.split("&").filter(Boolean)) {
      const [name, value = ""] = pair.split("=");
      params[decodeURIComponent(name)] = decodeURIComponent(value);
    }
    return { view: parts[1] || "builder", params };
  }

  function newId() {
    if (typeof crypto !== "undefined" && crypto.randomUUID) return crypto.randomUUID();
    return `id-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 12)}`;
  }

  function formatPercent(value) {
    return value === null || value === undefined ? "—" : `${Math.round(value * 100)}%`;
  }

  // ── Outbox (IndexedDB) ─────────────────────────────────────

  let dbPromise = null;

  function openOutbox() {
    if (typeof indexedDB === "undefined") return Promise.resolve(null);
    if (!dbPromise) {
      dbPromise = new Promise((resolve) => {
        let request;
        try {
          request = indexedDB.open(OUTBOX_DB, OUTBOX_VERSION);
        } catch (_error) {
          resolve(null);
          return;
        }
        request.onupgradeneeded = () => {
          const db = request.result;
          if (!db.objectStoreNames.contains("attempts")) db.createObjectStore("attempts", { keyPath: "attemptId" });
          if (!db.objectStoreNames.contains("flags")) db.createObjectStore("flags", { keyPath: "questionKey" });
        };
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => resolve(null);
        request.onblocked = () => resolve(null);
      });
    }
    return dbPromise;
  }

  async function outboxAll(store) {
    const db = await openOutbox();
    if (!db) return memoryOutbox[store].slice();
    return new Promise((resolve, reject) => {
      const request = db.transaction(store, "readonly").objectStore(store).getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  }

  async function outboxPut(store, record) {
    const db = await openOutbox();
    if (!db) {
      const keyName = store === "attempts" ? "attemptId" : "questionKey";
      memoryOutbox[store] = memoryOutbox[store].filter((item) => item[keyName] !== record[keyName]).concat(record);
      return;
    }
    await new Promise((resolve, reject) => {
      const tx = db.transaction(store, "readwrite");
      tx.objectStore(store).put(record);
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error);
    });
  }

  async function outboxDelete(store, keys, onlyIf) {
    if (!keys.length) return;
    const db = await openOutbox();
    const keyName = store === "attempts" ? "attemptId" : "questionKey";
    if (!db) {
      const drop = new Set(keys);
      memoryOutbox[store] = memoryOutbox[store].filter(
        (item) => !(drop.has(item[keyName]) && (!onlyIf || onlyIf(item)))
      );
      return;
    }
    await new Promise((resolve, reject) => {
      const tx = db.transaction(store, "readwrite");
      const objectStore = tx.objectStore(store);
      for (const key of keys) {
        if (!onlyIf) {
          objectStore.delete(key);
          continue;
        }
        const read = objectStore.get(key);
        read.onsuccess = () => {
          if (read.result && onlyIf(read.result)) objectStore.delete(key);
        };
      }
      tx.oncomplete = () => resolve();
      tx.onerror = () => reject(tx.error);
      tx.onabort = () => reject(tx.error);
    });
  }

  // Fallback when IndexedDB is unavailable (private windows): pending items
  // survive only while the page stays open.
  const memoryOutbox = { attempts: [], flags: [] };

  // ── UI state ───────────────────────────────────────────────

  const state = {
    ctx: null,
    bank: null,
    questionsByKey: {},
    serverProgress: null,
    pendingAttempts: [],
    pendingFlags: [],
    stats: {},
    loadError: "",
    notices: [],
    flushing: null,
    flushAgain: false,
    outboxPersistent: true,
  };

  function storageGet(storage, key) {
    try {
      const raw = storage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    } catch (_error) {
      return null;
    }
  }

  function storageSet(storage, key, value) {
    try {
      if (value === null) storage.removeItem(key);
      else storage.setItem(key, JSON.stringify(value));
    } catch (_error) {
      /* storage unavailable: the session just won't survive a reload */
    }
  }

  const loadSession = () => storageGet(sessionStorage, SESSION_KEY);
  const saveSession = (session) => storageSet(sessionStorage, SESSION_KEY, session);

  async function fetchJson(url, options) {
    const response = await fetch(url, options);
    if (!response.ok) {
      const error = new Error(`HTTP ${response.status}`);
      error.status = response.status;
      throw error;
    }
    return response.json();
  }

  async function loadBank() {
    try {
      state.bank = await fetchJson("/api/quiz/questions");
      state.questionsByKey = Object.fromEntries(state.bank.questions.map((question) => [question.key, question]));
      state.loadError = "";
    } catch (_error) {
      if (!state.bank) state.loadError = "Quiz questions are unavailable. Check that the study site is reachable and reload.";
    }
  }

  async function refreshPending() {
    try {
      state.pendingAttempts = await outboxAll("attempts");
      state.pendingFlags = await outboxAll("flags");
    } catch (_error) {
      state.pendingAttempts = memoryOutbox.attempts.slice();
      state.pendingFlags = memoryOutbox.flags.slice();
    }
    state.outboxPersistent = Boolean(await openOutbox());
    recomputeStats();
  }

  function recomputeStats() {
    state.stats = mergeProgress(state.serverProgress, state.pendingAttempts, state.pendingFlags, state.questionsByKey);
  }

  async function loadProgress() {
    try {
      state.serverProgress = await fetchJson("/api/quiz/progress");
    } catch (_error) {
      /* keep the last known progress; pending items still merge on top */
    }
    await refreshPending();
  }

  function isReachable() {
    return typeof navigator === "undefined" || navigator.onLine !== false;
  }

  /** Send queued writes. Items leave the outbox only after the server answers for them. */
  function flushOutbox() {
    if (state.flushing) {
      // Items queued during an in-flight flush are sent by one follow-up pass.
      state.flushAgain = true;
      return state.flushing;
    }
    state.flushing = (async () => {
      let sent = false;
      try {
        const attempts = await outboxAll("attempts");
        for (let i = 0; i < attempts.length; i += MAX_BATCH) {
          const batch = attempts.slice(i, i + MAX_BATCH);
          const result = await postBatch("/api/quiz/attempts", "POST", {
            attempts: batch.map(({ attemptId, questionKey, selected, sessionId, answeredAt }) => ({
              attemptId,
              questionKey,
              selected,
              sessionId,
              answeredAt,
            })),
          });
          if (!result) break;
          sent = true;
          const settled = result.all
            ? batch.map((item) => item.attemptId)
            : [...result.body.accepted, ...result.body.rejected].map((item) => item.attemptId);
          for (const item of (result.body && result.body.rejected) || []) {
            state.notices.push(`An answer could not be saved (${item.reason}) and was discarded.`);
          }
          await outboxDelete("attempts", settled);
        }
        const flags = await outboxAll("flags");
        for (let i = 0; i < flags.length; i += MAX_BATCH) {
          const batch = flags.slice(i, i + MAX_BATCH);
          const result = await postBatch("/api/quiz/flags", "PUT", { flags: batch });
          if (!result) break;
          sent = true;
          const sentAt = Object.fromEntries(batch.map((flag) => [flag.questionKey, flag.updatedAt]));
          const settled = result.all
            ? batch.map((flag) => flag.questionKey)
            : [...result.body.flags, ...result.body.rejected].map((item) => item.questionKey);
          // A newer toggle queued while this request was in flight must survive.
          await outboxDelete("flags", settled, (stored) => stored.updatedAt === sentAt[stored.questionKey]);
        }
      } catch (_error) {
        /* outbox unreadable: nothing to do until next time */
      }
      if (sent) await loadProgress();
      else await refreshPending();
      return sent;
    })().finally(() => {
      state.flushing = null;
      if (state.flushAgain) {
        state.flushAgain = false;
        flushOutbox().then(updateSyncBadges);
      }
    });
    return state.flushing;
  }

  /** Returns {body} on success, {all:true} when the batch can never succeed, or null to retry later. */
  async function postBatch(url, method, payload) {
    let response;
    try {
      response = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } catch (_error) {
      return null;
    }
    if (response.ok) return { body: await response.json() };
    if (response.status === 400) {
      state.notices.push("Some queued quiz data was malformed and was discarded.");
      return { all: true, body: null };
    }
    return null;
  }

  async function recordAnswer(question, selected, session) {
    const attempt = {
      attemptId: newId(),
      questionKey: question.key,
      selected: [...selected].sort(),
      sessionId: session.id,
      answeredAt: new Date().toISOString(),
    };
    try {
      await outboxPut("attempts", attempt);
    } catch (_error) {
      memoryOutbox.attempts.push(attempt);
    }
    state.pendingAttempts.push(attempt);
    recomputeStats();
    flushOutbox().then(updateSyncBadges);
    return attempt;
  }

  async function setFlag(questionKey, flagged) {
    const record = { questionKey, flagged, updatedAt: new Date().toISOString() };
    try {
      await outboxPut("flags", record);
    } catch (_error) {
      memoryOutbox.flags.push(record);
    }
    state.pendingFlags = state.pendingFlags.filter((flag) => flag.questionKey !== questionKey).concat(record);
    recomputeStats();
    flushOutbox().then(updateSyncBadges);
  }

  // ── Rendering helpers ──────────────────────────────────────

  function esc(value) {
    return state.ctx.esc(String(value === null || value === undefined ? "" : value));
  }

  function md(text) {
    return state.ctx.renderMarkdown(String(text || ""));
  }

  function inlineMd(text) {
    return md(text).replace(/^<p>([\s\S]*)<\/p>\s*$/, "$1");
  }

  function syncBadge() {
    const pending = state.pendingAttempts.length + state.pendingFlags.length;
    const parts = [];
    if (pending) parts.push(`<span class="quiz-sync-pending">${pending} change${pending === 1 ? "" : "s"} waiting to sync</span>`);
    if (!state.outboxPersistent) parts.push('<span class="quiz-sync-warning">Offline answers will not be kept in this browser mode.</span>');
    for (const notice of state.notices.splice(0)) parts.push(`<span class="quiz-sync-warning">${esc(notice)}</span>`);
    return parts.join("");
  }

  function updateSyncBadges() {
    document.querySelectorAll("[data-quiz-sync]").forEach((el) => {
      el.innerHTML = syncBadge();
    });
  }

  function header(view) {
    const crumbs = [`<a href="#" data-quiz-home>Home</a>`, '<span class="sep">/</span>'];
    if (view === "builder") crumbs.push("<span>Quiz</span>");
    else crumbs.push('<a href="#_quiz">Quiz</a>', '<span class="sep">/</span>', `<span>${view === "run" ? "Session" : "Progress"}</span>`);
    return crumbs.join("");
  }

  function openConcept(route, event) {
    if (event) event.preventDefault();
    history.pushState({ quizReturn: true }, "", `#${route}`);
    state.ctx.handleRoute();
  }

  function conceptLink(question, label) {
    return `<a class="quiz-concept-link" href="#${esc(question.conceptRoute)}" data-concept-route="${esc(question.conceptRoute)}">${label}</a>`;
  }

  function bindConceptLinks(root) {
    root.querySelectorAll("[data-concept-route]").forEach((link) => {
      link.addEventListener("click", (event) => openConcept(link.dataset.conceptRoute, event));
    });
  }

  /** questions → technologies → quiz sets → topics (each topic is a selection unit). */
  function techGroups(questions, quizzes) {
    const quizMeta = Object.fromEntries((quizzes || []).map((quiz) => [quiz.key, quiz]));
    const techs = new Map();
    for (const question of questions) {
      if (!techs.has(question.techDir)) {
        techs.set(question.techDir, {
          dir: question.techDir,
          num: question.techNum,
          title: question.techTitle,
          quizzes: new Map(),
        });
      }
      const tech = techs.get(question.techDir);
      if (!tech.quizzes.has(question.quizKey)) {
        const meta = quizMeta[question.quizKey] || {};
        tech.quizzes.set(question.quizKey, {
          key: question.quizKey,
          id: question.quizId,
          title: question.quizTitle,
          description: meta.description || "",
          units: new Map(),
        });
      }
      const quiz = tech.quizzes.get(question.quizKey);
      const key = unitKey(question);
      if (!quiz.units.has(key)) {
        quiz.units.set(key, {
          key,
          dir: question.topicDir,
          num: question.topicNum,
          title: question.topicTitle,
          questions: [],
        });
      }
      quiz.units.get(key).questions.push(question);
    }
    return [...techs.values()].map((tech) => {
      const quizList = [...tech.quizzes.values()].map((quiz) => ({ ...quiz, units: [...quiz.units.values()] }));
      return { ...tech, quizzes: quizList, units: quizList.flatMap((quiz) => quiz.units) };
    });
  }

  // ── Views ──────────────────────────────────────────────────

  async function render(hash) {
    const route = parseRoute(hash) || { view: "builder", params: {} };
    const container = document.querySelector("#quiz-view");
    const ctx = state.ctx;
    document.querySelector("#breadcrumb").innerHTML = header(route.view);
    document.querySelector("#breadcrumb [data-quiz-home]").addEventListener("click", (event) => {
      event.preventDefault();
      ctx.navigate("");
    });
    document.querySelector("#content-title").textContent = route.view === "progress" ? "Quiz progress" : "Quiz";

    if (!state.bank) container.innerHTML = '<div class="empty-state">Loading quiz…</div>';
    const token = (render.token = (render.token || 0) + 1);
    await loadBank();
    if (isReachable()) await flushOutbox();
    await loadProgress();
    if (token !== render.token) return;

    if (!state.bank) {
      container.innerHTML = `<div class="empty-state">${esc(state.loadError)}</div>`;
      return;
    }
    if (route.view === "run") renderRun(container);
    else if (route.view === "progress") renderProgress(container);
    else renderBuilder(container, route.params);
    ctx.scrollTop();
  }

  function renderIssues() {
    const issues = state.bank.issues || [];
    if (!issues.length) return "";
    return `<details class="quiz-issues"><summary>${issues.length} quiz question${issues.length === 1 ? "" : "s"} skipped because of content errors</summary><ul>${issues
      .map((issue) => `<li><code>${esc(issue.file)}</code> ${esc(issue.question)}: ${esc(issue.message)}</li>`)
      .join("")}</ul></details>`;
  }

  function renderBuilder(container, params) {
    const questions = state.bank.questions;
    const techs = techGroups(questions, state.bank.quizzes);
    const saved = storageGet(localStorage, BUILDER_KEY) || {};
    const preset = params.concept || params.technology || params.quiz || params.filter;
    const activeSession = loadSession();

    const selectedUnits = new Set();
    let concept = params.concept || "";
    if (params.concept) {
      const matches = questions.filter((question) => question.conceptRoute === params.concept);
      if (matches.length) matches.forEach((question) => selectedUnits.add(unitKey(question)));
      else concept = "";
    } else if (params.quiz) {
      techs.forEach((tech) =>
        tech.quizzes
          .filter((quiz) => quiz.key === params.quiz)
          .forEach((quiz) => quiz.units.forEach((unit) => selectedUnits.add(unit.key)))
      );
    } else if (params.technology) {
      const tech = techs.find((item) => item.dir === params.technology);
      if (tech) tech.units.forEach((unit) => selectedUnits.add(unit.key));
    } else if (params.filter) {
      techs.forEach((tech) => tech.units.forEach((unit) => selectedUnits.add(unit.key)));
    } else if (!preset && Array.isArray(saved.units)) {
      saved.units.forEach((key) => selectedUnits.add(key));
    }
    const conceptQuestion = concept ? questions.find((question) => question.conceptRoute === concept) : null;
    const filter = FILTERS.some((item) => item.id === params.filter)
      ? params.filter
      : !preset && saved.filter
      ? saved.filter
      : "all";

    if (!questions.length) {
      container.innerHTML = `<div class="empty-state">No quiz questions have been written yet.</div>${renderIssues()}`;
      return;
    }

    const attemptedIn = (list) => list.filter((q) => (state.stats[q.key] || {}).attempts).length;

    container.innerHTML = `
      <section class="quiz-panel">
        <div class="quiz-toolbar">
          <p class="quiz-intro">Pick technologies, quiz sets or individual topics, choose which questions to include, then start. Each question links to the concept card it tests.</p>
          <div class="quiz-toolbar-actions">
            <a class="quiz-button quiz-button-secondary" href="#_quiz/progress">View progress</a>
            ${
              activeSession && !activeSession.finishedAt
                ? `<a class="quiz-button quiz-button-secondary" href="#_quiz/run">Resume session (${activeSession.index + 1}/${activeSession.keys.length})</a>`
                : ""
            }
          </div>
        </div>
        <div class="quiz-sync" data-quiz-sync>${syncBadge()}</div>
        ${renderIssues()}
        ${
          conceptQuestion
            ? `<div class="quiz-concept-filter">Practising one concept: <strong>${esc(conceptQuestion.conceptTitle)}</strong> <button type="button" class="quiz-link-button" id="quiz-clear-concept">Show all topics</button></div>`
            : ""
        }
        <div class="quiz-builder-controls">
          <button type="button" class="quiz-chip" id="quiz-select-all">Select all</button>
          <button type="button" class="quiz-chip" id="quiz-clear">Clear</button>
          <button type="button" class="quiz-chip" id="quiz-all-flagged">All flagged questions</button>
        </div>
        <div class="quiz-chapters" id="quiz-chapters">
          ${techs
            .map((tech) => {
              const techQuestions = tech.units.flatMap((unit) => unit.questions);
              return `
                <details class="quiz-chapter" data-tech="${esc(tech.dir)}">
                  <summary>
                    <input type="checkbox" class="quiz-chapter-check" aria-label="Select technology ${esc(tech.title)}">
                    <span class="quiz-chapter-num">${esc(tech.num)}</span>
                    <span class="quiz-chapter-title">${esc(tech.title)}</span>
                    <span class="quiz-chapter-meta">${tech.quizzes.length} quiz${tech.quizzes.length === 1 ? "" : "zes"} · ${techQuestions.length} questions · ${attemptedIn(techQuestions)} attempted</span>
                  </summary>
                  <div class="quiz-sets">
                    ${tech.quizzes
                      .map((quiz) => {
                        const quizQuestions = quiz.units.flatMap((unit) => unit.questions);
                        return `
                          <div class="quiz-set" data-quiz="${esc(quiz.key)}">
                            <label class="quiz-set-header">
                              <input type="checkbox" class="quiz-set-check" aria-label="Select quiz ${esc(quiz.title)}">
                              <span class="quiz-set-title">${esc(quiz.title)}</span>
                              <span class="quiz-lesson-meta">${quizQuestions.length} · ${attemptedIn(quizQuestions)} attempted</span>
                            </label>
                            ${quiz.description ? `<p class="quiz-set-description">${esc(quiz.description)}</p>` : ""}
                            <div class="quiz-lessons">
                              ${quiz.units
                                .map(
                                  (unit) => `
                                    <label class="quiz-lesson">
                                      <input type="checkbox" class="quiz-lesson-check" value="${esc(unit.key)}"${
                                    selectedUnits.has(unit.key) ? " checked" : ""
                                  }>
                                      <span class="quiz-lesson-title">${esc(unit.num)}. ${esc(unit.title)}</span>
                                      <span class="quiz-lesson-meta">${unit.questions.length}</span>
                                    </label>`
                                )
                                .join("")}
                            </div>
                          </div>`;
                      })
                      .join("")}
                  </div>
                </details>`;
            })
            .join("")}
        </div>
        <fieldset class="quiz-filters">
          <legend>Include</legend>
          ${FILTERS.map(
            (item) => `
              <label class="quiz-radio"><input type="radio" name="quiz-filter" value="${item.id}"${
              item.id === filter ? " checked" : ""
            }> ${item.label}</label>`
          ).join("")}
        </fieldset>
        <div class="quiz-options">
          <label><input type="checkbox" id="quiz-shuffle-questions"${saved.shuffleQuestions === false ? "" : " checked"}> Shuffle questions</label>
          <label><input type="checkbox" id="quiz-shuffle-choices"${saved.shuffleChoices === false ? "" : " checked"}> Shuffle answers</label>
          <label>Length
            <select id="quiz-limit">
              ${[10, 20, 0]
                .map(
                  (value) =>
                    `<option value="${value}"${(saved.limit ?? 10) === value ? " selected" : ""}>${value ? `${value} questions` : "All matching"}</option>`
                )
                .join("")}
            </select>
          </label>
        </div>
        <div class="quiz-start-row">
          <button type="button" class="quiz-button" id="quiz-start" disabled>Start quiz</button>
          <span class="quiz-match-count" id="quiz-match-count" aria-live="polite"></span>
        </div>
      </section>`;

    const unitChecks = [...container.querySelectorAll(".quiz-lesson-check")];
    const startBtn = container.querySelector("#quiz-start");
    const countEl = container.querySelector("#quiz-match-count");
    let conceptFilter = concept;

    function criteria() {
      return {
        units: unitChecks.filter((check) => check.checked).map((check) => check.value),
        concept: conceptFilter,
        filter: container.querySelector('input[name="quiz-filter"]:checked').value,
      };
    }

    function syncGroup(groupCheck, scope) {
      const checks = [...scope.querySelectorAll(".quiz-lesson-check")];
      const checked = checks.filter((check) => check.checked).length;
      groupCheck.checked = checks.length > 0 && checked === checks.length;
      groupCheck.indeterminate = checked > 0 && checked < checks.length;
      return checked;
    }

    function syncGroupChecks() {
      container.querySelectorAll(".quiz-set").forEach((set) => syncGroup(set.querySelector(".quiz-set-check"), set));
      container.querySelectorAll(".quiz-chapter").forEach((details) => {
        const checked = syncGroup(details.querySelector(".quiz-chapter-check"), details);
        if (checked > 0 && preset) details.open = true;
      });
    }

    function update() {
      syncGroupChecks();
      const current = criteria();
      const matches = current.units.length ? selectQuestions(questions, state.stats, current) : [];
      const limit = Number(container.querySelector("#quiz-limit").value);
      const count = limit ? Math.min(limit, matches.length) : matches.length;
      countEl.textContent = current.units.length
        ? `${matches.length} matching question${matches.length === 1 ? "" : "s"}${count < matches.length ? ` · ${count} per session` : ""}`
        : "Select at least one quiz or topic";
      startBtn.disabled = matches.length === 0;
      storageSet(localStorage, BUILDER_KEY, {
        units: current.units,
        filter: current.filter,
        shuffleQuestions: container.querySelector("#quiz-shuffle-questions").checked,
        shuffleChoices: container.querySelector("#quiz-shuffle-choices").checked,
        limit,
      });
      return matches;
    }

    container.querySelectorAll(".quiz-chapter-check, .quiz-set-check").forEach((groupCheck) => {
      groupCheck.addEventListener("click", (event) => event.stopPropagation());
      groupCheck.addEventListener("change", () => {
        const scope = groupCheck.closest(groupCheck.classList.contains("quiz-set-check") ? ".quiz-set" : ".quiz-chapter");
        scope.querySelectorAll(".quiz-lesson-check").forEach((unitCheck) => {
          unitCheck.checked = groupCheck.checked;
        });
        update();
      });
    });
    // Bind to the freshly rendered panel, not the long-lived #quiz-view
    // container, so re-rendering never stacks stale listeners.
    container.querySelector(".quiz-panel").addEventListener("change", (event) => {
      const cls = event.target.classList;
      if (!cls.contains("quiz-chapter-check") && !cls.contains("quiz-set-check")) update();
    });
    const setAll = (checked) => {
      unitChecks.forEach((check) => {
        check.checked = checked;
      });
      update();
    };
    container.querySelector("#quiz-select-all").addEventListener("click", () => setAll(true));
    container.querySelector("#quiz-clear").addEventListener("click", () => setAll(false));
    container.querySelector("#quiz-all-flagged").addEventListener("click", () => {
      container.querySelector('input[name="quiz-filter"][value="flagged"]').checked = true;
      setAll(true);
    });
    const clearConcept = container.querySelector("#quiz-clear-concept");
    if (clearConcept) {
      clearConcept.addEventListener("click", () => {
        conceptFilter = "";
        clearConcept.parentElement.remove();
        update();
      });
    }
    startBtn.addEventListener("click", () => {
      const matches = update();
      if (!matches.length) return;
      const session = buildSession(matches, {
        shuffleQuestions: container.querySelector("#quiz-shuffle-questions").checked,
        shuffleChoices: container.querySelector("#quiz-shuffle-choices").checked,
        limit: Number(container.querySelector("#quiz-limit").value),
      });
      saveSession(session);
      state.ctx.navigate("_quiz/run");
    });
    update();
  }

  function renderRun(container) {
    const session = loadSession();
    if (!session) {
      container.innerHTML = `<div class="empty-state">No quiz in progress. <a href="#_quiz">Start a quiz</a></div>`;
      return;
    }
    // Questions removed since the session started are skipped.
    const keys = session.keys.filter((key) => state.questionsByKey[key]);
    if (keys.length !== session.keys.length) {
      session.index = session.keys.slice(0, session.index).filter((key) => state.questionsByKey[key]).length;
      session.keys = keys;
      saveSession(session);
    }
    if (session.index >= keys.length || session.finishedAt) {
      renderSummary(container, session, keys);
      return;
    }
    const key = keys[session.index];
    const question = state.questionsByKey[key];
    const order = (session.choiceOrder[key] || []).filter((id) => question.choices.some((c) => c.id === id));
    const choices = order.length === question.choices.length
      ? order.map((id) => question.choices.find((choice) => choice.id === id))
      : question.choices;
    const answer = session.answers[key];
    const flagged = Boolean((state.stats[key] || {}).flagged);
    const inputType = question.multiple ? "checkbox" : "radio";
    const last = session.index === keys.length - 1;

    container.innerHTML = `
      <section class="quiz-panel quiz-run">
        <div class="quiz-run-header">
          <div class="quiz-run-position">
            <strong>Question ${session.index + 1} / ${keys.length}</strong>
            <span>${esc(question.techTitle)} · ${esc(question.quizTitle)} · ${esc(question.topicTitle)}</span>
            ${question.placeholder ? '<span class="quiz-badge">Placeholder</span>' : ""}
          </div>
          <div class="quiz-run-actions">
            <button type="button" class="quiz-flag${flagged ? " is-flagged" : ""}" id="quiz-flag" aria-pressed="${flagged}">
              ${flagged ? "Flagged" : "Flag"}
            </button>
            <button type="button" class="quiz-link-button" id="quiz-quit">Quit</button>
          </div>
        </div>
        <div class="quiz-progress-bar"><span style="width:${Math.round((session.index / keys.length) * 100)}%"></span></div>
        <div class="quiz-sync" data-quiz-sync>${syncBadge()}</div>
        <div class="quiz-prompt markdown-body">${md(question.prompt)}</div>
        ${question.multiple ? `<p class="quiz-multi-hint">Select all that apply (${question.answer.length})</p>` : ""}
        <form class="quiz-choices" id="quiz-choices">
          ${choices
            .map(
              (choice) => `
                <label class="quiz-choice" data-choice="${esc(choice.id)}">
                  <input type="${inputType}" name="quiz-choice" value="${esc(choice.id)}">
                  <span class="quiz-choice-text">${inlineMd(choice.text)}</span>
                </label>`
            )
            .join("")}
        </form>
        <div class="quiz-feedback" id="quiz-feedback" aria-live="polite"></div>
        <div class="quiz-run-footer">
          <button type="button" class="quiz-button" id="quiz-submit" disabled>Submit answer</button>
          <button type="button" class="quiz-button" id="quiz-next" hidden>${last ? "Finish" : "Next question"}</button>
        </div>
      </section>`;

    const form = container.querySelector("#quiz-choices");
    const submitBtn = container.querySelector("#quiz-submit");
    const nextBtn = container.querySelector("#quiz-next");
    const selectedIds = () => [...form.querySelectorAll("input:checked")].map((input) => input.value);

    function reveal(selected, correct) {
      form.classList.add("is-revealed");
      form.querySelectorAll("input").forEach((input) => {
        input.disabled = true;
        input.checked = selected.includes(input.value);
      });
      form.querySelectorAll(".quiz-choice").forEach((label) => {
        const id = label.dataset.choice;
        const isAnswer = question.answer.includes(id);
        const picked = selected.includes(id);
        label.classList.toggle("is-correct", isAnswer);
        label.classList.toggle("is-wrong", picked && !isAnswer);
        label.classList.toggle("is-missed", isAnswer && !picked);
      });
      container.querySelector("#quiz-feedback").innerHTML = `
        <div class="quiz-result ${correct ? "is-correct" : "is-wrong"}">${correct ? "Correct" : "Incorrect"}</div>
        ${question.explanation ? `<div class="quiz-explanation markdown-body">${md(question.explanation)}</div>` : ""}
        ${conceptLink(question, `Review concept: ${esc(question.conceptTitle)} <span aria-hidden="true">&rarr;</span>`)}`;
      bindConceptLinks(container.querySelector("#quiz-feedback"));
      submitBtn.hidden = true;
      nextBtn.hidden = false;
      nextBtn.focus();
    }

    form.addEventListener("change", () => {
      submitBtn.disabled = selectedIds().length === 0;
    });
    submitBtn.addEventListener("click", async () => {
      const selected = selectedIds();
      if (!selected.length) return;
      submitBtn.disabled = true;
      const correct = grade(question, selected);
      // Persist to the outbox before showing the result, so a reload right
      // after the reveal can never lose the attempt.
      await recordAnswer(question, selected, session);
      session.answers[key] = { selected, correct };
      saveSession(session);
      reveal(selected, correct);
    });
    nextBtn.addEventListener("click", () => {
      session.index += 1;
      if (session.index >= keys.length) session.finishedAt = new Date().toISOString();
      saveSession(session);
      renderRun(container);
      state.ctx.scrollTop();
    });
    container.querySelector("#quiz-flag").addEventListener("click", async (event) => {
      const button = event.currentTarget;
      const next = button.getAttribute("aria-pressed") !== "true";
      button.disabled = true;
      await setFlag(key, next);
      button.disabled = false;
      button.setAttribute("aria-pressed", String(next));
      button.classList.toggle("is-flagged", next);
      button.textContent = next ? "Flagged" : "Flag";
    });
    container.querySelector("#quiz-quit").addEventListener("click", () => {
      saveSession(null);
      state.ctx.navigate("_quiz");
    });
    if (answer) reveal(answer.selected, answer.correct);
  }

  function renderSummary(container, session, keys) {
    const answered = keys.filter((key) => session.answers[key]);
    const correct = answered.filter((key) => session.answers[key].correct);
    const missed = answered.filter((key) => !session.answers[key].correct).map((key) => state.questionsByKey[key]);
    const minutes = session.finishedAt
      ? Math.max(1, Math.round((Date.parse(session.finishedAt) - Date.parse(session.startedAt)) / 60000))
      : null;
    const byTech = new Map();
    for (const key of answered) {
      const question = state.questionsByKey[key];
      const row = byTech.get(question.techDir) || { title: question.techTitle, num: question.techNum, total: 0, correct: 0 };
      row.total += 1;
      if (session.answers[key].correct) row.correct += 1;
      byTech.set(question.techDir, row);
    }

    container.innerHTML = `
      <section class="quiz-panel quiz-summary">
        <div class="quiz-score">
          <strong>${correct.length} / ${answered.length}</strong>
          <span>${formatPercent(ratio(correct.length, answered.length))} correct${minutes ? ` · ${minutes} min` : ""}</span>
        </div>
        <div class="quiz-sync" data-quiz-sync>${syncBadge()}</div>
        <table class="quiz-table">
          <thead><tr><th>Technology</th><th>Score</th></tr></thead>
          <tbody>
            ${[...byTech.values()]
              .map((row) => `<tr><td>${esc(row.num)}. ${esc(row.title)}</td><td>${row.correct} / ${row.total}</td></tr>`)
              .join("")}
          </tbody>
        </table>
        ${
          missed.length
            ? `<h3 class="quiz-subheading">Missed questions</h3>
               <ul class="quiz-missed">
                 ${missed
                   .map(
                     (question) => `<li><div class="quiz-missed-prompt">${inlineMd(question.prompt)}</div>${conceptLink(
                       question,
                       `Review ${esc(question.conceptTitle)} <span aria-hidden="true">&rarr;</span>`
                     )}</li>`
                   )
                   .join("")}
               </ul>`
            : '<p class="quiz-all-correct">Every question answered correctly.</p>'
        }
        <div class="quiz-run-footer">
          ${missed.length ? '<button type="button" class="quiz-button" id="quiz-retry">Retry missed</button>' : ""}
          <button type="button" class="quiz-button quiz-button-secondary" id="quiz-new">New quiz</button>
          <a class="quiz-button quiz-button-secondary" href="#_quiz/progress">View progress</a>
        </div>
      </section>`;
    bindConceptLinks(container);
    const retry = container.querySelector("#quiz-retry");
    if (retry) {
      retry.addEventListener("click", () => {
        saveSession(buildSession(missed, { shuffleQuestions: true, shuffleChoices: true }));
        renderRun(container);
      });
    }
    container.querySelector("#quiz-new").addEventListener("click", () => {
      saveSession(null);
      state.ctx.navigate("_quiz");
    });
  }

  function accuracyBar(value) {
    const pct = value === null || value === undefined ? 0 : Math.round(value * 100);
    const tone = value === null || value === undefined ? "none" : pct >= 80 ? "good" : pct >= 50 ? "ok" : "weak";
    return `<span class="quiz-accuracy quiz-accuracy-${tone}"><span class="quiz-accuracy-track"><span style="width:${pct}%"></span></span><span>${formatPercent(
      value
    )}</span></span>`;
  }

  function renderProgress(container) {
    const questions = state.bank.questions;
    const rollups = computeRollups(questions, state.stats);
    const weak = weakConcepts(rollups.concepts);
    const saved = storageGet(localStorage, `${BUILDER_KEY}-progress`) || {};

    container.innerHTML = `
      <section class="quiz-panel">
        <div class="quiz-toolbar">
          <div class="quiz-sync" data-quiz-sync>${syncBadge()}</div>
          <div class="quiz-toolbar-actions">
            <a class="quiz-button" href="#_quiz">New quiz</a>
          </div>
        </div>
        <div class="quiz-stats">
          <div><strong>${rollups.totals.questions}</strong><span>questions</span></div>
          <div><strong>${rollups.totals.attempted}</strong><span>attempted</span></div>
          <div><strong>${formatPercent(rollups.totals.accuracy)}</strong><span>accuracy</span></div>
          <div><strong>${rollups.totals.flagged}</strong><span>flagged</span></div>
        </div>

        <h3 class="quiz-subheading">By technology</h3>
        <div class="quiz-table-wrap">
          <table class="quiz-table">
            <thead><tr><th>Technology</th><th>Attempted</th><th>Accuracy</th><th>Wrong</th><th>Flagged</th><th></th></tr></thead>
            <tbody>
              ${rollups.technologies
                .map(
                  (tech) => `
                    <tr>
                      <td>${esc(tech.techNum)}. ${esc(tech.techTitle)}</td>
                      <td>${tech.attempted} / ${tech.questions}</td>
                      <td>${accuracyBar(tech.accuracy)}</td>
                      <td>${tech.wrong}</td>
                      <td>${tech.flagged}</td>
                      <td><a class="quiz-link-button" href="#_quiz?technology=${encodeURIComponent(tech.techDir)}">Practice</a></td>
                    </tr>`
                )
                .join("")}
            </tbody>
          </table>
        </div>

        <h3 class="quiz-subheading">By quiz</h3>
        <div class="quiz-table-wrap">
          <table class="quiz-table">
            <thead><tr><th>Quiz</th><th>Attempted</th><th>Accuracy</th><th>Wrong</th><th>Flagged</th><th></th></tr></thead>
            <tbody>
              ${rollups.quizzes
                .map(
                  (quiz) => `
                    <tr>
                      <td>${esc(quiz.quizTitle)}<span class="quiz-table-sub">${esc(quiz.techTitle)}</span></td>
                      <td>${quiz.attempted} / ${quiz.questions}</td>
                      <td>${accuracyBar(quiz.accuracy)}</td>
                      <td>${quiz.wrong}</td>
                      <td>${quiz.flagged}</td>
                      <td><a class="quiz-link-button" href="#_quiz?quiz=${encodeURIComponent(quiz.quizKey)}">Practice</a></td>
                    </tr>`
                )
                .join("")}
            </tbody>
          </table>
        </div>

        <h3 class="quiz-subheading">Weak concepts</h3>
        ${
          weak.length
            ? `<ul class="quiz-weak">
                ${weak
                  .map(
                    (concept) => `
                      <li>
                        <div class="quiz-weak-main">
                          <strong>${esc(concept.conceptTitle)}</strong>
                          <span>${esc(concept.techTitle)} · ${esc(concept.topicTitle)}</span>
                        </div>
                        ${accuracyBar(concept.accuracy)}
                        <span class="quiz-weak-meta">${concept.wrong} wrong · ${concept.lastCorrect}/${concept.questions} right last time</span>
                        <span class="quiz-weak-actions">
                          ${conceptLink(concept, "Review")}
                          <a class="quiz-link-button" href="#_quiz?concept=${encodeURIComponent(concept.conceptRoute)}">Practice</a>
                        </span>
                      </li>`
                  )
                  .join("")}
              </ul>`
            : '<p class="quiz-empty-note">Answer some questions to see which concepts need work.</p>'
        }

        <h3 class="quiz-subheading">Questions</h3>
        <div class="quiz-question-filters">
          <select id="quiz-progress-tech" aria-label="Technology">
            <option value="">All technologies</option>
            ${rollups.technologies
              .map(
                (tech) =>
                  `<option value="${esc(tech.techDir)}"${saved.tech === tech.techDir ? " selected" : ""}>${esc(tech.techNum)}. ${esc(
                    tech.techTitle
                  )}</option>`
              )
              .join("")}
          </select>
          <select id="quiz-progress-quiz" aria-label="Quiz">
            <option value="">All quizzes</option>
            ${rollups.quizzes
              .map(
                (quiz) =>
                  `<option value="${esc(quiz.quizKey)}"${saved.quiz === quiz.quizKey ? " selected" : ""}>${esc(quiz.quizTitle)}</option>`
              )
              .join("")}
          </select>
          <select id="quiz-progress-state" aria-label="Question state">
            ${[
              ["all", "Any state"],
              ["unanswered", "Never attempted"],
              ["wrong", "Wrong at least once"],
              ["wrong-last", "Wrong last time"],
              ["flagged", "Flagged"],
            ]
              .map(([value, label]) => `<option value="${value}"${saved.state === value ? " selected" : ""}>${label}</option>`)
              .join("")}
          </select>
        </div>
        <div class="quiz-question-list" id="quiz-question-list"></div>
      </section>`;

    bindConceptLinks(container);
    const list = container.querySelector("#quiz-question-list");
    const techSelect = container.querySelector("#quiz-progress-tech");
    const quizSelect = container.querySelector("#quiz-progress-quiz");
    const stateSelect = container.querySelector("#quiz-progress-state");

    function renderList() {
      storageSet(localStorage, `${BUILDER_KEY}-progress`, {
        tech: techSelect.value,
        quiz: quizSelect.value,
        state: stateSelect.value,
      });
      const rows = questions.filter(
        (question) =>
          (!techSelect.value || question.techDir === techSelect.value) &&
          (!quizSelect.value || question.quizKey === quizSelect.value) &&
          matchesFilter(state.stats[question.key], stateSelect.value)
      );
      list.innerHTML = rows.length
        ? rows
            .map((question) => {
              const s = state.stats[question.key] || emptyStats();
              const last = s.lastCorrect === null ? "—" : s.lastCorrect ? "Right" : "Wrong";
              return `
                <details class="quiz-question-row" data-key="${esc(question.key)}">
                  <summary>
                    <span class="quiz-question-prompt">${inlineMd(question.prompt)}</span>
                    <span class="quiz-question-stats">
                      <span title="Attempts">${s.attempts} tries</span>
                      <span title="Times wrong" class="${s.wrong ? "is-wrong" : ""}">${s.wrong} wrong</span>
                      <span title="Last result">Last: ${last}</span>
                    </span>
                    <button type="button" class="quiz-flag${s.flagged ? " is-flagged" : ""}" data-flag="${esc(question.key)}" aria-pressed="${
                s.flagged
              }">${s.flagged ? "Flagged" : "Flag"}</button>
                  </summary>
                  <div class="quiz-question-detail">
                    <p class="quiz-question-where">${esc(question.techTitle)} · ${esc(question.quizTitle)} · ${esc(question.topicTitle)}${
                s.lastAnsweredAt ? ` · last answered ${esc(new Date(s.lastAnsweredAt).toLocaleString())}` : ""
              }</p>
                    <ul class="quiz-question-choices">${question.choices
                      .map(
                        (choice) =>
                          `<li class="${question.answer.includes(choice.id) ? "is-correct" : ""}">${inlineMd(choice.text)}</li>`
                      )
                      .join("")}</ul>
                    ${question.explanation ? `<div class="markdown-body">${md(question.explanation)}</div>` : ""}
                    ${conceptLink(question, `Review concept: ${esc(question.conceptTitle)} <span aria-hidden="true">&rarr;</span>`)}
                  </div>
                </details>`;
            })
            .join("")
        : '<p class="quiz-empty-note">No questions match.</p>';
      bindConceptLinks(list);
      list.querySelectorAll("[data-flag]").forEach((button) => {
        button.addEventListener("click", async (event) => {
          event.preventDefault();
          event.stopPropagation();
          const next = button.getAttribute("aria-pressed") !== "true";
          button.disabled = true;
          await setFlag(button.dataset.flag, next);
          button.disabled = false;
          button.setAttribute("aria-pressed", String(next));
          button.classList.toggle("is-flagged", next);
          button.textContent = next ? "Flagged" : "Flag";
        });
      });
    }

    techSelect.addEventListener("change", renderList);
    quizSelect.addEventListener("change", renderList);
    stateSelect.addEventListener("change", renderList);
    renderList();
  }

  function mount(ctx) {
    state.ctx = ctx;
    const retry = () => flushOutbox().then(updateSyncBadges);
    window.addEventListener("online", retry);
    setInterval(() => {
      if (state.pendingAttempts.length || state.pendingFlags.length) retry();
    }, 30000);
    retry();
  }

  const api = {
    buildSession,
    computeRollups,
    grade,
    matchesFilter,
    mergeProgress,
    mount,
    parseRoute,
    render,
    selectQuestions,
    shuffle,
    techGroups,
    unitKey,
    weakConcepts,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  if (typeof window !== "undefined") window.SweStudyQuiz = api;
})();
