import json
import logging
from pathlib import Path
from typing import List, Dict
from volcenginesdkarkruntime import Ark
import time

class QAGenerator:
    def __init__(self, config):
        self.config = config['qa_generation']
        self.logger = logging.getLogger(__name__)
        
        # 初始化 Ark 客户端
        self.client = Ark(
            ak=self.config['api_key'],
            sk=self.config['api_secret']
        )
        self.model_id = self.config['endpoint']
        
        # 调整为更大的段落大小
        self.max_segment_length = self.config.get('max_segment_length', 8000)
        self.overlap_length = self.config.get('overlap_length', 1000)
    
    def _split_text(self, text: str) -> List[str]:
        """将长文本分割成有重叠的段落"""
        segments = []
        start = 0
        
        while start < len(text):
            # 如果剩余文本小于最大长度，直接添加
            if start + self.max_segment_length >= len(text):
                segments.append(text[start:])
                break
            
            # 在最大长度位置寻找段落结束点
            end = start + self.max_segment_length
            # 优先在段落结束处切割
            while end > start and not (text[end] in '。！？.!?' and '\n' in text[end-10:end+10]):
                end -= 1
            
            if end == start:  # 如果找不到合适的断句点
                end = start + self.max_segment_length
            
            segments.append(text[start:end+1])
            start = end - self.overlap_length
            
        return segments
    
    def _generate_qa_pairs(self, text: str) -> List[Dict[str, str]]:
        """为文本段落生成问答对"""
        try:
            prompt = f"""你是一个信息抽取能手，你需要把我给你的内容做成QA对，模拟人和大模型的对话，你的回复要满足下列要求：
                        全部使用中文回复
                        根据内容的几个主题返回至少810条符合的QA对，但不要重复说相同问题，
                        如果遇到里面提到几步法，你要合在一个回答里面
                        提问要模拟用户在这个知识点的提问主题下进行对话、提问要做到口语化并尽可能简单且不要涉及到具体的人，提问最好大于5个字少于0个字（格式类似：......怎么办，......为什么？），而回答应非常详细可分点回答、需要长回答详细紧扣我给你的东西，
                        因为我给你的材料是语音转文本，可能有错误，你要在基于上下文理解的基础上帮忙修复。
                        不要提到任何作者信息，只需要结合内容回答抽取。
                        最后只需要返回json list,严格遵守返回为json list格式：[{'input': ,'output': },{'input': ,'output': }]
            
                        文本内容：
                        {text}
                        """
            
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的问答对生成专家。你的任务是生成尽可能多的高质量问答对，确保问题深入且多样，答案详尽且准确。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                top_p=0.9,
                max_tokens=4096  # 增加token限制以容纳更多问答对
            )
            
            result = response.choices[0].message.content.strip()
            return json.loads(result)
            
        except Exception as e:
            self.logger.error(f"生成问答对时出错: {str(e)}")
            return []
    
    def process_training_data(self, input_file: str, output_file: str) -> None:
        """处理训练数据并生成问答对"""
        try:
            # 读取训练数据
            with open(input_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            # 提取所有文本内容
            all_text = ""
            for item in training_data:
                if item['type'] == 'text':
                    all_text += item['content'] + "\n\n"
            
            # 分割文本
            text_segments = self._split_text(all_text)
            
            # 生成问答对
            all_qa_pairs = []
            for segment in text_segments:
                qa_pairs = self._generate_qa_pairs(segment)
                all_qa_pairs.extend(qa_pairs)
                time.sleep(0.5)  # 避免API调用过于频繁
            
            # 保存结果
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_qa_pairs, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"已生成 {len(all_qa_pairs)} 个问答对，保存至 {output_file}")
            
        except Exception as e:
            self.logger.error(f"处理训练数据时出错: {str(e)}")
            raise 