"""
模拟页面中的 普通随访和慢病随访记录页面
这些页面显示随访年，下面是随访月和日的分组。
本类提供了：获取所有日期，点击某个日期，判断某个日期是否存在。
"""

from .shortcuts import WebDriver, EC, WebDriverWait, By
import re

class YearDateTree:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        driver.switch_to.default_content()

        first_iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="ext-gen21"]/iframe')))
        driver.switch_to.frame(first_iframe)

        # panel 的 类为 x-panel-body
        self.year_date_tree = self.driver.find_element(By.CLASS_NAME, "x-panel-body")

        self.selectors = {
            'panel': '//div[contains(@class, "x-panel-body")]',
            'collapsed_divs': '//div[contains(@class, "x-panel-body")]/div',
        }

        self.years = self.find_all_years()

        self.date_elements = {}

        self.init_all_dates()

    def find_all_years(self):
        """
        获取所有的年份
        :return: 年份列表
        """
        collapsed_divs = self.year_date_tree.find_elements(By.XPATH, self.selectors['collapsed_divs'])
        if len(collapsed_divs) == 0:
            return []

        years = []
        for div in collapsed_divs:
            # remove the class x-grid-group-collapsed
            self.driver.execute_script("""
                arguments[0].classList.remove('x-grid-group-collapsed');
            """, div)

            title = div.find_element(By.XPATH, './/div[contains(@class, "x-grid-group-title")]')
            # find year in ": 2025 (1 次)"
            year_text = re.findall(r': (\d{4})', title.text)
            if year_text:
                years.append(year_text[0])
        return years

    def init_all_dates(self):
        for year in self.years:
            year_div = self.year_date_tree.find_element(By.XPATH, f'.//div[contains(@class, "x-grid-group-title") and contains(text(), "{year}")]')

            date_divs = year_div.find_elements(By.XPATH, '//table/tbody/tr')
            for date_div in date_divs:
                date_text = date_div.text.strip()
                result = re.findall(r'(\d{2})-(\d{2})', date_text)
                if len(result) != 1:
                    continue
                month, day = result[0]
                month = int(month)
                day = int(day)
                self.date_elements[f"{year}-{month:02d}-{day:02d}"] = date_div

    def has_date(self, date: str) -> bool:
        """
        判断某个日期是否存在
        :param date: 日期字符串，格式为 'YYYY-MM-DD'
        :return: 如果存在返回 True，否则返回 False
        """
        return date in self.date_elements
    
    def click_date(self, date: str):
        """
        点击某个日期
        :param date: 日期字符串，格式为 'YYYY-MM-DD'
        :raises ValueError: 如果日期不存在
        """
        if not self.has_date(date):
            raise ValueError(f"Date {date} does not exist in the year date tree.")
        
        date_element = self.date_elements[date]
        self.driver.execute_script("arguments[0].click();", date_element)
