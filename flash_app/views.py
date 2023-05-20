from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView, ListView, UpdateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
import random

from .models import Category, QuestionText, FlashCardsTextStatus
from .forms import AddCategoryForm, ChooseLearnSessionForm


class AddCategoryView(SuccessMessageMixin, CreateView):
    model = Category
    success_url = reverse_lazy('add_category')
    fields = '__all__'

    def get_success_message(self, cleaned_data):
        return f"Category {cleaned_data['category_name']} added"


# class UpdateCategoryView(SuccessMessageMixin, UpdateView):
#     model = Category
#     success_url = reverse_lazy('update_category')
#     fields = '__all__'
#     template_name_suffix = '_update_form'
#
#     def get_success_message(self, cleaned_data):
#         return f"Category {cleaned_data['category_name']} updated"


class AddTextFlashcardView(SuccessMessageMixin, CreateView):
    model = QuestionText
    fields = ['question', 'answer', 'categories']
    success_url = reverse_lazy('add_textflashcard')
    success_message = 'flashcard added'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super(AddTextFlashcardView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


    # def save_model(self, request, obj, form, change):
    #     if not obj.pk:
    #         # Only set added_by during the first save.
    #         obj.user = request.user
    #     super().save_model(request, obj, form, change)


class ChooseLearnSessionView(FormView):
    form_class = ChooseLearnSessionForm
    template_name = 'choose_session.html'
    success_url = reverse_lazy('flashcard') # pierwsza fiszka

    def form_valid(self, form):
        number = int(form.cleaned_data['number_of_cards'])
        category = form.cleaned_data['category']
        cat = Category.objects.get(category_name=category)
        flashcards_list = QuestionText.objects.filter(categories=cat)
        random.shuffle(flashcards_list)
        if len(flashcards_list) <= number:
            flashcards_list = flashcards_list
        elif len(flashcards_list) > number:
            flashcards_list = flashcards_list[0:number+1]
        return flashcards_list



# class FlashcardTextView():

