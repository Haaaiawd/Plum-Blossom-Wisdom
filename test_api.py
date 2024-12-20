import logging
import yaml
import os
from volcenginesdkarkruntime import Ark
import pyttsx3

def test_api():
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    
    # 加载配置文件
    config_path = os.path.join(os.path.dirname(__file__), 'config', 'config.yaml')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 从配置文件中获取API配置信息
    api_key = config['qa_generation']['api_key']
    api_secret = config['qa_generation']['api_secret']
    endpoint = config['qa_generation']['endpoint']
    model_name = config['qa_generation']['model_name']
    
    # 初始化 Ark 客户端
    client = Ark(
        ak=api_key,
        sk=api_secret,
        region='cn-north-1'  # 确保指定正确的区域
    )
    
    # 初始化 pyttsx3 引擎
    engine = pyttsx3.init()
    
    # 配置 TTS 的语速和音量（可选）
    engine.setProperty('rate', 150)  # 语速
    engine.setProperty('volume', 1)  # 音量
    
    # 欢迎语
    Welcome_Text = "您好，我是豆包，您的大模型对话助手，请问有什么可以帮到您？(输入 'exit' 退出对话)"
    print(Welcome_Text)
    engine.say(Welcome_Text)
    engine.runAndWait()  # 等待语音播放完毕
    
    # 进入多轮对话的循环
    while True:
        # 从终端获取用户输入
        user_input = input("User：\r\n")
    
        # 检查用户是否想退出
        if user_input.lower() in ["exit", "quit"]:
            print("AI：感谢您的使用，再见！")
            break
    
        # 创建流式对话请求
        stream = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
                {"role": "user", "content": user_input},  # 使用终端输入的内容
            ],
            stream=True
        )
    
        print("AI:")
        # 初始化一个空字符串来存储所有文本
        full_text = ""
    
        # 逐块读取流式输出并将结果打印
        for chunk in stream:
            if not chunk.choices:
                continue
            # 获取文本内容
            text = chunk.choices[0].delta.content
    
            # 输出文本到控制台
            print(text, end="")
    
            # 将文本累积到 full_text
            full_text += text
    
        # 当流式结果全部接收完成后，开始将累积的文本通过 TTS 朗读出来
        if full_text:
            engine.say(full_text)
            engine.runAndWait()  # 等待语音播放完毕
    
        print("\r\n")

if __name__ == "__main__":
    test_api()