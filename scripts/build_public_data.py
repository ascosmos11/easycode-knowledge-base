from __future__ import annotations

import html
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "audit_work" / "teamly_api_cache"
ARTICLES = CACHE / "articles_active_refreshed.json"
PENDING = ROOT / "audit_work" / "pending_teamly_uploads.json"
TREE_ALL = CACHE / "tree_all.json"
OUTPUT_JSON = ROOT / "data" / "teamly_articles.json"
OUTPUT_JS = ROOT / "data" / "teamly_articles.js"

TEACHER_KB_ID = "33e24971-4830-529c-bb54-a661f173613a"
TEACHER_KB_TITLE = "База знаний для преподавателей"
METHOD_ARTICLE_ID = "080a5691-2c34-5da8-a372-f66d6d60165a"
TEAMLY_HOSTS = {"s1-easycode.teamly.ru", "app.teamly.ru"}
PUBLIC_BLOCKED_LINK_PATTERNS = (
    re.compile(r"https?://(?:www\.)?rutube\.ru/[^\s)\"'<]+", re.IGNORECASE),
)
METHOD_DATABASES = {
    "b2647532-b909-542f-bfd7-3251ad286bcc": {
        "title": "Общая методическая база знаний",
        "anchor": "method-db-general",
    },
    "cb2992a9-0725-41b2-b2ce-48cc1b7bb16a": {
        "title": "Методические материалы “Новая эра”",
        "anchor": "method-db-new-era",
    },
    "16af00aa-ecc0-4c87-ba92-4cb9315db0c5": {
        "title": "Методические материалы - таблица по всем направлениям",
        "anchor": "method-db-all",
    },
}
RECOVERED_METHOD_LINKS = {
    "method-db-general": [
        (
            "Профориентационный урок",
            [
                ("Материалы 6-9 лет", "https://drive.google.com/drive/folders/1lxF5rI_nEudGkUGLt7wZyBBRuXtH9FJm"),
                ("Материалы 10-17 лет", "https://drive.google.com/drive/folders/10EhKWOFLO5kva4O-Ls2885cf9xjrGE40"),
            ],
        ),
        (
            "Тестдрайв",
            [
                ("Методички по IT", "https://drive.google.com/drive/folders/1Ak7K86kHRX0Sp97mY49ImsAeTV57sCXp"),
                ("Методички по дизайну", "https://drive.google.com/drive/folders/1tJPV8fp_ry-G6oPKU80UEapciZ_Dg-Rt"),
            ],
        ),
        (
            "EasyCode ComeBack",
            [
                ("Программа продукта", "https://drive.google.com/drive/folders/1dsCn0FdWj13Ho6G3bZXPNeQbB6Dxa5z0"),
                ("Презентация по продукту", "https://docs.google.com/presentation/d/1oadTAeondBO9jqJiWwnc8gymAG7ssyv7bcdA6tHuanM/edit?slide=id.g3bb40b91be8_0_6#slide=id.g3bb40b91be8_0_6"),
            ],
        ),
        (
            "Летний лагерь",
            [
                ("КТП лагеря", "https://docs.google.com/document/d/1sQVKkqYP6BlG9_VxMjndr1JybF0AfUq8PJiyHcNnfZk/edit?usp=sharing"),
                ("Презентация лагеря", "https://docs.google.com/presentation/d/1UZN5BJAcMPVjCe5l9fJQ-9hBoW1UtDILC7vxcS3EmHo/edit?slide=id.p#slide=id.p"),
            ],
        ),
        (
            "Создатель интерактивных миров",
            [
                ("КТП Junior 6-9", "https://docs.google.com/document/d/1t7rVQdqt2_rMZvne3iybeDDwfZ1iHqg-/edit#heading=h.ackkt9vifyos"),
                ("КТП Middle 10-12", "https://docs.google.com/document/d/1UhX64tVFO8EwOtg1Kr2ezfIfBhtV_1FR/edit#heading=h.ackkt9vifyos"),
                ("КТП Senior 13-17", "https://docs.google.com/document/d/1Mm4azKdv8rin_-1mDbVQWZSYvFryZ90V/edit#heading=h.ackkt9vifyos"),
                ("Нейросети Junior", "https://docs.google.com/document/d/1XxwRasqwRZ7jC8NcpcL8u4xEBfulv4odxJgI1Q1OS3c/edit?tab=t.0#heading=h.hj5xvv2p73k3"),
                ("Нейросети Middle", "https://docs.google.com/document/d/1wtZ6js4CJuXnxgLwwd4txyiLFoGQJoeWAv6EtdRimm4/edit?tab=t.0#heading=h.ga6y186ou22b"),
                ("Нейросети Senior", "https://docs.google.com/document/d/1igc88V2gcDb5dUCex-1qG1ThLb_Zuzyk9dpNjMw4wbc/edit?tab=t.0"),
            ],
        ),
    ],
    "method-db-new-era": [
        (
            "Создатель интерактивных миров",
            [
                ("КТП Junior 6-9", "https://docs.google.com/document/d/1t7rVQdqt2_rMZvne3iybeDDwfZ1iHqg-/edit#heading=h.ackkt9vifyos"),
                ("КТП Middle 10-12", "https://docs.google.com/document/d/1UhX64tVFO8EwOtg1Kr2ezfIfBhtV_1FR/edit#heading=h.ackkt9vifyos"),
                ("КТП Senior 13-17", "https://docs.google.com/document/d/1Mm4azKdv8rin_-1mDbVQWZSYvFryZ90V/edit#heading=h.ackkt9vifyos"),
                ("Нейросети Junior", "https://docs.google.com/document/d/1XxwRasqwRZ7jC8NcpcL8u4xEBfulv4odxJgI1Q1OS3c/edit?tab=t.0#heading=h.hj5xvv2p73k3"),
                ("Нейросети Middle", "https://docs.google.com/document/d/1wtZ6js4CJuXnxgLwwd4txyiLFoGQJoeWAv6EtdRimm4/edit?tab=t.0#heading=h.ga6y186ou22b"),
                ("Нейросети Senior", "https://docs.google.com/document/d/1igc88V2gcDb5dUCex-1qG1ThLb_Zuzyk9dpNjMw4wbc/edit?tab=t.0"),
            ],
        ),
        (
            "EasyCode 2.0",
            [
                ("Программа продукта", "https://drive.google.com/drive/folders/1dsCn0FdWj13Ho6G3bZXPNeQbB6Dxa5z0"),
                ("Презентация по продукту", "https://docs.google.com/presentation/d/1oadTAeondBO9jqJiWwnc8gymAG7ssyv7bcdA6tHuanM/edit?slide=id.g3bb40b91be8_0_6#slide=id.g3bb40b91be8_0_6"),
            ],
        ),
        (
            "Профориентационный урок",
            [
                ("Материалы 6-9 лет", "https://drive.google.com/drive/folders/1lxF5rI_nEudGkUGLt7wZyBBRuXtH9FJm"),
                ("Материалы 10-17 лет", "https://drive.google.com/drive/folders/10EhKWOFLO5kva4O-Ls2885cf9xjrGE40"),
            ],
        ),
    ],
    "method-db-all": [
        (
            "Методические пособия",
            [
                ("Знакомство и рефлексия", "https://docs.google.com/presentation/d/1cRWN71CRj4EzaqV_QR3IngxDZMm58ea9/edit?usp=sharing&ouid=106754532266826184774&rtpof=true&sd=true"),
                ("Для самостоятельной работы", "https://docs.google.com/presentation/d/1K-lzdFM20jZ3gJs-dCNgu1VgOvyjKFluwtZ76_kcIfI/edit?usp=drive_link"),
                ("Виды уроков", "https://docs.google.com/presentation/d/1F2gIJ949i1kvfpNiLf8KJtFdwnSg3F_n_wjZGIXkxXE/edit?usp=drive_link"),
                ("Soft-skills", "https://docs.google.com/presentation/d/1MU7lpNBDJs9YOL20MsQnU2vIUWF6QdS5/edit?usp=sharing&ouid=106754532266826184774&rtpof=true&sd=true"),
                ("Возрастная периодизация", "https://docs.google.com/presentation/d/1JvqdFgSRwv2UKv9rlBjhMKOTl_twJ7le/edit?usp=sharing&ouid=106754532266826184774&rtpof=true&sd=true"),
                ("ОВЗ", "https://docs.google.com/presentation/d/1XPOGsl7HWGLvQGXlbdPthT4Re4dfORW4/edit?usp=sharing&ouid=106754532266826184774&rtpof=true&sd=true"),
                ("Figma", "https://drive.google.com/file/d/1knKd4dfSJBVB3_aiMpaFYmfScUvGsKvJ/view?usp=drive_link"),
                ("Пособие при возвратах", "https://docs.google.com/presentation/d/1xhMZAX6_U6Em6vGOQRz3S6VmpWt3fKMY/edit?slide=id.p1#slide=id.p1"),
                ("Работа в большой группе", "https://docs.google.com/presentation/d/1f0Ew3g2ge-FqsLrLpU0tYfzBSeiUSbs9/edit?slide=id.g344d84be975_0_0#slide=id.g344d84be975_0_0"),
                ("Физминутки", "https://drive.google.com/drive/folders/12U27TFgMdP6zYQj8sb9ywf0Q_QCU1efF?usp=sharing"),
            ],
        ),
        (
            "Предметные пособия",
            [
                ("MIT App Inventor", "https://docs.google.com/document/d/1JBBTS2XmYA9ZBKNmbF-GMx5RX5NFCo6F/edit?usp=sharing&ouid=106754532266826184774&rtpof=true&sd=true"),
                ("Kotlin", "https://docs.google.com/document/d/1yezlvr8PV9PhMCDZkVG3E5m6L2Dji3ZX/edit?usp=sharing&ouid=106754532266826184774&rtpof=true&sd=true"),
                ("3д моделирование", "https://docs.google.com/document/d/1p1lwVJjD2cTOXB-ELlcd90gg5Ge-RWSL/edit?usp=sharing&ouid=106754532266826184774&rtpof=true&sd=true"),
                ("Развитие soft-skills", "https://docs.google.com/presentation/d/1HdIueYJMXxZel49eO-l0q-XTMQMNV9IQ/edit?usp=sharing&ouid=106754532266826184774&rtpof=true&sd=true"),
                ("Основы веб-разработки", "https://docs.google.com/document/d/10HajL2BqfvGxlVrAf7OvKgKamlC7n6Z6/edit?usp=sharing&ouid=106754532266826184774&rtpof=true&sd=true"),
            ],
        ),
        (
            "Сезонные и мини-курсы",
            [
                ("Лагерь креаторов 2025", "https://drive.google.com/drive/folders/1EU0QqfdlwLLbRBjLSVm83HBSwAB0QhmV?usp=drive_link"),
            ],
        ),
        (
            "Дополнительные пособия",
            [
                ("Установка программ", "https://docs.google.com/document/d/1bjy9oiCXSC6MaArAZx8EwhK9v0FHbP8_wJ15lGVPD3s/edit?usp=drive_link"),
                ("Описание треков программирования", "https://docs.google.com/document/d/10UqLuh9C5naCYCViN50SRqqzhyvU4nN33io9yyfh6g0/edit?usp=drive_link"),
                ("Описание треков дизайна", "https://docs.google.com/document/d/15H6a7QTzsJEaxTTDxhIO-CDYPwr7ju_D/edit?usp=sharing&ouid=113549978808520396460&rtpof=true&sd=true"),
                ("Описание треков It-микса", "https://docs.google.com/document/d/1uV-uW5pc6tRzI2-qHN29IiuIKzq8VMAM/edit?usp=sharing&ouid=113549978808520396460&rtpof=true&sd=true"),
                ("Программы для всех предметов", "https://docs.google.com/document/d/19FlX8C9Rb7mkvpHPQB7oBdMoJiITqtXK5lwIGYyMZTo/edit?usp=drive_link"),
                ("Асинхронные курсы", "https://docs.google.com/presentation/d/1B0ktvn2ixI8Lz-bAYoYtkqoi8XdcNHbP/edit?slide=id.g36317fc5033_0_35#slide=id.g36317fc5033_0_35"),
            ],
        ),
        (
            "Большие группы",
            [
                ("Игры-помощники", "https://docs.google.com/presentation/d/164qRsQXU02PsipeXr4R9lAm6OfgXUof0/edit?usp=sharing&ouid=113549978808520396460&rtpof=true&sd=true"),
                ("Работа со слабыми учениками", "https://docs.google.com/presentation/d/1kZ4g6hnPRN0DkeK9121mCv1LWwNOg45L/edit?usp=sharing&ouid=113549978808520396460&rtpof=true&sd=true"),
            ],
        ),
    ],
}

