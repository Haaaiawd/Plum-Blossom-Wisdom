import os
import json
import sys
import dotenv
from volcenginesdkarkruntime import Ark

# 加载环境变量
dotenv.load_dotenv(".env")

# 初始化 Ark 客户端
client = Ark()

def read_txt_file(file_path):
    print(f"Reading input file: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def split_text(text, chunk_size=2000):
    print(f"Splitting text into chunks of {chunk_size} characters each.")
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def call_volcano_api(text_chunk):
    model_id = os.getenv("ENDPOINT_ID")
    prompt = (
        "你是一个信息抽取能手，你需要把我给你的内容做成QA对，模拟人和大模型的对话，你的回复要满足下列要求：\n"
        "全部使用中文回复\n"
        "根据内容的分类与系统返回QA对，至少20对，但不要重复说相同问题\n"
        "格式要求：返回的json list中每个元素包含三个字段：instruction（问题）、output（答案）、system（角色设定）\n"
        "system字段统一设置为：你是一个占卜和算命解释专家，你需要遵循文本标准来帮我解决相关问题\n"
        "提问要专注于如何进行计算算卦以及结果，原因，解释等等方面,每遇到卦象就一定把这个卦象转化为一个QA对\n"
        "因为我给你的材料是语音转文本，可能有错误，你要在基于上下文理解的基础上帮忙修复\n"
        "不要提到任何作者信息，只需要结合内容回答抽取\n"
        "回复格式示例：[\n"
        "    {\n"
        "        \"instruction\": \"问题1\",\n"
        "        \"output\": \"答案1\",\n"
        "        \"system\": \"你是一个占卜和算命解释专家，你需要遵循文本标准来帮我解决相关问题\"\n"
        "    }\n"
        "]"
    )
    print(f"Calling Volcano API with text chunk: {text_chunk[:50]}...")  # 只显示前50个字符
    stream = client.chat.completions.create(
        model=model_id,
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": text_chunk},
        ],
        stream=True
    )
    full_text = ""
    for chunk in stream:
        if not chunk.choices:
            continue
        text = chunk.choices[0].delta.content
        if text is None:
            print("Warning: Received NoneType text from API.")
            print(f"Full response: {chunk}")
            continue
        full_text += text
    print(f"Received response: {full_text[:50]}...")  # 只显示前50个字符
    return full_text

def save_text_chunks(chunks, output_folder):
    """保存文本切片到文件"""
    chunks_folder = os.path.join(output_folder, 'text_chunks')
    if not os.path.exists(chunks_folder):
        os.makedirs(chunks_folder)
    
    chunk_files = []
    for i, chunk in enumerate(chunks):
        chunk_file = os.path.join(chunks_folder, f'chunk_{i + 1}.txt')
        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(chunk)
        chunk_files.append(chunk_file)
    return chunk_files

def generate_qa_pairs(input_file, output_folder, start_index=0):
    """
    生成QA对，可以指定开始处理的切片索引
    :param input_file: 输入文件路径
    :param output_folder: 输出文件夹路径
    :param start_index: 开始处理的切片索引（从0开始）
    """
    # 读取和切割文本
    text = read_txt_file(input_file)
    text_chunks = split_text(text)
    total_chunks = len(text_chunks)
    
    # 保存文本切片
    print("Saving text chunks...")
    save_text_chunks(text_chunks, output_folder)
    
    # 处理每个文本块，从指定索引开始
    for i, chunk_text in enumerate(text_chunks[start_index:], start=start_index):
        print(f"Processing chunk {i + 1}/{total_chunks}...")
        
        # 调用API生成QA对
        qa_pair = call_volcano_api(chunk_text)
        
        # 解析返回的JSON字符串并保存
        try:
            qa_list = json.loads(qa_pair) if isinstance(qa_pair, str) else qa_pair
            output_file = os.path.join(output_folder, f'success{i + 1}.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(qa_list, f, ensure_ascii=False, indent=4)
            print(f"Chunk {i + 1}/{total_chunks} processed and saved to '{output_file}'.")
        except json.JSONDecodeError as e:
            print(f"Error processing chunk {i + 1}: {e}")
            print(f"Raw response: {qa_pair}")
            continue

    print("QA pairs generation completed.")

if __name__ == "__main__":
    if len(sys.argv) != 3 and len(sys.argv) != 4:
        print("Usage: python generate_qa.py <input_file> <output_folder> [<start_index>]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_folder = sys.argv[2]
    start_index = int(sys.argv[3]) if len(sys.argv) == 4 else 0
    generate_qa_pairs(input_file, output_folder, start_index)
