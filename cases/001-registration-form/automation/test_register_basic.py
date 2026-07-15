"""Спринт 9 — базовый тест: дубликат email при регистрации.

Что проверяем: система не позволяет зарегистрироваться дважды с одним email.
Предусловие: пользователь с таким email уже существует (фикстура registered_user).
Действие: POST /v1/auth/register с тем же email повторно.
Ожидание: 409 Conflict.

Первый автоматизированный тест против живой Sortula. Sprint 9, 15.07.2026.
"""

import requests
from conftest import BASE_URL


def test_register_duplicate_email_returns_409(registered_user):
    response = requests.post(
        f"{BASE_URL}/v1/auth/register",
        json={"email": registered_user["email"]}
    )

    assert response.status_code == 409
