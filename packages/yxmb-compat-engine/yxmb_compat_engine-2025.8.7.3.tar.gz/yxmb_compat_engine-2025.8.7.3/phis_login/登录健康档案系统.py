import logging
from kapybara import WebDriver, shared_data
from kapybara.form_element import FormElement
from phis_login.gui_error import gui_error
from phis_login.登录医生工作站 import 登录医生工作站

def 登录健康档案系统():
    from phis_config import AdminConfig
    url = AdminConfig.登录网址
    account = AdminConfig.登录用户名
    password = AdminConfig.登录密码
    department_name = AdminConfig.登录科室名称
    name = department_name

    driver: WebDriver = shared_data.driver

    # 设置登录超时
    driver.set_page_load_timeout(600)
    try:
        driver.get(url)
    except:
        try:
            driver.get(url)
        except:
            error_message = '登录页面加载失败，请检查URL是否正确或网络连接是否正常。'
            logging.error(error_message)
            gui_error(error_message)

            driver.quit()
            exit(-1)

    driver.maximize_window()

    登录医生工作站(account, password)

    FormElement('健康档案', '//*[@id="ext-gen3"]/section/div[3]/ul/li[1]/a').click()
    # 关闭 “系统提示” 对话框
    FormElement('确定', '//*[@id="button-1005-btnIconEl"]').click()
    # 点击慢病随访
    FormElement('档案管理', 'navLi_10103').click()
