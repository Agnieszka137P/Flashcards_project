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
def textflashcard(user):
    cat = Category.objects.create(
        category_name="Spanish language",
        category_description="words of spanish language"
    )
    textflashcard = QuestionText.objects.create(
        question="computer",
        answer="ordenador"
    )
    textflashcard.categories.set(cat)
    textflashcard.user.set(user)
    return textflashcard