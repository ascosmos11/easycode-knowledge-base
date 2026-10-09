function detectAdminMode() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("admin") === "1") {
    localStorage.setItem("kb-admin-mode", "1");
    return true;
  }
  if (params.get("admin") === "0") {
    localStorage.removeItem("kb-admin-mode");
    localStorage.removeItem("kb-show-media-slots");
    return false;
  }
  return localStorage.getItem("kb-admin-mode") === "1";
}

const state = {
  payload: window.KB_DATA,
  query: "",
  section: "all",
  activeId: null,
  isAdmin: detectAdminMode(),
  showMediaSlots:
    localStorage.getItem("kb-admin-mode") === "1" &&
    localStorage.getItem("kb-show-media-slots") === "1",
};

const elements = {
  search: document.querySelector("#searchInput"),
  section: document.querySelector("#sectionFilter"),
  mediaToggle: document.querySelector("#mediaToggle"),
  clear: document.querySelector("#clearButton"),
  articleCount: document.querySelector("#articleCount"),
  total: document.querySelector("#totalCount"),
  visible: document.querySelector("#visibleCount"),
  sectionCount: document.querySelector("#sectionCount"),
  list: document.querySelector("#articleList"),
  view: document.querySelector("#articleView"),
  empty: document.querySelector("#emptyState"),
};

const articleById = new Map(state.payload.articles.map((article) => [article.id, article]));

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, (char) => {
    const entities = {
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#039;",
    };
    return entities[char];
  });
}

function normalize(value) {
  return String(value || "").toLowerCase();
}

function searchScore(article, query) {
  if (!query) return 0;

  const title = normalize(article.title);
  const section = normalize(article.section);
  const excerpt = normalize(article.excerpt);
  const text = normalize(article.searchText);
  let score = Number(article.priority || 0);

  if (title === query) score += 1000;
  if (title.startsWith(query)) score += 650;
  if (title.includes(query)) score += 500;
  if (section.includes(query)) score += 180;
  if (excerpt.includes(query)) score += 90;
  if (text.includes(query)) score += 30;

  return score;
}

function populateSections() {
  state.payload.sections.forEach((section) => {
    const option = document.createElement("option");
    option.value = section.name;
    option.textContent = `${section.name} (${section.count})`;
    elements.section.append(option);
  });
}

function getFilteredArticles() {
  const query = normalize(state.query);
  const articles = state.payload.articles.filter((article) => {
    const matchesSection = state.section === "all" || article.section === state.section;
    const matchesQuery =
      !query ||
      normalize(`${article.title} ${article.section} ${article.searchText}`).includes(query);
    return matchesSection && matchesQuery;
  });

  if (!query) {
    return articles.sort((a, b) => {
      const priorityDiff = Number(b.priority || 0) - Number(a.priority || 0);
      if (priorityDiff) return priorityDiff;
      return a.title.localeCompare(b.title, "ru");
    });
  }

  return articles.sort((a, b) => {
    const scoreDiff = searchScore(b, query) - searchScore(a, query);
    if (scoreDiff) return scoreDiff;
    return a.title.localeCompare(b.title, "ru");
  });
}

function setHash(articleId) {
  if (window.location.hash !== `#article=${articleId}`) {
    window.location.hash = `article=${articleId}`;
  }
}

