from django.db import models
from django.contrib.auth.models import User


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



# class QuestionImage(models.Model):
#     question = models.ImageField(upload_to='images/')
#     answer = models.TextField()
#     categories = models.ManyToManyField(Category)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class FlashCardsTextStatus(models.Model):
    session = models.ForeignKey("Session", on_delete=models.CASCADE, null=True)
    flash_card = models.ForeignKey(QuestionText, on_delete=models.CASCADE)
    result = models.IntegerField(choices=RESULTS, null=True)
    date = models.DateTimeField(auto_now=True)


class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    flash_cards = models.ManyToManyField(QuestionText, through=FlashCardsTextStatus)
    amount_of_cards = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
