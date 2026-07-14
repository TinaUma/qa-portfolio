# Мобильное тестирование: Спринт 7

**Тестировщик:** Тина Юмашева  
**Дата:** 13.07.2026  
**Фидбек ментора:** «Спринт 7 закрыт полностью, обе части: мобильный веб + PWA на реальном кейсе Сортулы (с найденным архитектурным багом в валидации пароля на логине), плюс базовый навык Android Studio/эмулятор/Logcat на отдельном полигоне.»

---

## Часть A — Mobile Web + PWA (staging.sortula.ru)

**Среда:** staging.sortula.ru | Chrome DevTools Device Mode iPhone SE (375×667px) | Lighthouse

### Контекст

У Sortula нет нативного Android-приложения — намеренное архитектурное решение (vision.md: "Mobile native app — Roadmap Phase 4"). Мобильный опыт реализован через: адаптивный веб (Next.js + Bootstrap 5) + PWA (manifest.json + Service Worker) + Telegram-бот. iPhone SE выбран как "worst case" — самый маленький экран; если влезает здесь, влезет везде.

**Скриншоты среды:**
- [iPhone SE — DevTools Device Mode](evidence/sprint-07/block-a/iPhone%20SE%20%20%20в%20режиме%20DEVtool.PNG)
- [iPhone SE без плашки (чистый вид)](evidence/sprint-07/block-a/iPhone%20SE%20без%20плашки%20об%20истекшей%20сессии%20%20%20в%20режиме%20DEVtool.PNG)

---

### PWA-статус (Application → Manifest + Service Workers)

| Параметр | Значение | Статус |
|---|---|---|
| Display | standalone | ✅ открывается без адресной строки |
| Start URL | /dashboard | ✅ |
| Service Worker | #1619 activated and is running | ✅ |
| Shortcuts | 3 ярлыка: Добавить / Поиск / Важное | ✅ |
| Offline | кастомный экран "Нет подключения" | ✅ контент не кешируется (Info) |

**Скриншоты:**
- [Application Manifest](evidence/sprint-07/block-a/application%20manifest.PNG)
- [Service Worker](evidence/sprint-07/block-a/service%20woker.PNG)
- [Offline-тест](evidence/sprint-07/block-a/офланй%20тест.PNG)

---

### Lighthouse (iPhone SE viewport)

| Метрика | Балл |
|---|---|
| Performance | 64 🟠 |
| Accessibility | 85 🟠 |
| Best Practices | 100 🟢 |
| SEO | 69 🟠 |

**Ключевые метрики Performance:**
- FCP: 1.2s ✅ | **LCP: 7.8s ❌** (норма ≤2.5s) | TBT: 450ms 🟠 | CLS: 0.006 ✅
- Главная причина медленного LCP: Unused JS 522 КБ

**Скриншоты:**
- [Lighthouse-отчёт](evidence/sprint-07/block-a/lighthouse%20repport.PNG)
- [Итоги спринта 7](evidence/sprint-07/block-a/итоги%20спринта%207.PNG)

---

### Находки Части A

| # | Где | Что | Тип | Severity |
|---|-----|-----|-----|----------|
| 1 | Login → API | 422 при логине: валидация формата пароля срабатывает ДО проверки хеша в БД — логин не должен проверять формат | Architectural Smell | **Major** |
| 2 | Lighthouse Performance | LCP 7.8s на мобильном (норма 2.5s) | Performance | **Major** |
| 3 | manifest.json | Нет скриншотов — установочный превью PWA не показывается | PWA/UX | Minor |
| 4 | manifest.json | Иконки объявлены с `"any maskable"` вместе — Chrome рекомендует разделить | PWA | Minor |
| 5 | Offline | Контент закладок не доступен офлайн — только заглушка | PWA/UX | Info (намеренно) |
| 6 | Accessibility | Кнопка "+" без `aria-label` | Accessibility | Minor |
| 7 | Accessibility | Недостаточный контраст текста | Accessibility | Minor |
| 8 | UX мобиль | Вход через Telegram требует переключения браузер↔Telegram | UX | **Major** |
| 9 | UX | Кнопка "+" непонятна без подписи при первом контакте | UX | Minor |
| 10 | SEO | /bookmarks закрыт от индексации | Info | Не баг — намеренно |

**Скриншоты к находкам:**
- [Функционал первого экрана — кнопка «+»](evidence/sprint-07/block-a/функционал%20первого%20экрана%20кнокпка%20плюс.PNG)
- [Логин через стандартный флоу — 422](evidence/sprint-07/block-a/регистрация%20через%20стандратное%20флоу%20(%20логин%20и%20паротль)%20выдает%20ошибку.PNG)
- [Telegram magic link — консоль](evidence/sprint-07/block-a/регистрация%20через%20ТГ%20мэджик%20ссылку%20консоль.PNG)
- [Настройки — подписочный гейт 403](evidence/sprint-07/block-a/настройки%20%20подписочный%20гейт%20403%20апррейд.PNG)

---

### Ключевая находка #1 — архитектурный смелл на логине

