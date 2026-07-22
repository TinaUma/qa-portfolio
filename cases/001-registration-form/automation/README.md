# Автоматизированное тестирование: Регистрация (Спринты 9–18)

![QA Tests](https://github.com/TinaUma/qa-portfolio/actions/workflows/tests.yml/badge.svg)

**Тестировщик:** Тина Юмашева
**Дата:** 15.07.2026 – 20.07.2026 (продолжается)
**Окружение:** localhost:8001 (API-тесты) | staging.sortula.ru (UI-тесты)
**Инструменты:** Python 3.12, pytest 9.0, requests, Playwright (pytest-playwright)

---

## Что тестируем

Тот же флоу регистрации что в Спринтах 1-8 — теперь автоматизированными тестами.

Ручная проверка через Postman (Спринт 5) подтвердила поведение API.
Автотесты фиксируют это поведение и позволяют проверять его при каждом изменении кода.

---

## Структура

| Файл | Что проверяет |
|---|---|
| `conftest.py` | Фикстура `registered_user` — создаёт пользователя перед тестом |
| `test_register_basic.py` | Дубликат email → 409 (первый тест против живой Sortula) |
| `test_register_negative.py` | Параметризованные негативные сценарии |

---

## Матрица тестов

| Сценарий | Метод | Фикстура | Ожидаемый код | Статус |
|---|---|---|---|---|
| Дубликат email | POST /v1/auth/register | registered_user | 409 | ✅ PASSED |
| Невалидный формат email | POST /v1/auth/register | — | 422 | ✅ PASSED |
| Пустой email | POST /v1/auth/register | — | 422 | ✅ PASSED |
| Поле email отсутствует | POST /v1/auth/register | — | 422 | ✅ PASSED |

**Результат прогона:** 5 passed, 0.41s

---

## Ключевые находки

**Архитектурная особенность Sortula:** поле `password` при `POST /v1/auth/register`
игнорируется — пароль устанавливается отдельным эндпоинтом `POST /v1/auth/set-password`.
Поэтому тесты на "пустой пароль" при регистрации возвращают 201, а не 422.
Это намеренное архитектурное решение (подтверждено в Спринте 5).

---

## Как запустить

```bash
# Поднять Docker dev-стек Sortula
docker compose -f docker-compose.dev.yml up -d

# Запустить все тесты
cd cases/001-registration-form/automation
pytest -v

# Запустить один файл
pytest test_register_negative.py -v
```

---

## UI-тесты: Playwright (Спринт 13)

**Файл:** `ui/test_register_via_ui.py`  
**Окружение:** staging.sortula.ru  
**Запуск:** `pytest ui/ -v`  

| Тест | Что проверяет | Локатор | Результат |
|---|---|---|---|
| `test_submit_disabled_without_terms` | Кнопка disabled без чекбокса | `[data-testid="register-submit"]` | ✅ PASSED |
| `test_register_via_ui` | Успешная регистрация → `.alert-success` | `[data-testid="register-email"]`, `[data-testid="register-terms"]` | ✅ PASSED |

**Результат прогона:** 2 passed, 6.65s

**Скрины ручной проверки локаторов:** `../evidence/sprint-13/`

---

## Allure-отчёты (Спринт 14)

**Что добавлено:** декораторы `@allure.title`, `@allure.description`, `@allure.severity` и `allure.step()` к UI-тестам.

**Запуск с Allure:**
```bash
pytest ui/ -v --alluredir=ui/allure-results
allure serve ui/allure-results
```

| Декоратор | Где применён | Результат в отчёте |
|---|---|---|
| `@allure.title("...")` | Оба теста | Читаемое название вместо имени функции |
| `@allure.severity(CRITICAL)` | Оба теста | Приоритет в дашборде |
| `with allure.step("...")` | Каждый шаг | Раскрываемые шаги в деталях теста |

**Результат прогона:** 2 passed, 4.93s — отчёт открывается в браузере

**Скрины Allure-отчёта:** `../evidence/sprint-14/`

---

## Сквозной тест: psycopg2 (Спринт 15)

**Файл:** `ui/test_register_db_verify.py`  
**Тип:** cross-layer test — API → PostgreSQL верификация  
**Среда:** localhost:8001 (backend) + localhost:5433 (postgres, Docker dev-стек)  
**Запуск:** `pytest ui/test_register_db_verify.py -v`

| Тест | Что проверяет | Результат |
|---|---|---|
| `test_register_via_api_verified_in_db` | POST /v1/auth/register → SELECT из users | ✅ PASSED |

**Ключевое понимание:** UI-тесты и DB-верификация должны работать в одной среде. Смешивание staging UI + локальная БД даёт ложное падение — это не баг кода, а баг тестовой конфигурации.

**Результат прогона:** 1 passed, 2.24s

**Скрин прогона:** `../evidence/sprint-14/psycopg2-cross-layer-passed.PNG`

---

## CI/CD: GitHub Actions (Спринт 16)

**Файл:** `.github/workflows/tests.yml`  
**Триггер:** push и pull_request в ветку master  
**Среда:** ubuntu-latest (GitHub-сервер)

**Что делает pipeline:**
1. `actions/checkout@v4` — скачивает код
2. `setup-python@v5` — устанавливает Python 3.12
3. `pip install pytest pytest-playwright allure-pytest` — зависимости
4. `playwright install chromium` — браузер
5. `pytest test_register_via_ui.py -v` — запускает UI-тесты против staging.sortula.ru

**Результат первого прогона:** ✅ passed, 39s

**Почему API/DB тесты не в CI:** они требуют локального Docker-стека Sortula (localhost:8001 + localhost:5433) — в GitHub-среде его нет. Это нормально: часть тестов запускается только локально.

**Скрины:** `../evidence/sprint-16/`

---

## Page Object Model + Service Object (Спринт 18)

**Что изменилось:** рефакторинг под архитектурные паттерны Middle-уровня.

**Структура после рефакторинга:**

```
automation/
├── pages/
│   └── register_page.py    ← RegisterPage: локаторы и действия UI
├── services/
│   └── auth_service.py     ← AuthService: URL и структура API-запросов
└── ui/
    ├── test_register_via_ui.py      ← только сценарий, нет .locator()
    └── test_register_db_verify.py   ← только сценарий, нет requests.post()
```

**Принцип:** каждый слой знает своё. Тест знает **что** проверить. PageObject знает **где** найти элемент. AuthService знает **как** вызвать API. Если локатор или URL меняется — правишь в одном месте.

| Файл | До рефакторинга | После |
|---|---|---|
| `test_register_via_ui.py` | `page.locator('[data-testid="..."]')` прямо в тесте | `register_page.fill_email(email)` |
| `test_register_db_verify.py` | `requests.post("http://localhost:8001/...")` прямо в тесте | `auth.register(email)` |

**Результат:** pytest ui/ -v → **2 passed**; pytest ui/test_register_db_verify.py -v → **1 passed**

**Скрины:** `../evidence/sprint-18/`

---

## Docker + PostgreSQL service в CI (Спринт 19)

**Что добавлено:** второй CI job с PostgreSQL-контейнером — инфраструктурный smoke test работает в GitHub Actions без локального Docker-стека Sortula.

**Структура после спринта 19:**

```
.github/workflows/tests.yml
├── job: ui-tests    ← Playwright → staging.sortula.ru (как раньше)
└── job: db-tests    ← psycopg2 → postgres:15 контейнер (новый)
    └── services:
        └── postgres:15 с health-check (pg_isready)
```

**Новый тест:** `ui/test_db_direct.py`

| Тест | Что проверяет | Результат |
|---|---|---|
| `test_db_connection` | psycopg2 подключается к PostgreSQL | ✅ PASSED |
| `test_db_insert_and_select` | CREATE TABLE → INSERT → SELECT → cleanup | ✅ PASSED |

**Ключевые понятия:**
- `services: postgres:` в GitHub Actions — GitHub поднимает контейнер перед запуском steps
- `health-check: pg_isready` — pipeline ждёт готовности БД, не запускает тест раньше времени
- `os.getenv("DB_NAME", "sortula")` — конфиг через env-переменные: локально берёт `sortula`, в CI переопределяется на `sortula_test`
- `conftest.py` загружается для всех тестов в поддиректориях — все его зависимости нужны во всех job-ах

**Почему не `test_register_db_verify.py` в CI:** он делает POST на `localhost:8001` (backend) — в CI его нет. `test_db_direct.py` обходит это: тестирует только PostgreSQL-слой напрямую.

**Результат в CI:** оба job параллельно — `ui-tests` 33s + `db-tests` 32s → **Success**

**Скрины:** `../evidence/sprint-19/`

---

## pytest-mock — изоляция тестов (Спринт 20)

**Файл:** `ui/test_register_mocked.py`
**Тип:** unit-уровень с моками — без Docker, без backend, без сети
**Запуск:** `pytest ui/test_register_mocked.py -v`

| Тест | Что мокаем | Механизм | Результат |
|---|---|---|---|
| `test_register_success` | `requests.post` → 201 | `return_value` | ✅ PASSED |
| `test_register_duplicate_email` | `requests.post` → 409 | `return_value` | ✅ PASSED |
| `test_register_invalid_email` | `requests.post` → 422 | `return_value` | ✅ PASSED |
| `test_register_server_error` | `requests.post` → 500 | `return_value` | ✅ PASSED |
| `test_register_timeout` | Timeout исключение | `side_effect` | ✅ PASSED |
| `test_register_connection_error` | ConnectionError исключение | `side_effect` | ✅ PASSED |

**Результат прогона:** 6 passed, 0.03s — в 130 раз быстрее DB-теста из Спринта 19.

**Ключевые концепции:**
- `mocker.patch("services.auth_service.requests.post")` — патчим там где используется, не где определено
- `return_value` — что вернуть вместо реального ответа сервера
- `side_effect` — какое исключение бросить (Timeout, ConnectionError)
- `mock.assert_called_once()` — проверяем что запрос был сделан ровно 1 раз

**Почему без Docker:** `mocker.patch` перехватывает вызов до того как он уходит в сеть. Сервер не знает что его вызвали — потому что его и не вызывали.

**Скрины:** `../evidence/sprint-20/`

---

## Контрактное тестирование: Pact (Спринт 21)

**Файл:** `ui/test_register_pact.py`
**Тип:** Consumer-Driven Contract Testing — без Docker, без backend, без сети
**Запуск:** `pytest ui/test_register_pact.py -v`
**Контракт:** `ui/pacts/qa-portfolio-sortula-backend.json`

| Тест | Состояние (given) | Ожидаемый статус | Результат |
|---|---|---|---|
| `test_register_success` | пользователь не существует | 201 | ✅ PASSED |
| `test_register_duplicate_email` | пользователь уже существует | 409 | ✅ PASSED |
| `test_register_invalid_email` | невалидный формат email | 422 | ✅ PASSED |

**Результат прогона:** 3 passed, 0.14s

**Как устроен тест:**

```python
# Все взаимодействия описаны заранее — до старта mock-сервера
p.upon_receiving("POST-запрос регистрации нового email")
 .given("пользователь не существует")
 .with_request("POST", "/v1/auth/register")
 .with_body({"email": "new@example.com"})
 .will_respond_with(201)

# Pact запускает mock-сервер — backend не нужен
with p.serve() as srv:
    response = AuthService(base_url=str(srv.url)).register("new@example.com")
    # → hits mock server, gets 201
```

**Сгенерированный контракт (фрагмент `qa-portfolio-sortula-backend.json`):**

```json
{
  "consumer": { "name": "qa-portfolio" },
  "provider": { "name": "sortula-backend" },
  "interactions": [
    {
      "description": "POST-запрос регистрации нового email",
      "providerStates": [{ "name": "пользователь не существует" }],
      "request": {
        "method": "POST",
        "path": "/v1/auth/register",
        "body": { "content": { "email": "new@example.com" } }
      },
      "response": { "status": 201 }
    }
  ],
  "metadata": { "pactSpecification": { "version": "4.0" } }
}
```

**Ключевые концепции:**
- `upon_receiving` + `given` — описание взаимодействия и состояния провайдера
- `with_body` — ожидаемое тело запроса (consumer говорит что пошлёт)
- `will_respond_with` — что consumer ожидает получить
- `p.serve()` — Pact запускает настоящий HTTP mock-сервер на localhost
- `write_file()` — сохраняет контракт в JSON-файл (артефакт для провайдера)

**Отличие от pytest-mock (Спринт 20):**
- Sprint 20: подменяем `requests.post` в памяти — нет HTTP-запроса вообще
- Sprint 21: Pact поднимает реальный HTTP-сервер — запрос уходит, но не в Sortula

**Скрины:** `../evidence/sprint-21/`

---

## Связь с ручным тестированием

Эти тесты автоматизируют сценарии из:
- [API + БД тестирование (Спринт 5)](../api-db-testing.md) — мутационное тестирование Postman
- [Итоговый отчёт](../final-report.md) — BUG-02, BUG-08 найдены вручную, зафиксированы тут
