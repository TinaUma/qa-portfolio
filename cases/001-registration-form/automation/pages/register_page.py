"""Page Object для страницы регистрации staging.sortula.ru/register."""

from playwright.sync_api import Page, expect

BASE_URL = "https://staging.sortula.ru"


class RegisterPage:
    def __init__(self, page: Page):
        self.page = page
        self.email_input = page.locator('[data-testid="register-email"]')
        self.terms_checkbox = page.locator('[data-testid="register-terms"]')
        self.submit_button = page.locator('[data-testid="register-submit"]')
        self.success_alert = page.locator(".alert-success")

    def open(self):
        self.page.goto(f"{BASE_URL}/register")
        self.page.wait_for_load_state("networkidle")

    def fill_email(self, email: str):
        self.email_input.fill(email)

    def accept_terms(self):
        self.terms_checkbox.check()

    def submit(self):
        self.submit_button.click()

    def expect_submit_disabled(self):
        expect(self.submit_button).to_be_disabled()

    def expect_success(self):
        expect(self.success_alert).to_be_visible(timeout=5000)
