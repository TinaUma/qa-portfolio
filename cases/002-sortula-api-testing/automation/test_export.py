"""Integration tests for Export API (GitLab #43).

Business rules under test:
- EXP-1: GET /v1/bookmarks/export без токена → 401
- EXP-2: GET /v1/bookmarks/export?format=json с токеном, нет закладок → [] (empty)
- EXP-3: GET /v1/bookmarks/export?format=csv → 200, text/csv, header row present
- EXP-4: GET /v1/bookmarks/export?format=html → 200, text/html, Netscape format
- EXP-5: GET /v1/bookmarks/export?format=xyz → 400 (unsupported format)
"""

import json

import pytest
from httpx import AsyncClient
from app.models.user import User

pytestmark = [pytest.mark.integration, pytest.mark.api]

_URL = "/v1/bookmarks/export"


# ── EXP-1: 401 без токена ─────────────────────────────────────────────────────


class TestNoAuth:
    """Unauthenticated request → 401 (EXP-1)."""

    @pytest.mark.asyncio
    async def test_get_without_token_returns_401(self, client: AsyncClient):
        response = await client.get(_URL)
        assert response.status_code == 401


# ── EXP-2: JSON export — empty ────────────────────────────────────────────────


class TestJsonExport:
    """JSON export format (EXP-2)."""

    @pytest.mark.asyncio
    async def test_empty_export_returns_json_array(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.get(f"{_URL}?format=json", headers=auth_headers)
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        data = json.loads(response.content)
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_json_has_content_disposition(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.get(f"{_URL}?format=json", headers=auth_headers)
        assert "attachment" in response.headers.get("content-disposition", "")
        assert "bookmarks.json" in response.headers.get("content-disposition", "")


# ── EXP-3: CSV export ─────────────────────────────────────────────────────────


class TestCsvExport:
    """CSV export format (EXP-3)."""

    @pytest.mark.asyncio
    async def test_csv_returns_200_with_correct_media_type(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.get(f"{_URL}?format=csv", headers=auth_headers)
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_csv_has_header_row(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.get(f"{_URL}?format=csv", headers=auth_headers)
        content = response.content.decode("utf-8")
        assert "Title" in content
        assert "URL" in content


# ── EXP-4: HTML export ────────────────────────────────────────────────────────


class TestHtmlExport:
    """HTML (Netscape bookmark) export format (EXP-4)."""

    @pytest.mark.asyncio
    async def test_html_returns_200_with_correct_media_type(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.get(f"{_URL}?format=html", headers=auth_headers)
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    @pytest.mark.asyncio
    async def test_html_contains_netscape_header(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.get(f"{_URL}?format=html", headers=auth_headers)
        content = response.content.decode("utf-8")
        assert "NETSCAPE-Bookmark-file-1" in content


# ── EXP-5: Unsupported format ─────────────────────────────────────────────────


class TestUnsupportedFormat:
    """Invalid format → 400 (EXP-5)."""

    @pytest.mark.asyncio
    async def test_unknown_format_returns_400(
        self, client: AsyncClient, auth_headers: dict, test_user: User
    ):
        response = await client.get(f"{_URL}?format=xml", headers=auth_headers)
        assert response.status_code == 400
        assert "xml" in response.json()["detail"].lower()