import yaml
import logging
from src.qa_generator import QAGenerator

logging.basicConfig(level=logging.INFO)

def test_qa_generation():
    # 加载配置
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
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

if __name__ == "__main__":
    test_qa_generation() 
    
    