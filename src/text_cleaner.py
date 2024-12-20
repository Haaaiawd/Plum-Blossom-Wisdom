import re
import unicodedata
import logging
import argparse
import os
from typing import List, Dict
import yaml
import chardet

class TextCleaner:
    def __init__(self, config):
        self.logger = logging.getLogger(__name__)
        self.config = config['text_correction']
        
    def clean_text(self, text: str) -> str:
        """清理文本内容"""
        # 统一空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 移除特殊控制字符
        text = ''.join(ch for ch in text if unicodedata.category(ch)[0] != 'C')
        
        # 移除多余的空行
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # 移除页眉页脚常见的数字标记
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        return text.strip()
    
    def process_page_data(self, page_data: Dict) -> Dict:
        """处理单页数据"""
        try:
            page_data['text'] = self.clean_text(page_data['text'])
            return page_data
        except Exception as e:
            self.logger.error(f"处理页面 {page_data.get('page_number')} 时发生错误: {str(e)}")
            return page_data
    
    def process_document(self, document: List[Dict]) -> List[Dict]:
        """处理整个文档的数据"""
        return [self.process_page_data(page) for page in document]

def main(input_path='G:\see\梅花易数白话解 (（宋）邵雍著；刘光本，荣益译) (Z-Library).txt', output_dir='G:/see/output/'):
    with open('config/config.yaml', 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    cleaner = TextCleaner(config)
    if input_path and output_dir:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 首先检测文件编码
        with open(input_path, 'rb') as file:
            raw_data = file.read()
            detected = chardet.detect(raw_data)
            encoding = detected['encoding']
            print(f"Detected encoding: {encoding}")
        
        # 按检测到的编码读取文件
        try:
            with open(input_path, 'r', encoding=encoding) as infile:
                text = infile.read()
                print(f"Successfully read file with {encoding} encoding")
        except UnicodeDecodeError:
            # 如果检测失败，尝试其他常见编码
            encodings = ['gb18030', 'gbk', 'gb2312', 'utf-8', 'utf-16', 'big5']
            for enc in encodings:
                try:
                    with open(input_path, 'r', encoding=enc) as infile:
                        text = infile.read()
                        encoding = enc
                        print(f"Successfully read file with {enc} encoding")
                        break
                except UnicodeDecodeError:
                    continue
        
        cleaned_text = cleaner.clean_text(text)
        
        output_filename = os.path.basename(input_path)
        output_path = os.path.join(output_dir, output_filename)
        
        # 使用 UTF-8 编码写入
        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.write(cleaned_text)
        print(f"File saved with UTF-8 encoding")
    else:
        # 适配原来的运行方式
        document = [
            # ...existing code...
        ]
        cleaned_document = cleaner.process_document(document)
        # ...existing code...

if __name__ == "__main__":
    main()