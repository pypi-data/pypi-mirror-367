from kapybara.shared_data import shared_data
from kapybara import FormElement
import ddddocr
import time


class LoginPage:
    def __init__(self, locators, config):
        self.username = locators.get('username_input')
        self.password = locators.get('password_input')
        self.captcha = locators.get('captcha_input', None)
        self.login_button = locators.get('login_button')
        self.config = config
        self.then = config.get('then', [])

        self.ocr = ddddocr.DdddOcr(show_ad=False) if self.captcha else None

    def try_login(self, username, password, wait):
        FormElement(self.username[0], self.username[1]).set_value(username)
        FormElement(self.password[0], self.password[1]).set_value(password)
        if self.captcha:
            captcha_element = FormElement(self.captcha[0], self.captcha[1])
            text = self.ocr.classification(captcha_element.element.screenshot_as_png)
            captcha_element.set_value(text)
        FormElement(self.login_button[0], self.login_button[1]).click()
        time.sleep(wait)  # 等待页面加载

    def login(self):
        driver = shared_data.driver
        if not driver:
            raise RuntimeError('WebDriver is not initialized in shared_data.')

        username = self.config['args'][0]
        password = self.config['args'][1]

        username_value = (
            eval(username[(len('eval_') + 1) :])
            if username.startswith('eval_')
            else username
        )
        password_value = (
            eval(password[(len('eval_') + 1) :])
            if password.startswith('eval_')
            else password
        )

        retry = self.config.get('retry', 3)

        self.try_login(username_value, username_value)

        if not eval(self.config.get('check', 'True'), globals={'driver': driver}):
            for _ in range(retry - 1):
                self.try_login(username_value, password_value)

        if not eval(self.config.get('check', 'True'), globals={'driver': driver}):
            raise Exception('Login failed, please check your credentials or captcha.')

        for action in self.then:
            pass

