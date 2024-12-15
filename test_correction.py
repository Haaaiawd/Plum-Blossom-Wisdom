import yaml
from src.text_corrector import TextCorrector
import logging

logging.basicConfig(level=logging.INFO)

def test_correction():
    # 加载配置
    with open('config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 初始化文本校正器
    corrector = TextCorrector(config)
    
    # 测试文本
    test_text = """
    这是一段测试文本，包含一些错别字和排版问题。
    比如这个句子里有错别字：我今夭要去图书棧看节。
    """
    
    try:
        corrected_text = corrector.correct_text(test_text)
        print("\n原文：")
        print(test_text)
        print("\n校正后：")
        print(corrected_text)
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    test_correction() 