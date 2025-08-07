from yxmb_compat_engine.compat.get_mz_data import get_selected_mz_data
from yxmb_compatlib.comment.write_excle import excel_append
from yxmb_compatlib.compements.assemblies.check_sf_date import check_sf_date
from yxmb_compatlib.compements.assemblies.check_sf_date_same_day import check_sf_date_same_day
from yxmb_compatlib.compements.assemblies.get_new_sf_data import get_new_sf_data
from yxmb_compatlib.compements.assemblies.get_new_sf_date import get_new_sf_time
from yxmb_compatlib.compements.assemblies.get_sf_data import get_sf_data
from yxmb_compatlib.compements.assemblies.get_tj_data import get_tj_data
from yxmb_compatlib.compements.assemblies.has_current_quarter import has_current_quarter
from yxmb_compatlib.compements.new_assessment import new_follow_up
from yxmb_compatlib.compements.tool import process_date, safe_key


def new_follow_up_impl(driver, mz_time, sfzh, record, headers, skip, o_result, mb_data):
    print('符合条件的门诊日期:', mz_time)
    print('--------------------检查已新建随访日期--------------------')
    sf_time = check_sf_date(driver)
    print('已建随访日期:', sf_time)

    # 判断当前季度是否已有随访
    # 获取本季度已做过慢病随访，是否继续保存
    with open('./执行结果/env.txt', 'r', encoding='utf-8') as file:
        content = file.readlines()
    # 使用 split() 方法分割字符串
    yes = content[5].replace('：', ':').split(':')[1].strip()
    print('获取本季度已做过慢病随访，是否继续保存:', yes)

    if yes == '否':
        result = has_current_quarter(sf_time, record, headers)
    else:
        result = False

    # 判断是否存在同一天的随访日期
    same_result = check_sf_date_same_day(sf_time, record, headers)
    if same_result is True:
        excel_append(
            '执行结果/异常名单.xlsx',
            '身份证号',
            sfzh + '\t',
            '异常原因',
            '随访日期读表,但同一天已有随访',
        )
    else:
        if result is True and skip is False:
            print('随访日期读表,但同一季度已有随访')
            excel_append(
                '执行结果/异常名单.xlsx',
                '身份证号',
                sfzh + '\t',
                '异常原因',
                '随访日期读表,但同一季度已有随访',
            )
        else:
            # 根据门诊和随访日期，判断计算出需要新建随访的日期
            new_sf_time = get_new_sf_time(mz_time, sf_time)
            if skip is False:
                new_sf_time = record['随访日期']
                new_sf_time = [process_date(new_sf_time)]
            print('需要新建随访日期:', new_sf_time)

            print(
                '--------------------获取时间范围内所有的随访数据--------------------'
            )
            sf_data = get_sf_data(driver)
            print('获取时间范围内所有的随访数据:', sf_data)

            print('--------------------获取门诊数据--------------------')
            mz_data = get_selected_mz_data(o_result, new_sf_time)
            print('获取门诊数据:', mz_data)

            print('--------------------获取体检数据--------------------')
            tj_data = get_tj_data(driver)
            print('获取体检数据:', tj_data)

            if new_sf_time:
                for n_sf_time in new_sf_time:
                    """
                    根据档案、门诊、体检、往次随访数据  确定新建的随访数据
                    """
                    print(
                        '--------------------确定随访数据--------------------'
                    )
                    new_sf_data = get_new_sf_data(
                        mb_data, mz_data, tj_data, n_sf_time, sf_data, sfzh
                    )
                    print('确定随访数据', new_sf_data)

                    print('--------------------新建随访--------------------')
                    new_follow_up(driver, new_sf_data, sfzh, record, headers)

                    # 合并新随访数据
                    formatted_new_data = {
                        new_sf_data['随访日期']: {
                            '收缩压': str(new_sf_data['收缩压']),
                            '舒张压': str(new_sf_data['舒张压']),
                            '空腹血糖': str(new_sf_data['空腹血糖']),
                            '心率': str(new_sf_data['心率']),
                            '身高': str(new_sf_data['身高']),
                            '体重': str(new_sf_data['体重']),
                            '腰围': str(new_sf_data['腰围']),
                            '日吸烟量': str(new_sf_data['日吸烟量']),
                            '日饮酒量': str(new_sf_data['日饮酒量']),
                            '运动次数': str(new_sf_data['运动次数']),
                            '运动时间': str(new_sf_data['运动时间']),
                            '主食量': new_sf_data[
                                '主食量'
                            ],  # 保持原样，因为它是字符串类型
                        }
                    }
                    combined_data = {**sf_data, **formatted_new_data}
                    sf_data = dict(
                        sorted(
                            combined_data.items(),
                            key=lambda item: safe_key(item[1]),
                        )
                    )

                    # 输出结果
                    print('合并后的往次随访数据', sf_data)

            else:
                print('不需要新建随访')
                excel_append(
                    '执行结果/异常名单.xlsx',
                    '身份证号',
                    sfzh + '\t',
                    '异常原因',
                    f'已建随访日期-{sf_time}, 门诊日期-{mz_time}',
                )