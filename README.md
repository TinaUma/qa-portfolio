# QA Portfolio — Тина Юмашева

> **Статус:** Кейс 001 — Завершён · портфолио пополняется: новые кейсы добавляются по мере прохождения обучения на реальном продукте.

![QA Tests](https://github.com/TinaUma/qa-portfolio/actions/workflows/tests.yml/badge.svg)

Собираю портфолио параллельно с реальной QA-работой: пишу тест-кейсы, оформляю баг-репорты, тестирую формы и API на действующем продукте (Сортула). Каждая папка ниже — это законченный кейс тестирования, оформленный как полноценный рабочий артефакт, а не учебный «проект для галочки».

---

## Кейсы

| № | Название | Тип | Статус |
|---|---|---|---|
| 001 | Тестирование формы регистрации/авторизации (staging.sortula.ru) | Ручное UI, API (Postman), БД (SQL/DBeaver), логи, мобилка, pytest + requests, Playwright (UI), Allure-отчёты, Page Object Model, Service Object, Docker + PostgreSQL в CI, pytest-mock | Завершён — 14 дефектов, 18 автотестов, POM + Service Object + DB smoke test + моки в CI |

---

## Структура каждого кейса

Каждая папка кейса устроена одинаково:

```
cases/
└── NNN-название-фичи/
    ├── README.md           ← краткое summary: что сделано, сколько багов, инструменты
    ├── test-analysis.md    ← декомпозиция требований, объекты тестирования, серые зоны
    ├── checklist.md        ← чек-лист проверок с результатами
    ├── bug-reports.md      ← найденные баги в стандартном формате
    └── evidence/           ← скриншоты, референсы интерфейса
```

**Формат баг-репорта:** Severity · Priority · Окружение · Шаги воспроизведения · Ожидаемый результат · Фактический результат · Доказательства

---

## Обо мне

Перехожу в QA Engineering с бэкграундом в AI-разработке. Понимаю кодовую базу изнутри — это помогает тестировать осознанно: я вижу, что и почему может сломаться, а не просто следую чек-листу вслепую.

- **Инструменты:** ручное тестирование, Chrome DevTools (Network + Device Mode), Postman Desktop, DBeaver, SQL, Lighthouse, Android Studio + AVD Manager, Logcat, Docker, `grep`, GitLab · pytest, requests, Playwright, Allure, psycopg2, GitHub Actions, Page Object Model, Service Object, Docker Compose, PostgreSQL service в CI, pytest-mock
- **Фокус:** функциональное тестирование, тест-дизайн, API-тестирование, UI-автоматизация, архитектура тестовых фреймворков, регресс, баг-репортинг
- **Язык:** русский

**AI-инженерное портфолио:** [tinacodes.space](https://tinacodes.space)
**GitHub:** [github.com/TinaUma](https://github.com/TinaUma)
