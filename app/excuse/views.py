from rest_framework.response import Response
from rest_framework.views import APIView
import re, json

from .models import *
from .llmservices import *

# Post Excuse API
# 입력 받고 질문, 거짓말레벨, 기억레벨, 시나리오 반환
class MakeExcuse(APIView):

    # 질문 생성
    def post(self, request):
        
        try:
            identifier = request.data.get("id")
            if not identifier:
                return Response({"error" : "랜덤 id 가 필요합니다."}, status = 400)
            
            situation = request.data.get("situation")
            if not situation:
                return Response({"error" : "상황(사회적 위기)가 필요합니다."}, status = 400)
            
            reason = request.data.get("reason")
            if not reason:
                return Response({"error" : "우발~반복 척도가 필요합니다."}, status = 400)
            try:
                reason = int(reason)
            except (TypeError, ValueError):
                return Response({"error": "reason은 숫자여야 합니다."}, status=400)
            if not 1 <= reason <= 5:
                return Response({"error": "reason은 1~5 사이여야 합니다."}, status=400)
            
            mood = request.data.get("mood")
            if not mood:
                return Response({"error" : "mood 가 필요합니다."}, status = 400)
            
            target = request.data.get("target_audience")
            if not target:
                return Response({"error" : "target_audience가 필요합니다."}, status = 400)
            
            # Input 테이블 create
            input = Input.objects.create(
                identifier = identifier,
                situation = situation,
                reason = reason,
                mood = mood,
                target = target
            )

            # 핑계 생성(텍스트, 거짓말 레벨, 기억 난이도, 시나리오 3개 반환)
            raw_text = generate_excuse(input).strip() # 앞뒤 공백 제거
            #print(raw_text)
            # 마크다운 태그 제거 (가장 흔한 에러 원인)
            if raw_text.startswith("```"):
                raw_text = raw_text.replace("```json", "").replace("```", "").strip()
            #print(text)
            # 응답 파싱
            try:
                excuse_json = json.loads(raw_text)
                excuse_text = excuse_json["excuse"]
                responses = excuse_json["responses"]
            except (json.JSONDecodeError, KeyError):
                raise ValueError(f"핑계 JSON 파싱 실패:\n{raw_text}")

            # Vector S 생성 (LLM)
            print(excuse_text)
            raw_vector = generate_vector(excuse_text).strip()
            # 마크다운 태그 제거 (가장 흔한 에러 원인)
            if raw_vector.startswith("```"):
                raw_vector = raw_vector.replace("```json", "").replace("```", "").strip()
            print(f"raw_vector :{raw_vector}")
            try :
                vector_json = json.loads(raw_vector)
            except json.JSONDecodeError:
                raise ValueError(f"벡터 JSON 파싱 실패:\n{raw_vector}")
            
            # Vector 테이블 create
            vector = Vector.objects.create(
                severity= vector_json["severity"],
                specificity = vector_json["specificity"],
                verifiability = vector_json["verifiability"],
                frequency = vector_json["frequency"],
                truth_plausibility = vector_json["truth_plausibility"],
                fatigue = vector_json["fatigue"],
                memory_load = vector_json["memory_load"],
            )
            # Excuse 테이블 create
            excuse = Excuse.objects.create(
                input = input,
                text = excuse_text,
                vector = vector
            )
            # 응답 반환하기
            vector_values = vector_json.values()
            lie_level = sum(vector_values) / len(vector_values) if vector_values else 0

            return Response(
                {
                    "status" : 200,
                    "excuse" : excuse.text,
                    "lie_level" : round(lie_level,1) * 10,
                    "memory_level" : vector.memory_load * 10,
                    "scenario" : [
                        {"percent": f"{r['probability']}%", "reaction": r['text']}
                        for r in responses
                    ]
                },
                status = 201
            )


        except Exception as e:
            return Response(
                {"error" : "MakeExcuse 중 서버 내부 오류 발생", "detail" : str(e)},
                status=500,
            )