import os
import json

def merge_qa_files(input_folder, output_file):
    """
    合并所有success*.json文件到一个文件中
    """
    print(f"开始合并JSON文件，从目录: {input_folder}")
    all_qa_pairs = []

    # 获取所有success*.json文件并按序号排序
    json_files = [f for f in os.listdir(input_folder) if f.startswith('success') and f.endswith('.json')]
    json_files.sort(key=lambda x: int(x.replace('success', '').replace('.json', '')))

    total_files = len(json_files)
    print(f"找到 {total_files} 个JSON文件")

    # 处理每个文件
    for i, json_file in enumerate(json_files, 1):
        file_path = os.path.join(input_folder, json_file)
        print(f"处理文件 {i}/{total_files}: {json_file}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                qa_pairs = json.load(f)
                all_qa_pairs.extend(qa_pairs)
        except json.JSONDecodeError as e:
            print(f"处理文件 {json_file} 时出错: {e}")
            continue
        except Exception as e:
            print(f"处理文件 {json_file} 时发生未知错误: {e}")
            continue

    # 保存合并后的文件
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_qa_pairs, f, ensure_ascii=False, indent=4)
        print(f"合并完成！共处理 {len(all_qa_pairs)} 个QA对")
        print(f"合并结果已保存至: {output_file}")
    except Exception as e:
        print(f"保存合并文件时出错: {e}")

def main():
    # 设置输入输出路径
    input_folder = r"G:\see\output1"  # 包含success*.json文件的文件夹
    output_file = os.path.join(input_folder, "merged_qa_pairs.json")

    # 检查输入目录是否存在
    if not os.path.exists(input_folder):
        print(f"错误: 输入目录 '{input_folder}' 不存在")
        return

    # 执行合并操作
    merge_qa_files(input_folder, output_file)

if __name__ == "__main__":
    main()
