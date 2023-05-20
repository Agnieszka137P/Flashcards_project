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
from flash_app.views import AddCategoryView, AddTextFlashcardView, ChooseLearnSessionView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('add_category', AddCategoryView.as_view(), name='add_category'),
    #path('update_category', UpdateCategoryView.as_view(), name='update_category'),
    path('add_textflashcard', AddTextFlashcardView.as_view(), name='add_textflashcard'),
    path('accounts/', include("django.contrib.auth.urls")),
    path('choose_session', ChooseLearnSessionView.as_view(), name='choose_session'),
    # path('flashcard_text', FlashcardTextView.as_view(), name='flashcard'),
]
