from phis_doctor_advice import generate_doctor_advice

if __name__ == "__main__":
    # 示例：生成高血压患者的医生建议
    mb_type = "高血压"
    advice = generate_doctor_advice(mb_type)
    # print(f"针对{mb_type}的医生建议：")
    print(advice)
