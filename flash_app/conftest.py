from django.contrib.auth.models import User
from django.test import Client
import pytest

from .models import Category, QuestionText, FlashCardsTextStatus, Session



@pytest.fixture
def user():
    user = User.objects.create_user(username="user", password="")
    return user

@pytest.fixture
def client():
    client = Client()
    return client

@pytest.fixture
def category():
    category = Category.objects.create(
        category_name="Capital Cities",
        category_description="Capital cities of countries"
    )
    return category


@pytest.fixture
def textflashcard(user, category):
    textflashcard = QuestionText.objects.create(
        question="computer",
        answer="ordenador"
    )
    textflashcard.user = user
    textflashcard.categories.set([category])
    return textflashcard
