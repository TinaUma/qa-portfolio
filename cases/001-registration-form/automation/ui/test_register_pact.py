"""Спринт 21 — Контрактное тестирование: Pact v3.

Consumer-контракт: qa-portfolio (consumer) → sortula-backend (provider).
Все взаимодействия описаны заранее — Pact поднимает mock-сервер один раз.

Запуск:
    pytest ui/test_register_pact.py -v

Результат: ui/pacts/qa-portfolio-sortula-backend.json
"""

import pytest
import allure
from pathlib import Path
from pact import Pact

from services.auth_service import AuthService

PACTS_DIR = Path(__file__).parent / "pacts"


@pytest.fixture(scope="session")
def pact_server():
    p = Pact("qa-portfolio", "sortula-backend")

    (
        p.upon_receiving("POST-запрос регистрации нового email")
        .given("пользователь не существует")
        .with_request("POST", "/v1/auth/register")
        .with_body({"email": "new@example.com"})
        .will_respond_with(201)
    )

    (
        p.upon_receiving("POST-запрос с существующим email")
        .given("пользователь с таким email уже существует")
        .with_request("POST", "/v1/auth/register")
        .with_body({"email": "existing@example.com"})
        .will_respond_with(409)
    )

    (
        p.upon_receiving("POST-запрос с невалидным email")
        .given("невалидный формат email")
        .with_request("POST", "/v1/auth/register")
        .with_body({"email": "not-an-email"})
        .will_respond_with(422)
    )

    with p.serve() as srv:
        yield srv

    PACTS_DIR.mkdir(parents=True, exist_ok=True)
    p.write_file(PACTS_DIR)


@allure.title("Pact: успешная регистрация → 201")
@allure.severity(allure.severity_level.CRITICAL)
def test_register_success(pact_server):
    response = AuthService(base_url=str(pact_server.url)).register("new@example.com")
    with allure.step("Проверить статус 201"):
        assert response.status_code == 201


@allure.title("Pact: дубликат email → 409")
@allure.severity(allure.severity_level.CRITICAL)
def test_register_duplicate_email(pact_server):
    response = AuthService(base_url=str(pact_server.url)).register(
        "existing@example.com"
    )
    with allure.step("Проверить статус 409 Conflict"):
        assert response.status_code == 409


@allure.title("Pact: невалидный email → 422")
@allure.severity(allure.severity_level.NORMAL)
def test_register_invalid_email(pact_server):
    response = AuthService(base_url=str(pact_server.url)).register("not-an-email")
    with allure.step("Проверить статус 422 Unprocessable Entity"):
        assert response.status_code == 422
