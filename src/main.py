import argparse
import yaml
from pathlib import Path
from pdf_processor import PDFProcessor
from image_captioner import ImageCaptioner
from text_cleaner import TextCleaner
from text_corrector import TextCorrector
from data_formatter import DataFormatter
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='PDF内容提取与处理工具')
    parser.add_argument('pdf_path', help='PDF文件路径')
    parser.add_argument('--config', default='config/config.yaml', help='配置文件路径')
    args = parser.parse_args()
    
    logger = setup_logging()
    
    try:
        # 加载配置
        with open(args.config, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 初始化各个组件
        pdf_processor = PDFProcessor(args.config)
        image_captioner = ImageCaptioner(config)
        text_cleaner = TextCleaner()
        text_corrector = TextCorrector(config)
        data_formatter = DataFormatter(config)
        
        # 处理PDF
        logger.info("开始处理PDF文件...")
        raw_data = pdf_processor.extract_images_and_text(args.pdf_path)
        
        # 清理文本
        logger.info("清理提取的文本...")
        cleaned_data = text_cleaner.process_document(raw_data)
        
        # AI校正文本
        if config['text_correction']['enable']:
            logger.info("开始AI文本校正...")
            for page in cleaned_data:
                page['text'] = text_corrector.correct_text(page['text'])
        
        # 处理图片描述
        logger.info("生成图片描述...")
        for page in cleaned_data:
            for image in page.get('images', []):
                if 'path' in image:
                    image['caption'] = image_captioner.generate_caption(image['path'])
        
        # 保存处理后的数据
        logger.info("保存处理结果...")
        data_formatter.save_training_data(cleaned_data)
        
        logger.info("处理完成！")
        
    except Exception as e:
        logger.error(f"处理过程中发生错误: {str(e)}")
        raise

if __name__ == '__main__':
    main() 