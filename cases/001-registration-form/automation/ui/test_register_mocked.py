"""Спринт 20 — Изоляция тестов: pytest-mock.

Мокируем requests.post внутри AuthService — backend не нужен вообще.
Тесты запускаются без Docker, без сети, без localhost:8001.

Запуск:
    pytest ui/test_register_mocked.py -v
"""

import requests
import pytest
import allure

from services.auth_service import AuthService


@allure.title("Мок: успешная регистрация → 201")
@allure.severity(allure.severity_level.CRITICAL)
def test_register_success(mocker):
    mock_post = mocker.patch("services.auth_service.requests.post")
    mock_post.return_value.status_code = 201

    auth = AuthService()
    response = auth.register("new@example.com")

    with allure.step("Проверить статус 201"):
        assert response.status_code == 201
    with allure.step("Проверить что requests.post был вызван ровно 1 раз"):
        mock_post.assert_called_once()


@allure.title("Мок: дубликат email → 409")
@allure.severity(allure.severity_level.CRITICAL)
def test_register_duplicate_email(mocker):
    mock_post = mocker.patch("services.auth_service.requests.post")
    mock_post.return_value.status_code = 409

    auth = AuthService()
    response = auth.register("existing@example.com")

    with allure.step("Проверить статус 409 Conflict"):
        assert response.status_code == 409


@allure.title("Мок: невалидный email → 422")
@allure.severity(allure.severity_level.NORMAL)
def test_register_invalid_email(mocker):
    mock_post = mocker.patch("services.auth_service.requests.post")
    mock_post.return_value.status_code = 422

    auth = AuthService()
    response = auth.register("not-an-email")

    with allure.step("Проверить статус 422 Unprocessable Entity"):
        assert response.status_code == 422


@allure.title("Мок: сервер упал → 500")
@allure.severity(allure.severity_level.CRITICAL)
def test_register_server_error(mocker):
    mock_post = mocker.patch("services.auth_service.requests.post")
    mock_post.return_value.status_code = 500

    auth = AuthService()
    response = auth.register("user@example.com")

    with allure.step("Проверить статус 500 Internal Server Error"):
        assert response.status_code == 500


@allure.title("Мок: таймаут сети → Timeout")
@allure.severity(allure.severity_level.CRITICAL)
def test_register_timeout(mocker):
    mock_post = mocker.patch("services.auth_service.requests.post")
    mock_post.side_effect = requests.exceptions.Timeout("Request timed out")

    auth = AuthService()

    with allure.step("Проверить что бросается Timeout при зависшем соединении"):
        with pytest.raises(requests.exceptions.Timeout):
            auth.register("user@example.com")


@allure.title("Мок: нет соединения → ConnectionError")
@allure.severity(allure.severity_level.CRITICAL)
def test_register_connection_error(mocker):
    mock_post = mocker.patch("services.auth_service.requests.post")
    mock_post.side_effect = requests.exceptions.ConnectionError("Network unreachable")

    auth = AuthService()

    with allure.step(
        "Проверить что бросается ConnectionError когда backend недоступен"
    ):
        with pytest.raises(requests.exceptions.ConnectionError):
            auth.register("user@example.com")
