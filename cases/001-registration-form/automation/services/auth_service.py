"""Service Object для Auth API — инкапсулирует URL и структуру запросов.

Все тесты работают с методами класса, не знают про URL и JSON-структуру.
"""

import requests


class AuthService:
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url

    def register(self, email: str) -> requests.Response:
        return requests.post(
            f"{self.base_url}/v1/auth/register",
            json={"email": email},
        )

    def login(self, email: str, password: str) -> requests.Response:
        return requests.post(
            f"{self.base_url}/v1/auth/login",
            json={"email": email, "password": password},
        )