function highlightReader(shouldScroll) {
  const reader = document.querySelector(".reader");
  if (!reader) return;

  reader.classList.remove("reader-flash");
  void reader.offsetWidth;
  reader.classList.add("reader-flash");

  if (shouldScroll || window.matchMedia("(max-width: 920px)").matches) {
    reader.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function selectArticle(articleId, updateHash = true, options = {}) {
  const article = articleById.get(articleId);
  if (!article) return;

  state.activeId = articleId;
  if (updateHash) setHash(articleId);
  renderList();
  renderArticle(article);
  if (options.highlight) highlightReader(options.scrollToReader);
}

function renderList() {
  const articles = getFilteredArticles();
  elements.visible.textContent = articles.length.toLocaleString("ru-RU");
  elements.empty.hidden = articles.length !== 0;
  elements.list.replaceChildren();

  const grouped = new Map();
  if (state.query) {
    grouped.set("Результаты поиска", articles);
  } else if (state.section === "all") {
    grouped.set("Материалы по приоритету", articles);
  } else {
    articles.forEach((article) => {
      if (!grouped.has(article.section)) grouped.set(article.section, []);
      grouped.get(article.section).push(article);
    });
  }

  grouped.forEach((items, section) => {
    const sectionNode = document.createElement("section");
    sectionNode.className = "list-section";
    const title = document.createElement("h3");
    title.textContent = section;
    sectionNode.append(title);

    items.forEach((article) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "article-link";
      button.classList.toggle("is-active", article.id === state.activeId);
      button.dataset.articleId = article.id;
      button.innerHTML = `
        <span>${escapeHtml(article.title)}</span>
        <small>${escapeHtml(article.excerpt || "Открыть материал")}</small>
      `;
      sectionNode.append(button);
    });

    elements.list.append(sectionNode);
  });
}

function renderArticle(article) {
  const related = article.relatedArticleIds
    .map((id) => articleById.get(id))
    .filter(Boolean)
    .slice(0, 8);

  const relatedHtml = related.length
    ? `
      <section class="related">
        <h2>Связанные материалы</h2>
        <div>
          ${related
            .map(
              (item) =>
                `<a href="#article=${item.id}" data-article-id="${item.id}">${escapeHtml(item.title)}</a>`,
            )
            .join("")}
        </div>
      </section>
    `
    : "";

  const externalLinks = article.links.length
    ? `
      <section class="related">
        <h2>Внешние ссылки</h2>
        <div>
          ${article.links
            .slice(0, 12)
            .map((url) => `<a href="${escapeHtml(url)}" target="_blank" rel="noreferrer">${linkLabel(url)}</a>`)
            .join("")}
        </div>
      </section>
    `
    : "";

  elements.view.innerHTML = `
    <p class="eyebrow">${escapeHtml(article.section)}</p>
    <h1>${escapeHtml(article.title)}</h1>
    <p class="breadcrumbs">${escapeHtml(article.breadcrumbs.join(" / "))}</p>
    <div class="article-content">${article.html || "<p>В статье нет текстового содержимого.</p>"}</div>
    ${relatedHtml}
    ${externalLinks}
  `;
  elements.view.classList.toggle("show-media-slots", state.showMediaSlots);
  elements.view.scrollTop = 0;
  document.querySelector(".reader").scrollTop = 0;
}

function linkLabel(url) {
  try {
    const parsed = new URL(url);
    return escapeHtml(parsed.hostname.replace(/^www\./, ""));
  } catch {
    return "Ссылка";
  }
}

function render() {
  elements.articleCount.textContent = `${state.payload.articleCount.toLocaleString("ru-RU")} статей`;
  elements.total.textContent = state.payload.articleCount.toLocaleString("ru-RU");
  elements.sectionCount.textContent = state.payload.sections.length.toLocaleString("ru-RU");
  renderList();

  const filtered = getFilteredArticles();
  if (state.activeId && articleById.has(state.activeId)) return;
  if (filtered[0]) selectArticle(filtered[0].id);
}

function hydrateFromHash() {
  const match = window.location.hash.match(/article=([^&]+)/);
  const articleId = match ? decodeURIComponent(match[1]) : null;
  if (articleId && articleById.has(articleId)) {
    selectArticle(articleId, false);
  }
}

elements.list.addEventListener("click", (event) => {
  const button = event.target.closest("[data-article-id]");
  if (!button) return;
  selectArticle(button.dataset.articleId, true, {
    highlight: Boolean(state.query),
    scrollToReader: Boolean(state.query),
  });
});

elements.view.addEventListener("click", (event) => {
  const link = event.target.closest("a[data-article-id]");
  if (!link) return;
  event.preventDefault();
  selectArticle(link.dataset.articleId);
});

elements.search.addEventListener("input", (event) => {
  state.query = event.target.value.trim();
  state.activeId = null;
  render();
});

elements.section.addEventListener("change", (event) => {
  state.section = event.target.value;
  state.activeId = null;
  render();
});

elements.clear.addEventListener("click", () => {
  state.query = "";
  state.section = "all";
  state.activeId = null;
  elements.search.value = "";
  elements.section.value = "all";
  window.location.hash = "home";
  render();
});

if (state.isAdmin) {
  elements.mediaToggle.addEventListener("click", () => {
    state.showMediaSlots = !state.showMediaSlots;
    localStorage.setItem("kb-show-media-slots", state.showMediaSlots ? "1" : "0");
    elements.mediaToggle.setAttribute("aria-pressed", String(state.showMediaSlots));
    elements.mediaToggle.textContent = state.showMediaSlots ? "Скрыть места для фото" : "Места для фото";
    if (state.activeId && articleById.has(state.activeId)) {
      renderArticle(articleById.get(state.activeId));
    }
  });
} else {
  elements.mediaToggle.hidden = true;
  state.showMediaSlots = false;
}

window.addEventListener("hashchange", hydrateFromHash);

populateSections();
if (state.isAdmin) {
  elements.mediaToggle.setAttribute("aria-pressed", String(state.showMediaSlots));
  elements.mediaToggle.textContent = state.showMediaSlots ? "Скрыть места для фото" : "Места для фото";
}
hydrateFromHash();
render();
