"""Спринт 15/18 — Сквозной тест: API-регистрация → верификация записи в PostgreSQL.

Спринт 18: рефакторинг под Service Object.
API-вызовы вынесены в services/auth_service.py — тест читается как сценарий.

ВАЖНО: требует локального Docker dev-стека.
  - Backend: localhost:8001
  - PostgreSQL: localhost:5433
  - docker compose -f docker-compose.dev.yml up -d

Запуск: pytest ui/test_register_db_verify.py -v
"""

import uuid

import allure
import psycopg2

from services.auth_service import AuthService

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
    auth = AuthService()

    with allure.step(f"POST /v1/auth/register с email={email}"):
        response = auth.register(email)

    with allure.step("Проверить что API вернул 201 Created"):
        assert response.status_code == 201, (
            f"Ожидали 201, получили {response.status_code}: {response.text}"
        )

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
