import os
from generate_qa import generate_qa_pairs

def main():
    # 在这里填写输入文件路径和输出文件夹路径
    input_file = r"G:\see\output_入门.txt"
    output_folder = r'G:\see\output1'
    start_index = 18  # 从第19个切片开始处理

    if not os.path.isfile(input_file):
        print(f"Error: Input file '{input_file}' does not exist.")
        return

    if not os.path.isdir(output_folder):
        print(f"Error: Output folder '{output_folder}' does not exist.")
        return

    generate_qa_pairs(input_file, output_folder, start_index)
    print(f"QA pairs have been successfully generated and saved to '{output_folder}'.")

if __name__ == "__main__":
    main()
