# Автоматизация: API Integration Tests

Интеграционные тесты для Export API и Settings API Sortula.

## Стек

| Инструмент | Роль |
|---|---|
| pytest + pytest-asyncio | тест-фреймворк, поддержка async |
| httpx (AsyncClient) | асинхронный HTTP-клиент для FastAPI |
| Docker Compose | изолированный тест-стек (PostgreSQL 15, Redis 7) |
| real PostgreSQL | тесты работают с реальной БД, не с mocks |

## Запуск

Тесты являются частью backend-тест-сьюта Sortula и запускаются через Docker:

```bash
# Один файл:
./scripts/test-file.sh tests/api/test_export.py -x
./scripts/test-file.sh tests/api/test_settings.py -x

# Все интеграционные:
./scripts/test-all.sh
```

## Fixtures

Тесты используют фикстуры из `conftest.py` проекта:

| Фикстура | Что делает |
|---|---|
| `client` | `AsyncClient` подключённый к тестовому FastAPI-приложению |
| `auth_headers` | JWT-токен для тестового пользователя (`{"Authorization": "Bearer ..."}`) |
| `test_user` | Объект `User` созданный в тестовой БД для каждого теста, удаляется после |

## Маркеры

```python
pytestmark = [pytest.mark.integration, pytest.mark.api]
```

- `integration` — требует реальной БД, медленнее unit-тестов (~1-3s на тест)
- `api` — API endpoint-тесты (отдельно от Celery tasks, bot handlers)

## Файлы

- [`test_export.py`](test_export.py) — 8 тестов, `GET /v1/bookmarks/export`
- [`test_settings.py`](test_settings.py) — 5 тестов, Settings API