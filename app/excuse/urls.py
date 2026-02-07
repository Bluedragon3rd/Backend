from django.urls import path
from .views import *

urlpatterns = [
    # 입력페이지 post
    path('excuses', MakeExcuse.as_view(), name = 'make_excuse')
]