import PyPDF2
from pdf2image import convert_from_path
import pytesseract
from pathlib import Path
import yaml
import logging
from PIL import Image

class PDFProcessor:
    def __init__(self, config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.setup_logging()
        # 增加OCR配置选项
        self.ocr_config = '--oem 3 --psm 3'  # 使用更准确的OCR引擎模式
        
        # 检查Tesseract路径
        tesseract_path = self.config['pdf_processing']['tesseract_path']
        if not Path(tesseract_path).exists():
            raise FileNotFoundError(f"Tesseract执行文件未找到：{tesseract_path}")
        
        # 设置Tesseract路径
        pytesseract.pytesseract.tesseract_cmd = self.config['pdf_processing']['tesseract_path']
    
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_images_and_text(self, pdf_path):
        """提取PDF中的图片和文本"""
        self.logger.info(f"开始处理PDF: {pdf_path}")
        
        # 转换PDF页面为图片
        images = convert_from_path(
            pdf_path,
            dpi=self.config['pdf_processing']['dpi']
        )
        
        results = []
        for i, image in enumerate(images):
            # 图像预处理以提高OCR质量
            processed_image = self.preprocess_image(image)
            
            # 检测页面中的卦象图案
            hexagram_images = self.detect_hexagram_images(processed_image)
            
            page_data = {
                'page_number': i + 1,
                'text': pytesseract.image_to_string(
                    processed_image,
                    lang=self.config['pdf_processing']['language'],
                    config=self.ocr_config
                ),
                'images': hexagram_images
            }
            
            # 保存页面图片
            image_path = Path(self.config['output']['output_dir']) / f"page_{i+1}.png"
            image.save(str(image_path))
            
            results.append(page_data)
            
        return results 

    def preprocess_image(self, image):
        """图像预处理以提高OCR质量"""
        import cv2
        import numpy as np
        
        # 转换为OpenCV格式
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # 灰度化
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 二值化
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # 降噪
        denoised = cv2.fastNlMeansDenoising(binary)
        
        return Image.fromarray(denoised)

    def detect_hexagram_images(self, image):
        """检测页面中的卦象图案"""
        import cv2
        import numpy as np
        
        # 转换为OpenCV格式
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 使用Canny边缘检测
        edges = cv2.Canny(gray, 50, 150)
        
        # 寻找轮廓
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        hexagram_images = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            
            # 筛选可能的卦象图案（根据尺寸和形状）
            if w > 100 and h > 100 and 0.8 < w/h < 1.2:  # 近似正方形
                # 提取感兴趣区域
                roi = img[y:y+h, x:x+w]
                
                # 保存子图片
                output_path = Path(self.config['output']['output_dir']) / f"hexagram_{len(hexagram_images)}.png"
                cv2.imwrite(str(output_path), roi)
                
                hexagram_images.append({
                    'path': str(output_path),
                    'position': {'x': x, 'y': y, 'width': w, 'height': h}
                })
        
        return hexagram_images