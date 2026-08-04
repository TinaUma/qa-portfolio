# Чек-лист: API Sortula (Export + Settings)

**Дата тестирования:** 2026-08-04  
**Окружение:** тестовый Docker-контейнер (PostgreSQL 15, FastAPI), pytest + httpx  
**Тестировщик:** Тина Юмашева

---

## Export API — `GET /v1/bookmarks/export`

### Auth gate
- [x] Запрос без токена → 401 Unauthorized

### JSON format
- [x] `?format=json` с токеном → 200 OK
- [x] Content-Type: `application/json`
- [x] Тело ответа — массив `[]` (не null, не объект)
- [x] Header `Content-Disposition` содержит `attachment`
- [x] Header `Content-Disposition` содержит `bookmarks.json`

### CSV format
- [x] `?format=csv` с токеном → 200 OK
- [x] Content-Type содержит `text/csv`
- [x] Тело содержит заголовочную строку с "Title"
- [x] Тело содержит заголовочную строку с "URL"

### HTML format (Netscape bookmarks)
- [x] `?format=html` с токеном → 200 OK
- [x] Content-Type содержит `text/html`
- [x] Тело содержит `NETSCAPE-Bookmark-file-1` (стандарт формата импорта в браузеры)

### Неподдерживаемый формат
- [x] `?format=xml` → 400 Bad Request
- [x] Поле `detail` в ответе содержит "xml" — пользователь видит что именно не так

---

## Settings API

### Auth gate
- [x] `GET /v1/settings` без токена → 401 Unauthorized

### GET — получение настроек
- [x] `GET /v1/settings` с токеном → 200 OK
- [x] Поле `llm_language` = "ru" (дефолт для нового пользователя)
- [x] Поле `timezone` = "UTC" (дефолт для нового пользователя)

### PATCH — частичное обновление
- [x] `PATCH /v1/settings {"notifications": {"frequency": "daily"}}` → 200 OK
- [x] Ответ содержит обновлённое `notifications.frequency == "daily"`
- [x] `PATCH /v1/settings {"llm_language": "en"}` → 200 OK
- [x] Ответ содержит обновлённое `llm_language == "en"`

### GET /defaults — публичный эндпоинт
- [x] `GET /v1/settings/defaults` без токена → 200 OK
- [x] Ответ содержит `llm_language == "ru"`
- [x] Ответ содержит `timezone == "UTC"`

---

**Итого автоматизированных проверок:** 23 (13 тестов + assertions внутри)  
**Все прошли:** ✅ 13/13