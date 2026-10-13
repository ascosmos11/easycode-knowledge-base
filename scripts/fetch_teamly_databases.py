from __future__ import annotations

import json
import ssl
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

import certifi


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "audit_work"))

from teamly_api import request_json  # noqa: E402
from teamly_api import TeamlyError  # noqa: E402


DATABASES = {
    "b2647532-b909-542f-bfd7-3251ad286bcc": "Общая методическая база знаний",
    "cb2992a9-0725-41b2-b2ce-48cc1b7bb16a": "Методические материалы “Новая эра”",
    "16af00aa-ecc0-4c87-ba92-4cb9315db0c5": "Методические материалы - таблица по всем направлениям",
}
OUTPUT = ROOT / "audit_work" / "teamly_api_cache" / "method_databases.json"


def configure_ssl() -> None:
    context = ssl.create_default_context(cafile=certifi.where())
    opener = urllib.request.build_opener(urllib.request.HTTPSHandler(context=context))
    urllib.request.install_opener(opener)


def database_query(database_id: str) -> dict[str, Any]:
    return {
        "query": {
            "__filter": {"contentDatabaseId": database_id},
            "id": True,
            "title": True,
            "breadcrumbs": True,
            "schemaProperties": True,
            "content": {
                "article": {"id": True, "properties": {"properties": True}},
                "hasNested": True,
            },
        }
    }


def teamly_post(path: str, body: dict[str, Any]) -> Any:
    for attempt in range(6):
        try:
            _, payload = request_json("POST", path, body=body)
            return payload
        except TeamlyError as exc:
            if "HTTP 429" not in str(exc) or attempt == 5:
                raise
            time.sleep(8 * (attempt + 1))
    raise RuntimeError("unreachable")


def nested_query(parent_id: str, page: int = 1) -> dict[str, Any]:
    return {
        "query": {
            "__pagination": {"page": page, "per_page": 100},
            "__filter": {"parentId": parent_id},
            "article": {"id": True, "properties": {"properties": True}},
            "hasNested": True,
        }
    }


def load_nested(parent_id: str) -> list[dict[str, Any]]:
    page = 1
    result: list[dict[str, Any]] = []
    while True:
        payload = teamly_post(
            "/api/v1/ql/content-database/nestedContent",
            nested_query(parent_id, page),
        )
        items = payload.get("items", []) if isinstance(payload, dict) else []
        for item in items:
            article = item.get("article") or {}
            if item.get("hasNested") and article.get("id"):
                item["children"] = load_nested(str(article["id"]))
            result.append(item)
        pagination = payload.get("pagination", {}) if isinstance(payload, dict) else {}
        if page >= int(pagination.get("lastPage") or page):
            break
        page += 1
    return result


def load_database(database_id: str, title: str) -> dict[str, Any]:
    payload = teamly_post(
        "/api/v1/ql/content-database/content",
        database_query(database_id),
    )
    if not isinstance(payload, dict):
        raise RuntimeError(f"Unexpected response for {database_id}")
    for item in payload.get("content", []) or []:
        article = item.get("article") or {}
        if item.get("hasNested") and article.get("id"):
            item["children"] = load_nested(str(article["id"]))
    payload["_requestedTitle"] = title
    return payload


def main() -> None:
    configure_ssl()
    data = {
        database_id: load_database(database_id, title)
        for database_id, title in DATABASES.items()
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
