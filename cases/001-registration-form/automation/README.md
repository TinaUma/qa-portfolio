# Автоматизированное тестирование: Регистрация (Спринты 9–13)

**Тестировщик:** Тина Юмашева
**Дата:** 15.07.2026 – 18.07.2026
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

## Связь с ручным тестированием

Эти тесты автоматизируют сценарии из:
- [API + БД тестирование (Спринт 5)](../api-db-testing.md) — мутационное тестирование Postman
- [Итоговый отчёт](../final-report.md) — BUG-02, BUG-08 найдены вручную, зафиксированы тут
