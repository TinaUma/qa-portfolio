"""Спринт 13/14-16 — UI-тест: регистрация через форму на staging.sortula.ru.

Что проверяем:
  1. Кнопка отправки заблокирована без принятия условий (негативный сценарий)
  2. Успешная регистрация через UI показывает блок .alert-success

Инструменты: Playwright (pytest-playwright) + Allure-отчёты.
Запуск: pytest ui/ -v
        pytest ui/ -v --headed
        pytest ui/ -v --alluredir=allure-results   # с Allure
"""

import uuid

import allure
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "https://staging.sortula.ru"


@allure.title("Негативный: кнопка submit disabled без принятия условий")
@allure.description(
    "Проверяем что кнопка отправки заблокирована пока пользователь не поставил галочку terms"
)
@allure.severity(allure.severity_level.CRITICAL)
def test_submit_disabled_without_terms(page: Page):
    """Негативный сценарий: кнопка неактивна, пока не приняты условия использования."""
    with allure.step("Открыть страницу регистрации"):
        page.goto(f"{BASE_URL}/register")
        page.wait_for_load_state("networkidle")

    with allure.step("Проверить что кнопка submit disabled"):
        submit = page.locator('[data-testid="register-submit"]')
        expect(submit).to_be_disabled()


@allure.title("Успешная регистрация: появляется .alert-success")
@allure.description(
    "Заполняем email, принимаем условия, нажимаем submit — ожидаем блок подтверждения"
)
@allure.severity(allure.severity_level.CRITICAL)
def test_register_via_ui(page: Page):
    """Успешная регистрация: после отправки формы появляется .alert-success."""
    email = f"tina-ui-{uuid.uuid4().hex[:8]}@example.com"

    with allure.step(f"Открыть страницу регистрации"):
        page.goto(f"{BASE_URL}/register")
        page.wait_for_load_state("networkidle")

    with allure.step(f"Ввести email: {email}"):
        page.locator('[data-testid="register-email"]').fill(email)

    with allure.step("Принять условия использования (checkbox terms)"):
        page.locator('[data-testid="register-terms"]').check()

    with allure.step("Нажать кнопку Зарегистрироваться"):
        page.locator('[data-testid="register-submit"]').click()

    with allure.step("Проверить появление .alert-success"):
        success_alert = page.locator(".alert-success")
        expect(success_alert).to_be_visible(timeout=5000)
