from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, URLValidator
from django.forms import ModelForm

from .models import Category, QuestionText, FlashCardsTextStatus


class AddCategoryForm(ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


# class LoginForm(forms.Form):
#     username = forms.CharField(max_length=255)
#     password = forms.CharField(widget=forms.PasswordInput)



class FlashcardTextAnswerForm(ModelForm):
    class Meta:
        model = FlashCardsTextStatus
        fields = ['result']
        widgets = {
            'result': forms.Select,
        }
