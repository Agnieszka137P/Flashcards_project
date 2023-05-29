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
# testy widoków logowania (login, logout, change password)
# testy widoku ChooseLearnSessionView
# testy widoku FlashcardTextQuestionView
# testy widoku FlashcardTextAnswerView


# testy widoków związanych z modelem Category (add_x, delete_x, update_x, lista)

@pytest.mark.django_db
def test_category_addition_requires_login(client, user):
    client.force_login(user=user)
    response = client.get('/add_category')
    assert response.status_code == 200
    initial_categories_count = Category.objects.count()
    response = client.post('/add_category', {"category_name": "Finish", "category_description": "Flahcard for finish language"})  # przysłane dane z formularza
    assert response.status_code == 302
    assert response.url == '/add_category'
    assert Category.objects.count() == initial_categories_count + 1


def test_category_addition_for_not_logged(client):
    client = Client()
    response = client.get('/add_category')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/add_category'  # na jaki adress


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
    assert list(Category.objects.all()) == list(Category.objects.none())


# List view??

# @pytest.mark.django_db
# def test_list_view(client, category):
#     response = client.get('/category_list')
#     assert response.status_code == 200
#     #categories = Category.objects.all()
#     # assert len(response.context) == 1
#     # print(response.contex)
#     #assert response.context[0] == category
#     assert category.category_name in response.context


# testy widoków związanych z modelem QuestionText (add, delete, update, lista)
def test_questiontext_addition_for_not_logged(client):
    client = Client()
    response = client.get('/add_textflashcard')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/add_textflashcard'  # na jaki adress


# @pytest.mark.django_db
# def test_questiontext_addition_requires_login(client, user, category):
#     client.force_login(user=user)
#     response = client.get('/add_textflashcard')
#     assert response.status_code == 200
#     initial_questiontext_count = QuestionText.objects.count()
#     # flashcard = textflashcard
#     # flashcard.user.set(user)
#     response = client.post('/add_textflashcard', {'question': "computer", 'answer': "ordenador"}, {'user'=user, 'categories'=category})  # przysłane dane z formularza
#     assert response.status_code == 200
#     assert QuestionText.objects.count() == initial_questiontext_count + 1


@pytest.mark.django_db
def test_flashcard_delete_without_login(client, user, textflashcard):
    client.force_login(user=user)
    response = client.post(reverse('delete_questiontext', kwargs={"pk": textflashcard.id}))
    assert response.status_code == 403


# @pytest.mark.django_db
# def test_category_delete_with_login(client, user, category):
#     p = Permission.objects.get(codename='delete_category')
#     user.user_permissions.add(p)
#     client.force_login(user=user)
#     response = client.get(reverse('delete_category', kwargs={"pk": category.id}))
#     assert response.status_code == 200
#     response = client.post(reverse('delete_category', kwargs={"pk": category.id}))
#     assert response.status_code == 302
#     assert list(Category.objects.all()) == list(Category.objects.none())

