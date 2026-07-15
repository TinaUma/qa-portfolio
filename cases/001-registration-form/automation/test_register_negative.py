"""Спринт 9 — параметризованные негативные сценарии регистрации.

Матрица:
  Невалидный email    -> 422 (валидация формата)
  Пустой email        -> 422 (пустая строка не проходит валидацию)
  Отсутствие email    -> 422 (обязательное поле)
  Дубликат email      -> 409 (конфликт, нужна фикстура)

Вывод из исследования Спринта 5:
  password при регистрации игнорируется (UserCreate schema не принимает поле password).
  Пароль устанавливается отдельно через POST /v1/auth/set-password.
  Поэтому "пустой пароль" при регистрации даёт 201, не 422.
"""

import pytest
import requests
from conftest import BASE_URL


# --- БЕЗ фикстуры: проверяем валидацию формата данных ---
# Предусловие: пользователь не нужен — просто кривые данные

@pytest.mark.parametrize("payload, expected_status, scenario", [
    ({"email": "это-не-email"},  422, "невалидный формат email"),
    ({"email": ""},              422, "пустой email"),
    ({},                         422, "поле email отсутствует"),
])
def test_register_invalid_data(payload, expected_status, scenario):
    response = requests.post(
        f"{BASE_URL}/v1/auth/register",
        json=payload
    )

    assert response.status_code == expected_status, \
        f"Сценарий '{scenario}': ожидали {expected_status}, получили {response.status_code}. Ответ: {response.text}"


# --- С фикстурой: пользователь уже существует ---
# Предусловие: registered_user создаёт пользователя до теста

def test_register_duplicate_email_returns_409(registered_user):
    response = requests.post(
        f"{BASE_URL}/v1/auth/register",
        json={"email": registered_user["email"]}
    )

    assert response.status_code == 409, \
        f"Ожидали 409 Conflict, получили {response.status_code}. Ответ: {response.text}"
