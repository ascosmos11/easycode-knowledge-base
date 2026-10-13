from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "teamly_articles.json"
PENDING = ROOT / "audit_work" / "pending_teamly_uploads.json"
REPORT_MD = ROOT / "audit_work" / "public_kb_intervention_report.md"
REPORT_JSON = ROOT / "audit_work" / "public_kb_intervention_report.json"


ARCHIVE_ACTION_WORDS = (
    "archive",
    "hide",
    "unpublish",
    "do_not_reference",
)

TEAMLEAD_RE = re.compile(r"\bТЛ\b|тимлид|тимлидер", re.IGNORECASE)
SUPPORT_BOT_RE = re.compile(r"@ec_tsupport_bot", re.IGNORECASE)
OLD_PEOPLE_RE = re.compile(r"Роберт|Динара|Дим(?:а|ы|у|ой)?\s+Капралов|Дмитрий\s+Капралов", re.IGNORECASE)
SALARY_RE = re.compile(r"\bзарплат[а-я]*\b", re.IGNORECASE)
TRIAL_RE = re.compile(r"испытательн[а-я]+\s+срок[а-я]*", re.IGNORECASE)
OLD_TOOLS_RE = re.compile(
    r"rutube|рутуб|zoom|google\s*meet|гугл\s*мит|Чаты для преподавателя|@slice13",
    re.IGNORECASE,
)
TEAMLY_URL_RE = re.compile(r"https?://(?:s1-easycode|app)\.teamly\.ru/[^\s)\"'<]+", re.IGNORECASE)


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def strip_tags(value: str) -> str:
    return compact(re.sub(r"<[^>]+>", " ", html.unescape(value)))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_archive_ids(pending: dict[str, Any]) -> dict[str, str]:
    archived: dict[str, str] = {}
    for item in pending.get("items", []):
        action = str(item.get("action") or "")
        status = str(item.get("status") or "")
        title = str(item.get("title") or "без названия")
        item_no = str(item.get("item") or "?")
        if "check" in status or "ask" in status or status == "needs_user_confirmation":
            continue
        if status in {"rejected_do_not_change", "manual_done_do_not_touch"}:
            continue
        should_archive = (
            action == "archive"
            or action.startswith("archive_")
            or "_archive_" in action
            or action.endswith("_from_teacher_kb")
            or action in {
                "archive_or_remove_old_payment_policy",
                "archive_or_remove_duplicate_if_covered_else_keep_current",
                "archive_or_remove_duplicate",
                "archive_or_remove_from_teacher_kb",
            }
            or action in ARCHIVE_ACTION_WORDS
        )
        if should_archive:
            article_id = item.get("article_id")
            if article_id:
                archived[str(article_id)] = f"{item_no}: {title}"
            for nested in item.get("articles", []) or []:
                nested_id = nested.get("article_id")
                if nested_id:
                    archived[str(nested_id)] = f"{item_no}: {nested.get('title') or title}"
        if status in {"rejected_do_not_change", "manual_done_do_not_touch"}:
            article_id = item.get("article_id")
            if article_id and article_id in archived:
                archived.pop(str(article_id), None)
    return archived


def article_label(article: dict[str, Any]) -> str:
    return f"{article.get('title') or 'Без названия'} ({article.get('id')})"


def add_issue(issues: list[dict[str, Any]], kind: str, article: dict[str, Any], detail: str) -> None:
    issues.append(
        {
            "kind": kind,
            "article_id": article.get("id"),
            "title": article.get("title"),
            "section": article.get("section"),
            "detail": detail,
        }
    )


