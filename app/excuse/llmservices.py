# llmservice.py
import os
from openai import OpenAI
from decouple import config
from .models import *

# LLM 사용 함수
client = OpenAI(
    api_key=config("UPSTAGE_API_KEY"),
    base_url="https://api.upstage.ai/v1",
)

MODEL_NAME = "solar-pro3"  # 또는 chat-reasoning

def upstage_chat(messages, temperature=0.6):
    print("--- API 호출 시작 ---") # 디버깅용
    full_content = ""
    try :
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            #max_tokens=max_tokens,
            stream=True,
            reasoning_effort='low',
        )
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="")
                full_content = full_content+chunk.choices[0].delta.content
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
        #max_tokens=1024,
    )

# 벡터 생성 함수
def generate_vector(excuse_text):
    system_prompt = """# Role
    You are an advanced linguistic analyst specializing in semantic quantification. Your task is to analyze the given text (usually an excuse, reason, or statement) and convert it into a 7-dimensional vector based on specific criteria."""

    user_prompt = """

    
    # Evaluation Criteria (Range: 0.0 to 1.0)
    Analyze the input text based on the following 7 dimensions. Return a float value between 0.0 and 1.0 for each.
    
    1. **severity** (Severity of the situation)
       - 0.0: Trivial, everyday occurrence (e.g., overslept).
       - 1.0: Critical, life-altering, or emergency situation (e.g., severe accident, hospitalization).
    
    2. **specificity** (Degree of detail)
       - 0.0: Vague, abstract, or ambiguous.
       - 1.0: Highly specific, includes proper nouns, numbers, or precise time/location.
    
    3. **verifiability** (Ease of fact-checking)
       - 0.0: Impossible to verify (e.g., "I felt sick").
       - 1.0: Easily verifiable with tangible proof (e.g., "I have a doctor's note" or public transit delay logs).
    
    4. **frequency** (Risk of repetitive/cliché use)
       - 0.0: Unique, rare, or creative reason.
       - 1.0: Highly common, cliché, or overused excuse (e.g., "Traffic was bad").
    
    5. **truth_plausibility** (Realism/Believability)
       - 0.0: Absurd, logically inconsistent, or clearly invented.
       - 1.0: Highly realistic and aligns with common sense.
    
    6. **fatigue** (Opponent's questioning fatigue)
       - 0.0: Invites follow-up questions; the listener becomes curious or suspicious.
       - 1.0: Shuts down the conversation; makes the listener feel it's rude or unnecessary to ask further (e.g., TMI, emotional distress).
    
    7. **memory_load** (Cognitive load to maintain the story)
       - 0.0: Simple truth or easy lie; no details to remember.
       - 1.0: Complex fabrication; requires remembering specific fabricated details to avoid contradiction later.
    
    # Output Format
    You must output ONLY a valid JSON object. Do not include any explanation or markdown formatting (like ```json).
    
    {
      "severity": <float>,
      "specificity": <float>,
      "verifiability": <float>,
      "frequency": <float>,
      "truth_plausibility": <float>,
      "fatigue": <float>,
      "memory_load": <float>
    }
    
    #given text
    """+excuse_text

    messages = [
        {"role" : "system", "content" : system_prompt.strip()},
        {"role" : "user", "content" : user_prompt.strip()},
    ]

    return upstage_chat(
        messages,
        temperature = 0.4,
        #max_tokens = 1024,
    )
