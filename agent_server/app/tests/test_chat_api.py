from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    api_key = os.getenv("openai_api_key")
    base_url = os.getenv("openai_base_url", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = os.getenv("openai_model", "qwen-plus")

    if not api_key:
        raise ValueError("openai_api_key 未配置，请检查 .env")

    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )

    print("开始请求千问接口...")
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "你是一个简洁的校园系统助手。"},
            {"role": "user", "content": "请用一句话介绍你自己。"},
        ],
        temperature=0.3,
        timeout=30,
    )

    print("请求成功。")
    print("模型回复：")
    print(response.choices[0].message.content)


if __name__ == "__main__":
    main()