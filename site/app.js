(() => {
  "use strict";

  let studyData = null;
  let currentTech = null;
  let currentTopic = null;

  const $ = (sel, ctx = document) => ctx.querySelector(sel);
  const $$ = (sel, ctx = document) => [...ctx.querySelectorAll(sel)];

  // ── Boot ───────────────────────────────────────────

  async function init() {
    const res = await fetch("/api/content");
    studyData = await res.json();
    renderSidebar();
    renderStats();
    bindSearch();
    handleRoute();
    window.addEventListener("hashchange", handleRoute);
  }

  // ── Routing ────────────────────────────────────────

  function handleRoute() {
    const hash = decodeURIComponent(location.hash.slice(1));
    if (!hash) return showWelcome();

    const parts = hash.split("/");
    const techDir = parts[0];
    const topicDir = parts[1];

    const tech = studyData.technologies.find((t) => t.dir === techDir);
    if (!tech) return showWelcome();

    if (topicDir) {
      const topic = tech.topics.find((t) => t.dir === topicDir);
      if (topic) return showTopic(tech, topic);
    }
    showTechnology(tech);
  }

  function navigate(hash) {
    location.hash = hash;
  }

  // ── Sidebar ────────────────────────────────────────

  function renderSidebar() {
    const nav = $("#chapter-nav");
    nav.innerHTML = studyData.technologies
      .map(
        (tech) => `
      <div class="nav-chapter" data-dir="${tech.dir}">
        <button class="nav-chapter-btn" data-dir="${tech.dir}">
          <span class="nav-chapter-num">${tech.num}</span>
          <span class="nav-chapter-title">${esc(tech.title)}</span>
          <svg class="nav-chevron" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
        <div class="nav-lessons">
          ${tech.topics
            .map(
              (topic) => `
            <button class="nav-lesson-btn" data-ch="${tech.dir}" data-ls="${topic.dir}">
              <span class="nav-lesson-num">${topic.num}.</span>
              <span>${esc(topic.title)}</span>
              <span class="nav-lesson-indicators">
                ${topic.notesFile ? '<span class="nav-indicator has-notes" title="Notes"></span>' : ""}
                ${topic.hasConcepts ? '<span class="nav-indicator has-concepts" title="Concepts"></span>' : ""}
              </span>
            </button>
          `
            )
            .join("")}
        </div>
      </div>
    `
      )
      .join("");

    nav.addEventListener("click", (e) => {
      const chBtn = e.target.closest(".nav-chapter-btn");
      if (chBtn) {
        navigate(chBtn.dataset.dir);
        return;
      }
      const lsBtn = e.target.closest(".nav-lesson-btn");
      if (lsBtn) {
        navigate(`${lsBtn.dataset.ch}/${lsBtn.dataset.ls}`);
      }
    });
  }

  function updateSidebarActive(techDir, topicDir) {
    $$(".nav-chapter-btn.active").forEach((el) => el.classList.remove("active"));
    $$(".nav-chapter.expanded").forEach((el) => el.classList.remove("expanded"));
    $$(".nav-lesson-btn.active").forEach((el) => el.classList.remove("active"));

    if (!techDir) return;

    const chEl = $(`.nav-chapter[data-dir="${techDir}"]`);
    if (chEl) {
      chEl.classList.add("expanded");
      chEl.querySelector(".nav-chapter-btn").classList.add("active");
    }

    if (topicDir) {
      const lsBtn = $(`.nav-lesson-btn[data-ch="${techDir}"][data-ls="${topicDir}"]`);
      if (lsBtn) lsBtn.classList.add("active");
    }
  }

  // ── Welcome / Stats ───────────────────────────────

  function renderStats() {
    const totalTopics = studyData.technologies.reduce((s, t) => s + t.topics.length, 0);
    const totalWithNotes = studyData.technologies.reduce(
      (s, t) => s + t.topics.filter((tp) => tp.notesFile).length,
      0
    );
    $("#stats").innerHTML = `
      <div class="stat-card"><div class="stat-value">${studyData.technologies.length}</div><div class="stat-label">Technologies</div></div>
      <div class="stat-card"><div class="stat-value">${totalTopics}</div><div class="stat-label">Topics</div></div>
      <div class="stat-card"><div class="stat-value">${totalWithNotes}</div><div class="stat-label">Notes</div></div>
    `;
  }

  function showWelcome() {
    currentTech = null;
    currentTopic = null;
    updateSidebarActive(null, null);
    $("#welcome").style.display = "";
    $("#content").style.display = "none";
  }

  // ── Technology Overview ──────────────────────────────

  function showTechnology(tech) {
    currentTech = tech;
    currentTopic = null;
    updateSidebarActive(tech.dir, null);

    $("#welcome").style.display = "none";
    $("#content").style.display = "";
    $("#chapter-overview").style.display = "";
    $("#lesson-detail").style.display = "none";

    $("#breadcrumb").innerHTML = `<a href="#" onclick="location.hash='';return false">Home</a><span class="sep">/</span><span>${esc(tech.title)}</span>`;
    $("#content-title").textContent = tech.title;

    const topicCount = tech.topics.length;
    const noteCount = tech.topics.filter((t) => t.notesFile).length;
    const conceptCount = tech.topics.filter((t) => t.hasConcepts).length;

    let metaHtml = `
      <span class="meta-badge">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        ${topicCount} topics
      </span>
      <span class="meta-badge">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
        ${noteCount} with notes
      </span>
    `;

    if (tech.hasTechnologyConcepts) {
      metaHtml += `
        <span class="meta-badge" onclick="showTechnologyConcepts('${tech.dir}')" style="cursor:pointer">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>
          Technology Overview
        </span>
      `;
    }

    $("#chapter-meta").innerHTML = metaHtml;

    $("#lesson-grid").innerHTML = tech.topics
      .map(
        (topic) => `
      <div class="lesson-card" onclick="location.hash='${tech.dir}/${topic.dir}'">
        <div class="lesson-card-header">
          <span class="lesson-card-num">${topic.num}</span>
          <span class="lesson-card-title">${esc(topic.title)}</span>
        </div>
        <div class="lesson-card-badges">
          ${topic.notesFile ? '<span class="lesson-badge notes">Notes</span>' : ""}
          ${topic.hasConcepts ? '<span class="lesson-badge concepts">Concepts</span>' : ""}
        </div>
      </div>
    `
      )
      .join("");

    $("#main").scrollTop = 0;
  }

  window.showTechnologyConcepts = async function (techDir) {
    const tech = studyData.technologies.find((t) => t.dir === techDir);
    if (!tech) return;
    currentTech = tech;
    currentTopic = null;
    updateSidebarActive(tech.dir, null);

    $("#chapter-overview").style.display = "none";
    $("#lesson-detail").style.display = "";

    $("#breadcrumb").innerHTML = `
      <a href="#" onclick="location.hash='';return false">Home</a>
      <span class="sep">/</span>
      <a href="#${tech.dir}">${esc(tech.title)}</a>
      <span class="sep">/</span>
      <span>Overview</span>
    `;
    $("#content-title").textContent = `${tech.title} — Overview`;

    $("#tab-bar").innerHTML = "";
    const md = await fetchText(`/content/${tech.dir}/technology_concepts.md`);
    $("#tab-content").innerHTML = `<div class="markdown-body">${renderMarkdown(md)}</div>`;
    $("#main").scrollTop = 0;
  };

  // ── Topic Detail ─────────────────────────────────

  function showTopic(tech, topic) {
    currentTech = tech;
    currentTopic = topic;
    updateSidebarActive(tech.dir, topic.dir);

    $("#welcome").style.display = "none";
    $("#content").style.display = "";
    $("#chapter-overview").style.display = "none";
    $("#lesson-detail").style.display = "";

    $("#breadcrumb").innerHTML = `
      <a href="#" onclick="location.hash='';return false">Home</a>
      <span class="sep">/</span>
      <a href="#${tech.dir}">${esc(tech.title)}</a>
      <span class="sep">/</span>
      <span>${esc(topic.title)}</span>
    `;
    $("#content-title").textContent = topic.title;

    const tabs = [];
    if (topic.notesFile) tabs.push({ id: "notes", label: "Notes" });
    if (topic.hasConcepts) tabs.push({ id: "concepts", label: "Concepts" });

    if (tabs.length === 0) {
      $("#tab-bar").innerHTML = "";
      $("#tab-content").innerHTML = emptyState("No content available for this topic yet.");
      return;
    }

    renderTabs(tabs, tech, topic);
    activateTab(tabs[0].id, tech, topic);
    $("#main").scrollTop = 0;
  }

  function renderTabs(tabs, tech, topic) {
    const bar = $("#tab-bar");
    bar.innerHTML = tabs
      .map(
        (t) =>
          `<button class="tab-btn" data-tab="${t.id}">${t.label}</button>`
      )
      .join("");

    bar.addEventListener("click", (e) => {
      const btn = e.target.closest(".tab-btn");
      if (btn) activateTab(btn.dataset.tab, tech, topic);
    });
  }

  async function activateTab(tabId, tech, topic) {
    $$(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tabId));
    const container = $("#tab-content");
    const base = `/content/${tech.dir}/${topic.dir}`;

    if (tabId === "notes") {
      const md = await fetchText(`${base}/${topic.notesFile}`);
      container.innerHTML = `<div class="markdown-body">${renderMarkdown(md)}</div>`;
    } else if (tabId === "concepts") {
      const md = await fetchText(`${base}/concepts.md`);
      const concepts = parseConcepts(md);
      if (concepts.length) {
        container.innerHTML = `<div class="concept-list">${concepts.map((c) => `<div class="concept-item"><span class="concept-dot"></span>${esc(c)}</div>`).join("")}</div>`;
      } else {
        container.innerHTML = `<div class="markdown-body">${renderMarkdown(md)}</div>`;
      }
    }
  }

  // ── Search ─────────────────────────────────────────

  function bindSearch() {
    const input = $("#search-input");
    input.addEventListener("input", () => {
      const q = input.value.toLowerCase().trim();
      $$(".nav-chapter").forEach((el) => {
        const techDir = el.dataset.dir;
        const tech = studyData.technologies.find((t) => t.dir === techDir);
        if (!tech) return;

        const techMatch = tech.title.toLowerCase().includes(q);
        const matchingTopics = tech.topics.filter((t) => t.title.toLowerCase().includes(q));

        if (!q) {
          el.style.display = "";
          el.classList.remove("expanded");
          el.querySelectorAll(".nav-lesson-btn").forEach((lb) => (lb.style.display = ""));
          return;
        }

        if (techMatch || matchingTopics.length) {
          el.style.display = "";
          if (matchingTopics.length && !techMatch) {
            el.classList.add("expanded");
            el.querySelectorAll(".nav-lesson-btn").forEach((lb) => {
              const topicDir = lb.dataset.ls;
              const topic = tech.topics.find((t) => t.dir === topicDir);
              lb.style.display = topic && topic.title.toLowerCase().includes(q) ? "" : "none";
            });
          } else {
            el.classList.add("expanded");
            el.querySelectorAll(".nav-lesson-btn").forEach((lb) => (lb.style.display = ""));
          }
        } else {
          el.style.display = "none";
        }
      });
    });
  }

  // ── Helpers ────────────────────────────────────────

  async function fetchText(url) {
    try {
      const res = await fetch(url);
      if (!res.ok) return "";
      return await res.text();
    } catch {
      return "";
    }
  }

  function renderMarkdown(md) {
    if (!md) return emptyState("No content available.");
    if (typeof marked !== "undefined") {
      marked.setOptions({ breaks: false, gfm: true });
      return marked.parse(md);
    }
    return `<pre>${esc(md)}</pre>`;
  }

  function parseConcepts(md) {
    return md
      .split("\n")
      .map((l) => l.trim())
      .filter((l) => l.startsWith("- "))
      .map((l) => l.slice(2).trim())
      .filter(Boolean);
  }

  function esc(s) {
    const d = document.createElement("div");
    d.textContent = s;
    return d.innerHTML;
  }

  function emptyState(msg) {
    return `<div class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <p>${msg}</p>
    </div>`;
  }

  // ── Start ──────────────────────────────────────────

  document.addEventListener("DOMContentLoaded", init);
})();
