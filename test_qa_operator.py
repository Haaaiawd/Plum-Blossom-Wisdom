import os
import json

def extract_and_merge_conversations(folder_path, output_file):
    all_conversations = []

    # 遍历指定文件夹
    for filename in os.listdir(folder_path):
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            
            # 打开并读取JSON文件
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                # 提取需要的字段
                for item in data:
                    try:
                        extracted = {
                            'instruction': item['input'],
                            'output': item['output'],
                            'system': SYSTEM_PROMPT,
                        }
                        # 将每个对话包装在一个 'conversation' 键中，并作为独立对象加入列表
                        all_conversations.append(extracted)
                    except Exception as e:
                        # 如果不满足json条件就不进行保存，这个时候一般都是json出错
                        print(f"Error processing item: {item}, error: {e}")

    # 将合并后的所有对话数据写入一个新的JSON文件
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(all_conversations, file, ensure_ascii=False, indent=4)

# 使用示例
SYSTEM_PROMPT = """你是精通西马的左派人士，反对修正主义，批判性看待西马"""
folder_path = 'real'  # 要扫描的文件夹路径
output_file = 'success.json'  # 输出文件的名称和路径
extract_and_merge_conversations(folder_path, output_file)