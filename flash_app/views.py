from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.template.response import TemplateResponse
from django.views import View
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import FormView, ListView, UpdateView, CreateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
import random

from .models import Category, QuestionText, FlashCardsTextStatus, Session, QuestionImage
from .forms import FlashcardTextAnswerForm


class FlashcardsView(View):
    """Start page with link to loggin view"""
    def get(self, request):
        return TemplateResponse(request, 'main_flashcards.html')


class AddCategoryView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View allowing to create categories"""
    model = Category
    success_url = reverse_lazy('add_category')
    fields = '__all__'

    def get_success_message(self, cleaned_data):
        return f"Category {cleaned_data['category_name']} added"


class CategoryListView(ListView):
    """List of all categories with links to update and delete views"""
    paginate_by = 20
    model = Category
    ordering = ('category_name', 'category_description')


class UpdateCategoryView(LoginRequiredMixin,  PermissionRequiredMixin, SuccessMessageMixin, UpdateView):
    """Updating of existing flashcard category for logged user with required permission"""
    model = Category
    success_url = reverse_lazy('category_list')
    fields = '__all__'
    template_name_suffix = '_update_form'
    permission_required = 'flash_app.change_category'

    def get_success_message(self, cleaned_data):
        return f"Category {cleaned_data['category_name']} updated"


class DeleteCategoryView(PermissionRequiredMixin, DeleteView):
    """Delete of existing flashcard category for logged user with required permission"""
    permission_required = 'flash_app.delete_category'
    model = Category
    success_url = reverse_lazy('category_list')


class AddTextFlashcardView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View allowing to create QuestionText flashcards for logged users"""
    model = QuestionText
    fields = ['question', 'answer', 'categories']
    success_url = reverse_lazy('add_textflashcard')
    success_message = 'flashcard added'

    def form_valid(self, form):
        """logged user is assigned as QuestionText object user"""
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class FlashcardsListView(LoginRequiredMixin, ListView):
    """List of QuestionText flashcards created by logged user with links to update and delete views"""
    paginate_by = 20
    model = QuestionText
    ordering = ('question', 'answer')

    def get_queryset(self):
        """Filtering to return only flashcards created by logged user"""
        query_set = super().get_queryset()
        return query_set.filter(user_id=self.request.user.id)

# to add sorting by category


class UpdateQuestionTextView(LoginRequiredMixin, SuccessMessageMixin, UserPassesTestMixin, UpdateView):
    """View allowing to update flashcard by their user"""
    model = QuestionText
    success_url = reverse_lazy('flashcards_list')
    fields = ['question', 'answer', 'categories']
    template_name_suffix = '_update_form'
    success_message = 'flashcard updated'

    def test_func(self):
        """check if logged user is the same as updated object user"""
        object = self.get_object()
        return object.user == self.request.user


class DeleteQuestionTextView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """View allowing to delete flashcard by their user"""
    model = QuestionText
    success_url = reverse_lazy('flashcards_list')

    def test_func(self):
        """check if logged user is the same as updated object user"""
        object = self.get_object()
        return object.user == self.request.user


