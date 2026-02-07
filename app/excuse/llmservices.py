# llmservice.py
import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1",
)

MODEL_NAME = "solar-pro3"  # 또는 chat-reasoning

def upstage_chat(messages, temperature=0.2, max_tokens=1024):
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
    )

    return response.choices[0].message.content
