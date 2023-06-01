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
def category_2():
    category_2 = Category.objects.create(
        category_name="Mountains",
        category_description="The highest mountains in groups"
    )
    return category_2


@pytest.fixture
def textflashcard(user, category):
    textflashcard = QuestionText.objects.create(
        question="Peru",
        answer="Lima",
        user=user
    )
    textflashcard.categories.set([category])
    return textflashcard


@pytest.fixture
def textflashcard_2(user, category):
    textflashcard_2 = QuestionText.objects.create(
        question="Chile",
        answer="Santiago",
        user=user
    )
    textflashcard_2.categories.set([category])
    return textflashcard_2


@pytest.fixture
def textflashcard_3(user, category):
    textflashcard_3 = QuestionText.objects.create(
        question="Kolumbia",
        answer="Bogota",
        user=user
    )
    textflashcard_3.categories.set([category])
    return textflashcard_3


@pytest.fixture
def session(user, category, textflashcard, textflashcard_2, textflashcard_3):
    session = Session.objects.create(
        amount_of_cards=3,
        category=category,
        user=user,
    )
    session.flash_cards.set([textflashcard, textflashcard_2, textflashcard_3])
    return session

#
# @pytest.fixture
# def flashcards_status_1(user, session, textflashcard):
#     flashcardsstatus_1 = FlashCardsTextStatus.objects.create(
#         session=session,
#         flash_card=textflashcard,
#         result=0
#     )
#     return flashcardsstatus_1
#
#
# @pytest.fixture
# def flashcards_status_2(user, session, textflashcard_1):
#     flashcardsstatus_2 = FlashCardsTextStatus.objects.create(
#         session=session,
#         flash_card=textflashcard_2,
#         result=0
#     )
#     return flashcardsstatus_2
#
#
# @pytest.fixture
# def flashcards_status_3(user, session, textflashcard_3):
#     flashcardsstatus_3 = FlashCardsTextStatus.objects.create(
#         session=session,
#         flash_card=textflashcard_3,
#         result=0
#     )
#     return flashcardsstatus_3
