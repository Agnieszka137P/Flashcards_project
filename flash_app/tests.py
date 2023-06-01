from django.test import TestCase, Client
import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission

from .models import Category, QuestionText, FlashCardsTextStatus, Session


def test_main(client):
    response = client.get('/')
    assert response.status_code == 200


def test_view_requires_login(client):
    response = client.get('/add_textflashcard')  # jakiś widok wymagający zalogowania
    assert response.status_code == 302  # redirect
    assert response.url == '/accounts/login/?next=/add_textflashcard'  # na jaki adres


@pytest.mark.django_db
def test_view_requires_login2(client, user):
    response = client.get('/add_textflashcard')  # jakiś widok wymagający zalogowania
    assert response.status_code == 302  # redirect
    assert response.url == '/accounts/login/?next=/add_textflashcard'  # na jaki adres
    client.force_login(user=user)
    response = client.get('/add_textflashcard')
    assert response.status_code == 200

# @pytest.mark.django_db
# def test_band_addition():
#     client = Client()
#     response = client.get('/add-band/')
#     assert response.status_code == 200
#     initial_bands_count = Band.objects.count()
#     response = client.post('/add-band/', {"name": "Nowy zespół", "year": "1999"})  # przysłane dane z formularza
#     assert response.status_code == 200
#     assert Band.objects.count() == initial_bands_count + 1


# testy widoku strony głównej (jeszcze bedzie dodany contex)
# testy widoku FinishPage (jeszcze bedzie dodany contex)
# testy widoku Settings
# testy widoków logowania (login, logout, change password)
# testy widoku FlashcardTextAnswerView


# testy widoków związanych z modelem Category (add_x, delete_x, update_x, lista_x)

@pytest.mark.django_db
def test_category_addition_requires_login(client, user):
    client.force_login(user=user)
    response = client.get('/add_category')
    assert response.status_code == 200
    initial_categories_count = Category.objects.count()
    response = client.post('/add_category', {"category_name": "Finish", "category_description": "Flahcard for finish language"})
    assert response.status_code == 302
    assert response.url == '/add_category'
    assert Category.objects.count() == initial_categories_count + 1


def test_category_addition_not_logged(client):
    client = Client()
    response = client.get('/add_category')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/add_category'


