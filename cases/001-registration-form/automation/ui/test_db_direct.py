"""Спринт 19 — Инфраструктурный тест: PostgreSQL доступен в CI.

Не требует backend. Проверяет что:
  - psycopg2 подключается к PostgreSQL
  - CREATE TABLE / INSERT / SELECT работают
  - CI-окружение настроено правильно

Запуск локально:
  docker compose -f docker-compose.dev.yml up -d postgres
  pytest ui/test_db_direct.py -v

В CI: запускается автоматически через job db-tests (services: postgres:15).
"""

import os
import uuid

import allure
import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "port": int(os.getenv("DB_PORT", "5433")),
    "dbname": os.getenv("DB_NAME", "sortula"),  # CI переопределяет на sortula_test
    "user": os.getenv("DB_USER", "sortula_user"),
    "password": os.getenv("DB_PASSWORD", "sortula_password"),
}


@allure.title("Инфраструктура: PostgreSQL доступен и принимает соединения")
@allure.severity(allure.severity_level.CRITICAL)
def test_db_connection():
    """Базовая проверка: можем подключиться к PostgreSQL."""
    with allure.step("Подключиться к PostgreSQL"):
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()


@allure.title("Инфраструктура: INSERT → SELECT работает корректно")
@allure.severity(allure.severity_level.CRITICAL)
def test_db_insert_and_select():
    """Создаём тестовую таблицу, вставляем запись, проверяем что она там есть."""
    email = f"ci-test-{uuid.uuid4().hex[:8]}@example.com"

    with allure.step("Подключиться к PostgreSQL"):
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

    with allure.step("Создать тестовую таблицу ci_test_users"):
        cur.execute("""
            CREATE TABLE IF NOT EXISTS ci_test_users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL
            )
        """)
        conn.commit()

    with allure.step(f"INSERT пользователя с email={email}"):
        cur.execute("INSERT INTO ci_test_users (email) VALUES (%s)", (email,))
        conn.commit()

    with allure.step(f"SELECT пользователя с email={email}"):
        cur.execute("SELECT id, email FROM ci_test_users WHERE email = %s", (email,))
        row = cur.fetchone()

    with allure.step("Проверить что запись существует в БД"):
        assert row is not None, f"Запись {email} не найдена в БД после INSERT"
        assert row[1] == email, (
            f"Email не совпадает: ожидали {email}, получили {row[1]}"
        )

    with allure.step("Очистить тестовые данные"):
        cur.execute("DELETE FROM ci_test_users WHERE email = %s", (email,))
        conn.commit()
        conn.close()
