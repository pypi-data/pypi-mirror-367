from phis_lifestyle_advice import generate_lifestyle_advice

if __name__ == '__main__':
    # 示例
    new_sf_data = {'日吸烟量': 10, '日饮酒量': 20, '运动时间': 30}
    mb_group = ['无偏好', '老年人']
    mb_type = ['高血压']
    bmi = 25
    xb = '男'
    advice = generate_lifestyle_advice(new_sf_data, mb_group, bmi, xb)
    print(advice)
