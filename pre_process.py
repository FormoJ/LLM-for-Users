import json
import os
# 读取原始JSON文件
folder_path = './data/pretrain'
for filename in os.listdir(folder_path):
    with open(folder_path + '/' + filename, 'r', encoding='GBK') as file:
        # 初始化一个空列表来存储结果
        result = []
        # 读取每一行
        for line in file:
            # 将每一行的JSON字符串转换为字典，并添加到结果列表中
            result.append(json.loads(line))

    # 将结果列表转换为JSON字符串，并写入新的文件
    with open('./data/processed'+filename, 'w', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=2)

    print("转换完成，结果已保存到" + filename)