# Баг-репорты: API Sortula (Export + Settings)

**Тестировщик:** Тина Юмашева  
**Дата:** 2026-08-04  
**Окружение:** production codebase, pytest + Docker, PostgreSQL 15

---

## BUG-01: ImportError в production-коде — browser extension handler

**Severity:** Critical  
**Priority:** High  
**Статус:** ✅ Исправлено  
**Компонент:** `backend/app/extension_receiver/handlers/bookmarks.py`

---

**Окружение:** production codebase (локальный dev + тестовый Docker-стек)

**Шаги воспроизведения:**
1. Установить браузерное расширение Sortula в Chrome
2. Перейти на любую страницу и нажать кнопку "Сохранить"
3. Расширение отправляет запрос на `POST /extension/bookmarks`
4. Запрос попадает в `extension_receiver/handlers/bookmarks.py`

**Ожидаемый результат:** Закладка сохраняется, возвращается 201 с `{"status": "processing"}`.

**Фактический результат:**
```
ImportError: cannot import name 'async_session_maker' from 'app.database'
```
Весь handler крашится при первом реальном запросе к расширению. Функциональность браузерного расширения полностью сломана для всех пользователей в production.

**Root cause:**  
В файле `extension_receiver/handlers/bookmarks.py` использовался устаревший import:
```python
# Было (неверно):
from app.database import async_session_maker

# Стало (верно):
from app.database import AsyncSessionLocal
```
Объект называется `AsyncSessionLocal`, а не `async_session_maker`. Ошибка прошла code review, потому что Python проверяет imports в runtime, а не на этапе синтаксического анализа.

**Как был обнаружен:**  
В процессе написания юнит-теста для handler'а. Тест пытался замокать `AsyncSessionLocal` (правильное имя из документации модуля) — и стало понятно, что в самом handler'е стоит другое имя. Проверка исходного кода подтвердила баг.

**Исправление:** Заменено `async_session_maker` на `AsyncSessionLocal` в import и во всех местах использования в файле.

**Урок:** Тесты на реальный код (не mocks) находят ошибки импорта, которые code review пропускает — Python молча принимает неверное имя до момента вызова.