EXCLUDE_ACTIONS = {
    "archive",
    "archive_and_do_not_reference",
    "archive_or_do_not_reference",
    "archive_and_remove_mentions",
    "archive_or_remove_duplicate",
    "archive_or_remove_from_teacher_kb",
    "archive_or_remove_old_payment_policy",
    "archive_or_remove_duplicate_and_reference_common_policy",
    "merge_or_replace_with_link",
}
CONTENT_ACTIONS = {
    "edit_content",
    "edit_content_or_archive_if_duplicate",
    "clarify_purpose_if_active",
    "rename_or_add_intro",
    "rewrite_content",
    "replace_teamlead_in_coin_questions",
    "remove_outdated_incentive",
    "edit_or_remove_dead_miro_reference",
    "keep_one_article_archive_duplicate_and_clean_roles",
    "check_then_replace_old_terms",
}
HIGH_PRIORITY_IDS = {
    "71d41d1b-0cf2-5dbf-ad1b-a26c61cd4cba",  # FAQ для преподавателей
    "19058cdf-d215-58fa-8e01-54d04778ffbd",  # Важные ссылки
    "11ac17ef-c6cd-5e98-a318-f9233132b43b",  # Вовлечение учеников
    "080a5691-2c34-5da8-a372-f66d6d60165a",  # Методический отдел
    "be3945d9-94b0-479d-9641-6bf190a9dc83",  # Политика оплаты услуг
    "11bc4f5a-1298-4dbc-a82b-b962d7401645",  # Политика оплаты услуг Английского языка
}
MEDIUM_PRIORITY_IDS = {
    "0c43c4bc-c423-5acc-aa0a-b688a50c7858",
    "b602f46f-e08b-4457-a6df-36ce59634927",
    "fe566105-23c6-5a46-b7bf-ad7e4166f207",
    "5975464a-d96c-5fd3-aeab-d39775f26866",  # Перерыв
    "602ea656-1147-515d-8e91-1bf93de6d12c",  # ПДП
    "bd0179fb-dd28-4d73-b24e-c909223bd922",  # Частые техпроблемы
    "7888736b-cf8e-4c92-bc5e-2f1ccf8a4b18",  # Инструкция по работе с платформой
}
PUBLIC_EXCLUDED_IDS = {
    "85b91f83-2250-4f20-95ae-9a3cdea67066",  # НОВОЕ оффер для команды IT
    "3d5b91f7-8eb7-4ca6-9049-70eee5f76d1c",  # Онбординг для заботы
    "15e69f71-7ba5-4b7c-bf6b-81ae137ce9f2",  # Скрипт проведения практики ПУ
    "1bccbbc5-36d2-4b33-b01a-9bb10c7a87f3",  # Удаление неактивных пользователей платформы EasyEng
    "e1dd58ae-35b8-5027-857a-4f43bdbe7aff",  # Чаты для преподавателя
    "ee3376ee-a49b-4bc9-8fee-7af35b3a26f1",  # Формат параллельных уроков (неактуален)
    "02ad5ddb-eadd-5f0f-9c3e-cf00d995f009",  # Перед началом параллельки
    "b73ced4a-19ca-53c4-9915-0a479476b6cb",  # Как установить и настроить Zoom?
    "52228167-ac05-5c4e-a2be-d8f0a45e77c8",  # Что делать если нет свободного зума?
    "6457f88d-c9a0-583b-abc9-c0defef94f66",  # Формат параллельных уроков
    "e9769bda-15b6-50bc-bc48-5d799890f007",  # Инструкция по работе с ботом для замен
    "4a6aec97-2899-588a-8391-fc4b99036fec",  # Дискорд Бот – Пока не работает
    "58349c1b-7775-5a5e-bb20-109744c49a47",  # English: Как получать выплату?
    "1c63ce29-f4ee-5efc-8711-5210a7352b6d",  # English: Как установить и настроить Zoom?
    "b896ba31-be3b-5266-9274-62c4505071d3",  # English: Как зайти в корпоративный Zoom
    "17e8436f-2c98-5e21-b20f-ae5c5c910289",  # English: Что делать если нет свободного зума?
    "2c7e03dd-9452-5ee6-86a2-e9ee4b313b93",  # English: Инструкция по записи и выгрузке уроков
    "51ffdac7-feee-428b-bdad-de92013f0f0f",  # Оповещения преподавателей
    "b51f1082-dddd-5a9d-b85f-d83b24634978",  # English: Важные ссылки
    "6ccc7d31-db10-4a7d-adf9-70f790cdfdb2",  # Похвала и мотивация
    "9f5c7731-4aeb-4db5-81a5-393a153db33e",  # Использование
    "dad5e77b-bdce-4d2a-90de-1b227997947c",  # Без названия
    "c6fda411-7f2e-5067-aadf-dc6d66a0027c",  # Команды преподавателей
    "abb49bb5-6bed-5f48-83e0-001c72d996a2",  # Летние интенсивы
}

