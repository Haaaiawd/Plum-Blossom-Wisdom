# Plum Blossom Wisdom



> 灵感来自同类型算卦AI
>
> 梅花易数入门 (中国易学文化研究院 编)
>



:::info
目录：

1. 项目背景及概述
2. 数据准备
+ 数据收集与提取
+ 数据清洗
+ 数据预处理
3. 微调训练
4. prompt调整

:::

## 项目背景及概述：
### 项目背景：
在科学占据主导地位的今天，玄学以其神秘色彩仍然吸引着人们的目光。![在billibili，这样的教学视频有上百万的播放](https://cdn.nlark.com/yuque/0/2024/png/45387460/1734157198665-b2bf7f24-16c0-46fa-b793-37b573a1bd9d.png)


对于将卦象用运算表示，<font style="color:rgb(13, 13, 13);">通过数字、点滴变化推演出各种可能性的梅花易数来说，玄学是否具有其独到之处尚无定论。。</font>

在这样的情形下，**最理智的行为是去真正了解它，然后再来看到底是猫是虎**。在学习成本已经传承等方面的妥协下，也许将其做成AI来一探究竟是最好的选择

### 项目概述
本项目使用**《梅花易数入门 (中国易学文化研究院 编)》**、**《****梅花易数白话解****》**作为基础框架，使用讯飞大模型进行精调。使用该大模型时，梅花易数AI会询问时间，人物，环境，动静等要素，根据要素进行计算后给出发生某件事的预测。

#### 后续考虑添加:
1. 《图解邵康节易数 1：邵康节梅花易数》
2. 《梅花易数高层之路》
3. 《皇极经世》
4. 《干支易象学》
5. 《指点春风 —— 独解梅花易数之八法》

等内容

---

## 数据准备
### 数据收集与提取
#### 安装依赖：
```plain
PyPDF2==3.0.1
pdf2image==1.16.3
pytesseract==0.3.10
transformers==4.30.2
torch==2.0.1
pandas==2.0.3
pyyaml==6.0.1
pillow==9.5.0
opencv-python==4.8.0
numpy==1.24.3
requests==2.31.0
tenacity==8.2.3
```
github中安装tesseract及其中文包与poppler
> tesseract项目https://github.com/tesseract-ocr/tesseract
> tesseract中文包https://github.com/tesseract-ocr/tessdata/blob/main/chi_sim.traineddata
> poppler项目https://github.com/oschwartz10612/poppler-windows
> poppler需要设置环境变量并重启电脑

#### 提取pdf
这部分的项目结构
+ project/
+ ├── README.md
+ ├── requirements.txt
+ ├── src/
+ │   ├── main.py           # 主程序
+ │   ├── pdf_processor.py  # PDF处理核心类
+ │   ├── image_captioner.py # 图片描述生成器
+ │   ├── text_cleaner.py   # 文本清洗工具
+ │   └── data_formatter.py # 数据格式化工具
+ ├── config/
+ │   └── config.yaml       # 配置文件
+ └── output/               # 输出目录

**由于tesseract精度有限，因此我们使用ai进行校正**
```python
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
```

![在跑中的ai校正](https://cdn.nlark.com/yuque/0/2024/png/45387460/1734173725632-adb5adcd-d8d5-4fcb-9c66-cda52a3efce4.png)



---

## 🚫以下正在施工🚧
### 数据清洗
先使用正则运算进行基本的清洗

### 数据预处理
如tianji项目中的数据处理模块，使用ai转化为问答形式

(经实践，tianji生成的格式不对称于讯飞的格式要求，已在其基础上修改为Alpaca格式)

### 微调训练
使用讯飞大模型网站进行微调，视效果调整



### prompt调整
预计我们会将我们的梅花易数AI设置统一的输入输出及追问模版，以便其规范性。同时会让其输出他的数学运算过程，及算卦依据。
