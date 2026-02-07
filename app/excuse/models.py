from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# 추상 클래스 정의 
class BaseModel(models.Model): # models.Model을 상속받음
    created_at = models.DateTimeField(auto_now_add=True) # 객체를 생성할 때 날짜와 시간 저장
    updated_at = models.DateTimeField(auto_now=True) # 객체를 저장할 때 날짜와 시간 갱신

    class Meta:
        abstract = True

class Input(BaseModel):

    MOOD = (
        ('TIRED', '피곤'),
        ('SICK', '아픔'),
        ('MENTAL', '멘탈'),
        ('GOOD', '멀쩡')
    )

    TARGET = (
        ('BOSS','FM 상사'),
        ('EMOTION', '공감형'),
        ('SMART', '눈치 100단'),
        ('FRIEND', '친한 친구'),
        ('TEAMMATE', '회사 팀원')
    )


    id = models.AutoField(primary_key = True)
    identifier = models.CharField(max_length = 20)
    situation = models.CharField(max_length = 50)
    reason = models.IntegerField()
    mood = models.CharField(choices=MOOD)
    target = models.CharField(choices=TARGET)

    def __str__(self):
        return self.identifier
    
class Vector(BaseModel) :
    id = models.AutoField(primary_key = True)

    score_range = [MinValueValidator(0.0), MaxValueValidator(1.0)]

    severity = models.FloatField(validators=score_range, verbose_name="심각도")
    specificity = models.FloatField(validators=score_range, verbose_name="구체성")
    verifiability = models.FloatField(validators=score_range, verbose_name="검증 가능성")
    frequency = models.FloatField(validators=score_range, verbose_name="빈도")
    truth_plausibility = models.FloatField(validators=score_range, verbose_name="개연성")
    fatigue = models.FloatField(validators=score_range, verbose_name="추궁 피로도")
    memory_load = models.FloatField(validators=score_range, verbose_name="기억 정보량")


class Excuse(BaseModel) : # BaseModel 상속

    id = models.AutoField(primary_key = True)
    input = models.ForeignKey(Input,on_delete=models.CASCADE, related_name = 'excuse')
    text = models.TextField()
    vector = models.ForeignKey(Vector, on_delete=models.CASCADE, related_name = 'excuse')

    def __str__(self):
        return self.text
    