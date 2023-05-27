"""
URL configuration for flashcards project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views, urls
from django.contrib.auth import authenticate, logout, login
from django.urls import path, include
from flash_app.views import AddCategoryView, AddTextFlashcardView, ChooseLearnSessionView, FlashcardTextQuestionView, \
    FlashcardTextAnswerView, FinishPageView, CategoryListView, FlashcardsView, FlashcardsListView, UpdateCategoryView, \
    DeleteCategoryView, UpdateQuestionTextView, DeleteQuestionTextView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', FlashcardsView.as_view(), name="index"),
    path('accounts/', include("django.contrib.auth.urls")),
    path('accounts/profile/', FlashcardsView.as_view(), name="index"), #czy to jest dobrze?
    path('add_category', AddCategoryView.as_view(), name='add_category'),
    path('category/update/<int:pk>', UpdateCategoryView.as_view(), name='update_category'),
    path('category/delete/<int:pk>', DeleteCategoryView.as_view(), name='delete_category'),
    path('add_textflashcard', AddTextFlashcardView.as_view(), name='add_textflashcard'),
    path('choose_session', ChooseLearnSessionView.as_view(), name='choose_session'),
    path('flashcard_question/<int:session_id>', FlashcardTextQuestionView.as_view(), name='flashcard_question'),
    path('flashcard_answer/<int:session_id>/<int:questiontext_id>', FlashcardTextAnswerView.as_view(), name='flashcard_answer'),
    path('finish_page', FinishPageView.as_view(), name='finish_page'),
    path('category_list', CategoryListView.as_view(), name='category_list'),
    path('flashcards_list/<int:category_id>', FlashcardsListView.as_view(), name='flashcards_list'),
    path('flashcards_list/questiontext/update/<int:pk>', UpdateQuestionTextView.as_view(), name='update_questiontext'),
    path('flashcards_list/questiontext/delete/<int:pk>', DeleteQuestionTextView.as_view(), name='delete_questiontext'),
]
