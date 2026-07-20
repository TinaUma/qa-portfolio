"""Спринт 13/14-16/18 — UI-тест: регистрация через форму на staging.sortula.ru.

Спринт 18: рефакторинг под Page Object Model.
Локаторы вынесены в pages/register_page.py — тест читается как сценарий.

Запуск: pytest ui/ -v
        pytest ui/ -v --headed
        pytest ui/ -v --alluredir=allure-results
"""

import uuid

import allure
import pytest
from playwright.sync_api import Page

from pages.register_page import RegisterPage


@allure.title("Негативный: кнопка submit disabled без принятия условий")
@allure.description(
    "Проверяем что кнопка отправки заблокирована пока пользователь не поставил галочку terms"
)
@allure.severity(allure.severity_level.CRITICAL)
def test_submit_disabled_without_terms(page: Page):
    register_page = RegisterPage(page)

    with allure.step("Открыть страницу регистрации"):
        register_page.open()

    with allure.step("Проверить что кнопка submit disabled"):
        register_page.expect_submit_disabled()


@allure.title("Успешная регистрация: появляется .alert-success")
@allure.description(
    "Заполняем email, принимаем условия, нажимаем submit — ожидаем блок подтверждения"
)
@allure.severity(allure.severity_level.CRITICAL)
def test_register_via_ui(page: Page):
    email = f"tina-ui-{uuid.uuid4().hex[:8]}@example.com"
    register_page = RegisterPage(page)

    with allure.step("Открыть страницу регистрации"):
        register_page.open()

    with allure.step(f"Ввести email: {email}"):
        register_page.fill_email(email)

    with allure.step("Принять условия использования"):
        register_page.accept_terms()

    with allure.step("Нажать кнопку Зарегистрироваться"):
        register_page.submit()

    with allure.step("Проверить появление .alert-success"):
        register_page.expect_success()
