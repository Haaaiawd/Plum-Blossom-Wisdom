import logging
from image_captioner import ImageCaptioner
import yaml
import cv2
import numpy as np
from pathlib import Path

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def split_image(image_path):
    """将图片分割成多个区域"""
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("无法读取图片")
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # 寻找轮廓
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    regions = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w > 50 and h > 50:  # 过滤小区域
            roi = image[y:y+h, x:x+w]
            regions.append(roi)
    
    return regions

def analyze_image(image_path, config_path='config/config.yaml'):
    logger = setup_logging()
    
    try:
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 初始化ImageCaptioner
        image_captioner = ImageCaptioner(config)
        
        # 分割图片
        regions = split_image(image_path)
        
        # 分析每个区域
        for i, region in enumerate(regions):
            region_path = Path("output") / f"region_{i}.png"
            cv2.imwrite(str(region_path), region)
            
            logger.info(f"开始分析区域: {region_path}")
            analysis_result = image_captioner.analyze_hexagram(str(region_path))
            
            # 输出结果
            print(f"区域 {i} 分析结果:\n{analysis_result}")
        
    except Exception as e:
        logger.error(f"分析过程中发生错误: {str(e)}")
        raise

if __name__ == '__main__':
    # 在这里指定图片路径
    image_path = 'path/to/hexagram_image.png'
    analyze_image(image_path)
