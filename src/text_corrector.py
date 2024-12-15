import time
import logging
from typing import List, Dict
from volcenginesdkarkruntime import Ark

class TextCorrector:
    def __init__(self, config):
        self.config = config['text_correction']
        self.logger = logging.getLogger(__name__)
        
        # 初始化 Ark 客户端
        self.client = Ark(
            ak=self.config['api_key'],
            sk=self.config['api_secret']
        )
        self.model_id = self.config['endpoint']
        
        self.max_retries = self.config.get('max_retries', 3)
        self.batch_size = self.config.get('batch_size', 1000)
    
    def _call_api(self, text: str) -> str:
        """调用豆包API进行文本校正"""
        try:
            # 创建对话请求
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的文本校对专家，负责修正OCR文本中的错误。请直接返回修正后的文本，不需要任何额外说明。"
                    },
                    {
                        "role": "user",
                        "content": f"请帮我校对和修正以下OCR识别的文本，确保文字通顺、无错别字：\n\n{text}"
                    }
                ],
                temperature=0.3,
                top_p=0.8,
                max_tokens=2048
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            self.logger.error(f"API调用失败: {str(e)}")
            raise
    
    def correct_text(self, text: str) -> str:
        """处理文本并进行校正"""
        if not text.strip():
            return text
            
        # 分段处理长文本
        segments = self._split_text(text)
        corrected_segments = []
        
        for segment in segments:
            try:
                corrected_text = self._call_api(segment)
                corrected_segments.append(corrected_text)
                # 添加延时避免API限制
                time.sleep(0.5)
            except Exception as e:
                self.logger.error(f"处理文本段落时出错: {str(e)}")
                corrected_segments.append(segment)  # 如果失败则保留原文
        
        return "\n".join(corrected_segments)
    
    def _split_text(self, text: str) -> List[str]:
        """将长文本分割成适合API处理的片段"""
        segments = []
        current_segment = []
        current_length = 0
        
        for paragraph in text.split('\n'):
            if current_length + len(paragraph) > self.batch_size:
                if current_segment:
                    segments.append('\n'.join(current_segment))
                current_segment = [paragraph]
                current_length = len(paragraph)
            else:
                current_segment.append(paragraph)
                current_length += len(paragraph)
        
        if current_segment:
            segments.append('\n'.join(current_segment))
        
        return segments 