PLATFORM_INSTRUCTION_ID = "7888736b-cf8e-4c92-bc5e-2f1ccf8a4b18"
ENGLISH_PAYMENT_ID = "11bc4f5a-1298-4dbc-a82b-b962d7401645"
PREP_RECOMMENDATIONS_ID = "df3dcebb-be11-586d-9a99-02f76db9e48a"
TEACHER_DISCIPLINE_ID = "d0b6f89a-2882-5ec1-acfc-9cc08159b801"
EASYENG_PLATFORM_ID = "0c43c4bc-c423-5acc-aa0a-b688a50c7858"
REPLACEMENTS_ID = "a0c530d1-003a-5e6f-aa05-b5c40d5b9298"
SUPPORT_BOT_ARTICLE_ID = "e2b9c4b9-1023-4780-9c2e-5a55361e9256"
REGISTRATION_ID = "cb58e9b2-cf85-5f65-baf5-dd0311b2bc77"
LIVE_DIGITAL_ID = "04923c37-0ada-587a-84b6-9fcb41cd8161"
TECH_ISSUES_ID = "bd0179fb-dd28-4d73-b24e-c909223bd922"
LESSON_CHECKLIST_ID = "23d2d493-034b-43a0-a38e-32e6cfa019e9"

PLATFORM_HUB_TEXT = """Инструкция по работе с платформой — основной хаб по рабочим действиям на платформе.

В этом разделе должны быть собраны актуальные инструкции по входу и доступу, расписанию и слотам, передаче урока на замену, LiveDigital, аварийной ссылке, EasyCode Lab и действиям при ошибке.

Если нужного сценария нет в статье или возникла нестандартная ошибка, обратитесь к старшему преподавателю или в сообщество преподавателей, топик «Проблемы»."""

