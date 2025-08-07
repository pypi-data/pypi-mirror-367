def generate_lifestyle_advice(new_sf_data, mb_group, bmi, xb):
    # 生活指导建议项
    advice_items = []
    # 戒烟建议（增加具体替代方案）
    if new_sf_data['日吸烟量'] != 0:
        advice_items.append(
            '建议采用"5D戒烟法"：Delay（延迟吸烟）、Deep breathing（深呼吸）、Drink water（喝水）、Do something（转移注意）、Discuss（寻求支持）')

    # 控制饮酒（细化酒精换算）
    if new_sf_data['日饮酒量'] != 0:
        alcohol_advice = {
            '男': '建议控制饮酒量（25克酒精≈啤酒750ml/葡萄酒250ml/白酒75ml），避免混合饮酒',
            '女': '建议控制饮酒量（15克酒精≈啤酒450ml/葡萄酒150ml/白酒50ml），经期孕期禁酒'
        }
        advice_items.append(alcohol_advice.get(xb, '建议减少酒精摄入'))

    # 饮食调节（增加具体营养素建议）
    if '无偏好' not in mb_group:
        advice_items.extend([
            '饮食建议：每日盐摄入<5g，烹调油25-30g',
            '优质蛋白选择：鱼虾禽类＞畜肉，每周至少2次深海鱼',
            '膳食纤维摄入：每日25-30g（如燕麦、杂豆、绿叶菜）',
            '烹饪方式建议：蒸煮炖优于煎炸烤'
        ])

    # 运动建议（增加运动类型指导）
    if '残疾人' not in mb_group:
        if new_sf_data['运动时间'] == 0:
            advice_items.append('运动建议：从每天10分钟快走开始，每周递增5分钟')
        elif bmi >= 24:
            advice_items.extend([
                '有氧运动：每周5次，每次30分钟（快走、游泳、骑行）',
                '抗阻训练：每周2-3次（弹力带、深蹲）',
                '核心训练：每天5分钟平板支撑'
            ])
    waist = new_sf_data['腰围']
    idf = False
    if xb == '女':
        if waist >= 85:
            idf = True
    elif xb == '男':
        if waist >= 90:
            idf = True
    if idf:
        advice_items.append('通过健康饮食和规律运动，减小腰围')

    # 老年人专项（增加具体措施）
    if '老年人' in mb_group:
        advice_items.extend([
            '防跌倒措施：居家安装扶手，穿防滑鞋',
            '骨质疏松预防：每日钙摄入1000-1200mg+维生素D800IU',
            '认知训练：每日脑力活动（阅读、棋牌）30分钟'
        ])

    # 新增健康管理模块
    advice_items.extend([
        '睡眠管理：保证7-8小时/天，避免睡前使用电子设备',
        '心理调节：每日正念冥想10分钟',
        '环境健康：室内PM2.5＜37μg/m³，湿度40%-60%'
    ])

    # 用药指导（增加具体注意事项）
    advice_items.append('用药管理：使用分药盒，设置服药提醒，注意药物相互作用（如阿司匹林与酒精）')

    # 卫生防疫（增加具体标准）
    advice_items.extend([
        '手卫生：七步洗手法，接触公共物品后及时消毒',
        '呼吸道防护：N95口罩每4小时更换',
        '环境通风：每日开窗3次，每次＞30分钟'
    ])

    # 生成最终生活指导建议
    life_suggestions = '\n'.join([f'{i + 1}. {item}' for i, item in enumerate(advice_items)])

    return life_suggestions
