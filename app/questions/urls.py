from django.urls import path, include
from .view import CreateQuestion, GetScore

urlpatterns = [
    path('', CreateQuestion.as_view()),
    path('/score', GetScore.as_view()),
]