class ChooseLearnSessionView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View for choose learning session, it is doing by create object of Session model.
    User can choose only flashcards created by himself or placed in database without assigned user"""
    model = Session
    fields = ['amount_of_cards', 'category']

    def form_valid(self, form):
        """flashcards from chosen category are filter by user (logged user or no user)
        and put in one list. List is shuffled. Flashcards from list are put in "through" table"""
        form.instance.user = self.request.user
        result = super().form_valid(form)
        number = form.cleaned_data['amount_of_cards']
        category_id = form.cleaned_data['category']
        flashcards_of_user = QuestionText.objects.filter(categories=category_id).filter(user_id=self.request.user.id).order_by('?')
        flashcards_common_list = QuestionText.objects.filter(categories=category_id).filter(user_id__isnull=True)
        flashcards_list = []
        for card in flashcards_common_list:
            flashcards_list.append(card)
        for card in flashcards_of_user:
            flashcards_list.append(card)
        random.shuffle(flashcards_list)
        if len(flashcards_list) == 0:
            messages.success(self.request, "You don't have flashcards in chosen category")
            return redirect('choose_session')
        if len(flashcards_list) <= number:
            flashcards_list = flashcards_list
        elif len(flashcards_list) > number:
            flashcards_list = flashcards_list[0:number]
        for card in flashcards_list:
            FlashCardsTextStatus.objects.create(result=None, session=form.instance, flash_card=card)   # flashcards from list are put in through table, each have at begin result "None"
        return super().form_valid(form)

    def get_success_url(self):
        """Redirection to question from first flashcard"""
        return reverse('flashcard_question', kwargs={'session_id': self.object.id})


class FlashcardTextQuestionView(LoginRequiredMixin, View):
    """View showing flashcard question using FlashCardsTextStatus model. Question is display and
    then pressing "check" button redirect to the page with answer. After each ques (on FlashcardTextAnswer View)
    flashcard is saved as FlashCardsTextStatus record with time of create and result, and the same session_id
    and flash_card_id.
    """
    def get(self, request, session_id):
        """Id of QuestionText flashcards from one session are put in list and shuffle. Then flashcard with first id
        is checking - if the newest record in FlashCardsTextStatus is "wrong" or null (0 or null) question is display
        if the newest record is "correct" or "correct but difficult" (1 or 2) next Flashcard is checking.
        when there are no Flashcards with the newest record "wrong" or null session id finished with redirect to
        the "finish page".
        """
        flashcards = FlashCardsTextStatus.objects.filter(session_id=session_id)
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
        return redirect('finish_page', session_id=session_id)


class FlashcardTextAnswerView(LoginRequiredMixin, FormView):
    """View showing QuestionText flashcard answer with 3 options of result ("wrong", correct but difficult", "correct")
    after choosing result new record is saved in flashcardstextstatus table and user is redirect to the
    FlashcardTextQuestionView
    """
    form_class = FlashcardTextAnswerForm
    template_name = 'flashcardtextanswer.html'

    def get_queryset(self):
        """Session and QuestionText id are get form the URL"""
        query_set = super().get_queryset()
        return query_set.filter(session_id=int(self.kwargs['session_id'])).filter(questiontext_id=int(self.kwargs['questiontext_id']))

    def get_context_data(self):
        """Getting context to display answer"""
        context = super().get_context_data()
        context['flashcard'] = QuestionText.objects.get(id=int(self.kwargs['questiontext_id']))
        return context

    def form_valid(self, form):
        """Result is choosing and new record is saved in flashcardstextstatus table"""
        session = Session.objects.get(id=int(self.kwargs['session_id']))
        flashcard = QuestionText.objects.get(id=int(self.kwargs['questiontext_id']))
        result = form.cleaned_data['result']

        FlashCardsTextStatus.objects.create(result=result, session=session, flash_card=flashcard)
        return super().form_valid(form)

    def get_success_url(self) -> str:
        """Redirect to FlashcardTextQuestionView"""
        session = Session.objects.get(id=int(self.kwargs['session_id']))
        return reverse('flashcard_question', kwargs={'session_id': session.id})


class FinishPageView(LoginRequiredMixin, View):
    """View diplay after finishing learn session, with brief summary"""
    def get(self, request, session_id):
        flashcards_done = FlashCardsTextStatus.objects.filter(session_id=session_id)
        session = Session.objects.get(id=session_id)
        category = session.category.category_name
        flashcards_id_list = []
        for card in flashcards_done:
            if card.flash_card_id not in flashcards_id_list:
                flashcards_id_list.append(card.flash_card_id)
        amount = len(flashcards_id_list)
        time = flashcards_done[len(flashcards_done)-1].date - flashcards_done[0].date
        return render(request, "finish_page.html", context={"amount": amount, "time": time, "category": category})


class ProfileView(LoginRequiredMixin, View):
    """View of user profile, at this moment with link change password page"""
    def get(self, request):
        return render(request, "profile.html")


class AddImageFlashcardView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    """View allowing to create QuestionImage flashcards for logged users"""
    model = QuestionImage
    fields = ['question', 'answer', 'categories']
    success_url = reverse_lazy('add_imageflashcard')
    success_message = 'flashcard added'

    def form_valid(self, form):
        """logged user is assigned as QuestionText object user"""
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.save()
        return super().form_valid(form)


class FlashcardsImageListView(LoginRequiredMixin, ListView):
    """List of QuestionImage flashcards created by logged user with links to update and delete views
    (views to be added)"""
    paginate_by = 20
    model = QuestionImage
    ordering = ('question', 'answer')

    def get_queryset(self):
        """Filtering to return only flashcards created by logged user"""
        query_set = super().get_queryset()
        return query_set.filter(user_id=self.request.user.id)
