# get_mz_time 已被 get_mz_data 替换

# 旧代码
def _nouse1(driver, record, headers):
    get_mz_time = lambda :1
    get_mz_data = lambda :1
    new_sf_time = 1

    print("--------------------检查门诊日期--------------------")
    mz_time = get_mz_time(driver, record, headers)

    # ...

    print("--------------------获取门诊数据--------------------")
    mz_data = get_mz_data(driver, new_sf_time)
    print("获取门诊数据:", mz_data)


# 新代码
def _nouse(driver, record, headers):
    get门诊数据 = lambda x: 1
    get_selected_mz_data = 1
    new_sf_time = 1

    print('--------------------检查门诊日期--------------------')
    mz_time, o_result = get门诊数据(driver, record, headers)


    # ...

    print('--------------------获取门诊数据--------------------')
    mz_data = get_selected_mz_data(o_result, new_sf_time)
    print('获取门诊数据:', mz_data)