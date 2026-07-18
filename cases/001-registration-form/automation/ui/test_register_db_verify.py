"""Спринт 14-16 — Сквозной тест: API-регистрация → верификация записи в PostgreSQL.

Что проверяем:
  1. Пользователь регистрируется через локальный API (requests → localhost:8001)
  2. После 201 Created — проверяем что запись РЕАЛЬНО появилась в БД (psycopg2)
  3. Негативный сценарий: тест падает с понятным сообщением если записи нет

Это называется cross-layer test: API → БД — вся цепочка проверена в одной среде.

ВАЖНО: UI-тесты (test_register_via_ui.py) тестируют staging.sortula.ru.
       Этот тест работает с ЛОКАЛЬНЫМ стеком — API и БД в одной среде.

Требования:
  - Docker dev-стек Sortula запущен: docker compose -f docker-compose.dev.yml up -d
  - Backend: localhost:8001, PostgreSQL: localhost:5433
  - pip install psycopg2-binary requests

Запуск: pytest ui/test_register_db_verify.py -v
"""

import uuid

import allure
import psycopg2
import pytest
import requests

API_URL = "http://localhost:8001"

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "dbname": "sortula",
    "user": "sortula_user",
    "password": "sortula_password",
}


@allure.title("Сквозной: регистрация через API → запись появилась в БД")
@allure.description(
    "POST /v1/auth/register на локальный backend, "
    "затем SELECT из таблицы users подтверждает что запись сохранена в PostgreSQL."
)
@allure.severity(allure.severity_level.CRITICAL)
def test_register_via_api_verified_in_db():
    email = f"tina-db-{uuid.uuid4().hex[:8]}@example.com"

    # --- API часть ---
    with allure.step(f"POST /v1/auth/register с email={email}"):
        response = requests.post(
            f"{API_URL}/v1/auth/register",
            json={"email": email},
        )

    with allure.step("Проверить что API вернул 201 Created"):
        assert response.status_code == 201, (
            f"Ожидали 201, получили {response.status_code}: {response.text}"
        )

    # --- DB часть ---
    with allure.step("Подключиться к PostgreSQL (localhost:5433)"):
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

    with allure.step(f"SELECT пользователя с email={email} из таблицы users"):
        cur.execute("SELECT id, email FROM users WHERE email = %s", (email,))
        row = cur.fetchone()
        conn.close()

    with allure.step("Проверить что запись существует в БД"):
        assert row is not None, (
            f"Пользователь {email} не найден в таблице users после API-регистрации. "
            "Значит backend не сохранил запись — это баг!"
        )
        assert row[1] == email, (
            f"Email в БД не совпадает: ожидали {email}, получили {row[1]}"
        )
