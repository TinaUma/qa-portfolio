"""Спринт 22-23 — Нагрузочное тестирование: Locust.

Сценарий: POST /v1/auth/register (sortula.ru staging)
Два типа нагрузки:
  - [new]       уникальный email → 201 или 429 (rate limit)
  - [duplicate] фиксированный email → 409 или 429 (rate limit)

Находка Sprint 22-23: staging защищён rate limiter'ом.
429 Too Many Requests — ожидаемое поведение при нагрузке, не провал.

Запуск с веб-UI:
    cd cases/001-registration-form/automation
    locust -f load/locustfile.py --host https://api.sortula.ru
    → открыть http://localhost:8089

Запуск headless (CSV-отчёт):
    locust -f load/locustfile.py --host https://api.sortula.ru \
      --headless --users 20 --spawn-rate 2 --run-time 30s \
      --csv=load/results/locust-report
"""

import uuid
from locust import HttpUser, task, between


class RegisterUser(HttpUser):
    host = "https://api.sortula.ru"
    wait_time = between(1, 3)

    @task(3)
    def register_new_user(self):
        """Регистрация с уникальным email — 201 в норме, 429 при rate limit."""
        email = f"loadtest-{uuid.uuid4().hex[:8]}@test.com"
        with self.client.post(
            "/v1/auth/register",
            json={"email": email},
            catch_response=True,
            name="/v1/auth/register [new]",
        ) as response:
            if response.status_code in (201, 429):
                response.success()
            else:
                response.failure(
                    f"Expected 201 or 429, got {response.status_code}: {response.text[:100]}"
                )

    @task(1)
    def register_duplicate(self):
        """Регистрация с существующим email — 409 в норме, 429 при rate limit."""
        with self.client.post(
            "/v1/auth/register",
            json={"email": "loadtest-duplicate@test.com"},
            catch_response=True,
            name="/v1/auth/register [duplicate]",
        ) as response:
            if response.status_code in (201, 409, 429):
                response.success()
            else:
                response.failure(
                    f"Unexpected: {response.status_code}: {response.text[:100]}"
                )
