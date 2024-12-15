import re
import unicodedata
import logging
from typing import List, Dict

class TextCleaner:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
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