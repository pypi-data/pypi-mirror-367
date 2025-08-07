from kapybara.browserlib.custom_browser import create_browser
from kapybara.shared_data import shared_data
from kapybara import WebDriver
from .LoginPage import LoginPage

def login(config):
    if not hasattr(shared_data, 'driver'):
        _driver = create_browser()
    driver: WebDriver = shared_data.driver
    driver.get(config['base_url'])
    workflow = config.get('workflow', [])
    if not workflow:
        raise ValueError('Workflow is empty or not defined in the configuration.')

    for action in workflow:
        key = action.keys()[0]
        if key != 'page':
            continue
        page_name = action['page']

        if page_name == 'login_page':
            args = {
                'args': action['args'],
                'wait': action.get('wait', 1),
                'check': action.get('check', ''),
                'retry': action.get('retry', 3),
                'then': action.get('then', []),
            }
            locators = config.get('locators', {}).get(page_name, {})
            page = LoginPage(locators, args)
            page.login()
