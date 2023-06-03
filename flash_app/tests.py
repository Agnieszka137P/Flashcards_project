from django.test import Client
import pytest
from django.urls import reverse
from django.contrib.auth.models import Permission

from .models import Category, QuestionText, FlashCardsTextStatus, Session, QuestionImage


def test_main(client):
    """test for start page"""
    response = client.get('/')
    assert response.status_code == 200


# Tests of views related to the Category model

@pytest.mark.django_db
def test_category_addition_requires_login(client, user):
    """test for AddCategoryView with logged user"""
    client.force_login(user=user)
    response = client.get('/add_category')
    assert response.status_code == 200
    initial_categories_count = Category.objects.count()
    response = client.post('/add_category', {"category_name": "Finish", "category_description": "Flahcard for finish language"})
    assert response.status_code == 302
    assert response.url == '/add_category'
    assert Category.objects.count() == initial_categories_count + 1


def test_category_addition_not_logged(client):
    """test for AddCategoryView with no logged user"""
    client = Client()
    response = client.get('/add_category')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/add_category'


@pytest.mark.django_db
def test_category_edition_without_required_permission(client, user, category):
    """test for UpdateCategoryView when user doesn't have required permission"""
    client.force_login(user=user)
    response = client.post(reverse('update_category', kwargs={"pk": category.id}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_category_edition_with_required_permission(client, user, category):
    """test for UpdateCategoryView when user have required permission"""
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
    """test for DeleteCategoryView when user doesn't have required permission"""
    client.force_login(user=user)
    response = client.post(reverse('delete_category', kwargs={"pk": category.id}))
    assert response.status_code == 403


@pytest.mark.django_db
def test_category_delete_with_required_permission(client, user, category):
    """test for DeleteCategoryView when user have required permission"""
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
    """test for CategoryListView"""
    response = client.get('/category_list')
    assert response.status_code == 200
    assert len(response.context['category_list']) == 1
    assert response.context['category_list'][0] == category


# Test of Views related to QuestionText Model  update, lista_x)

def test_questiontext_addition_not_logged(client):
    """test for AddTextFlashcardView with no logged user"""
    client = Client()
    response = client.get('/add_textflashcard')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/add_textflashcard'


@pytest.mark.django_db
def test_questiontext_addition_requires_login(client, user, category):
    """test for AddTextFlashcardView with logged user"""
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
    """test for DeleteQuestionTextView with no logged user"""
    response = client.post(reverse('delete_questiontext', kwargs={"pk": textflashcard.id}))
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=' + reverse('delete_questiontext', kwargs={"pk": textflashcard.id})


@pytest.mark.django_db
def test_questiontext_delete_with_login(client, user, textflashcard):
    """test for DeleteQuestionTextView with logged user"""
    client.force_login(user=user)
    response = client.get(reverse('delete_questiontext', kwargs={"pk": textflashcard.id}))
    assert user == textflashcard.user
    assert response.status_code == 200
    response = client.post(reverse('delete_questiontext', kwargs={"pk": textflashcard.id}))
    assert response.status_code == 302
    assert QuestionText.objects.count() == 0


@pytest.mark.django_db
def test_questiontext_edition_without_login(client, textflashcard):
    """test for UpdateQuestionTextView with no logged user"""
    response = client.get(reverse('update_questiontext', kwargs={"pk": textflashcard.id}))
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=' + reverse('update_questiontext', kwargs={"pk": textflashcard.id})


@pytest.mark.django_db
def test_questiontext_edition_with_login(client, user, textflashcard, category):
    """test for UpdateQuestionTextView with logged user"""
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
    """test for QuestionTextListView for logged user"""
    client.force_login(user=user)
    response = client.get('/flashcards_list')
    assert response.status_code == 200
    assert len(response.context['questiontext_list']) == 1
    assert response.context['questiontext_list'][0] == textflashcard


def test_questiontext_list_view_without_login(client):
    """test for QuestionTextListView for no logged user"""
    response = client.get('/flashcards_list')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/flashcards_list'


# tests for ChooseLearnSessionView:
def test_chooseleaarningsession_view_without_login(client):
    """test for ChooseLearnSessionView for no logged user"""
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


@pytest.mark.django_db
def test_chooseleaarningsession_view_for_empty_category(client, user, category_2, textflashcard, textflashcard_2, textflashcard_3):
    """check if when user choose category where does not have flashcards
    will be redirected to "choose_session" and nothing will be put to the FlashCardsTextStatus model"""
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
    # assert response.url == reverse('flashcard_question', kwargs={"session_id": session.id})


# tests for FlashcardTextQuestionView:

@pytest.mark.django_db
def test_flashcardtextquestionview_view_without_login(client, session):
    """test for FlashcardTextQuestionView for no logged user"""
    response = client.get(reverse('flashcard_question', kwargs={'session_id': session.id}))
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=' + reverse('flashcard_question', kwargs={'session_id': session.id})


@pytest.mark.django_db
def test_flashcardtextquestionview_with_result_zero(client, user, category, session, textflashcard, textflashcard_2,
                                                    textflashcard_3, flashcards_status_1, flashcards_status_2,
                                                    flashcards_status_3):
    """Check if flashcard with result "0" will be chosen"""
    client.force_login(user=user)
    response = client.get(reverse('flashcard_question', kwargs={'session_id': session.id}))
    assert response.status_code == 200
    assert response.context["questiontext"] == textflashcard_2  # flashcard with result "0""
    assert response.context["flashcard_status"] == flashcards_status_2


# tests for FlashcardTextAnswerView:
@pytest.mark.django_db
def test_flashcardtextanswerview_view_without_login(client, session, textflashcard_2):
    """test for FlashcardTextQuestionView for no logged user"""
    response = client.get(reverse('flashcard_answer', kwargs={'session_id': session.id, 'questiontext_id': textflashcard_2.id}))
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=' + reverse('flashcard_answer', kwargs={'session_id': session.id,
                                                                                          'questiontext_id': textflashcard_2.id})


