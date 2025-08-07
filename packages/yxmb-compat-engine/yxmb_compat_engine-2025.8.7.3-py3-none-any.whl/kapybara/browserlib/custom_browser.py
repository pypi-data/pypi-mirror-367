from yxmb_compatlib.mylib.main import create_browser as _create_browser
from yxmb_compatlib.mylib.main import CustomBrowser as _CustomBrowser


def create_browser(disable_image=False):
    driver = _create_browser(disable_image=disable_image)
    from kapybara.shared_data import shared_data

    shared_data.driver = driver
    return driver


class CustomBrowser(_CustomBrowser):
    """
    继承自 yxmb_compatlib 的 CustomBrowser，使用 create_browser 工厂方法。
    保持与原有 CustomBrowser 的兼容性。
    """

    def __init__(self, disable_image=False):
        # 不调用 super().__init__() 来避免创建第一个浏览器实例。
        # 直接使用本模块的 create_browser 函数创建浏览器，
        # 它会处理共享数据的逻辑，并返回 driver 实例。
        self._driver = create_browser(disable_image=disable_image)
