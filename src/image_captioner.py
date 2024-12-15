from transformers import BlipProcessor, BlipForConditionalGeneration
from PIL import Image
import torch

class ImageCaptioner:
    def __init__(self, config):
        self.config = config
        self.device = torch.device(config['image_captioning']['device'])
        
        # 加载模型和处理器
        self.processor = BlipProcessor.from_pretrained(
            config['image_captioning']['model_name']
        )
        self.model = BlipForConditionalGeneration.from_pretrained(
            config['image_captioning']['model_name']
        ).to(self.device)
    
    def generate_caption(self, image_path):
        """生成图片描述"""
        image = Image.open(image_path)
        inputs = self.processor(
            image, 
            return_tensors="pt"
        ).to(self.device)
        
        output = self.model.generate(
            **inputs,
            max_length=self.config['image_captioning']['max_length']
        )
        
        return self.processor.decode(output[0], skip_special_tokens=True) 