DISCIPLINE_UPDATE_TEXT = """Учебная часть, старшие преподаватели и ответственные сотрудники отслеживают соблюдение регламентов, качество уроков и динамику исправления нарушений. Если ситуация требует уточнения, преподаватель обращается к старшему преподавателю или сообщество преподавателей, в топик «Проблемы»."""


def should_exclude_item(item: dict[str, Any]) -> bool:
    action = str(item.get("action") or "")
    status = str(item.get("status") or "")
    if "check" in status or "ask" in status or status == "needs_user_confirmation":
        return False
    if status in {"rejected_do_not_change", "manual_done_do_not_touch"}:
        return False
    if action in EXCLUDE_ACTIONS:
        return True
    if action == "archive":
        return True
    if action.startswith("archive_"):
        return True
    if "_archive_" in action:
        return True
    if action.startswith("check_then_archive"):
        return False
    if action in {
        "archive_or_remove_after_check",
        "archive_or_do_not_reference_after_check",
        "check_then_archive_or_move_unique_links",
    }:
        return False
    if action.endswith("_from_teacher_kb"):
        return True
    if action in {
        "archive_or_remove_old_payment_policy",
        "archive_or_remove_duplicate_if_covered_else_keep_current",
    }:
        return True
    return False


def should_apply_content_item(item: dict[str, Any]) -> bool:
    status = str(item.get("status") or "")
    if not status.startswith("approved"):
        return False
    if "check" in status or "ask" in status:
        return False
    if should_exclude_item(item):
        return False
    return bool(str(item.get("replacement") or "").strip() or item.get("replacement_title"))


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9а-яА-ЯёЁ]+", "-", value).strip("-").lower()
    return slug or "article"


def compact_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def clean_article_text(article: dict[str, Any]) -> str:
    editor_text = text_from_node(article.get("editorContent") or {})
    fallback = str(article.get("text") or "")
    return strip_teamly_urls(editor_text or fallback)


def make_excerpt(text: str, limit: int = 280) -> str:
    compact = compact_text(text)
    if len(compact) <= limit:
        return compact
    return compact[:limit].rstrip() + "..."


def extract_links(text: str) -> list[str]:
    links = re.findall(r"https?://[^\s)\"'<]+", text)
    seen: set[str] = set()
    result: list[str] = []
    for link in links:
        cleaned = link.rstrip(".,;:")
        if cleaned not in seen:
            seen.add(cleaned)
            result.append(cleaned)
    return result


def is_public_blocked_url(url: str) -> bool:
    return any(pattern.search(url) for pattern in PUBLIC_BLOCKED_LINK_PATTERNS)


