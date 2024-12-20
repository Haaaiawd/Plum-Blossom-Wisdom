import os
import json

def convert_qa_format(input_folder, output_file):
    """
    将qa_pairs_*.json文件转换为统一的格式并合并
    """
    print(f"Converting QA pairs from {input_folder}")
    all_qa_pairs = []

    # 获取所有qa_pairs_*.json文件
    qa_files = [f for f in os.listdir(input_folder) if f.startswith('qa_pairs_') and f.endswith('.json')]
    qa_files.sort(key=lambda x: int(x.split('_')[2].split('.')[0]))  # 按序号排序

    for qa_file in qa_files:
        print(f"Processing {qa_file}...")
        file_path = os.path.join(input_folder, qa_file)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            
            # 解析JSON字符串
            if isinstance(content[0], str):
                qa_list = json.loads(content[0])
            else:
                qa_list = content[0]

            # 转换格式
            for qa in qa_list:
                converted_qa = {
                    "instruction": qa["question"],
                    "output": qa["answer"],
                    "system": "你是一个占卜和算命解释专家，你需要遵循文本标准来帮我解决相关问题。"
                }
                all_qa_pairs.append(converted_qa)

    # 保存转换后的文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_qa_pairs, f, ensure_ascii=False, indent=4)
    
    print(f"Conversion completed. Output saved to {output_file}")
    print(f"Total QA pairs converted: {len(all_qa_pairs)}")

if __name__ == "__main__":
    input_folder = r"G:\see\output"  # 包含qa_pairs_*.json文件的文件夹
    output_file = os.path.join(input_folder, "formatted_qa_pairs.json")
    convert_qa_format(input_folder, output_file)
