import os
from dotenv import load_dotenv

import openai
from openai import OpenAI

# 加载环境变量
env_path = os.path.join(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))), '.env')
load_dotenv(env_path)

# 获取配置
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL")

openai.api_key = os.getenv("GEMINI_API_KEY")
openai.api_base="https://api.siliconflow.cn/v1"
client = OpenAI(api_key=openai.api_key ,base_url=openai.api_base)


class ResponseWrap:
    def __init__(self, text):
        self.text = text


class GeminiLikeAPI:
    def __init__(self, client=client, model=model_name):
        """
        初始化 Gemini 风格的接口。
        :param model: 使用的 OpenAI 模型，默认为 gpt-3.5-turbo。
        """
        self.client=client
        self.model = model

    def chat(self, messages):
        """
        模拟 Gemini 的聊天接口。
        :param messages: 对话历史，格式为 [{"role": "user", "content": "Hello"}]
        :return: 模型的回复
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {e}"

    def generate_content(self, content):
        """
        模拟 Gemini 的文本生成接口。
        :param prompt: 提示文本
        :param max_tokens: 最大生成的 token 数量
        :return: 生成的文本
        """
        try:
            messages = [
                {"role": "user", "content": content},
            ]
            response = self.chat(messages)
            return ResponseWrap(response)
        except Exception as e:
            return f"Error: {e}"

# 示例用法
if __name__ == "__main__":
    api = GeminiLikeAPI()

    # 聊天示例
    messages = [
        {"role": "user", "content": "Hello, how are you?"},
    ]
    response = api.chat(messages)
    print("Chat Response:", response)

    # 文本生成示例
    prompt = "Write a short story about a magical forest."
    generated_text = api.generate_content(prompt)
    print("Generated Text:", generated_text.text)