# Plum Blossom Wisdom 梅花智数

> 灵感来自同类型算卦AI
>
> 梅花易数入门 (中国易学文化研究院 编)
>

## 项目背景及概述：
### 项目背景：
在科学占据主导地位的今天，玄学以其神秘色彩仍然吸引着人们的目光。

![在billibili，这样的教学视频有上百万的播放](https://cdn.nlark.com/yuque/0/2024/png/45387460/1734157198665-b2bf7f24-16c0-46fa-b793-37b573a1bd9d.png)
> 在billibili，这样的教学视频有上百万的播放

对于将卦象用运算表示，通过数字、点滴变化推演出各种可能性的梅花易数来说，玄学是否具有其独到之处尚无定论。

在这样的情形下，**最理智的行为是去真正了解它，然后再来看到底是猫是虎**。在学习成本已经传承等方面的妥协下，也许将其做成AI来一探究竟是最好的选择

### 项目概述
本项目使用**《梅花易数入门 (中国易学文化研究院 编)》**、**《梅花易数白话解》**作为基础框架，使用讯飞大模型进行精调。使用该大模型时，梅花易数AI会询问时间，人物，环境，动静等要素，根据要素进行计算后给出发生某件事的预测。

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
+ │   ├── text_corrector.py # 文本校正工具
+ │   ├── data_formatter.py # 数据格式化工具
+ │   ├── qa_generator.py   # 问答对生成器
+ │   └── analyze_hexagram.py # 卦象分析工具
+ ├── config/
+ │   └── config.yaml       # 配置文件
+ └── output/               # 输出目录

**由于tesseract精度有限，因此我们使用豆包AI进行校正和识图**

### 文本清理工具使用说明
项目中的文本清理工具 `text_cleaner.py` 提供了以下功能：
1. 自动检测和处理文件编码
2. 清理文本格式，包括：
   - 统一空白字符
   - 移除特殊控制字符
   - 清理多余空行
   - 移除页眉页脚数字标记
3. 自动将输出文件保存为UTF-8编码

#### 使用方法：
直接运行 text_cleaner.py：
```bash
python src/text_cleaner.py
```

脚本会：
- 自动检测输入文件的编码
- 尝试多种编码方式读取文件
- 清理文本内容
- 以UTF-8编码保存处理后的文件

### 问答对生成工具使用说明
项目提供了完整的文本处理到问答对生成的流程：

1. **文本清理**
```bash
python src/text_cleaner.py
```
- 自动处理文件编码
- 清理文本格式
- 输出清理后的UTF-8文本文件

2. **生成问答对**
```bash
python test_qa_generator.py
```
- 自动识别和分割章节
- 为每个章节生成问答对
- 输出：
  - 各章节问答对（`chapter_XXX_章节名.json`）
  - 合并后的完整问答对（`all_qa_pairs.json`）

3. **问答对处理**
```bash
python test_qa_operator.py
```
- 处理生成的问答对
- 转换为训练所需格式

### 注意事项
- 确保已正确配置 `config.yaml` 中的API密钥
- 每个章节的处理都有延时，避免API调用过于频繁
- 生成的问答对存储在指定的输出目录中

---

## 使用说明

### 1. 安装依赖
确保你已经安装了所有必要的依赖项。你可以使用以下命令安装依赖项：
```bash
pip install -r requirements.txt
```

### 2. 配置文件
确保 `config/config.yaml` 文件存在并且配置正确。特别是 `image_captioning` 和 `pdf_processing` 部分的配置。

### 3. 处理PDF文件
使用以下命令运行主程序，提取PDF中的图片和文本：
```bash
python src/main.py path/to/your.pdf --config config/config.yaml
```

### 4. 使用豆包AI进行识图
你可以使用 `analyze_hexagram.py` 脚本来分析卦象图片，并生成描述。首先在代码中指定图片路径，然后运行脚本：
```bash
python src/analyze_hexagram.py
```

### 5. 手动插入数据
将豆包AI生成的描述手动插入到数据集中，并使用 `data_formatter.py` 格式化数据。

### 6. 生成问答对
使用 `qa_generator.py` 生成问答对：
```bash
python src/qa_generator.py input_file.json output_file.json
```

### 目录结构
确保你的项目目录结构如下：
```
project/
├── README.md
├── requirements.txt
├── src/
│   ├── main.py
│   ├── pdf_processor.py
│   ├── image_captioner.py
│   ├── text_cleaner.py
│   ├── text_corrector.py
│   ├── data_formatter.py
│   ├── qa_generator.py
│   └── analyze_hexagram.py
├── config/
│   └── config.yaml
└── output/
```

这样，你就可以使用豆包AI进行识图，并手动插入数据到数据集中。然后使用项目中的工具进行数据处理和问答对生成。