**Что должен делать эндпоинт логина (и только это):**
```
1. Взять email → найти пользователя в БД
2. Взять введённый пароль → сравнить с bcrypt-хешем из БД
3. Совпало → выдать JWT. Не совпало → 401
```

**Что происходит в Sortula сейчас:**
```
0. Проверить ФОРМАТ пароля: есть спецсимвол? заглавная? цифра?
   → нет → 422, до БД вообще не доходим   ← ЛИШНИЙ ШАГ (архитектурная ошибка)
1. Найти пользователя в БД
2. Сравнить хеш
```

**Сценарий, который сломается:**  
Пользователь год назад создал пароль `MyDog123` (без спецсимвола, тогда требований не было). Разработчики добавили проверку формата в схему логина. Пользователь вводит свой правильный пароль → получает 422. До хеша дело не доходит. Пароль верный — система его даже не проверила.

**Принцип:**
- `set-password` — "придумай НОВЫЙ пароль" → проверять формат **правильно ✅**
- `login` — "введи СУЩЕСТВУЮЩИЙ пароль" → проверять формат **бессмысленно ❌**

**Почему сейчас никто не пострадал (случайность, не гарантия):**  
`set-password` тоже использует тот же валидатор `Password` → все пароли в БД уже с спецсимволом. Но если завтра требования в set-password ослабят — пользователи с "мягкими" паролями будут заблокированы на логине навсегда.

**Доказательство из кода:**
- `backend/app/schemas/user.py` — `UserLogin` и `UserSetPassword` используют один тип `Password`
- `backend/tests/schemas/test_validation_limits.py` — тест `test_rejects_no_special_char` тестирует `UserLogin` на формат

**Severity: Major** (не Blocker)

---

## Часть B — Android Studio + AVD Manager + Logcat

**Среда:** Android Studio Quail 1 | 2026.1.1 Patch 2, Windows 10, эмулятор Pixel 6  
**Важно:** Sortula не имеет APK — это полигон для отработки навыка

### Что сделано

1. AVD Manager → создан Pixel 6, Android 17.0 "CinnamonBun", API 37.1, x86_64, 2 GB образ
2. Эмулятор запущен без ошибок HAXM
3. Создан проект-заглушка "Sortula" (нужен для открытия панели Logcat)
4. Logcat подключён к `emulator-5554`
5. Фильтр по пакету: `package:com.android.settings` ✅
6. Фильтр по уровню: `level:ERROR` ✅
7. Разобрана структура строки лога

**Скриншоты:**
- [Pixel 6 — эмулятор Android 17](evidence/sprint-07/block-b/Pixel6%20эмулятор%20Андроид%2017.PNG)
- [Logcat](evidence/sprint-07/block-b/logcat.PNG)
- [Logcat — фильтр по уровню ERROR](evidence/sprint-07/block-b/logcat%20фильтр%20по%20уровню%20логов%20ERROR.PNG)

---

### Структура строки лога

```
2026-07-13 22:21:46.640   711-1319   WifiDataStall   system_server   Ignore this poll...
│ Дата+время         │ PID-TID  │ Тег            │ Процесс       │ Сообщение
```

- **PID** — номер процесса
- **TID** — номер потока внутри процесса
- **Тег** — имя класса/компонента, который написал запись
- **Процесс** — имя приложения

### Фильтры Logcat

```
package:com.android.settings  → логи только от этого приложения
level:ERROR                   → только ошибки
level:WARN                    → предупреждения и выше
package:mine                  → только логи текущего открытого проекта
```

### Инсайт #1: Logcat = GUI над adb logcat

Панель Logcat в Android Studio — графическая обёртка над `adb logcat`. Те же фильтры в терминале:
```bash
adb logcat --pid <pid>              # по процессу
adb logcat *:E                      # только ERROR
adb logcat | grep "com.android"     # тот же grep, что в Спринте 6 при расследовании BUG-02
```
Смысл одинаковый: сузить поток шума до нужного сигнала.

### Инсайт #2: ERROR в эмуляторе ≠ баг приложения

Ошибки `WifiDataStall` и `SatelliteController` — системные компоненты ищут реальный WiFi-чип и спутниковый модем, не находят → ERROR. Это шум окружения эмулятора, не дефект кода.

Правило QA:
- ERROR в `system_server`, `com.android.phone` → системный шум, игнорируем
- ERROR в пакете тестируемого приложения → расследуем

Именно для этого фильтруем по пакету, а не читаем Logcat целиком.

---

## Итог Спринта 7

| Что сделано | Результат |
|---|---|
| PWA-аудит (Manifest + Service Workers + Offline) | PWA базово работает; 2 Minor-улучшения в манифесте |
| Lighthouse на мобильном (iPhone SE) | LCP 7.8s ❌ — Major; Best Practices 100 ✅ |
| Мутационное тестирование логина | Архитектурный смелл: валидация формата пароля на логине — Major |
| Android Studio / AVD / Logcat | Навык отработан: эмулятор, фильтрация логов, структура строки |
| Находок Спринт 7 | 3 Major, 5 Minor, 2 Info (намеренно) |
