"""Спринт 13 — UI-тест: регистрация через форму на staging.sortula.ru.

Что проверяем:
  1. Кнопка отправки заблокирована без принятия условий (негативный сценарий)
  2. Успешная регистрация через UI показывает блок .alert-success

Инструменты: Playwright (pytest-playwright), синхронный API.
Запуск: pytest ui/ -v
        pytest ui/ -v --headed          # с открытым браузером
        pytest ui/ -v --browser webkit  # на WebKit
"""

import uuid

import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://staging.sortula.ru"


def test_submit_disabled_without_terms(page: Page):
    """Негативный сценарий: кнопка неактивна, пока не приняты условия использования."""
    page.goto(f"{BASE_URL}/register")
    page.wait_for_load_state("networkidle")

    submit = page.locator('[data-testid="register-submit"]')
    expect(submit).to_be_disabled()


def test_register_via_ui(page: Page):
    """Успешная регистрация: после отправки формы появляется .alert-success."""
    email = f"tina-ui-{uuid.uuid4().hex[:8]}@example.com"

    # Открываем страницу регистрации
    page.goto(f"{BASE_URL}/register")
    page.wait_for_load_state("networkidle")

    # Заполняем email
    page.locator('[data-testid="register-email"]').fill(email)

    # Принимаем условия — без этого кнопка disabled (data-testid="register-terms")
    page.locator('[data-testid="register-terms"]').check()

    # Нажимаем кнопку отправки
    page.locator('[data-testid="register-submit"]').click()

    # Проверяем успех: появился блок с подтверждением
    success_alert = page.locator(".alert-success")
    expect(success_alert).to_be_visible(timeout=5000)
