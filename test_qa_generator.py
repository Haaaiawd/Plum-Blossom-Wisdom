import yaml
import logging
import os
from src.qa_generator import QAGenerator

logging.basicConfig(level=logging.DEBUG)

def test_qa_generation():
    # 修改配置文件的加载路径
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 如果没有qa_generation配置，使用text_correction的配置
    if 'qa_generation' not in config:
        config['qa_generation'] = {
            'api_key': config['text_correction']['api_key'],
            'api_secret': config['text_correction']['api_secret'],
            'endpoint': config['text_correction']['endpoint'],
            'model_name': "doubao-pro-128k",
            'max_segment_length': 8000,
            'overlap_length': 1000
        }
    
    # 初始化生成器
    generator = QAGenerator(config)
    
    # 处理训练数据
    generator.process_training_data(
        'output/training_data.json',
        'output/qa_pairs.json'
    )

def test_book_qa_generation():
    # 修改配置文件的加载路径
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 初始化生成器
    generator = QAGenerator(config)
    
    # 处理书籍文本
    input_file = r"G:\see\111梅花易数白话解 (（宋）邵雍著；刘光本，荣益译) (Z-Library).txt"  # 输入的txt文件路径
    output_dir = 'G:/see/qa_output'  # 输出目录
    
    generator.process_book(input_file, output_dir)

if __name__ == "__main__":
    test_book_qa_generation()