@pytest.mark.django_db
def test_flashcardtextanswerview(client, user, session, textflashcard_2):
    """test for FlashcardTextQuestionView - add 1 object to FlashCardsTextStatus table"""
    client.force_login(user=user)
    response = client.get(reverse('flashcard_answer', kwargs={'session_id': session.id, 'questiontext_id': textflashcard_2.id}))
    assert response.status_code == 200
    assert response.context['flashcard'] == textflashcard_2
    initial_flashcardstextstatus_count = FlashCardsTextStatus.objects.count()
    response = client.post(reverse('flashcard_answer', kwargs={'session_id': session.id, 'questiontext_id': textflashcard_2.id}), {'result': 2})
    assert response.status_code == 302
    assert response.url == reverse('flashcard_question', kwargs={'session_id': session.id})
    assert FlashCardsTextStatus.objects.count() == initial_flashcardstextstatus_count + 1


# tests for finish page

@pytest.mark.django_db
def test_finish_page_view_without_login(client, session):
    """test for FinishPageView for no logged user"""
    response = client.get(reverse('finish_page', kwargs={'session_id': session.id}))
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=' + reverse('finish_page', kwargs={'session_id': session.id})


@pytest.mark.django_db
def test_finish_page_view_with_login(client, user, session):
    """test for FinishPageView for no logged user"""
    client.force_login(user=user)
    response = client.get(reverse('finish_page', kwargs={'session_id': session.id}))
    assert response.status_code == 200
    assert response.context['amount'] == 3
    assert response.context['category'] == session.category.category_name


# tests for profile view

@pytest.mark.django_db
def test_profile_view(client, user):
    """test for profile view for looged user"""
    client.force_login(user=user)
    response = client.get('/profile')
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_requires_login(client):
    """test for profile view for not looged user"""
    response = client.get('/profile')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/profile'


# tests related to QuestionImage model

def test_questionimage_addition_not_logged(client):
    """test for AddImageFlashcardView with no logged user"""
    client = Client()
    response = client.get('/add_imageflashcard')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/add_imageflashcard'


# not work
@pytest.mark.django_db
def test_questionimage_addition_requires_login(client, user, category):
    """test for AddImageFlashcardView with logged user"""
    client.force_login(user=user)
    response = client.get('/add_imageflashcard')
    assert response.status_code == 200
    initial_questionimage_count = QuestionImage.objects.count()
    response = client.post('/add_imageflashcard', {'question': '/media/images/lights_1.png', 'answer': "Peru", 'user': user.pk,
                                                   'categories': category.pk})
    assert response.status_code == 302
    assert response.url == '/add_imageflashcard'
    assert QuestionImage.objects.count() == initial_questionimage_count + 1


# not work
@pytest.mark.django_db
def test_questionimage_list_view(client, user, imageflashcard):
    """test for ImageTextListView for logged user"""
    client.force_login(user=user)
    response = client.get('/image_list')
    assert response.status_code == 200
    assert len(response.context['image_list']) == 1
    assert response.context['image_list'][0] == imageflashcard


def test_questionimage_list_view_without_login(client):
    """test for ImageTextListView for no logged user"""
    response = client.get('/image_list')
    assert response.status_code == 302
    assert response.url == '/accounts/login/?next=/image_list'
