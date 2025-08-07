import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from yxmb_compatlib.comment.check_element import check_element
from yxmb_compatlib.comment.envWrite import env_write
from yxmb_compatlib.comment.excle_create import check_and_create_excel
from yxmb_compatlib.comment.write_excle import excel_append
from kapybara import create_browser, FormElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from yxmb_compatlib.comment.登录头 import time, is_software_expired
from yxmb_compatlib.compements.assemblies.check_diseases import check_diseases
from yxmb_compatlib.compements.assemblies.get_mb_data import get_mb_data
from yxmb_compatlib.compements.quarterly_statistics import quarterly_statistics
from yxmb_compat_engine.compat.get_mz_data import get门诊数据
from .new_followup_impl import new_follow_up_impl
from yxmb_compatlib.comment.登录头 import login

def main1(quaterly_statistics_only=False):
    # 等待时间设置为10秒，或根据需要调整
    wait_time = 10

    folder_path = '执行结果/异常名单.xlsx'
    check_and_create_excel(folder_path)
    # 检查文件是否包含表头
    try:
        existing_data = pd.read_excel(folder_path)
        required_columns = {'身份证号', '异常原因'}
        if not required_columns.issubset(existing_data.columns):
            # 文件没有表头，需要添加表头
            header_df = pd.DataFrame(columns=['身份证号', '异常原因'])
            header_df.to_excel(folder_path, index=False, header=True)
            print('文件没有表头,已添加表头')
    except pd.errors.EmptyDataError:
        # 文件为空，需要添加表头
        header_df = pd.DataFrame(columns=['身份证号', '异常原因'])
        header_df.to_excel(folder_path, index=False, header=True)
        print('文件为空,已添加表头')

    folder_path = '执行结果/成功名单.xlsx'
    check_and_create_excel(folder_path)
    # 检查文件是否包含表头
    try:
        existing_data = pd.read_excel(folder_path)
        required_columns = {'身份证号', '成功'}
        if not required_columns.issubset(existing_data.columns):
            # 文件没有表头，需要添加表头
            header_df = pd.DataFrame(columns=['身份证号', '成功'])
            header_df.to_excel(folder_path, index=False, header=True)
            print('文件没有表头,已添加表头')
    except pd.errors.EmptyDataError:
        # 文件为空，需要添加表头
        header_df = pd.DataFrame(columns=['身份证号', '成功'])
        header_df.to_excel(folder_path, index=False, header=True)
        print('文件为空,已添加表头')

    # 读取已查询数量
    try:
        with open('执行结果/env.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            fourth_line = lines[2].strip().split(':')
            # 提取查询数量并去除空白字符
            number = int(fourth_line[-1].strip())
            print('已完成数量:', number)
    except FileNotFoundError:
        print('文件不存在，请检查文件路径是否正确。')
    except Exception as e:
        print(f'读取文件时发生错误：{e}')

    df1 = pd.read_excel('文档/名单.xlsx', engine='openpyxl')
    data1 = df1.to_dict('records')
    max_number1 = len(data1)
    # 获取表头（列名）
    headers = df1.columns.tolist()
    print('总操作数:', max_number1)

    env_write('执行结果/env.txt', 1, f'总操作数:{max_number1}')
    df = pd.read_excel(
        '文档/名单.xlsx', engine='openpyxl', skiprows=range(1, number + 1)
    )
    data = df.to_dict('records')
    sy_number = len(data)
    print('剩余操作数:', sy_number)

    driver = create_browser()
    login(driver)

    iframe_element = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located(
            (By.XPATH, "//iframe[contains(@src, '/phis/app/ehr')]")
        )
    )
    driver.switch_to.frame(iframe_element)

    # 包含子机构
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                '//*[@id="includeSubOrgs"]',
            )
        )
    ).click()

    # 输入身份证号
    for index, record in enumerate(data):
        driver.switch_to.default_content()
        iframe = FormElement('iframe', '//*[@id="ehrCenterPanel"]/iframe').element
        driver.switch_to.frame(iframe)
        sfzh = record['身份证号']
        sfzh = str(sfzh).replace('x', 'X').strip()
        timeout_occurred = False  # 设置一个标志变量
        print('当前处理身份证号:', sfzh)
        env_write('执行结果/env.txt', 2, f'当前处理身份证号:{sfzh}')

        id_number = f'{sfzh}'

        shen_fen = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="idNumber"]'))
        )
        shen_fen.clear()  # 清除输入框
        shen_fen.send_keys(str(id_number))

        FormElement('查询', '//*[@id="chaxun"]').click()
        print('点击查询')

        # 使用一个无限循环，直到找不到元素
        while True:
            try:
                # 如果找不到元素，break跳出循环
                if not check_element(driver):
                    break
            except:
                print('元素不存在')
                break
        try:
            # 等待元素可见并获取该元素
            tsd = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located(
                    (By.XPATH, f'//div[contains(text(), "{id_number}")]')
                )
            )
        except:
            number = number + 1
            env_write('执行结果/env.txt', 3, f'已完成数量:{number}')
            print(f'无档案')
            excel_append(
                '执行结果/异常名单.xlsx',
                '身份证号',
                sfzh + '\t',
                '异常原因',
                '暂无建档',
            )
            continue

        # 慢病类型
        # 等待元素可见并获取该元素
        mb_fl = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located(
                (By.XPATH, '//*[@id="ext-gen27"]/div/table/tbody/tr/td[8]/div')
            )
        )

        # 获取该元素的文本
        mb_fl_text = mb_fl.text
        print('慢病分类:', mb_fl_text)

        element_xpath = f'//div[contains(text(), "{id_number}")]'
        script = f"""
                    var element = document.evaluate('{element_xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                    if (element) {{
                        var event = new MouseEvent('dblclick', {{
                            'view': window,
                            'bubbles': true,
                            'cancelable': true
                        }});
                        element.dispatchEvent(event);
                    }}
                    """
        driver.execute_script(script)  # 双击进入
        time.sleep(1.5)
        original_windows = driver.current_window_handle

        # 切换到最新的窗口
        driver.switch_to.window(driver.window_handles[-1])
        driver.maximize_window()

        # 判断日期是否需要读表
        if '随访日期' in headers:
            skip = False
        else:
            skip = True

        """
        获取档案数据
        """
        print('--------------------获取档案数据--------------------')
        mb_data = get_mb_data(driver)
        print('获取档案数据', mb_data)
        sign = False

        # 检查是否有慢病随访按钮
        s = check_diseases(driver)
        if not s:
            print('没有慢病随访按钮')
            print(f'{sfzh}运行完成')
            excel_append(
                '执行结果/异常名单.xlsx',
                '身份证号',
                sfzh + '\t',
                '异常原因',
                '没有慢病随访按钮',
            )

            number += 1
            env_write('执行结果/env.txt', 3, f'已完成数量:{number}')

            driver.close()
            # 切换回原始窗口
            driver.switch_to.window(original_windows)
            continue

        mz_time = []
        if not quaterly_statistics_only:
            """
            检查需要新建的随访日期
            """
            print('--------------------检查门诊日期--------------------')
            mz_time, o_result = get门诊数据(driver, record, headers)
            print('检查门诊日期', mz_time)
            if not mz_time and skip is True:
                print('无符合条件的门诊日期')
                excel_append(
                    '执行结果/异常名单.xlsx',
                    '身份证号',
                    sfzh + '\t',
                    '异常原因',
                    '无符合条件的门诊日期',
                )
            else:
                new_follow_up_impl(driver=driver, 
                                mb_data=mb_data,
                                sfzh=sfzh,
                                mz_time=mz_time,
                                skip=skip,
                                headers=headers,
                                record=record,
                                o_result=o_result,)
        # 慢病随访季度统计
        print('--------------------随访季度统计--------------------')

        quarterly_statistics(driver, sfzh, mz_time)

        print(f'{sfzh}运行完成')

        number += 1
        env_write('执行结果/env.txt', 3, f'已完成数量:{number}')

        driver.close()
        # 切换回原始窗口
        driver.switch_to.window(original_windows)

    driver.quit()
    print('程序已执行完成')
    env_write('执行结果/env.txt', 10, f'执行完成:1')


def main(quaterly_statistics_only=False):
    from phis_logging import setup_logging
    setup_logging()
    if is_software_expired():
        print('软件已到期')
    else:
        main1(quaterly_statistics_only)

if __name__ == '__main__':
    main()
