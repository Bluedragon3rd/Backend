# llmservice.py
import os
from openai import OpenAI
from decouple import config
from .models import *

# LLM 사용 함수
client = OpenAI(
    api_key="up_5qRrJ8sa0Ey0awZAlW4CGsJz3ExtN",
    base_url="https://api.upstage.ai/v1",
)

MODEL_NAME = "solar-pro3"  # 또는 chat-reasoning

def upstage_chat(messages, temperature=0.6, max_tokens=1024):
    print("--- API 호출 시작 ---") # 디버깅용
    full_content = ""
    try :
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
                full_content += chunk.choices[0].delta.content
        #content = response.choices[0].message.content
        #print(f"--- API 응답 내용: {content} ---") # 여기가 비어있는지 확인
        return full_content.strip()
    except Exception as e:
        print(f"--- API 호출 에러 발생: {e} ---")
        return ""

# 핑계 생성 함수
def generate_excuse(input_obj):
    system_prompt = """
너는 한국 문화에 매우 익숙한 핑계 생성 전문가다. 상대방이 불쾌하지 않도록 상황에 맞는 자연스러운 핑계를 만들어야 한다.
"""

    user_prompt = f"""
다음 정보를 바탕으로 한국어 핑계를 만들어줘. 그리고 그 핑계에 대해 올 수 있는 답변 시나리오를 한 문장 + 퍼센트 로 3개도 만들어줘. (이 외의 다른 문장은 대답하지마)

출력은 반드시 아래 JSON 구조를 정확히 따를 것.


출력 형식:
{{
  "excuse": "핑계 텍스트",
  "responses": [
    {{
      "text": "예상 답변 문장",
      "probability": 0
    }},
    {{
      "text": "예상 답변 문장",
      "probability": 0
    }},
    {{
      "text": "예상 답변 문장",
      "probability": 0
    }}
  ]
}}

[상황]
{input_obj.situation}

[핑계 강도] (1~5)
{input_obj.reason}
- 1: 일반적인 핑계, 무난
- 3: 꽤 그럴듯한 강한 핑계, 흔하지 않은 이유
- 5: 진짜 급하고 창의적인 이유

[현재 상태]
{input_obj.get_mood_display()}

[상대 대상]
{input_obj.get_target_display()}

조건:
- JSON 외의 어떤 텍스트도 출력하지 말 것
- probability는 0~100 사이 정수
- 실제로 쓸 수 있는 자연스러운 말투 
- 상대방이 불쾌하지 않도록 최대한 미안한 마음을 담은 문장들 사이사이에 넣기 
- 한 문단, 2~6문장 
- 너무 추상적이지 않게
"""

    messages = [
        {"role": "system", "content": system_prompt.strip()},
        {"role": "user", "content": user_prompt.strip()},
    ]

    return upstage_chat(
        messages,
        temperature=0.6,
        max_tokens=1024,
    )

# 벡터 생성 함수
def generate_vector(excuse_text):
    system_prompt = """너는 사회적 핑계를 분석하여 수치화하는 평가 모델이다."""

    user_prompt = """
아래에 주어지는 "핑계 텍스트"를 읽고,
각 항목을 아래에 있는 평가 기준을 바탕으로 0.00 ~ 1.00 사이의 실수로 평가하라. JSON 형식으로 답할 것. (수치 외의 불필요한 말은 하지 말 것.)

출력은 반드시 아래 JSON 구조를 정확히 따를 것.

[핑계 텍스트]
"{excuse_text}"

출력 형식:
{{
  "severity": 0.7,
  "specificity": 0.3,
  "verifiability": 0.5,
  "frequency": 0.1,
  "truth_plausibility": 0.2,
  "fatigue": 0.4,
  "memory_load": 0.5
}}


[평가 기준]
- severity (심각도):
  핑계가 다루는 문제의 객관적 심각성
  (가벼운 개인 사정=0.0, 중대한 사고/질병=1.0)

- specificity (구체성):
  시간, 장소, 원인, 상황 묘사가 얼마나 구체적인가
  (모호함=0.0, 매우 구체적=1.0)

- verifiability (검증 가능성):
  제3자가 사실 여부를 확인할 수 있을 가능성
  (전혀 불가=0.0, 쉽게 가능=1.0)

- frequency (빈도):
  이런 핑계가 일반적으로 얼마나 자주 사용되는 유형인가
  (희귀=0.0, 매우 흔함=1.0)

- truth_plausibility (개연성):
  실제로 일어났을 법한 이야기인가
  (억지=0.0, 매우 그럴듯함=1.0)

- fatigue (추궁 피로도):
  상대가 추가 질문을 하게 될 가능성
  (추궁 거의 없음=1.0, 질문 많아짐=0.0)

- memory_load (기억 정보량):
  이후에 동일한 설명을 유지하기 위해 기억해야 할 정보의 양
  (거의 없음=0.0, 많음=1.0)

규칙:
- JSON 외의 어떤 텍스트도 출력하지 말 것
- 모든 값은 반드시 0.0 이상 1.0 이하
- 소수점 둘째 자리까지
- 설명 없이 JSON만 출력

"""

    messages = [
        {"role" : "system", "content" : system_prompt.strip()},
        {"role" : "user", "content" : user_prompt.strip()},
    ]

    return upstage_chat(
        messages,
        temperature = 0.4,
        max_tokens = 1024,
    )