def strip_teamly_urls(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        url = match.group(0)
        return "" if is_teamly_url(url) else url

    return compact_text(re.sub(r"https?://[^\s)\"'<]+", replace, text))


def article_id_from_url(url: str) -> str | None:
    patterns = [
        r"/at/([0-9a-fA-F-]{32,36})",
        r"/article/([0-9a-fA-F-]{32,36})",
        r"article/([0-9a-fA-F-]{32,36})",
        r"source_id=([0-9a-fA-F-]{32,36})",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def method_database_id_from_url(url: str) -> str | None:
    match = re.search(r"/(?:db|database)/([0-9a-fA-F-]{32,36})", url)
    if match and match.group(1) in METHOD_DATABASES:
        return match.group(1)
    return None


def is_teamly_url(url: str) -> bool:
    if url.startswith(("space/", "/space/", "database/", "/database/", "db/", "/db/")):
        return True
    try:
        return re.sub(r"^www\.", "", __import__("urllib.parse").parse.urlparse(url).netloc) in TEAMLY_HOSTS
    except Exception:
        return False


def section_from_breadcrumbs(breadcrumbs: list[str]) -> str:
    try:
        root_index = breadcrumbs.index(TEACHER_KB_TITLE)
    except ValueError:
        return TEACHER_KB_TITLE
    return breadcrumbs[root_index + 1] if len(breadcrumbs) > root_index + 1 else TEACHER_KB_TITLE


def priority_for(article_id: str) -> int:
    if article_id in HIGH_PRIORITY_IDS:
        return 100
    if article_id in MEDIUM_PRIORITY_IDS:
        return 50
    return 0


def text_from_node(node: Any) -> str:
    if isinstance(node, list):
        return " ".join(text_from_node(child) for child in node)
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return str(node.get("text", ""))
    if node.get("type") == "hardBreak":
        return "\n"
    body = " ".join(text_from_node(child) for child in node.get("content", []) or [])
    if node.get("type") in {
        "paragraph",
        "heading",
        "list_item",
        "bullet_list",
        "ordered_list",
        "todo_item",
        "todo_list",
        "blockquote",
        "panel",
        "table_cell",
        "table_header",
        "table_row",
    }:
        return f"{body}\n"
    return body


def load_agreed_updates() -> tuple[dict[str, list[dict[str, Any]]], set[str], list[dict[str, Any]]]:
    if not PENDING.exists():
        return {}, set(), []

    payload = json.loads(PENDING.read_text(encoding="utf-8"))
    updates: dict[str, list[dict[str, Any]]] = defaultdict(list)
    excluded: set[str] = set()
    new_articles: list[dict[str, Any]] = []

    for item in payload.get("items", []):
        action = item.get("action")
        article_id = item.get("article_id")

        if should_exclude_item(item):
            if article_id:
                excluded.add(article_id)
            for article in item.get("articles", []):
                nested_id = article.get("article_id")
                if nested_id:
                    excluded.add(nested_id)
            continue

        if action == "create_article_and_add_as_work_tool":
            text = (item.get("replacement") or "").strip()
            title = item.get("title") or "Новый материал"
            new_articles.append(
                {
                    "id": f"generated-{slugify(str(title))}",
                    "title": title,
                    "section": "Рабочие инструменты",
                    "breadcrumbs": [TEACHER_KB_TITLE, "Рабочие инструменты", title],
                    "updatedAt": None,
                    "publishedAt": None,
                    "text": text,
                    "html": html_from_plain_text(text),
                }
            )
            continue

        if article_id and (action in CONTENT_ACTIONS or should_apply_content_item(item)):
            updates[article_id].append(item)

    return updates, excluded, new_articles


def load_tree_rows() -> dict[str, list[str]]:
    if not TREE_ALL.exists():
        return {}
    tree = json.loads(TREE_ALL.read_text(encoding="utf-8"))
    rows: dict[str, list[str]] = {database_id: [] for database_id in METHOD_DATABASES}
    for item in tree:
        if not isinstance(item, dict) or item.get("isArchived"):
            continue
        parent_id = str(item.get("parentSpaceId") or "")
        title = compact_text(str(item.get("title") or ""))
        if parent_id in rows and title and title != "Без названия":
            rows[parent_id].append(title)
    return rows


def render_recovered_method_databases(tree_rows: dict[str, list[str]]) -> str:
    sections = ['<section class="method-recovery"><h2>Методические материалы</h2>']
    for database_id, meta in METHOD_DATABASES.items():
        anchor = meta["anchor"]
        sections.append(f'<section id="{anchor}" class="method-db-block">')
        sections.append(f'<h3>{html.escape(meta["title"])}</h3>')
        groups = RECOVERED_METHOD_LINKS.get(anchor, [])
        if groups:
            sections.append('<div class="method-link-grid">')
            for group_title, links in groups:
                sections.append('<article class="method-link-card">')
                sections.append(f'<h4>{html.escape(group_title)}</h4>')
                sections.append("<ul>")
                for label, url in links:
                    sections.append(
                        f'<li><a href="{html.escape(url, quote=True)}" target="_blank" rel="noreferrer">'
                        f"{html.escape(label)}</a></li>"
                    )
                sections.append("</ul></article>")
            sections.append("</div>")
        rows = tree_rows.get(database_id, [])
        if rows:
            sections.append("<details><summary>Каталог материалов из исходной базы</summary><ul>")
            for title in rows:
                sections.append(f"<li>{html.escape(title)}</li>")
            sections.append("</ul></details>")
        sections.append("</section>")
    sections.append("</section>")
    return "".join(sections)


def enhance_method_article_html(rendered_html: str, recovery_html: str) -> str:
    intro_list = (
        '<ol start="1"><li><p><strong><a href="#method-db-general">Общая методическая база знаний</a></strong>'
        '<strong>(нажми меня)</strong></p></li><li><p><strong><a href="#method-db-new-era">Методические материалы “Новая эра”</a></strong>'
        '<strong>(нажми меня)</strong></p></li><li><p><strong><a href="#method-db-all">Методические материалы - таблица по всем направлениям</a></strong>'
        '<strong>(нажми меня)</strong></p></li></ol>'
    )
    jump_list = (
        '<nav class="method-jump-list" aria-label="Разделы методических материалов">'
        '<a class="method-jump-card" href="#method-db-general"><span>Общая методическая база знаний</span></a>'
        '<a class="method-jump-card" href="#method-db-new-era"><span>Методические материалы “Новая эра”</span></a>'
        '<a class="method-jump-card" href="#method-db-all"><span>Методические материалы по всем направлениям</span></a>'
        "</nav>"
    )
    if intro_list in rendered_html:
        return rendered_html.replace(intro_list, jump_list + recovery_html, 1)

    schedule_heading = "<p><strong>Расписание вебинаров </strong></p>"
    if schedule_heading in rendered_html:
        return rendered_html.replace(schedule_heading, jump_list + recovery_html + schedule_heading, 1)
    return rendered_html + recovery_html


def method_recovery_text(tree_rows: dict[str, list[str]]) -> str:
    parts: list[str] = ["Методические материалы"]
    for database_id, meta in METHOD_DATABASES.items():
        parts.append(meta["title"])
        for title, links in RECOVERED_METHOD_LINKS.get(meta["anchor"], []):
            parts.append(title)
            parts.extend(label for label, _ in links)
        parts.extend(tree_rows.get(database_id, []))
    return " ".join(parts)


def html_from_plain_text(text: str, article_ids: set[str] | None = None) -> str:
    blocks = []
    for paragraph in re.split(r"\n{2,}", text.strip()):
        lines = "<br>".join(html.escape(line) for line in paragraph.splitlines())
        blocks.append(f"<p>{linkify_plain_urls(lines, article_ids or set())}</p>")
    return "\n".join(blocks)


def normalize_public_text(article_id: str, text: str) -> str:
    text = re.sub(r"https?://(?:www\.)?rutube\.ru/[^\s)\"'<]+", "", text, flags=re.IGNORECASE)
    text = text.replace("зарплата", "выплата").replace("Зарплата", "Выплата")
    text = re.sub(r"LiveDigital/Zoom/Google Meet", "LiveDigital", text, flags=re.IGNORECASE)
    text = re.sub(r"Live Digital/Google Meet", "LiveDigital", text, flags=re.IGNORECASE)
    text = re.sub(r"Google\s*Meet|GoogleMeet|гугл\s*мит", "LiveDigital", text, flags=re.IGNORECASE)
    text = re.sub(r"\bZoom\b|зум", "LiveDigital", text, flags=re.IGNORECASE)
    text = re.sub(r"Rutube|рутуб", "платформа", text, flags=re.IGNORECASE)
    text = re.sub(r"тимлид(?:ер|ера|еру|ером|еры|еров|ерам|ерами)?", "старший преподаватель", text, flags=re.IGNORECASE)
    text = re.sub(r"\bТЛ\b", "старший преподаватель", text)
    if article_id == PREP_RECOMMENDATIONS_ID:
        text = text.replace("Сумму выплат определяет регион", "Размер выплаты определяет регион")
        text = text.replace("среднюю зарплату выпускников", "средний доход выпускников")
    article_replacements = ARTICLE_TEXT_REPLACEMENTS.get(article_id, [])
    for old, new in article_replacements:
        text = text.replace(old, new)
    return text


def normalize_public_html(article_id: str, rendered_html: str) -> str:
    rendered_html = re.sub(r"https?://(?:www\.)?rutube\.ru/[^\s)\"'<]+", "", rendered_html, flags=re.IGNORECASE)
    rendered_html = re.sub(
        r"(?<![>/])@ec_tsupport_bot(?!</a>)",
        '<a href="https://t.me/ec_tsupport_bot" target="_blank" rel="noreferrer">@ec_tsupport_bot</a>',
        rendered_html,
    )
    rendered_html = rendered_html.replace("зарплата", "выплата").replace("Зарплата", "Выплата")
    rendered_html = re.sub(r"LiveDigital/Zoom/Google Meet", "LiveDigital", rendered_html, flags=re.IGNORECASE)
    rendered_html = re.sub(r"Live Digital/Google Meet", "LiveDigital", rendered_html, flags=re.IGNORECASE)
    rendered_html = re.sub(r"Google\s*Meet|GoogleMeet|гугл\s*мит", "LiveDigital", rendered_html, flags=re.IGNORECASE)
    rendered_html = re.sub(r"\bZoom\b|зум", "LiveDigital", rendered_html, flags=re.IGNORECASE)
    rendered_html = re.sub(r"Rutube|рутуб", "платформа", rendered_html, flags=re.IGNORECASE)
    rendered_html = rendered_html.replace("@slice13", '<a href="https://t.me/ec_tsupport_bot" target="_blank" rel="noreferrer">@ec_tsupport_bot</a>')
    rendered_html = re.sub(r"тимлид(?:ер|ера|еру|ером|еры|еров|ерам|ерами)?", "старший преподаватель", rendered_html, flags=re.IGNORECASE)
    rendered_html = re.sub(r"\bТЛ\b", "старший преподаватель", rendered_html)
    if article_id == PREP_RECOMMENDATIONS_ID:
        rendered_html = rendered_html.replace("Сумму выплат определяет регион", "Размер выплаты определяет регион")
        rendered_html = rendered_html.replace("среднюю зарплату выпускников", "средний доход выпускников")
    for old, new in ARTICLE_TEXT_REPLACEMENTS.get(article_id, []):
        rendered_html = rendered_html.replace(html.escape(old), html.escape(new))
        rendered_html = rendered_html.replace(old, new)
    return rendered_html


ARTICLE_TEXT_REPLACEMENTS = {
    EASYENG_PLATFORM_ID: [
        ("Все наши уроки проводятся по видеосвязи через LiveDigital/Zoom/Google Meet и платформы EasyEng.", "Все наши уроки проводятся по видеосвязи через LiveDigital и платформу EasyEng."),
    ],
    REPLACEMENTS_ID: [
        ("В случае технических проблем, урок стоит провести в LD или ОЧЕНЬ крайнем случае Google Meet или другой сервис. Как пользоваться Google Meet? Для этого необходимо пройти регистрацию в Google (если у вас нет аккаунта в Google) и создать постоянную ссылку для подключения к встрече. Урок необходимо записать и пред", "В случае технических проблем действуйте по актуальному регламенту замен и переносов. Если провести урок в LiveDigital невозможно, зафиксируйте ситуацию в рабочих инструментах и обратитесь к старшему преподавателю или в сообщество преподавателей, топик «Проблемы»."),
    ],
    SUPPORT_BOT_ARTICLE_ID: [
        ("Если остались вопросы, то пишите @slice13", "Если остались вопросы, напишите в бот запросов в поддержку @ec_tsupport_bot"),
    ],
    REGISTRATION_ID: [
        ("Ссылка на GoogleMeet создается 1 раз и сохраняется в закрепленных сообщениях в вашем чате.", "Основная ссылка на урок находится на платформе. Для аварийных ситуаций используйте актуальный регламент по экстренной ссылке."),
        ("Если у вас есть группа/индивидуальное, которое будет заниматься в Meet они будут всегда подключаться по этой ссылке.", "Если платформа или ссылка работают некорректно, передайте проблему через рабочие каналы школы."),
    ],
    LIVE_DIGITAL_ID: [
        ("Занятия происходят внутри платформы, без участия zoom, google meet…", "Занятия происходят внутри платформы через LiveDigital."),
    ],
    TECH_ISSUES_ID: [
        ("Если не работает Live Digital: Используем Google Meet", "Если не работает LiveDigital: действуем по актуальному регламенту"),
        ("Чтобы оперативно разослать ученикам ссылки на новую конференцию в гугл мит, воспользуйтесь кнопкой “Обновить ссылку” в карте курса. Создайте конференцию в google meet и введите ссылку на нее в это поле. Нажмите “Отправить”.", "Если нужна аварийная ссылка, используйте соответствующий инструмент в CRM/платформе и зафиксируйте ситуацию в рабочих каналах."),
    ],
    LESSON_CHECKLIST_ID: [
        ("Загрузить запись занятия на платформу (крайние ситуации Rutube и Яндекс Диск школы)", "Загрузить запись занятия на платформу"),
    ],
}


def linkify_plain_urls(value: str, article_ids: set[str]) -> str:
    def replace(match: re.Match[str]) -> str:
        url = match.group(1)
        target_id = article_id_from_url(url)
        if target_id and target_id in article_ids:
            return f'<a href="#article={target_id}" data-article-id="{target_id}">связанная статья</a>'
        if is_teamly_url(url):
            return ""
        return f'<a href="{html.escape(url, quote=True)}" target="_blank" rel="noreferrer">{html.escape(url)}</a>'

    return re.sub(
        r"(https?://[^\s<]+)",
        replace,
        value,
    )


def attrs_to_link(attrs: dict[str, Any]) -> str:
    link = attrs.get("link") or {}
    if isinstance(link, dict):
        return str(link.get("url") or "")
    return ""


class Renderer:
    def __init__(self, article_ids: set[str]) -> None:
        self.article_ids = article_ids
        self.internal_refs: set[str] = set()
        self.external_links: list[str] = []

    def render(self, node: Any) -> str:
        if isinstance(node, list):
            return "".join(self.render(child) for child in node)
        if not isinstance(node, dict):
            return ""

        node_type = node.get("type")
        content = node.get("content", []) or []

        if node_type == "doc":
            return self.render(content)
        if node_type == "text":
            return self.render_text(node)
        if node_type == "hardBreak":
            return "<br>"
        if node_type == "paragraph":
            body = self.render(content)
            return f"<p>{body}</p>" if body.strip() else ""
        if node_type == "heading":
            level = min(max(int((node.get("attrs") or {}).get("level", 2)), 2), 4)
            return f"<h{level}>{self.render(content)}</h{level}>"
        if node_type == "bullet_list":
            return f"<ul>{self.render(content)}</ul>"
        if node_type == "ordered_list":
            start = (node.get("attrs") or {}).get("start", 1)
            return f'<ol start="{html.escape(str(start), quote=True)}">{self.render(content)}</ol>'
        if node_type == "list_item":
            return f"<li>{self.render(content)}</li>"
        if node_type == "horizontal_rule":
            return "<hr>"
        if node_type == "blockquote":
            return f"<blockquote>{self.render(content)}</blockquote>"
        if node_type == "panel":
            return f'<aside class="kb-note">{self.render(content)}</aside>'
        if node_type == "expandSection":
            title = ""
            body = []
            for child in content:
                if child.get("type") == "expandTitle":
                    title = compact_text(text_from_node(child))
                else:
                    body.append(child)
            summary = html.escape(title or "Подробнее")
            return f"<details><summary>{summary}</summary>{self.render(body)}</details>"
        if node_type == "layoutSection":
            return f'<div class="layout-section">{self.render(content)}</div>'
        if node_type == "layoutColumn":
            width = (node.get("attrs") or {}).get("width")
            style = ""
            try:
                width_value = float(width)
                if width_value > 0:
                    style = f' style="--column-width: {width_value:g}%"'
            except (TypeError, ValueError):
                pass
            return f'<div class="layout-column"{style}>{self.render(content)}</div>'
        if node_type in {"expandTitle", "expandContent"}:
            return self.render(content)
        if node_type == "table":
            return f'<div class="table-wrap"><table>{self.render(content)}</table></div>'
        if node_type == "table_row":
            return f"<tr>{self.render(content)}</tr>"
        if node_type in {"table_cell", "table_header"}:
            tag = "th" if node_type == "table_header" else "td"
            return f"<{tag}>{self.render(content)}</{tag}>"
        if node_type == "todo_list":
            return f'<ul class="todo-list">{self.render(content)}</ul>'
        if node_type == "todo_item":
            checked = " checked" if (node.get("attrs") or {}).get("checked") else ""
            return f'<li><input type="checkbox" disabled{checked}> {self.render(content)}</li>'
        if node_type == "codeBlock":
            return f"<pre><code>{html.escape(text_from_node(node))}</code></pre>"
        if node_type in {"mediaWrapper", "media", "image", "remote_video"}:
            return self.render_media(node)
        if node_type == "nestedArticle":
            return self.render_nested_article(node)
        if node_type in {"tableOfContents", "codeEditor"}:
            return ""
        return self.render(content)

    def render_text(self, node: dict[str, Any]) -> str:
        marks = node.get("marks", []) or []
        link_mark = next((mark for mark in marks if mark.get("type") == "link"), None)
        value = html.escape(str(node.get("text", ""))) if link_mark else self.render_plain_text(str(node.get("text", "")))
        for mark in marks:
            mark_type = mark.get("type")
            if mark_type == "bold":
                value = f"<strong>{value}</strong>"
            elif mark_type == "italic":
                value = f"<em>{value}</em>"
            elif mark_type == "underline":
                value = f"<u>{value}</u>"
            elif mark_type == "code":
                value = f"<code>{value}</code>"
            elif mark_type == "link":
                href = attrs_to_link(mark.get("attrs") or {})
                value = self.wrap_link(value, href)
        return value

    def render_plain_text(self, value: str) -> str:
        parts: list[str] = []
        cursor = 0
        for match in re.finditer(r"https?://[^\s)\"'<]+", value):
            parts.append(html.escape(value[cursor : match.start()]))
            url = match.group(0).rstrip(".,;:")
            trailing = match.group(0)[len(url) :]
            target_id = article_id_from_url(url)
            if target_id and target_id in self.article_ids:
                self.internal_refs.add(target_id)
                parts.append(f'<a href="#article={target_id}" data-article-id="{target_id}">связанная статья</a>')
            elif not is_teamly_url(url):
                self.external_links.append(url)
                safe_url = html.escape(url, quote=True)
                parts.append(f'<a href="{safe_url}" target="_blank" rel="noreferrer">{html.escape(url)}</a>')
            parts.append(html.escape(trailing))
            cursor = match.end()
        parts.append(html.escape(value[cursor:]))
        return "".join(parts)

    def wrap_link(self, label: str, href: str) -> str:
        if not href:
            return label
        target_id = article_id_from_url(href)
        if target_id and target_id in self.article_ids:
            self.internal_refs.add(target_id)
            safe_label = "связанная статья" if "teamly.ru" in label else label
            return f'<a href="#article={target_id}" data-article-id="{target_id}">{safe_label}</a>'
        database_id = method_database_id_from_url(href)
        if database_id:
            anchor = METHOD_DATABASES[database_id]["anchor"]
            safe_label = METHOD_DATABASES[database_id]["title"] if is_teamly_url(label) else label
            return f'<a href="#{anchor}">{safe_label}</a>'
        if is_teamly_url(href):
            return "" if "teamly.ru" in label else label
        self.external_links.append(href)
        safe_href = html.escape(href, quote=True)
        return f'<a href="{safe_href}" target="_blank" rel="noreferrer">{label}</a>'

    def render_media(self, node: dict[str, Any]) -> str:
        attrs = node.get("attrs") or {}
        src = str(attrs.get("src") or "")
        meta = attrs.get("_meta") or {}
        title_raw = str(meta.get("title") or "иллюстрация")
        title = html.escape(title_raw)
        media_id = html.escape(str(attrs.get("id") or meta.get("attachmentId") or ""), quote=True)
        source_id = html.escape(str((attrs.get("_context") or {}).get("id") or ""), quote=True)
        if not src or is_teamly_url(src):
            return (
                '<span class="media-slot" '
                f'data-media-id="{media_id}" '
                f'data-source-article-id="{source_id}" '
                f'data-title="{html.escape(title_raw, quote=True)}" '
                'title="Место для иллюстрации из исходной базы">'
                f'Иллюстрация будет добавлена позже: {title}'
                "</span>"
            )
        safe_src = html.escape(src, quote=True)
        if node.get("type") in {"image", "media"}:
            return f'<img src="{safe_src}" alt="{title}" loading="lazy">'
        return f'<p><a href="{safe_src}" target="_blank" rel="noreferrer">{title}</a></p>'

    def render_nested_article(self, node: dict[str, Any]) -> str:
        attrs = node.get("attrs") or {}
        target_id = str(attrs.get("sourceId") or attrs.get("id") or "")
        title = html.escape(str(attrs.get("title") or "Связанная статья"))
        if target_id in self.article_ids:
            self.internal_refs.add(target_id)
            return f'<p><a href="#article={target_id}" data-article-id="{target_id}">{title}</a></p>'
        return f"<p>{title}</p>"


def apply_agreed_updates(
    article: dict[str, Any],
    text: str,
    rendered_html: str,
    updates: list[dict[str, Any]],
) -> tuple[str, str, str]:
    title = str(article.get("title") or "")
    additions: list[str] = []

    for update in updates:
        replacement_title = update.get("replacement_title")
        if replacement_title:
            title = str(replacement_title)

        replacement = str(update.get("replacement") or "").strip()
        if replacement and replacement not in text and replacement not in additions:
            additions.append(replacement)

    if additions:
        addition_text = "\n\n".join(additions)
        addition_text_for_text = strip_teamly_urls(addition_text)
        text = "\n\n".join([addition_text_for_text, text]).strip()
        rendered_html = f'<section class="article-update"><h2>Актуальная информация</h2>{html_from_plain_text(addition_text)}</section>{rendered_html}'

    return title, text, rendered_html


def main() -> None:
    articles_payload = json.loads(ARTICLES.read_text(encoding="utf-8"))
    agreed_updates, excluded_ids, generated_articles = load_agreed_updates()
    method_tree_rows = load_tree_rows()

    selected = [
        article
        for article in articles_payload.get("articles", [])
        if TEACHER_KB_ID in article.get("breadcrumb_ids", [])
        and article.get("id") not in excluded_ids
        and article.get("id") not in PUBLIC_EXCLUDED_IDS
        and not article.get("archived")
        and not article.get("is_hidden")
    ]
    final_ids = {str(article.get("id")) for article in selected}
    final_ids.update(str(article["id"]) for article in generated_articles)

    articles: list[dict[str, Any]] = []
    sections: dict[str, int] = defaultdict(int)

    for article in selected:
        article_id = str(article.get("id"))
        text = clean_article_text(article)
        renderer = Renderer(final_ids)
        rendered_html = renderer.render(article.get("editorContent") or {})
        title, text, rendered_html = apply_agreed_updates(
            article,
            text,
            rendered_html,
            agreed_updates.get(article_id, []),
        )
        if article_id == PLATFORM_INSTRUCTION_ID and PLATFORM_HUB_TEXT not in text:
            text = "\n\n".join([PLATFORM_HUB_TEXT, text]).strip()
            rendered_html = (
                '<section class="article-update"><h2>Актуальная структура</h2>'
                + html_from_plain_text(PLATFORM_HUB_TEXT, final_ids)
                + "</section>"
                + rendered_html
            )
        if article_id == TEACHER_DISCIPLINE_ID and DISCIPLINE_UPDATE_TEXT not in text:
            text = "\n\n".join([DISCIPLINE_UPDATE_TEXT, text]).strip()
            rendered_html = (
                '<section class="article-update"><h2>Актуальная информация</h2>'
                + html_from_plain_text(DISCIPLINE_UPDATE_TEXT, final_ids)
                + "</section>"
                + rendered_html
            )
        text = normalize_public_text(article_id, text)
        rendered_html = normalize_public_html(article_id, rendered_html)
        if article_id == METHOD_ARTICLE_ID:
            recovery_html = render_recovered_method_databases(method_tree_rows)
            recovery_text = method_recovery_text(method_tree_rows)
            rendered_html = enhance_method_article_html(rendered_html, recovery_html)
            text = compact_text(" ".join([text, recovery_text]))
        breadcrumbs = article.get("breadcrumb_titles", [])
        if breadcrumbs:
            breadcrumbs = [*breadcrumbs[:-1], title]
        section = section_from_breadcrumbs(breadcrumbs)
        sections[section] += 1

        links = [link for link in renderer.external_links if not is_teamly_url(link) and not is_public_blocked_url(link)]
        articles.append(
            {
                "id": article_id,
                "title": title,
                "section": section,
                "breadcrumbs": breadcrumbs,
                "updatedAt": article.get("tree", {}).get("updatedAt"),
                "publishedAt": article.get("tree", {}).get("publishedAt"),
                "excerpt": make_excerpt(text),
                "text": text,
                "html": rendered_html,
                "links": sorted(set(links)),
                "relatedArticleIds": sorted(renderer.internal_refs),
                "priority": priority_for(article_id),
                "searchText": text,
            }
        )

    for article in generated_articles:
        section = str(article["section"])
        sections[section] += 1
        article["text"] = strip_teamly_urls(str(article["text"]))
        article["html"] = html_from_plain_text(str(article["text"]), final_ids)
        article["excerpt"] = make_excerpt(str(article["text"]))
        article["links"] = [
            link
            for link in extract_links(str(article["text"]))
            if not is_teamly_url(link) and not is_public_blocked_url(link)
        ]
        article["relatedArticleIds"] = []
        article["priority"] = priority_for(str(article["id"]))
        article["searchText"] = article["text"]
        articles.append(article)

    articles.sort(key=lambda item: (str(item["section"]), str(item["title"] or "")))
    payload = {
        "generatedAt": "2026-10-09",
        "title": TEACHER_KB_TITLE,
        "source": "Teamly backup",
        "rootArticleId": TEACHER_KB_ID,
        "articleCount": len(articles),
        "sections": [
            {"name": name, "count": count}
            for name, count in sorted(sections.items(), key=lambda pair: pair[0])
        ],
        "articles": articles,
    }

    OUTPUT_JSON.parent.mkdir(exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    OUTPUT_JS.write_text(
        "window.KB_DATA = "
        + json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
        + ";\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_JSON.relative_to(ROOT)} and {OUTPUT_JS.relative_to(ROOT)} with {len(articles)} articles")


if __name__ == "__main__":
    main()
