import os
import unittest
import dotenv
from volcenginesdkarkruntime import Ark

# 加载环境变量
dotenv.load_dotenv(".env")

# 初始化 Ark 客户端
client = Ark()

class TestVolcanoAPI(unittest.TestCase):

    def test_call_volcano_api(self):
        model_id = os.getenv("ENDPOINT_ID")
        stream = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
                {"role": "user", "content": "这是一个测试文本。"},
            ],
            stream=True
        )
        full_text = ""
        for chunk in stream:
            if not chunk.choices:
                continue
            text = chunk.choices[0].delta.content
            full_text += text
        self.assertTrue(len(full_text) > 0)

if __name__ == "__main__":
    unittest.main()
