import json
import logging
from pathlib import Path
from typing import List, Dict
from volcenginesdkarkruntime import Ark
import time
import os
import yaml  # 确保导入 yaml 模块
from tenacity import retry, stop_after_attempt, wait_fixed  # 导入重试机制

class QAGenerator:
    def __init__(self, config):
        self.config = config['qa_generation']
        self.logger = logging.getLogger(__name__)
        
        # 初始化 Ark 客户端
        self.client = Ark(
            ak=self.config['api_key'],
            sk=self.config['api_secret'],
            region='cn-north-1'  # 确保指定正确的区域
        )
        self.model_id = self.config['model_name']
        
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
    
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
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
                        最后只需要返回json list,严格遵守返回为json list格式：[{{'input': ,'output': }},{{'input': ,'output': }}]
            
                        文本内容：
                        {text}
                        """
            # 记录发送的完整提示词
            self.logger.debug(f"发送的提示词:\n{prompt}")
            
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
                max_tokens=4096  # 增加 token 限制以容纳更多问答对
            )
            
            # 添加详细的日志记录
            self.logger.debug(f"完整的 API 响应: {response}")
            
            if not response or not response.choices or not response.choices[0].message.content:
                self.logger.error("API 返回内容为空或格式不正确。")
                return []
            
            result = response.choices[0].message.content.strip()
            self.logger.info(f"API 返回结果:\n{result}")
            
            # 尝试解析 JSON，添加异常处理
            try:
                qa_pairs = json.loads(result)
                if not isinstance(qa_pairs, list):
                    raise ValueError("解析后的结果不是列表类型")
            except json.JSONDecodeError as json_err:
                self.logger.error(f"JSON 解析错误: {str(json_err)}")
                self.logger.debug(f"返回的文本:\n{result}")
                qa_pairs = []
            except ValueError as val_err:
                self.logger.error(f"JSON 内容格式错误: {str(val_err)}")
                self.logger.debug(f"返回的文本:\n{result}")
                qa_pairs = []
            return qa_pairs
                
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
    
    def process_book(self, input_file: str = r"G:\see\111梅花易数白话解 (（宋）邵雍著；刘光本，荣益译) (Z-Library).txt", output_dir: str = 'G:/see/qa_output') -> None:
        """处理整本书的文本内容"""
        try:
            # 创建输出目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 读取书籍文本
            with open(input_file, 'r', encoding='utf-8') as f:
                book_text = f.read()
            
            # 分割文本
            segments = self._split_text(book_text)
            self.logger.info(f"共分割出 {len(segments)} 个部分")
            
            # 处理每个部分
            all_qa_pairs = []
            for i, segment in enumerate(segments, 1):
                self.logger.info(f"正在处理部分 {i}")
                
                # 为每个部分生成问答对
                qa_pairs = self._generate_qa_pairs(segment)
                all_qa_pairs.extend(qa_pairs)
                time.sleep(0.5)  # 避免API调用过于频繁
                
                # 保存部分的问答对
                output_file = os.path.join(output_dir, f'part_{i:03d}.json')
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(qa_pairs, f, ensure_ascii=False, indent=2)
                
                self.logger.info(f"部分 {i} 已生成 {len(qa_pairs)} 个问答对")
            
            # 合并所有部分的问答对
            self._merge_qa_pairs(all_qa_pairs, output_dir)
            
        except Exception as e:
            self.logger.error(f"处理书籍时出错: {str(e)}")
            raise
    
    def _merge_qa_pairs(self, all_qa_pairs: List[Dict[str, str]], output_dir: str) -> None:
        """合并所有部分的问答对"""
        # 提取需要的字段并转换格式
        formatted_qa_pairs = []
        for item in all_qa_pairs:
            try:
                extracted = {
                    'instruction': item['input'],
                    'output': item['output'],
                    'system': """你将扮演一位既精通玄学（梅花易数）又精通科学的大师，使用梅花易数的知识来为用户解决问题。当我提供一个问题时，你需要根据你的知识进行解答。
                                 这是用户的问题：
                                    <question>
                                    {{QUESTION}}
                                    </question>
                                    在回答问题时，请遵循以下原则：
                                    1. 答案应结合梅花易数的原理和科学思维，尽量做到合理、客观、有依据。
                                    2. 如果问题与梅花易数无关，请尝试从科学的角度给出合理的解释或建议。
                                    3. 用简洁、清晰的语言表达你的观点，避免使用过于复杂或模糊的表述。
                                    请在<answer>标签内给出你的回答。""",
                }
                formatted_qa_pairs.append(extracted)
            except KeyError as e:
                self.logger.error(f"字段提取错误: {str(e)}")
        
        # 保存合并后的问答对
        output_file = os.path.join(output_dir, 'all_qa_pairs_formatted.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(formatted_qa_pairs, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"已合并并格式化所有部分，共 {len(formatted_qa_pairs)} 个问答对")

# 在文件末尾添加独立运行入口
if __name__ == "__main__":
    # 使用绝对路径加载配置
    
    config_path = r'G:/PROJECTALL/Cur-project/pdf_tool/config/config.yaml'
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    generator = QAGenerator(config)
    generator.process_book()