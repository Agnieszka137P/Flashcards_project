from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView, ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib.auth import authenticate, logout, login
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
import random

from .models import Category, QuestionText, FlashCardsTextStatus, Session
from .forms import FlashcardTextAnswerForm


class FlashcardsView(View):
    def get(self, request):
        return TemplateResponse(request, 'main_flashcards.html')

    #context = {}


class AddCategoryView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Category
    success_url = reverse_lazy('add_category')
    fields = '__all__'

    def get_success_message(self, cleaned_data):
        return f"Category {cleaned_data['category_name']} added"


class CategoryListView(ListView):
    paginate_by = 20
    model = Category
    ordering = ('category_name', 'category_description')


class UpdateCategoryView(LoginRequiredMixin,  PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Category
    success_url = reverse_lazy('category_list')
    fields = '__all__'
    template_name_suffix = '_update_form'
    permission_required = 'flash_app.change_category'

    def get_success_message(self, cleaned_data):
        return f"Category {cleaned_data['category_name']} updated"


class DeleteCategoryView(PermissionRequiredMixin, DeleteView):
    permission_required = 'flash_app.delete_category'
    model = Category
    success_url = reverse_lazy('category_list')


class AddTextFlashcardView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = QuestionText
    fields = ['question', 'answer', 'categories']
    success_url = reverse_lazy('add_textflashcard')
    success_message = 'flashcard added'

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class FlashcardsListView(LoginRequiredMixin, ListView):
    paginate_by = 20
    model = QuestionText
    ordering = ('question', 'answer')

    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(user_id=self.request.user.id)

# dodać możliwość posortowania po kategorii


class UpdateQuestionTextView(LoginRequiredMixin, SuccessMessageMixin, UserPassesTestMixin, UpdateView):
    model = QuestionText
    success_url = reverse_lazy('flashcards_list')
    fields = ['question', 'answer', 'categories']
    template_name_suffix = '_update_form'
    success_message = 'flashcard updated'

    #  edycje i usuwanie może zrobić tylko user bedacy ownerem fiszki
    def test_func(self):
        self.object = self.get_object()
        return self.object.user == self.request.user


class DeleteQuestionTextView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = QuestionText
    success_url = reverse_lazy('flashcards_list')

    #  edycje i usuwanie może zrobić tylko user bedacy ownerem fiszki
    def test_func(self):
        self.object = self.get_object()
        return self.object.user == self.request.user


class ChooseLearnSessionView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Session
    fields = ['amount_of_cards', 'category']

    def form_valid(self, form):
        form.instance.user = self.request.user
        result = super().form_valid(form)
        number = form.cleaned_data['amount_of_cards']
        category_id = form.cleaned_data['category']
        #category = Category.objects.get(pk=category_id)
        flashcards_user = QuestionText.objects.filter(categories=category_id).filter(user_id=self.request.user.id).order_by('?')
        flashcards_common_list = QuestionText.objects.filter(categories=category_id).filter(user_id__isnull=True)
        flashcards_list = []
        for card in flashcards_common_list:
            flashcards_list.append(card)
        for card in flashcards_user:
            flashcards_list.append(card)

        random.shuffle(flashcards_list)
        if len(flashcards_list) == 0:
            messages.success(self.request, "You don't have flashcards in chosen category")
            return redirect('choose_session')
        if len(flashcards_list) <= number:
            flashcards_list = flashcards_list
        elif len(flashcards_list) > number:
            flashcards_list = flashcards_list[0:number]
        #zapełniamy tą listą tabelę pośrednią
        for card in flashcards_list:
            FlashCardsTextStatus.objects.create(result=None, session=form.instance, flash_card=card)
            #user=self.request.user,
            #c.flash_card.add(card)
        return super().form_valid(form)

    # przekierowanie do pierwszej fiszki w sesji
    def get_success_url(self):
        return reverse('flashcard_question', kwargs={'session_id': self.object.id})



class FlashcardTextQuestionView(LoginRequiredMixin, View):
    def get(self, request, session_id):
        flashcards = FlashCardsTextStatus.objects.filter(session_id=session_id)
        #session = Session.objects.get(id=session_id)
        flashcards_id_list = []
        for card in flashcards:
            if card.flash_card_id not in flashcards_id_list:
                flashcards_id_list.append(card.flash_card_id)

        random.shuffle(flashcards_id_list)
        num = 0
        while num < len(flashcards_id_list):
            item = flashcards_id_list[num]

            questiontext = QuestionText.objects.get(id=item)
            flashcard_status = FlashCardsTextStatus.objects.filter(session_id=session_id, flash_card_id=item).order_by("-date").first()
            if flashcard_status.result != 1 and flashcard_status.result != 2:
                return TemplateResponse(request, "flashcard_question.html",
                                        context={"questiontext": questiontext, "flashcard_status": flashcard_status, "session_id": session_id})
            else:
                num += 1
        session_id = session_id
        return redirect('finish_page', session_id=session_id) #przekierowanie do strony "koniec sesji" z linkiem do głównej
        # return redirect("flashcard_answer", session_id=session.id, questiontext_id=questiontext.id)

    # wybiera fiszki z danym id, sortuje po dacie i sprawdza status najnowszej - jeśli jest 0 lub null wyrzuca ją,
    # jeśli nie przechodzi do kolejnej, jeśli wszystkie ostatnie są zgadnięte przekierowuje do strony "koniec sesji" z linkiem do głównej



class FlashcardTextAnswerView(LoginRequiredMixin, FormView):
    form_class = FlashcardTextAnswerForm
    template_name = 'flashcardtextanswer.html'

    def get_queryset(self):
        query_set = super().get_queryset()
        return query_set.filter(session_id=int(self.kwargs['session_id'])).filter(questiontext_id=int(self.kwargs['questiontext_id']))

    def get_context_data(self):
        context = super().get_context_data()
        context['flashcard'] = QuestionText.objects.get(id=int(self.kwargs['questiontext_id']))
        return context

    def form_valid(self, form):
        session = Session.objects.get(id=int(self.kwargs['session_id'])) # pobieramy sesję
        flashcard = QuestionText.objects.get(id=int(self.kwargs['questiontext_id'])) # pobieramy fiszkę
        result = form.cleaned_data['result']

        FlashCardsTextStatus.objects.create(result=result, session=session, flash_card=flashcard)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        session = Session.objects.get(id=int(self.kwargs['session_id']))
        return reverse('flashcard_question', kwargs={'session_id': session.id})

# wynik zapisujemy w modelu FlashcardsTextStatus


class FinishPageView(LoginRequiredMixin, View): #dodać kategorię itp
    def get(self, request, session_id):
        flashcards_done = FlashCardsTextStatus.objects.filter(session_id=session_id)
        flashcards_id_list = []
        for card in flashcards_done:
            if card.flash_card_id not in flashcards_id_list:
                flashcards_id_list.append(card.flash_card_id)
        amount = len(flashcards_id_list)
        time = flashcards_done[len(flashcards_done)-1].date - flashcards_done[0].date
        return render(request, "finish_page.html", context={"amount": amount, "time": time})


