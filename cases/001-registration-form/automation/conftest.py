import pytest
import requests
import uuid

BASE_URL = "http://localhost:8001"


@pytest.fixture
def registered_user():
    """Регистрирует нового пользователя и возвращает его данные.

    Использует uuid для уникального email — каждый запуск теста
    начинается с чистого пользователя, нет конфликтов между запусками.
    """
    email = f"test-{uuid.uuid4().hex[:8]}@example.com"
    password = "TestPass1!"

    response = requests.post(
        f"{BASE_URL}/v1/auth/register",
        json={"email": email}
    )

    assert response.status_code == 201, \
        f"Фикстура: не удалось создать пользователя -> {response.text}"

    return {"email": email, "password": password}
