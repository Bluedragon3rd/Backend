from rest_framework.views import APIView
from rest_framework.response import Response
from .service.llm import *
from .service.crud import *
import json

from app.excuse.models import Excuse, Vector

class CreateQuestion(APIView):
    def post(self, request):
        excuse = request.data['answer']
        prev_excuses = get_excuse_by_content(request.data['id'], excuse)
        context = get_context_by_identifier(request.data['id'])
        res_and_ans = json.loads(send_message_for_question(create_question_prompt(excuse, context)))
        if not prev_excuses:
            excuses, vectors = get_data_by_identifier(request.data['id'])
            res = json.loads(send_message(create_test_prompt(excuses, vectors, res_and_ans['question'], excuse)))
            new_v = Vector.objects.create(
                severity=vectors[-1].severity+res['vector_delta']['severity'],
                specificity=vectors[-1].specificity+res['vector_delta']['specificity'],
                verifiability=vectors[-1].verifiability+res['vector_delta']['verifiability'],
                frequency=vectors[-1].frequency+res['vector_delta']['frequency'],
                truth_plausibility=vectors[-1].truth_plausibility+res['vector_delta']['truth_plausibility'],
                fatigue=vectors[-1].fatigue+res['vector_delta']['fatigue'],
                memory_load=vectors[-1].memory_load+res['vector_delta']['memory_load'],
            )
            new_v.save()
            new_excuse = Excuse.objects.create(
                input=context,
                text=excuse,
                vector=new_v
            )
            new_excuse.save()
        return Response(res_and_ans)

class GetScore(APIView):
    def get(self, request):
        return Response({'message': 'Question created'})