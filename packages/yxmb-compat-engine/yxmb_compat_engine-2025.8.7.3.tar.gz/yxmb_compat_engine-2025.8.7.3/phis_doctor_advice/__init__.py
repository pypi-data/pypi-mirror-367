import random

# 重构建议池：每条建议都标记适用的疾病类型
advice_pool = [
    # 核心监测建议（根据疾病类型自动选择）
    {'condition': ('高血压', '糖尿病'), 'advice': '定期监测血压、血糖、足背动脉;'},
    {'condition': ('高血压',), 'advice': '定期监测血压、足背动脉;'},
    {'condition': ('糖尿病',), 'advice': '定期监测血糖、足背动脉;'},
    # 核心通用建议（所有患者都适用）
    {
        'condition': ('通用',),
        'advice': '严格遵医嘱用药，注意药物剂量、用法、时间，勿自行更改或停药;',
    },
    {'condition': ('通用',), 'advice': '低盐低脂饮食，每日食盐摄入量不超过5克;'},
    {'condition': ('通用',), 'advice': '避免被动吸烟;'},
    {'condition': ('通用',), 'advice': '保证7-8小时优质睡眠，避免熬夜;'},
    # 糖尿病专用建议
    {'condition': ('糖尿病',), 'advice': '每日监测晨起空腹血糖;'},
    {'condition': ('糖尿病',), 'advice': '学习低血糖识别与处理，随身携带糖果;'},
    {'condition': ('糖尿病',), 'advice': '每年至少1次眼底检查、肾功能检查;'},
    {'condition': ('糖尿病',), 'advice': '足部每日检查，预防糖尿病足;'},
    {'condition': ('糖尿病',), 'advice': '限制精制碳水摄入，增加全谷物比例;'},
    {'condition': ('糖尿病',), 'advice': '学习食物升糖指数(GI)概念;'},
    {'condition': ('糖尿病',), 'advice': '控制餐后2小时血糖在10mmol/L以下;'},
    {'condition': ('糖尿病',), 'advice': '记录血糖监测日记;'},
    # 高血压专用建议
    {'condition': ('高血压',), 'advice': '每日监测晨起空腹血压;'},
    {'condition': ('高血压',), 'advice': '保持情绪稳定，避免情绪剧烈波动;'},
    {'condition': ('高血压',), 'advice': '冬季注意保暖，避免寒冷刺激;'},
    {'condition': ('高血压',), 'advice': '收缩压控制在130mmHg以下;'},
    {'condition': ('高血压',), 'advice': '记录血压监测日记;'},
    # 通用扩展建议
    {'condition': ('通用',), 'advice': '烹饪使用植物油，避免动物油脂;'},
    {'condition': ('通用',), 'advice': '外出携带疾病卡片和应急药物;'},
    {'condition': ('通用',), 'advice': '避免长时间静坐，每小时活动5分钟;'},
    {'condition': ('通用',), 'advice': '出现头晕、心悸、视物模糊立即就医;'},
    {'condition': ('通用',), 'advice': '定期进行心血管风险评估;'},
    {'condition': ('通用',), 'advice': '流感季节前接种疫苗;'},
    # 结尾建议（所有患者都适用）
    {'condition': ('通用',), 'advice': '预防并发症，如有不适立即就医，定期复诊;'},
    {'condition': ('通用',), 'advice': '若控制不佳或出现异常，建议上级医院就诊'},
]


def _generate_doctor_advice(mb_type):
    """根据疾病类型生成针对性的医生建议组合"""
    advice_list = []

    # 1. 添加监测建议（根据疾病类型）
    for item in advice_pool:
        if isinstance(item, dict) and all(
            disease in mb_type for disease in item['condition']
        ):
            advice_list.append(item['advice'])
            break

    # 2. 添加核心通用建议（必选）
    core_advices = [
        item['advice']
        for item in advice_pool
        if isinstance(item, dict)
        and '通用' in item['condition']
        and '建议' not in item['advice']
    ]
    # 确保核心建议按顺序添加
    core_advices = core_advices[:4]  # 取前4条核心通用建议
    advice_list.extend(core_advices)

    # 3. 根据疾病类型筛选相关建议
    disease_specific = []
    general_advices = []

    for item in advice_pool:
        if not isinstance(item, dict):
            continue

        # 跳过已经添加的核心建议
        if item['advice'] in advice_list:
            continue

        # 收集特定疾病建议
        if '通用' not in item['condition']:
            if all(disease in mb_type for disease in item['condition']):
                disease_specific.append(item['advice'])

        # 收集通用建议
        elif '通用' in item['condition']:
            general_advices.append(item['advice'])

    # 4. 添加疾病特定建议（优先）
    # 根据疾病数量决定添加数量：单病种2-4条，双病种4-6条
    num_disease = len(mb_type)
    num_to_add = random.randint(2, 4) if num_disease == 1 else random.randint(4, 6)

    if len(disease_specific) > num_to_add:
        advice_list.extend(random.sample(disease_specific, num_to_add))
    else:
        advice_list.extend(disease_specific)

    # 5. 添加通用建议（补充）
    remaining = 15 - len(advice_list)  # 目标总建议数约15条
    if remaining > 0 and general_advices:
        num_general = min(remaining, random.randint(3, 5), len(general_advices))
        advice_list.extend(random.sample(general_advices, num_general))

    # 6. 添加结尾建议
    ending_advices = [
        item['advice']
        for item in advice_pool
        if isinstance(item, dict)
        and '建议' in item['advice']
        and item['advice'] not in advice_list  # 确保不添加重复的建议
    ]
    advice_list.extend(ending_advices)

    # 7. 重新编号并组合
    renumbered_advice = ''
    for i, advice in enumerate(advice_list, 1):
        renumbered_advice += f'{i}.{advice}\n'

    return renumbered_advice


def generate_doctor_advice(mb_type):
    if '高血压' in mb_type and '糖尿病' not in mb_type:
        doctor_advice = _generate_doctor_advice('高血压')
    elif '糖尿病' in mb_type and '高血压' not in mb_type:
        doctor_advice = _generate_doctor_advice('糖尿病')
    elif '高血压' in mb_type and '糖尿病' in mb_type:
        doctor_advice = _generate_doctor_advice('糖尿病')
        doctor_advice = doctor_advice.replace(
            '定期监测血糖、足背动脉', '定期监测血糖、血压，足背动脉'
        )
    return doctor_advice
