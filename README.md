# База знаний преподавателей EasyCode

Статический сайт для GitHub Pages с резервной базой знаний для преподавателей EasyCode.

База работает автономно: полные тексты статей хранятся в репозитории, внутренние связи между статьями ведут на локальные страницы внутри сайта, ссылки на Teamly из публичных данных удаляются.

## Что внутри

- `index.html` — главная страница базы знаний.
- `styles.css` — оформление.
- `app.js` — поиск, фильтры и отрисовка карточек.
- `data/teamly_articles.json` — публичные очищенные данные для сайта.
- `data/teamly_articles.js` — те же данные в формате JS, чтобы база открывалась даже локально через `file://`.
- локальные рабочие материалы добавлены в `.gitignore` и не должны уходить в GitHub.

## Обновить данные

```bash
python3 scripts/build_public_data.py
```

После генерации закоммитьте только файлы сайта, workflow, README, скрипт генерации и `data/teamly_articles.json`.

## Опубликовать на GitHub Pages

1. Создайте репозиторий на GitHub, например `teacher-knowledge-base`.
2. Выполните в этой папке:

```bash
git add .
git commit -m "Add teacher knowledge base site"
git branch -M main
git remote add origin https://github.com/USER/teacher-knowledge-base.git
git push -u origin main
```

3. В настройках репозитория откройте `Settings -> Pages`.
4. В `Build and deployment` выберите `GitHub Actions`.
5. Дождитесь выполнения workflow `Deploy static site to Pages`.

Сайт будет доступен по адресу:

```text
https://USER.github.io/teacher-knowledge-base/
```
