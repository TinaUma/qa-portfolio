"""Integration tests for Settings API (GitLab #42).

Business rules under test:
- ST-1: GET /v1/settings без токена → 401
- ST-2: GET /v1/settings с токеном → 200, defaults (llm_language=ru, timezone=UTC)
- ST-3: PATCH /v1/settings notifications.frequency=daily → 200, field updated
- ST-4: GET /v1/settings/defaults без токена → 200, default values
"""

import pytest
from httpx import AsyncClient
from app.models.user import User

pytestmark = [pytest.mark.integration, pytest.mark.api]

_URL = "/v1/settings"


# ── ST-1: 401 без токена ───────────────────────────────────────────────────────


class TestNoAuth:
    """Unauthenticated GET → 401 (ST-1)."""

    @pytest.mark.asyncio
    async def test_get_without_token_returns_401(self, client: AsyncClient):
        response = await client.get(_URL)
        assert response.status_code == 401


# ── ST-2: GET defaults ────────────────────────────────────────────────────────


class TestGetSettings:
    """Authenticated GET returns default settings for new user (ST-2)."""

    @pytest.mark.asyncio
    async def test_returns_200_with_default_llm_language(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.get(_URL, headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["llm_language"] == "ru"
        assert data["timezone"] == "UTC"


# ── ST-3: PATCH ────────────────────────────────────────────────────────────────


class TestPatchSettings:
    """PATCH partially updates settings (ST-3)."""

    @pytest.mark.asyncio
    async def test_patch_notifications_frequency(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.patch(
            _URL,
            json={"notifications": {"frequency": "daily"}},
            headers=auth_headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["notifications"]["frequency"] == "daily"

    @pytest.mark.asyncio
    async def test_patch_llm_language(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.patch(
            _URL,
            json={"llm_language": "en"},
            headers=auth_headers,
        )
        assert response.status_code == 200
        assert response.json()["llm_language"] == "en"


# ── ST-4: GET /defaults — no auth required ────────────────────────────────────


class TestGetDefaults:
    """GET /settings/defaults returns defaults without auth (ST-4)."""

    @pytest.mark.asyncio
    async def test_returns_200_without_token(self, client: AsyncClient):
        response = await client.get(f"{_URL}/defaults")
        assert response.status_code == 200
        data = response.json()
        assert data["llm_language"] == "ru"
        assert data["timezone"] == "UTC"