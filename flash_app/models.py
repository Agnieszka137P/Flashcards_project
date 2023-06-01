from django.db import models
from django.contrib.auth.models import User


RESULTS = (
    (0, 'WRONG'),
    (1, 'Correct but difficult'),
    (2, 'CORRECT'),
)


class Category(models.Model):
    """Model for categories of flashcards"""
    category_name = models.CharField(max_length=64, unique=True)
    category_description = models.TextField()

    def __str__(self):
        return f"{self.category_name}"


class QuestionText(models.Model):
    """Flashcards with text question and text answer"""
    question = models.TextField()
    answer = models.TextField()
    categories = models.ManyToManyField(Category)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


class FlashCardsTextStatus(models.Model):
    """Model to record results of each learning session for QuestionText objects"""
    session = models.ForeignKey("Session", on_delete=models.CASCADE, null=True)
    flash_card = models.ForeignKey(QuestionText, on_delete=models.CASCADE)
    result = models.IntegerField(choices=RESULTS, null=True)
    date = models.DateTimeField(auto_now=True)


class Session(models.Model):
    """Model to create learning session for QuestionText objects"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    flash_cards = models.ManyToManyField(QuestionText, through=FlashCardsTextStatus)
    amount_of_cards = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)


class QuestionImage(models.Model):
    """Flashcards with image as a question and text answer"""
    question = models.ImageField(upload_to='images/')
    answer = models.TextField()
    categories = models.ManyToManyField(Category)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)


# class QuestionImageStatus(models.Model):
# """Model to record results of each learning session for QuestionImage objects"""
#     session = models.ForeignKey("SessionImage", on_delete=models.CASCADE, null=True)
#     flash_card = models.ForeignKey(QuestionImage, on_delete=models.CASCADE)
#     result = models.IntegerField(choices=RESULTS, null=True)
#     date = models.DateTimeField(auto_now=True)
#
#
# class SessionImage(models.Model):
# """Model to create learning session for QuestionImage objects"""
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     start_date = models.DateTimeField(auto_now_add=True)
#     flash_cards = models.ManyToManyField(QuestionImage, through=QuestionImageStatus)
#     amount_of_cards = models.IntegerField()
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)

