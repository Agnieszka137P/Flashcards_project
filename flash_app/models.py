from django.db import models
from django.contrib.auth.models import User

from flashcards import settings

RESULTS = (
    (0, 'WRONG'),
    (1, 'Correct but difficult'),
    (2, 'CORRECT'),
)


class Category(models.Model):
    category_name = models.CharField(max_length=64, unique=True)
    category_description = models.TextField()

    def __str__(self):
        return f"{self.category_name}"


class QuestionText(models.Model):
    question = models.TextField()
    answer = models.TextField()
    categories = models.ManyToManyField(Category)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    #user = models.ForeignKey(settings.AUTH_USER_MODEL,
                      #null=True, blank=True, on_delete=models.SET_NULL)


# class QuestionImage(models.Model):
#     question = models.ImageField(upload_to='images/')
#     answer = models.TextField()
#     categories = models.ManyToManyField(Category)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class FlashCardsTextStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flash_card = models.ForeignKey(QuestionText, on_delete=models.CASCADE)
    result_1 = models.IntegerField(choices=RESULTS)
    date_1 = models.DateTimeField(auto_now=True)
    result_2 = models.IntegerField(choices=RESULTS, null=True)
    date_2 = models.DateTimeField(null=True)
    result_3 = models.IntegerField(choices=RESULTS, null=True)
    date_3 = models.DateTimeField(null=True)