@pytest.mark.django_db
def test_category_edition_without_required_permission(client, user, category):
    client.force_login(user=user)
    response = client.post(reverse('update_category', kwargs={"pk": category.id}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_category_edition_with_required_permission(client, user, category):
    p = Permission.objects.get(codename='change_category')
    user.user_permissions.add(p)
    client.force_login(user=user)
    response = client.get(reverse('update_category', kwargs={"pk": category.id}))
    assert response.status_code == 200
    response = client.post(reverse('update_category', kwargs={"pk": category.id}), {"category_name": "Finish",
                                                                                    "category_description": "Flashcard for finish language"})
    assert response.status_code == 302
    assert response.url == '/category_list'
    cat = Category.objects.get(pk=category.id)
    assert cat.category_name == "Finish"
    assert cat.category_description == "Flashcard for finish language"


@pytest.mark.django_db
def test_category_delete_without_required_permission(client, user, category):
    client.force_login(user=user)
    response = client.post(reverse('delete_category', kwargs={"pk": category.id}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_category_delete_with_required_permission(client, user, category):
    p = Permission.objects.get(codename='delete_category')
    user.user_permissions.add(p)
    client.force_login(user=user)
    response = client.get(reverse('delete_category', kwargs={"pk": category.id}))
    assert response.status_code == 200
    response = client.post(reverse('delete_category', kwargs={"pk": category.id}))
    assert response.status_code == 302
    assert Category.objects.count() == 0


@pytest.mark.django_db
def test_category_list_view(client, category):
    response = client.get('/category_list')
    assert response.status_code == 200
    assert len(response.context['category_list']) == 1
    assert response.context['category_list'][0] == category


# testy widoków związanych z modelem QuestionText (add_x, delete_x, update, lista_x)

def test_questiontext_addition_not_logged(client):
    client = Client()
    response = client.get('/add_textflashcard')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/add_textflashcard'


@pytest.mark.django_db
def test_questiontext_addition_requires_login(client, user, category):
    client.force_login(user=user)
    response = client.get('/add_textflashcard')
    assert response.status_code == 200
    initial_questiontext_count = QuestionText.objects.count()
    response = client.post('/add_textflashcard', {'question': "computer", 'answer': "ordenador", 'user': user.pk, 'categories': category.pk})
    assert response.status_code == 302
    assert response.url == '/add_textflashcard'
    assert QuestionText.objects.count() == initial_questiontext_count + 1


@pytest.mark.django_db
def test_questiontext_delete_without_login(client, textflashcard):
    response = client.post(reverse('delete_questiontext', kwargs={"pk": textflashcard.id}))
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/questiontext/delete/<"pk": textflashcard.id>'


@pytest.mark.django_db
def test_questiontext_delete_with_login(client, user, textflashcard):
    client.force_login(user=user)
    response = client.get(reverse('delete_questiontext', kwargs={"pk": textflashcard.id}))
    assert user == textflashcard.user
    assert response.status_code == 200
    response = client.post(reverse('delete_questiontext', kwargs={"pk": textflashcard.id}))
    assert response.status_code == 302
    assert QuestionText.objects.count() == 0


@pytest.mark.django_db
def test_questiontext_edition_without_login(client, textflashcard):
    response = client.get(reverse('update_questiontext', kwargs={"pk": textflashcard.id}))
    assert response.status_code == 302
    assert response.url == ('/accounts/login/?next=/questiontext/delete/', {"pk": textflashcard.id})


@pytest.mark.django_db
def test_questiontext_edition_with_login(client, user, textflashcard, category):
    client.force_login(user=user)
    response = client.get(reverse('update_questiontext', kwargs={"pk": textflashcard.id}))
    assert response.status_code == 200
    response = client.post(reverse('update_questiontext', kwargs={"pk": textflashcard.id}), {'question': "computer",
                                                                                             'answer': "ordenador", 'user': user.pk, 'categories': category.pk})
    assert response.status_code == 302
    assert response.url == '/flashcards_list'
    flash = QuestionText.objects.get(pk=textflashcard.id)
    assert flash.question == "computer"
    assert flash.answer == "ordenador"
    assert flash.categories.get() == category



@pytest.mark.django_db
def test_questiontext_list_view(client, user, textflashcard):
    client.force_login(user=user)
    response = client.get('/flashcards_list')
    assert response.status_code == 200
    assert len(response.context['questiontext_list']) == 1
    assert response.context['questiontext_list'][0] == textflashcard


def test_questiontext_list_view_without_login(client):
    response = client.get('/flashcards_list')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/flashcards_list'


# tests for ChooseLearnSessionView:
def test_chooseleaarningsession_view_without_login(client):
    response = client.get('/choose_session')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/choose_session'

@pytest.mark.django_db
def test_chooseleaarningsession_view(client, user, category, textflashcard, textflashcard_2, textflashcard_3):
    """check if data are added to the Session model
    then check if data are added to Through model FlashCardsTextStatus"""
    client.force_login(user=user)
    response = client.get('/choose_session')
    assert response.status_code == 200
    initial_session_count = Session.objects.count()
    initial_flashcardstextstatus_count = FlashCardsTextStatus.objects.count()
    response = client.post('/choose_session', {'amount_of_cards': 3, 'category': category.pk, 'user': user.pk})
    assert response.status_code == 302
    assert Session.objects.count() == initial_session_count + 1
    assert FlashCardsTextStatus.objects.count() == initial_flashcardstextstatus_count + 3
    assert response.url == '/flashcard_question/? session.id'

@pytest.mark.django_db
def test_chooseleaarningsession_view_for_empty_category(client, user, category_2, textflashcard, textflashcard_2, textflashcard_3):
    """check if when user choose category where does not have flashcards
    will be redirect to "choose_session" and nothing will be put to the FlashCardsTextStatus model"""
    client.force_login(user=user)
    response = client.get('/choose_session')
    assert response.status_code == 200
    initial_session_count = Session.objects.count()
    initial_flashcardstextstatus_count = FlashCardsTextStatus.objects.count()
    response = client.post('/choose_session', {'amount_of_cards': 3, 'category': category_2.pk, 'user': user.pk})
    assert response.status_code == 302
    assert response.url == '/choose_session'
    assert Session.objects.count() == initial_session_count + 1
    assert FlashCardsTextStatus.objects.count() == initial_flashcardstextstatus_count
# how to assert message?

@pytest.mark.django_db
def test_chooseleaarningsession_view_for_less_flashcards(client, user, category, textflashcard, textflashcard_2):
    """check if when user choose more flashcards that are available in category,
    avaliable amount will be put to the FlashCardsTextStatus model"""
    client.force_login(user=user)
    response = client.get('/choose_session')
    assert response.status_code == 200
    initial_session_count = Session.objects.count()
    initial_flashcardstextstatus_count = FlashCardsTextStatus.objects.count()
    response = client.post('/choose_session', {'amount_of_cards': 3, 'category': category.pk, 'user': user.pk})
    assert response.status_code == 302
    assert Session.objects.count() == initial_session_count + 1
    assert FlashCardsTextStatus.objects.count() == initial_flashcardstextstatus_count + 2
    #assert response.url == '/flashcard_question/? session.id'


# tests for FlashcardTextQuestionView:

@pytest.mark.django_db
def test_flashcardtextquestionView(client, user, category, session):
    client.force_login(user=user)
    response = client.get(reverse('flashcard_question', kwargs={'session_id': session.id}))
    assert response.status_code == 200
