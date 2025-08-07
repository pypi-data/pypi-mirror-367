import logging

import ddddocr
from pathlib import Path
from kapybara.form_element import FormElement
from kapybara import shared_data, WebDriver
from phis_login.gui_error import gui_error

retry_count = 0


def 登录医生工作站(username: str, password: str):
    """
    输入用户名和密码并点击登录
    """
    global retry_count
    FormElement('用户名', 'phisname').set_value(username)
    FormElement('密码', 'password').set_value(password)

    captcha_element = FormElement('验证码', 'img')
    captcha_element.element.screenshot('captcha.png')

    ocr = ddddocr.DdddOcr(show_ad=False)
    img_bytes = Path('captcha.png').read_bytes()
    Path("captcha.img").unlink(missing_ok=True)
    res = ocr.classification(img_bytes)
    logging.info('识别出的验证码为：' + res)
    FormElement('验证码输入', 'verifyCode').set_value(res)
    try:
        FormElement('登录', '.submit-btn').click()
    except:
        logging.info('无需点击登录')

    import time

    time.sleep(1)  # 等待页面加载
    driver: WebDriver = shared_data.driver
    current_url = driver.current_url
    if 'phis/app/login' in current_url:
        retry_count += 1
        if retry_count < 3:
            logging.warning(f'登录失败，正在重试... ({retry_count}/3)')
            登录医生工作站(username, password)
        else:
            error_message = '登录失败，请检查用户名、密码或验证码是否正确。'
            logging.error(error_message)
            gui_error(error_message)
            raise Exception(error_message)