def find_issues(data: dict[str, Any], pending: dict[str, Any]) -> list[dict[str, Any]]:
    archived_ids = collect_archive_ids(pending)
    issues: list[dict[str, Any]] = []
    articles_by_id = {str(article.get("id")): article for article in data.get("articles", [])}

    for article in data.get("articles", []):
        text = str(article.get("text") or "")
        html_body = str(article.get("html") or "")
        combined = "\n".join([text, strip_tags(html_body), " ".join(article.get("links") or [])])

        if TEAMLEAD_RE.search(combined):
            add_issue(issues, "term_teamlead", article, "Есть тимлид/ТЛ/тимлидер; заменить по контексту.")
        if OLD_PEOPLE_RE.search(combined):
            add_issue(issues, "old_person_name", article, "Есть Роберт/Динара/Дима Капралов; заменить ролью или спросить.")
        if SALARY_RE.search(combined):
            add_issue(issues, "term_salary", article, "Есть «зарплата»; заменить на «выплата» или «оплата услуг».")
        if TRIAL_RE.search(combined):
            add_issue(issues, "term_trial_period", article, "Есть «испытательный срок»; заменить на «период дополнительной проверки».")
        if OLD_TOOLS_RE.search(combined):
            add_issue(issues, "old_tool_or_channel", article, "Есть Rutube/Zoom/Google Meet/старый чат/личный контакт.")
        if TEAMLY_URL_RE.search(combined):
            add_issue(issues, "teamly_url", article, "Осталась ссылка на Teamly в публичной базе.")
        if SUPPORT_BOT_RE.search(combined) and "https://t.me/ec_tsupport_bot" not in html_body and "https://t.me/ec_tsupport_bot" not in combined:
            add_issue(issues, "support_bot_unlinked", article, "@ec_tsupport_bot упомянут без ссылки.")

        for related_id in article.get("relatedArticleIds") or []:
            related_id = str(related_id)
            if related_id in archived_ids:
                add_issue(
                    issues,
                    "archived_related_link",
                    article,
                    f"Связь с архивной/скрываемой статьей: {archived_ids[related_id]}",
                )
            elif related_id not in articles_by_id:
                add_issue(issues, "missing_related_link", article, f"Связь ведет на отсутствующую статью: {related_id}")

    return issues


def pending_check_first(pending: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for item in pending.get("items", []):
        status = str(item.get("status") or "")
        if "check" in status or "ask" in status or status == "needs_user_confirmation":
            result.append(
                {
                    "item": item.get("item"),
                    "status": status,
                    "title": item.get("title"),
                    "url": item.get("url"),
                    "action": item.get("action"),
                }
            )
    return result


def render_report(data: dict[str, Any], issues: list[dict[str, Any]], check_first: list[dict[str, Any]]) -> str:
    by_kind: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in issues:
        by_kind[issue["kind"]].append(issue)

    lines = [
        "# Public KB Intervention Report",
        "",
        f"- Articles in public base: {len(data.get('articles', []))}",
        f"- Issues found: {len(issues)}",
        f"- Pending items that require check/decision before upload: {len(check_first)}",
        "",
        "## Commands",
        "",
        "```bash",
        "python3 scripts/build_public_data.py",
        "python3 scripts/audit_public_kb.py",
        "python3 -m http.server 8000",
        "git diff -- data/teamly_articles.json data/teamly_articles.js scripts/build_public_data.py scripts/audit_public_kb.py",
        "git add index.html styles.css app.js data/teamly_articles.json data/teamly_articles.js scripts README.md",
        "git commit -m \"Update teacher knowledge base\"",
        "git push origin main",
        "```",
        "",
        "## Issues By Type",
        "",
    ]

    for kind in sorted(by_kind):
        rows = by_kind[kind]
        lines.extend([f"### {kind} ({len(rows)})", ""])
        for issue in rows:
            lines.append(
                f"- `{issue['article_id']}` — **{issue['title']}** / {issue['section']}: {issue['detail']}"
            )
        lines.append("")

    lines.extend(["## Needs Human Check Before Applying", ""])
    if not check_first:
        lines.append("- Нет пунктов со статусом check/ask.")
    else:
        for item in check_first:
            url = f" — {item['url']}" if item.get("url") else ""
            lines.append(f"- `{item['item']}` [{item['status']}] **{item['title']}**{url}; action: `{item['action']}`")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    data = load_json(DATA)
    pending = load_json(PENDING)
    issues = find_issues(data, pending)
    check_first = pending_check_first(pending)

    REPORT_JSON.write_text(
        json.dumps({"issues": issues, "check_first": check_first}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    REPORT_MD.write_text(render_report(data, issues, check_first), encoding="utf-8")
    print(f"Wrote {REPORT_MD.relative_to(ROOT)} with {len(issues)} issues")


if __name__ == "__main__":
    main()
