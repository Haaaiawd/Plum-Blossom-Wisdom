import cv2
import numpy as np
from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch
import logging

class ImageCaptioner:
    def __init__(self, config):
        self.config = config
        self.device = torch.device(config['image_captioning']['device'])
        self.logger = logging.getLogger(__name__)
        
        # 加载BLIP模型
        self.processor = BlipProcessor.from_pretrained(
            config['image_captioning']['model_name']
        )
        self.model = BlipForConditionalGeneration.from_pretrained(
            config['image_captioning']['model_name']
        ).to(self.device)
        
        # 添加OCR配置
        self.use_ocr = True
        if self.use_ocr:
            import pytesseract
            pytesseract.pytesseract.tesseract_cmd = config.get('pdf_processing', {}).get(
                'tesseract_path', 'tesseract'
            )
    
    def detect_hexagram_features(self, image):
        """检测卦象图案的特征"""
        try:
            # 转换为灰度图
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # 二值化处理
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # 检测圆形（外圈）
            circles = cv2.HoughCircles(
                gray, cv2.HOUGH_GRADIENT, dp=1, minDist=50,
                param1=50, param2=30, minRadius=30, maxRadius=100
            )
            
            # 检测矩形
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            rectangles = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                if w > 30 and h > 30:  # 过滤小矩形
                    rectangles.append((x, y, w, h))
            
            # 检测直线（卦象线条）
            edges = cv2.Canny(binary, 50, 150)
            lines = cv2.HoughLinesP(
                edges, 1, np.pi/180, threshold=50,
                minLineLength=50, maxLineGap=10
            )
            
            features = {
                'has_circle': circles is not None,
                'has_rectangle': len(rectangles) > 0,
                'line_count': len(lines) if lines is not None else 0,
                'is_hexagram': self._check_if_hexagram(lines) if lines is not None else False,
                'rectangles': rectangles
            }
            
            return features
            
        except Exception as e:
            self.logger.error(f"卦象特征检测失败: {str(e)}")
            return None
    
    def _check_if_hexagram(self, lines):
        """检查是否符合卦象的基本特征"""
        if lines is None:
            return False
            
        # 统计水平线数量
        horizontal_lines = 0
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = abs(np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi)
            if abs(angle) < 10:  # 允许10度的误差
                horizontal_lines += 1
        
        # 卦象通常有6到8条水平线
        return 6 <= horizontal_lines <= 8
    
    def extract_text(self, image):
        """提取图片中的文字"""
        try:
            if not self.use_ocr:
                return ""
            import pytesseract
            text = pytesseract.image_to_string(image, lang='chi_sim+eng')
            return text.strip()
        except Exception as e:
            self.logger.error(f"文字提取失败: {str(e)}")
            return ""
    
    def analyze_hexagram(self, image_path):
        """分析卦象图片并生成描述"""
        try:
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("无法读取图片")
            
            # 检测卦象特征
            features = self.detect_hexagram_features(image)
            if not features:
                return "无法识别卦象特征"
            
            # 提取文字
            text = self.extract_text(image)
            
            # 生成描述
            feature_text = "图中"
            if features['has_circle'] and features['has_rectangle']:
                feature_text += "包含圆形和方形卦象结构，"
            elif features['has_circle']:
                feature_text += "包含圆形卦象结构，"
            elif features['has_rectangle']:
                feature_text += "包含方形卦象结构，"
            
            if features['line_count'] > 0:
                feature_text += f"检测到{features['line_count']}条线条，"
            
            if features['is_hexagram']:
                feature_text += "符合卦象基本特征。"
            else:
                feature_text += "不完全符合卦象特征。"
            
            if text:
                feature_text += f"\n图中包含文字信息：{text}"
            
            return feature_text
            
        except Exception as e:
            self.logger.error(f"卦象分析失败: {str(e)}")
            return "图片分析失败"
    
    def generate_caption(self, image_path):
        """生成完整的图片描述"""
        try:
            # 首先进行卦象分析
            hexagram_analysis = self.analyze_hexagram(image_path)
            
            # 使用BLIP生成基础描述
            image = Image.open(image_path)
            inputs = self.processor(
                image, 
                return_tensors="pt"
            ).to(self.device)
            
            output = self.model.generate(
                **inputs,
                max_length=self.config['image_captioning']['max_length']
            )
            
            blip_description = self.processor.decode(output[0], skip_special_tokens=True)
            
            # 合并两种描述
            combined_description = f"{hexagram_analysis}\n基础图像描述：{blip_description}"
            
            return combined_description
            
        except Exception as e:
            self.logger.error(f"生成图片描述失败: {str(e)}")
            return "图片描述生成失败"