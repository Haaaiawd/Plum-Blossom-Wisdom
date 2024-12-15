import json
import pandas as pd
from pathlib import Path
import logging
from typing import List, Dict

class DataFormatter:
    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.output_dir = Path(config['output']['output_dir'])
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def format_to_json(self, data: List[Dict], output_file: str = 'output.json') -> None:
        """将数据保存为JSON格式"""
        try:
            output_path = self.output_dir / output_file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            self.logger.info(f"数据已保存至: {output_path}")
        except Exception as e:
            self.logger.error(f"保存JSON数据时发生错误: {str(e)}")
    
    def format_to_training_data(self, data: List[Dict]) -> List[Dict]:
        """将数据转换为训练格式"""
        training_data = []
        
        for page in data:
            # 处理文本段落
            if page['text'].strip():
                training_data.append({
                    'type': 'text',
                    'content': page['text'],
                    'page': page['page_number']
                })
            
            # 处理图片描述
            for img in page.get('images', []):
                if img.get('caption'):
                    training_data.append({
                        'type': 'image',
                        'content': img['caption'],
                        'page': page['page_number'],
                        'image_path': img.get('path', '')
                    })
        
        return training_data
    
    def save_training_data(self, data: List[Dict], output_file: str = 'training_data.json') -> None:
        """保存训练数据"""
        formatted_data = self.format_to_training_data(data)
        self.format_to_json(formatted_data, output_file) 